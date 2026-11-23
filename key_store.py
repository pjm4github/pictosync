"""
key_store.py

Durable, app-managed storage for API keys so a key set in the setup wizard
survives a restart or reboot — independent of ``setx`` / registry inheritance
quirks (e.g. a launcher that hands the relaunched app a stale environment).

Keys are stored by their *environment-variable name* in
``<user_settings_dir>/api_keys.dat`` and loaded back into ``os.environ`` at app
startup, so the rest of the app keeps reading them as ordinary env vars. A real
environment variable of the same name always wins over the stored copy.

On Windows the value is encrypted with DPAPI (``CryptProtectData``, per-user,
via ctypes — no extra dependency), so it is not readable by other users and
never sits on disk in plaintext. On other platforms it falls back to base64
obfuscation (not encryption) and the caller is told so.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

_FILENAME = "api_keys.dat"


# ── DPAPI (Windows) via ctypes ────────────────────────────────────────────

def _dpapi(protect: bool, data: bytes) -> Optional[bytes]:
    """Run CryptProtectData / CryptUnprotectData. Returns None on failure."""
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_char))]

    buf = ctypes.create_string_buffer(data, len(data))
    blob_in = DATA_BLOB(len(data),
                        ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    blob_out = DATA_BLOB()
    func = (ctypes.windll.crypt32.CryptProtectData if protect
            else ctypes.windll.crypt32.CryptUnprotectData)
    ok = func(ctypes.byref(blob_in), None, None, None, None, 0,
              ctypes.byref(blob_out))
    if not ok:
        return None
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


def _encrypt(plaintext: str) -> Dict[str, str]:
    """Encrypt *plaintext*, returning a ``{scheme, value}`` record."""
    raw = plaintext.encode("utf-8")
    enc = _dpapi(True, raw)
    if enc is not None:
        return {"scheme": "dpapi", "value": base64.b64encode(enc).decode("ascii")}
    return {"scheme": "b64", "value": base64.b64encode(raw).decode("ascii")}


def _decrypt(record: Dict[str, str]) -> Optional[str]:
    """Decrypt a ``{scheme, value}`` record back to plaintext."""
    try:
        blob = base64.b64decode(record.get("value", ""))
    except Exception:
        return None
    scheme = record.get("scheme", "b64")
    if scheme == "dpapi":
        dec = _dpapi(False, blob)
        if dec is None:
            return None
        return dec.decode("utf-8", "replace")
    return blob.decode("utf-8", "replace")


# ── store file access ─────────────────────────────────────────────────────

def _path(settings_manager) -> Optional[Path]:
    directory = getattr(settings_manager, "user_settings_dir", None)
    if directory is None:
        return None
    return Path(directory) / _FILENAME


def _read_map(settings_manager) -> Dict[str, Dict[str, str]]:
    path = _path(settings_manager)
    if path is None:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if isinstance(v, dict)}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def _write_map(settings_manager, data: Dict[str, Dict[str, str]]) -> None:
    path = _path(settings_manager)
    if path is None:
        raise OSError("No settings directory available for key store.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".dat.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    tmp.replace(path)
    # Best-effort: restrict the file to the current user on Windows.
    if os.name == "nt":
        try:
            import subprocess
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            user = os.environ.get("USERNAME", "")
            if user:
                subprocess.run(
                    ["icacls", str(path), "/inheritance:r",
                     "/grant:r", f"{user}:F"],
                    capture_output=True, timeout=10, creationflags=flags)
        except Exception:
            pass


# ── public API ─────────────────────────────────────────────────────────────

def save_key(settings_manager, env_name: str, key: str) -> Tuple[bool, str]:
    """Persist *key* under *env_name* and set it in the current environment.

    Args:
        settings_manager: The app SettingsManager (for the storage directory).
        env_name: Environment-variable name the key is stored under.
        key: The secret value.

    Returns:
        ``(encrypted, scheme)`` where *encrypted* is True when DPAPI was used.
    """
    env_name = (env_name or "").strip()
    if not env_name:
        raise ValueError("env_name is required")
    os.environ[env_name] = key  # immediate: this running process
    record = _encrypt(key)
    data = _read_map(settings_manager)
    data[env_name] = record
    _write_map(settings_manager, data)
    return record["scheme"] == "dpapi", record["scheme"]


def delete_key(settings_manager, env_name: str) -> None:
    """Remove the stored key for *env_name* (leaves the live env var alone)."""
    data = _read_map(settings_manager)
    if env_name in data:
        del data[env_name]
        _write_map(settings_manager, data)


def has_key(settings_manager, env_name: str) -> bool:
    """Return True if a key is stored for *env_name*."""
    return env_name in _read_map(settings_manager)


def export_all(settings_manager) -> Dict[str, str]:
    """Decrypt and return every legacy-stored key as ``{env_name: value}``.

    Used to migrate keys saved by the old per-key DPAPI store into the vault.
    Entries that can't be decrypted are skipped.
    """
    out: Dict[str, str] = {}
    for name, record in _read_map(settings_manager).items():
        value = _decrypt(record)
        if value:
            out[name] = value
    return out


def legacy_file_exists(settings_manager) -> bool:
    """True if the old per-key store file is present."""
    path = _path(settings_manager)
    return bool(path and path.exists())


def load_keys_into_env(settings_manager) -> int:
    """Load stored keys into ``os.environ`` (real env vars take precedence).

    Call once at application startup, before any provider/worker runs.

    Returns:
        The number of keys loaded into the environment.
    """
    loaded = 0
    for name, record in _read_map(settings_manager).items():
        if os.environ.get(name, "").strip():
            continue  # a real environment variable wins
        value = _decrypt(record)
        if value:
            os.environ[name] = value
            loaded += 1
    return loaded
