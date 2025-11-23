from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem

from app.core.db import Database


class CashView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.addInBtn = QPushButton(self.tr("Entr?e"))
        self.addOutBtn = QPushButton(self.tr("Sortie"))
        self.refreshBtn = QPushButton(self.tr("Actualiser"))
        top.addWidget(self.addInBtn)
        top.addWidget(self.addOutBtn)
        top.addWidget(self.refreshBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Mouvement"), self.tr("Montant"), self.tr("Libell?")])
        layout.addWidget(self.table)

        self.addInBtn.clicked.connect(lambda: self._add("in"))
        self.addOutBtn.clicked.connect(lambda: self._add("out"))
        self.refreshBtn.clicked.connect(self._load)

    def _load(self) -> None:
        rows = self.db.query("SELECT id, movement, amount, label FROM cash_register ORDER BY id DESC;")
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["movement"]))
            self.table.setItem(r, 2, QTableWidgetItem(f"{row['amount']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(row["label"]))
        self.table.resizeColumnsToContents()

    @Slot()
    def _add(self, movement: str) -> None:
        amount = 10.0 if movement == "in" else -5.0
        label = "Encaissement" if movement == "in" else "D?caissement"
        self.db.execute("INSERT INTO cash_register (movement, amount, label) VALUES (?, ?, ?);", (movement, abs(amount), label))
        self._load()

