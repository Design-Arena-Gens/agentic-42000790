from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem

from app.core.db import Database


class StockView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.refreshBtn = QPushButton(self.tr("Actualiser"))
        top.addWidget(self.refreshBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([self.tr("Produit ID"), self.tr("SKU"), self.tr("Quantit?")])
        layout.addWidget(self.table)

        self.refreshBtn.clicked.connect(self._load)

    def _load(self) -> None:
        rows = self.db.query("""
        SELECT p.id as product_id, p.sku as sku, IFNULL(s.qty,0) as qty
        FROM products p
        LEFT JOIN stock s ON s.product_id=p.id
        ORDER BY p.id DESC
        """)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["product_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["sku"]))
            self.table.setItem(r, 2, QTableWidgetItem(str(row["qty"])))
        self.table.resizeColumnsToContents()

