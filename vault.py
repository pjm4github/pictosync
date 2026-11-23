"""
vault.py

A single-key encrypted vault for all vendor API keys.

One master secret — the ``PICTOSYNC_VAULT_KEY`` environment variable — unlocks
one encrypted file (``vault.dat``) that holds every saved API key, keyed by its
environment-variable name. The master key is required for every operation:
reading, creating, updating and deleting a key all decrypt → modify → re-encrypt
the file with it.

Cryptography (stdlib only — no external dependency):
  * KDF: scrypt(passphrase, random 16-byte salt) → 64 bytes, split into a
    32-byte encryption key and a 32-byte MAC key.
  * Confidentiality: HMAC-SHA256 counter-mode keystream XORed with the plaintext.
  * Integrity/authenticity: HMAC-SHA256 over salt|nonce|ciphertext
    (encrypt-then-MAC). A wrong passphrase derives a different MAC key, so the
    tag check fails and we can report "wrong vault key" vs "corrupt file".

Persistence of the master key itself: optionally remembered on this machine by
encrypting it with Windows DPAPI (per-user) in ``vault_key.dat`` and reloading
it into the environment at startup. Otherwise the user supplies
``PICTOSYNC_VAULT_KEY`` through the real environment each session.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import struct
from pathlib import Path
from typing import Dict, List, Optional

VAULT_KEY_ENV = "PICTOSYNC_VAULT_KEY"

_VAULT_FILE = "vault.dat"
_VAULT_KEY_FILE = "vault_key.dat"

_SCRYPT_N = 1 << 14      # 16384
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_MAXMEM = 64 * 1024 * 1024


class VaultLocked(RuntimeError):
    """Raised when an operation needs the vault key but it isn't available."""


class VaultKeyError(RuntimeError):
    """Raised when the supplied vault key can't decrypt the vault (wrong key)."""


# ── DPAPI (Windows) for remembering the master key ────────────────────────

def _dpapi(protect: bool, data: bytes) -> Optional[bytes]:
    """CryptProtectData / CryptUnprotectData via ctypes. None on failure."""
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
    if not func(ctypes.byref(blob_in), None, None, None, None, 0,
                ctypes.byref(blob_out)):
        return None
    try:
        return ctypes.string_at(blob_out.pbData, blob_out.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob_out.pbData)


# ── cipher ────────────────────────────────────────────────────────────────

def _derive(passphrase: str, salt: bytes, n: int, r: int, p: int):
    dk = hashlib.scrypt(
        passphrase.encode("utf-8"), salt=salt, n=n, r=r, p=p,
        dklen=64, maxmem=_SCRYPT_MAXMEM)
    return dk[:32], dk[32:]


