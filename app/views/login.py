from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6 import QtUiTools
from PySide6.QtCore import QFile, QIODevice, Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from app.core.auth import authenticate
from app.core.db import Database
from app.core.i18n import I18n


class LoginDialog(QDialog):
    def __init__(self, db: Database, i18n: I18n, signals, parent=None):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self._user: Optional[dict] = None
        self._load_ui()
        self._wire()
        signals.languageChanged.connect(self._applyTranslations)

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parents[1] / "ui" / "login.ui"
        file = QFile(str(ui_path))
        file.open(QIODevice.ReadOnly)
        loader = QtUiTools.QUiLoader()
        dialog = loader.load(file, self)
        file.close()
        self.setLayout(dialog.layout())
        self.setWindowTitle(dialog.windowTitle())
        self.usernameEdit = dialog.findChild(type(self), "usernameEdit") or dialog.findChild(object, "usernameEdit")
        self.passwordEdit = dialog.findChild(type(self), "passwordEdit") or dialog.findChild(object, "passwordEdit")
        self.loginButton = dialog.findChild(type(self), "loginButton") or dialog.findChild(object, "loginButton")
        self.cancelButton = dialog.findChild(type(self), "cancelButton") or dialog.findChild(object, "cancelButton")
        self.langCombo = dialog.findChild(type(self), "langCombo") or dialog.findChild(object, "langCombo")
        # Fallback attribute resolution
        self.usernameEdit = getattr(dialog, "usernameEdit", self.usernameEdit)
        self.passwordEdit = getattr(dialog, "passwordEdit", self.passwordEdit)
        self.loginButton = getattr(dialog, "loginButton", self.loginButton)
        self.cancelButton = getattr(dialog, "cancelButton", self.cancelButton)
        self.langCombo = getattr(dialog, "langCombo", self.langCombo)
        self.setFixedSize(dialog.size())

    def _wire(self) -> None:
        self.loginButton.clicked.connect(self._on_login)
        self.cancelButton.clicked.connect(self.reject)
        self.langCombo.currentIndexChanged.connect(self._on_lang_change)

    @Slot()
    def _on_lang_change(self, idx: int) -> None:
        if idx == 0:
            self.i18n.set_language("fr")
        else:
            self.i18n.set_language("ar")

    @Slot()
    def _on_login(self) -> None:
        username = self.findChild(type(self), "usernameEdit") or self.usernameEdit
        password = self.findChild(type(self), "passwordEdit") or self.passwordEdit
        user = authenticate(self.db, username.text(), password.text())
        if not user:
            QMessageBox.warning(self, self.tr("Erreur"), self.tr("Identifiants invalides"))
            return
        self._user = user
        self.accept()

    def get_authenticated_user(self) -> Optional[dict]:
        return self._user

    def _applyTranslations(self) -> None:
        # Minimal retranslate; since loaded via .ui, Qt takes care of dynamic texts
        pass

