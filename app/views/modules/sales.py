from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPdf import QPdfDocument

from app.core.db import Database
from app.core.pdf import generate_document_pdf


class SalesView(QWidget):
    def __init__(self, db: Database, parent=None, kind: str = "invoice"):
        super().__init__(parent)
        self.db = db
        self.kind = kind
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.addBtn = QPushButton(self.tr("Nouveau"))
        self.genPdfBtn = QPushButton(self.tr("PDF"))
        self.previewBtn = QPushButton(self.tr("Aper?u"))
        top.addWidget(self.addBtn)
        top.addWidget(self.genPdfBtn)
        top.addWidget(self.previewBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Num?ro"), self.tr("Date"), self.tr("Client"), self.tr("Total TTC"), self.tr("Statut")])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        self.pdfDoc = QPdfDocument(self)
        self.pdfView = QPdfView(self)
        self.pdfView.setDocument(self.pdfDoc)
        layout.addWidget(self.pdfView)

        self.addBtn.clicked.connect(self._add)
        self.genPdfBtn.clicked.connect(self._export_pdf)
        self.previewBtn.clicked.connect(self._preview_pdf)

    def _load(self) -> None:
        rows = self.db.query("""
        SELECT d.id, d.number, d.date, d.total_ttc, d.status, IFNULL(p.name_fr,'') as partner
        FROM documents d
        LEFT JOIN partners p ON p.id=d.partner_id
        WHERE d.kind=?
        ORDER BY d.id DESC
        """, (self.kind,))
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["number"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["date"]))
            self.table.setItem(r, 3, QTableWidgetItem(row["partner"]))
            self.table.setItem(r, 4, QTableWidgetItem(f"{row['total_ttc']:.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(row["status"]))
        self.table.resizeColumnsToContents()

    def _current_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return int(self.table.item(indexes[0].row(), 0).text())

    def _next_number(self) -> str:
        prefix = {
            "invoice": "INV-",
            "quote": "QTE-",
            "delivery": "BL-",
        }.get(self.kind, "DOC-")
        last = self.db.query("SELECT number FROM documents WHERE kind=? ORDER BY id DESC LIMIT 1;", (self.kind,))
        if not last:
            return f"{prefix}000001"
        l = last[0]["number"]
        try:
            n = int(l.split("-")[-1]) + 1
        except Exception:
            n = 1
        return f"{prefix}{n:06d}"

    @Slot()
    def _add(self) -> None:
        number = self._next_number()
        self.db.execute("INSERT INTO documents (kind, number, date, status) VALUES (?, ?, ?, 'draft');", (self.kind, number, date.today().isoformat()))
        doc_id = self.db.scalar("SELECT last_insert_rowid();")
        # Minimal line
        self.db.execute("INSERT INTO document_lines (document_id, description, qty, unit_price) VALUES (?, ?, 1, 100.0);", (doc_id, f"Ligne {number}"))
        # Totals
        self.db.execute("""
        UPDATE documents SET 
            total_ht=(SELECT SUM(qty*unit_price) FROM document_lines WHERE document_id=?),
            total_tva=ROUND((SELECT SUM(qty*unit_price*0.2) FROM document_lines WHERE document_id=?),2),
            total_ttc=ROUND((SELECT SUM(qty*unit_price*1.2) FROM document_lines WHERE document_id=?),2)
        WHERE id=?;
        """, (doc_id, doc_id, doc_id, doc_id))
        self._load()

    def _generate_pdf_to_path(self, doc_id: int, path: Path) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        generate_document_pdf(self.db, doc_id, path, base_dir)

    @Slot()
    def _export_pdf(self) -> None:
        doc_id = self._current_id()
        if not doc_id:
            return
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Exporter PDF"), f"{self.kind}-{doc_id}.pdf", self.tr("PDF (*.pdf)"))
        if not path:
            return
        self._generate_pdf_to_path(doc_id, Path(path))
        QMessageBox.information(self, self.tr("Succ?s"), self.tr("PDF g?n?r?"))

    @Slot()
    def _preview_pdf(self) -> None:
        doc_id = self._current_id()
        if not doc_id:
            return
        tmp = Path.cwd() / f"preview-{self.kind}-{doc_id}.pdf"
        self._generate_pdf_to_path(doc_id, tmp)
        self.pdfDoc.load(str(tmp))