def _keystream(enc_key: bytes, nonce: bytes, nbytes: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < nbytes:
        out.extend(hmac.new(
            enc_key, nonce + struct.pack(">Q", counter), hashlib.sha256
        ).digest())
        counter += 1
    return bytes(out[:nbytes])


def _xor(data: bytes, ks: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(data, ks))


def _encrypt(passphrase: str, plaintext: bytes) -> Dict:
    salt = os.urandom(16)
    nonce = os.urandom(16)
    enc_key, mac_key = _derive(passphrase, salt, _SCRYPT_N, _SCRYPT_R, _SCRYPT_P)
    ct = _xor(plaintext, _keystream(enc_key, nonce, len(plaintext)))
    tag = hmac.new(mac_key, salt + nonce + ct, hashlib.sha256).digest()
    b64 = lambda b: base64.b64encode(b).decode("ascii")
    return {
        "version": 1, "kdf": "scrypt",
        "n": _SCRYPT_N, "r": _SCRYPT_R, "p": _SCRYPT_P,
        "salt": b64(salt), "nonce": b64(nonce),
        "ciphertext": b64(ct), "tag": b64(tag),
    }


def _decrypt(passphrase: str, rec: Dict) -> bytes:
    try:
        salt = base64.b64decode(rec["salt"])
        nonce = base64.b64decode(rec["nonce"])
        ct = base64.b64decode(rec["ciphertext"])
        tag = base64.b64decode(rec["tag"])
        n = int(rec.get("n", _SCRYPT_N))
        r = int(rec.get("r", _SCRYPT_R))
        p = int(rec.get("p", _SCRYPT_P))
    except (KeyError, ValueError, TypeError) as exc:
        raise VaultKeyError("Vault file is malformed.") from exc
    enc_key, mac_key = _derive(passphrase, salt, n, r, p)
    expected = hmac.new(mac_key, salt + nonce + ct, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, tag):
        raise VaultKeyError("Wrong vault key (or the vault file was altered).")
    return _xor(ct, _keystream(enc_key, nonce, len(ct)))


# ── paths ─────────────────────────────────────────────────────────────────

def _dir(sm) -> Optional[Path]:
    d = getattr(sm, "user_settings_dir", None)
    return Path(d) if d is not None else None


def _vault_path(sm) -> Optional[Path]:
    d = _dir(sm)
    return (d / _VAULT_FILE) if d else None


def _vault_key_path(sm) -> Optional[Path]:
    d = _dir(sm)
    return (d / _VAULT_KEY_FILE) if d else None


def _secure_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    tmp.replace(path)
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


# ── master-key state ──────────────────────────────────────────────────────

def vault_key_present() -> bool:
    """True if ``PICTOSYNC_VAULT_KEY`` is set in the environment."""
    return bool(os.environ.get(VAULT_KEY_ENV, "").strip())


def _current_key() -> str:
    key = os.environ.get(VAULT_KEY_ENV, "").strip()
    if not key:
        raise VaultLocked(
            f"The vault is locked: {VAULT_KEY_ENV} is not set. Run the key "
            "vault setup to unlock it.")
    return key


def set_session_key(passphrase: str) -> None:
    """Make *passphrase* the active vault key for this running process."""
    os.environ[VAULT_KEY_ENV] = passphrase


def remember_key(sm, passphrase: str) -> bool:
    """Persist the vault key on this machine (DPAPI). Returns True if encrypted.

    Falls back to raising on non-Windows (the caller should keep the env var).
    """
    enc = _dpapi(True, passphrase.encode("utf-8"))
    path = _vault_key_path(sm)
    if path is None:
        raise OSError("No settings directory for the vault key.")
    if enc is not None:
        _secure_write(path, json.dumps(
            {"scheme": "dpapi",
             "value": base64.b64encode(enc).decode("ascii")}))
        return True
    _secure_write(path, json.dumps(
        {"scheme": "b64",
         "value": base64.b64encode(passphrase.encode("utf-8")).decode("ascii")}))
    return False


def forget_remembered_key(sm) -> None:
    """Delete the remembered (DPAPI) vault key, if any. Env var is untouched."""
    path = _vault_key_path(sm)
    if path and path.exists():
        try:
            path.unlink()
        except OSError:
            pass


def is_key_remembered(sm) -> bool:
    path = _vault_key_path(sm)
    return bool(path and path.exists())


def load_vault_key_into_env(sm) -> bool:
    """Load a remembered vault key into the environment at startup.

    A real ``PICTOSYNC_VAULT_KEY`` already in the environment takes precedence.

    Returns:
        True if a key is available in the environment afterwards.
    """
    if vault_key_present():
        return True
    path = _vault_key_path(sm)
    if not path or not path.exists():
        return False
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
        blob = base64.b64decode(rec.get("value", ""))
    except Exception:
        return False
    if rec.get("scheme") == "dpapi":
        dec = _dpapi(False, blob)
        if dec is None:
            return False
        os.environ[VAULT_KEY_ENV] = dec.decode("utf-8", "replace")
    else:
        os.environ[VAULT_KEY_ENV] = blob.decode("utf-8", "replace")
    return True


# ── vault file contents ───────────────────────────────────────────────────

def vault_exists(sm) -> bool:
    path = _vault_path(sm)
    return bool(path and path.exists())


def read_all(sm) -> Dict[str, str]:
    """Return every stored key as ``{env_name: value}``.

    Raises:
        VaultLocked: if the vault key isn't available.
        VaultKeyError: if the key can't decrypt the vault.
    """
    key = _current_key()
    path = _vault_path(sm)
    if not path or not path.exists():
        return {}
    rec = json.loads(path.read_text(encoding="utf-8"))
    obj = json.loads(_decrypt(key, rec).decode("utf-8"))
    return {str(k): str(v) for k, v in obj.items()} if isinstance(obj, dict) else {}


def _write_all(sm, mapping: Dict[str, str]) -> None:
    key = _current_key()
    path = _vault_path(sm)
    if path is None:
        raise OSError("No settings directory for the vault.")
    _secure_write(path, json.dumps(_encrypt(key, json.dumps(mapping).encode("utf-8"))))


def create_vault(sm, passphrase: str, initial: Optional[Dict[str, str]] = None) -> None:
    """Create (or overwrite) the vault, encrypting it with *passphrase*.

    Sets *passphrase* as the active session key, then writes the file.
    """
    set_session_key(passphrase)
    _write_all(sm, dict(initial or {}))


def verify_passphrase(sm, passphrase: str) -> bool:
    """Return True if *passphrase* can decrypt the existing vault.

    An absent vault file counts as verifiable (nothing to contradict).
    """
    path = _vault_path(sm)
    if not path or not path.exists():
        return True
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
        _decrypt(passphrase, rec)
        return True
    except (VaultKeyError, json.JSONDecodeError, OSError):
        return False


def change_passphrase(sm, new_passphrase: str) -> None:
    """Re-encrypt the whole vault under *new_passphrase* (vault must be unlocked)."""
    data = read_all(sm)
    create_vault(sm, new_passphrase, data)


# ── per-key operations ────────────────────────────────────────────────────

def save_key(sm, env_name: str, value: str) -> None:
    """Add/update one API key in the vault and in the current environment."""
    env_name = (env_name or "").strip()
    if not env_name:
        raise ValueError("env_name is required")
    data = read_all(sm)
    data[env_name] = value
    _write_all(sm, data)
    os.environ[env_name] = value


def get_key(sm, env_name: str) -> Optional[str]:
    return read_all(sm).get(env_name)


def has_key(sm, env_name: str) -> bool:
    return env_name in read_all(sm)


def list_names(sm) -> List[str]:
    return sorted(read_all(sm).keys())


def delete_key(sm, env_name: str) -> None:
    data = read_all(sm)
    if env_name in data:
        del data[env_name]
        _write_all(sm, data)


def load_keys_into_env(sm) -> int:
    """Decrypt the vault and load keys into ``os.environ`` at startup.

    Silent no-op when the vault is locked or absent. A real environment
    variable of the same name takes precedence.

    Returns:
        Number of keys loaded.
    """
    if not vault_key_present() or not vault_exists(sm):
        return 0
    try:
        data = read_all(sm)
    except (VaultLocked, VaultKeyError, json.JSONDecodeError, OSError):
        return 0
    loaded = 0
    for name, value in data.items():
        if os.environ.get(name, "").strip():
            continue
        os.environ[name] = value
        loaded += 1
    return loaded
