"""
provider_setup_wizard.py

A short "walk me through it" wizard for getting a vision provider ready:

  1. **Library** — detect whether the provider's SDK is installed and, if not,
     run ``pip install <package>`` right here (into the running interpreter /
     virtualenv), streaming the output.
  2. **API key** — choose the environment-variable *name* that will hold the
     key (so it can be dedicated to PictoSync + this provider), paste the key,
     and save it. The key is applied to the current session immediately and,
     applied to the current session immediately and saved durably (encrypted
     with DPAPI on Windows) so it survives a restart/reboot.
  3. **Verify** — do a live "list models" call to confirm the key + SDK work.

The key value is never written to a settings file or logged; only the env-var
*name* is persisted (in ``settings.ai_providers``).
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QProcess, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from providers import get_provider, get_spec, resolve_api_key, sdk_installed


def _recheck_sdk(spec) -> bool:
    """Re-check SDK availability after a possible install."""
    import importlib
    importlib.invalidate_caches()
    return sdk_installed(spec)


class LibraryPage(QWizardPage):
    """Page 1 — detect and install the provider SDK."""

    def __init__(self, spec, parent=None):
        super().__init__(parent)
        self.spec = spec
        self._proc: Optional[QProcess] = None
        self.setTitle(f"1. Install the {spec.label} library")
        self.setSubTitle(
            f"PictoSync talks to {spec.label} through the "
            f"'{spec.pip_package}' Python package.")

        lay = QVBoxLayout(self)
        self.status = QLabel("")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        row = QHBoxLayout()
        self.install_btn = QPushButton(f"Install {spec.pip_package}")
        self.install_btn.clicked.connect(self._install)
        row.addWidget(self.install_btn)
        self.recheck_btn = QPushButton("Re-check")
        self.recheck_btn.clicked.connect(self._refresh)
        row.addWidget(self.recheck_btn)
        row.addStretch()
        lay.addLayout(row)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("pip output appears here…")
        lay.addWidget(self.log, 1)

        hint = QLabel(
            f"Installs into:\n{sys.executable}\n\n"
            "If install fails behind a proxy, install it yourself in a "
            f"terminal:\n    {spec.install_hint}")
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#666; font-size:11px;")
        lay.addWidget(hint)

    def initializePage(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        if _recheck_sdk(self.spec):
            self.status.setText(
                f"<b style='color:#16a34a'>✓ {self.spec.pip_package} is "
                "installed.</b> You can continue.")
            self.install_btn.setEnabled(False)
        else:
            self.status.setText(
                f"<b style='color:#d97706'>{self.spec.pip_package} is not "
                "installed.</b> Click Install, or install it yourself and "
                "click Re-check.")
            self.install_btn.setEnabled(True)
        self.completeChanged.emit()

    def _install(self) -> None:
        if self._proc is not None:
            return
        self.log.clear()
        self.install_btn.setEnabled(False)
        self.recheck_btn.setEnabled(False)
        self.status.setText("Installing… this can take a minute.")
        self._proc = QProcess(self)
        self._proc.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels)
        self._proc.readyReadStandardOutput.connect(self._read)
        self._proc.finished.connect(self._done)
        self._proc.start(
            sys.executable,
            ["-m", "pip", "install", "--upgrade", self.spec.pip_package])

    def _read(self) -> None:
        if self._proc is None:
            return
        chunk = bytes(self._proc.readAllStandardOutput()).decode(
            "utf-8", "replace")
        if chunk:
            self.log.appendPlainText(chunk.rstrip("\n"))

    def _done(self, code: int, _status) -> None:
        self._proc = None
        self.recheck_btn.setEnabled(True)
        if code == 0:
            self.log.appendPlainText("\n[pip finished successfully]")
        else:
            self.log.appendPlainText(f"\n[pip exited with code {code}]")
        self._refresh()

    def isComplete(self) -> bool:
        # Allow advancing regardless; Verify will catch a real failure. But the
        # button state reflects install status for guidance.
        return True


class KeyPage(QWizardPage):
    """Page 2 — name the env var, enter the key, save it."""

    def __init__(self, spec, cfg, settings_manager, parent=None):
        super().__init__(parent)
        self.spec = spec
        self.cfg = cfg
        self.settings_manager = settings_manager
        self.setTitle(f"2. Set your {spec.label} API key")
        self.setSubTitle(
            "The key is read from an environment variable. You choose its "
            "name, so you can dedicate a key to PictoSync.")

        lay = QVBoxLayout(self)

        getkey = QPushButton("Open the API keys page in my browser…")
        getkey.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(spec.api_keys_url)))
        lay.addWidget(getkey)

        lay.addWidget(QLabel("Environment variable name:"))
        self.name_edit = QLineEdit(cfg.env_key or spec.default_env_key)
        self.name_edit.textChanged.connect(self._on_name_changed)
        lay.addWidget(self.name_edit)

        lay.addWidget(QLabel("API key (paste it here):"))
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("Leave blank if the variable is "
                                         "already set")
        lay.addWidget(self.key_edit)

        row = QHBoxLayout()
        self.save_btn = QPushButton("Save key")
        self.save_btn.clicked.connect(self._save)
        row.addWidget(self.save_btn)
        self.show_btn = QPushButton("Show")
        self.show_btn.setCheckable(True)
        self.show_btn.toggled.connect(self._toggle_show)
        row.addWidget(self.show_btn)
        row.addStretch()
        lay.addLayout(row)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        note = QLabel(
            "Saving stores the key in PictoSync's encrypted vault (unlocked by "
            "your single PICTOSYNC_VAULT_KEY) and applies it to this running "
            "app. It reloads automatically whenever the vault is unlocked. A "
            "real environment variable of the same name always overrides it.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#666; font-size:11px;")
        lay.addWidget(note)

    def initializePage(self) -> None:
        self._refresh_status()

    def _toggle_show(self, on: bool) -> None:
        self.key_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password)
        self.show_btn.setText("Hide" if on else "Show")

    def _on_name_changed(self, text: str) -> None:
        name = text.strip()
        if name:
            self.cfg.env_key = name
        self._refresh_status()

    def _refresh_status(self) -> None:
        name = self.name_edit.text().strip()
        if name and resolve_api_key(name):
            self.status.setText(
                f"<b style='color:#16a34a'>✓ {name} is set</b> for this "
                "session.")
        else:
            self.status.setText(
                f"<b style='color:#d97706'>{name or '(no name)'} is not set.</b>")
        self.completeChanged.emit()

    def _save(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            self.status.setText(
                "<b style='color:#dc2626'>Enter a variable name first.</b>")
            return
        key = self.key_edit.text().strip()
        if not key:
            # Nothing to save, but maybe it's already set in the environment.
            self._refresh_status()
            return

        # Store the key in the encrypted vault (unlocked by PICTOSYNC_VAULT_KEY).
        # If the vault isn't set up / unlocked yet, run its wizard first.
        import vault
        from vault_wizard import ensure_unlocked
        if not (vault.vault_key_present() and vault.vault_exists(
                self.settings_manager)):
            if not ensure_unlocked(self.settings_manager, self):
                self.status.setText(
                    "<b style='color:#d97706'>Vault not unlocked — key not "
                    "saved. Set up the key vault first.</b>")
                return

        try:
            vault.save_key(self.settings_manager, name, key)
        except Exception as exc:
            os.environ[name] = key  # at least keep this session working
            self.status.setText(
                f"<b style='color:#d97706'>⚠ {name} set for this session, but "
                f"saving to the vault failed: {exc}</b>")
            self.key_edit.clear()
            self.show_btn.setChecked(False)
            self.completeChanged.emit()
            return

        # Clear the field so the secret doesn't linger on screen.
        self.key_edit.clear()
        self.show_btn.setChecked(False)
        self.status.setText(
            f"<b style='color:#16a34a'>✓ {name} saved to the encrypted vault. "
            "It loads automatically whenever the vault is unlocked.</b>")
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        name = self.name_edit.text().strip()
        return bool(name and resolve_api_key(name))


class VerifyPage(QWizardPage):
    """Page 3 — live test the connection."""

    def __init__(self, spec, cfg, parent=None):
        super().__init__(parent)
        self.spec = spec
        self.cfg = cfg
        self._ok = False
        self.setTitle(f"3. Verify {spec.label}")
        self.setSubTitle("Confirm the library and key work with a real call.")

        lay = QVBoxLayout(self)
        self.test_btn = QPushButton("Test connection")
        self.test_btn.clicked.connect(self._test)
        lay.addWidget(self.test_btn)
        self.status = QLabel("Click Test connection.")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        lay.addWidget(self.detail, 1)

    def _test(self) -> None:
        from providers.base import ProviderError

        name = self.cfg.env_key or self.spec.default_env_key
        key = resolve_api_key(name)
        if not key:
            self.status.setText(
                f"<b style='color:#dc2626'>{name} is not set.</b> Go back a "
                "step.")
            return
        if not _recheck_sdk(self.spec):
            self.status.setText(
                f"<b style='color:#dc2626'>{self.spec.pip_package} is not "
                "installed.</b> Go back a step.")
            return

        self.status.setText("Testing…")
        self.detail.clear()
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            rows = get_provider(self.spec.id).list_models(key)
        except ProviderError as exc:
            self._ok = False
            self.status.setText(
                "<b style='color:#dc2626'>Test failed.</b>")
            self.detail.setPlainText(str(exc))
            self.completeChanged.emit()
            return
        finally:
            QApplication.restoreOverrideCursor()

        self._ok = True
        names = [r.name for r in rows]
        if names:
            self.cfg.models = names
            if self.cfg.default_model not in names:
                self.cfg.default_model = names[0]
        self.status.setText(
            f"<b style='color:#16a34a'>✓ Connected — {len(names)} models "
            "available.</b> Click Finish.")
        self.detail.setPlainText("\n".join(names[:60]))
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        return self._ok


class ProviderSetupWizard(QWizard):
    """Three-step setup wizard for one provider."""

    def __init__(self, settings_manager, provider_id: str,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.provider_id = provider_id
        spec = get_spec(provider_id)
        cfg = settings_manager.settings.ai_providers.providers.get(provider_id)
        if cfg is None:
            from settings import AIProviderConfig
            cfg = AIProviderConfig(env_key=spec.default_env_key)
            settings_manager.settings.ai_providers.providers[provider_id] = cfg
        self.cfg = cfg

        self.setWindowTitle(f"Set up {spec.label}")
        self.resize(640, 560)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.addPage(LibraryPage(spec, self))
        self.addPage(KeyPage(spec, cfg, settings_manager, self))
        self.addPage(VerifyPage(spec, cfg, self))

    def accept(self) -> None:
        # Persist the env-var name / discovered models (never the key itself).
        try:
            self.settings_manager.save()
        except Exception:
            pass
        super().accept()
