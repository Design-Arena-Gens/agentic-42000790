from __future__ import annotations

from datetime import date
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem

from app.core.db import Database


class PaymentsView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.addBtn = QPushButton(self.tr("Ajouter paiement"))
        self.refreshBtn = QPushButton(self.tr("Actualiser"))
        top.addWidget(self.addBtn)
        top.addWidget(self.refreshBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Document ID"), self.tr("Montant"), self.tr("Date")])
        layout.addWidget(self.table)

        self.addBtn.clicked.connect(self._add)
        self.refreshBtn.clicked.connect(self._load)

    def _load(self) -> None:
        rows = self.db.query("SELECT id, document_id, amount, paid_at FROM payments ORDER BY id DESC;")
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(str(row["document_id"] or "")))
            self.table.setItem(r, 2, QTableWidgetItem(f"{row['amount']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(row["paid_at"]))
        self.table.resizeColumnsToContents()

    @Slot()
    def _add(self) -> None:
        self.db.execute("INSERT INTO payments (document_id, method, amount, paid_at) VALUES (NULL, 'cash', 10.0, ?);", (date.today().isoformat(),))
        self._load()

