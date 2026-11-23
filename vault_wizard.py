"""
vault_wizard.py

A small wizard to set / unlock the single ``PICTOSYNC_VAULT_KEY`` that
encrypts the API-key vault (see ``vault.py``).

Three situations it handles:
  * **No vault yet** — choose a new vault key (entered twice), optionally
    remember it on this machine (DPAPI), and create the vault. If keys exist in
    the old per-key store, offer to import them.
  * **Vault exists, locked** — enter the existing vault key to unlock; wrong
    keys are rejected (verified against the file). A "reset" path erases the
    vault if the key is forgotten.
  * **Vault already unlocked** — show status; allow changing the key or
    toggling "remember on this machine".
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import vault
import key_store


class VaultSetupDialog(QDialog):
    """Guided setup / unlock for the API-key vault."""

    def __init__(self, settings_manager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.sm = settings_manager
        self.setWindowTitle("PictoSync key vault")
        self.resize(560, 420)
        self._build_ui()
        self._refresh()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        self.intro = QLabel("")
        self.intro.setWordWrap(True)
        root.addWidget(self.intro)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size:11px;")
        root.addWidget(self.status)

        root.addWidget(QLabel("Vault key:"))
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        root.addWidget(self.key_edit)

        self.confirm_label = QLabel("Confirm vault key:")
        root.addWidget(self.confirm_label)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        root.addWidget(self.confirm_edit)

        show_row = QHBoxLayout()
        self.show_cb = QCheckBox("Show key")
        self.show_cb.toggled.connect(self._toggle_show)
        show_row.addWidget(self.show_cb)
        show_row.addStretch()
        root.addLayout(show_row)

        self.remember_cb = QCheckBox(
            "Remember on this computer (encrypted with Windows DPAPI) so the "
            "vault unlocks automatically on startup")
        self.remember_cb.setChecked(True)
        root.addWidget(self.remember_cb)

        self.import_cb = QCheckBox(
            "Import API keys from the previous (non-vault) store")
        self.import_cb.setVisible(False)
        root.addWidget(self.import_cb)

        self.warn = QLabel(
            "If you forget this key, the saved API keys cannot be recovered — "
            "you would have to reset the vault and re-enter them.")
        self.warn.setWordWrap(True)
        self.warn.setStyleSheet("color:#92400e; font-size:11px;")
        root.addWidget(self.warn)

        root.addStretch()

        btn_row = QHBoxLayout()
        self.primary_btn = QPushButton("OK")
        self.primary_btn.clicked.connect(self._on_primary)
        btn_row.addWidget(self.primary_btn)
        self.reset_btn = QPushButton("Reset vault…")
        self.reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    def _toggle_show(self, on: bool) -> None:
        mode = (QLineEdit.EchoMode.Normal if on
                else QLineEdit.EchoMode.Password)
        self.key_edit.setEchoMode(mode)
        self.confirm_edit.setEchoMode(mode)

    # ── state-driven layout ───────────────────────────────────────────────

    def _mode(self) -> str:
        if not vault.vault_exists(self.sm):
            return "create"
        if vault.vault_key_present():
            return "unlocked"
        return "locked"

    def _refresh(self) -> None:
        mode = self._mode()
        self.key_edit.clear()
        self.confirm_edit.clear()
        has_legacy = key_store.legacy_file_exists(self.sm)

        if mode == "create":
            self.intro.setText(
                "<b>Create your key vault.</b> One vault key protects all of "
                "your vendor API keys in a single encrypted file. You'll use "
                "it automatically after this.")
            self.status.setText("")
            self.confirm_label.setVisible(True)
            self.confirm_edit.setVisible(True)
            self.remember_cb.setVisible(True)
            self.import_cb.setVisible(has_legacy)
            self.import_cb.setChecked(has_legacy)
            self.reset_btn.setVisible(False)
            self.warn.setVisible(True)
            self.primary_btn.setText("Create vault")
        elif mode == "locked":
            self.intro.setText(
                "<b>Unlock your key vault.</b> Enter your existing vault key "
                "to decrypt your saved API keys.")
            self.status.setText(
                "<span style='color:#d97706'>Vault is locked.</span>")
            self.confirm_label.setVisible(False)
            self.confirm_edit.setVisible(False)
            self.remember_cb.setVisible(True)
            self.import_cb.setVisible(False)
            self.reset_btn.setVisible(True)
            self.warn.setVisible(False)
            self.primary_btn.setText("Unlock")
        else:  # unlocked
            try:
                n = len(vault.read_all(self.sm))
            except Exception:
                n = 0
            self.intro.setText(
                "<b>Vault is unlocked.</b> You can change the vault key or "
                "update whether it's remembered on this computer.")
            remembered = ("remembered on this computer"
                          if vault.is_key_remembered(self.sm)
                          else "not remembered (set via environment)")
            self.status.setText(
                f"<span style='color:#16a34a'>Unlocked — {n} key(s) stored; "
                f"{remembered}.</span>")
            self.confirm_label.setVisible(True)
            self.confirm_label.setText("Confirm new vault key:")
            self.confirm_edit.setVisible(True)
            self.remember_cb.setChecked(vault.is_key_remembered(self.sm))
            self.remember_cb.setVisible(True)
            self.import_cb.setVisible(False)
            self.reset_btn.setVisible(True)
            self.warn.setVisible(True)
            self.key_edit.setPlaceholderText("Leave blank to keep current key")
            self.primary_btn.setText("Apply")

    # ── actions ───────────────────────────────────────────────────────────

    def _on_primary(self) -> None:
        mode = self._mode()
        if mode == "create":
            self._do_create()
        elif mode == "locked":
            self._do_unlock()
        else:
            self._do_update()

    def _do_create(self) -> None:
        key = self.key_edit.text()
        if len(key.strip()) < 6:
            QMessageBox.warning(self, "Vault",
                                "Choose a vault key of at least 6 characters.")
            return
        if key != self.confirm_edit.text():
            QMessageBox.warning(self, "Vault", "The two entries don't match.")
            return
        initial = {}
        if self.import_cb.isVisible() and self.import_cb.isChecked():
            try:
                initial = key_store.export_all(self.sm)
            except Exception:
                initial = {}
        try:
            vault.create_vault(self.sm, key, initial)
            if self.remember_cb.isChecked():
                vault.remember_key(self.sm, key)
            else:
                vault.forget_remembered_key(self.sm)
            vault.load_keys_into_env(self.sm)
        except Exception as exc:
            QMessageBox.critical(self, "Vault", f"Could not create vault:\n{exc}")
            return
        n = len(initial)
        extra = f" Imported {n} key(s)." if n else ""
        QMessageBox.information(self, "Vault", "Vault created." + extra)
        self.accept()

    def _do_unlock(self) -> None:
        key = self.key_edit.text()
        if not key:
            QMessageBox.warning(self, "Vault", "Enter your vault key.")
            return
        if not vault.verify_passphrase(self.sm, key):
            QMessageBox.warning(
                self, "Vault",
                "That vault key is incorrect. If you've forgotten it, use "
                "Reset vault to start over (saved API keys will be erased).")
            return
        vault.set_session_key(key)
        try:
            if self.remember_cb.isChecked():
                vault.remember_key(self.sm, key)
            else:
                vault.forget_remembered_key(self.sm)
            n = vault.load_keys_into_env(self.sm)
        except Exception as exc:
            QMessageBox.critical(self, "Vault", f"Unlock failed:\n{exc}")
            return
        QMessageBox.information(
            self, "Vault", f"Vault unlocked — {n} key(s) loaded.")
        self.accept()

    def _do_update(self) -> None:
        new_key = self.key_edit.text()
        if new_key:
            if len(new_key.strip()) < 6:
                QMessageBox.warning(
                    self, "Vault", "The new vault key is too short.")
                return
            if new_key != self.confirm_edit.text():
                QMessageBox.warning(self, "Vault", "The two entries don't match.")
                return
            try:
                vault.change_passphrase(self.sm, new_key)
            except Exception as exc:
                QMessageBox.critical(
                    self, "Vault", f"Could not change the vault key:\n{exc}")
                return
        active_key = new_key or os.environ.get(vault.VAULT_KEY_ENV, "")
        try:
            if self.remember_cb.isChecked():
                vault.remember_key(self.sm, active_key)
            else:
                vault.forget_remembered_key(self.sm)
        except Exception as exc:
            QMessageBox.critical(self, "Vault", f"{exc}")
            return
        QMessageBox.information(self, "Vault", "Vault settings updated.")
        self.accept()

    def _on_reset(self) -> None:
        resp = QMessageBox.question(
            self, "Reset vault",
            "This erases the encrypted vault and all saved API keys, so you "
            "can set a new vault key. This cannot be undone.\n\nReset now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return
        path = vault._vault_path(self.sm)
        if path and path.exists():
            try:
                path.unlink()
            except OSError as exc:
                QMessageBox.critical(self, "Vault", f"Could not reset:\n{exc}")
                return
        vault.forget_remembered_key(self.sm)
        os.environ.pop(vault.VAULT_KEY_ENV, None)
        QMessageBox.information(
            self, "Vault", "Vault reset. Create a new vault key.")
        self._refresh()


def ensure_unlocked(settings_manager, parent=None) -> bool:
    """Make sure the vault is set up and unlocked, prompting if needed.

    Returns:
        True if the vault is unlocked (keys can be read/written), else False.
    """
    if vault.vault_key_present() and vault.vault_exists(settings_manager):
        return True
    dlg = VaultSetupDialog(settings_manager, parent)
    dlg.exec()
    return vault.vault_key_present() and vault.vault_exists(settings_manager)
