from __future__ import annotations

from datetime import date
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem

from app.core.db import Database


class PurchasesView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.addBtn = QPushButton(self.tr("Nouvel achat"))
        self.refreshBtn = QPushButton(self.tr("Actualiser"))
        top.addWidget(self.addBtn)
        top.addWidget(self.refreshBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Num?ro"), self.tr("Date"), self.tr("Total TTC")])
        layout.addWidget(self.table)

        self.addBtn.clicked.connect(self._add)
        self.refreshBtn.clicked.connect(self._load)

    def _load(self) -> None:
        rows = self.db.query("SELECT id, number, date, total_ttc FROM documents WHERE kind='purchase' ORDER BY id DESC;")
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["number"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["date"]))
            self.table.setItem(r, 3, QTableWidgetItem(f"{row['total_ttc']:.2f}"))
        self.table.resizeColumnsToContents()

    @Slot()
    def _add(self) -> None:
        # minimal purchase document
        last = self.db.query("SELECT number FROM documents WHERE kind='purchase' ORDER BY id DESC LIMIT 1;")
        if not last:
            number = "PUR-000001"
        else:
            l = last[0]["number"]
            try:
                n = int(l.split("-")[-1]) + 1
            except Exception:
                n = 1
            number = f"PUR-{n:06d}"
        self.db.execute("INSERT INTO documents (kind, number, date, status) VALUES ('purchase', ?, ?, 'draft');", (number, date.today().isoformat()))
        doc_id = self.db.scalar("SELECT last_insert_rowid();")
        self.db.execute("INSERT INTO document_lines (document_id, description, qty, unit_price) VALUES (?, 'Achat', 1, 50.0);", (doc_id,))
        self.db.execute("""
        UPDATE documents SET 
            total_ht=(SELECT SUM(qty*unit_price) FROM document_lines WHERE document_id=?),
            total_tva=ROUND((SELECT SUM(qty*unit_price*0.2) FROM document_lines WHERE document_id=?),2),
            total_ttc=ROUND((SELECT SUM(qty*unit_price*1.2) FROM document_lines WHERE document_id=?),2)
        WHERE id=?;
        """, (doc_id, doc_id, doc_id, doc_id))
        self._load()

