from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QVBoxLayout, QFileDialog

from app.core.db import Database
from app.core.settings import AppSettings


class SettingsDialog(QDialog):
    def __init__(self, db: Database, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings = settings
        self.setWindowTitle(self.tr("Param?tres"))
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.vatEdit = QLineEdit(self)
        self.currencyEdit = QLineEdit(self)
        self.logoEdit = QLineEdit(self)
        self.logoBtn = QPushButton(self.tr("Choisir..."))
        self.invSeqEdit = QLineEdit(self)
        self.quoteSeqEdit = QLineEdit(self)
        self.delivSeqEdit = QLineEdit(self)
        form.addRow(self.tr("TVA (%)"), self.vatEdit)
        form.addRow(self.tr("Devise"), self.currencyEdit)
        form.addRow(self.tr("Logo"), self.logoEdit)
        form.addRow("", self.logoBtn)
        form.addRow(self.tr("Num?rotation facture"), self.invSeqEdit)
        form.addRow(self.tr("Num?rotation devis"), self.quoteSeqEdit)
        form.addRow(self.tr("Num?rotation BL"), self.delivSeqEdit)
        layout.addLayout(form)
        self.saveBtn = QPushButton(self.tr("Enregistrer"))
        layout.addWidget(self.saveBtn)
        self.logoBtn.clicked.connect(self._choose_logo)
        self.saveBtn.clicked.connect(self._save)

    def _load(self) -> None:
        self.vatEdit.setText(self.settings.get("vat_rate", "20.0") or "")
        self.currencyEdit.setText(self.settings.get("currency", "EUR") or "")
        self.logoEdit.setText(self.settings.get("company_logo_path", "") or "")
        self.invSeqEdit.setText(self.settings.get("invoice_seq", "INV-000000") or "")
        self.quoteSeqEdit.setText(self.settings.get("quote_seq", "QTE-000000") or "")
        self.delivSeqEdit.setText(self.settings.get("delivery_seq", "BL-000000") or "")

    @Slot()
    def _choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Choisir le logo"), "", self.tr("Images (*.png *.jpg *.jpeg)"))
        if path:
            self.logoEdit.setText(path)

    @Slot()
    def _save(self) -> None:
        self.settings.set("vat_rate", self.vatEdit.text().strip())
        self.settings.set("currency", self.currencyEdit.text().strip())
        self.settings.set("company_logo_path", self.logoEdit.text().strip())
        self.settings.set("invoice_seq", self.invSeqEdit.text().strip())
        self.settings.set("quote_seq", self.quoteSeqEdit.text().strip())
        self.settings.set("delivery_seq", self.delivSeqEdit.text().strip())
        self.accept()

