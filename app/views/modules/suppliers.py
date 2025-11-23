from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox

from app.core.db import Database


class SuppliersView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._page = 1
        self._page_size = 20
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.searchEdit = QLineEdit(self)
        self.searchEdit.setPlaceholderText(self.tr("Rechercher fournisseur..."))
        self.addBtn = QPushButton(self.tr("Ajouter"))
        self.editBtn = QPushButton(self.tr("Modifier"))
        self.delBtn = QPushButton(self.tr("Supprimer"))
        top.addWidget(self.searchEdit)
        top.addWidget(self.addBtn)
        top.addWidget(self.editBtn)
        top.addWidget(self.delBtn)
        layout.addLayout(top)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Nom (FR)"), self.tr("Nom (AR)"), self.tr("T?l?phone"), self.tr("Email")])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        bottom = QHBoxLayout()
        self.pageSpin = QSpinBox(self)
        self.pageSpin.setMinimum(1)
        self.pageSpin.setValue(1)
        self.pageSizeSpin = QSpinBox(self)
        self.pageSizeSpin.setRange(10, 200)
        self.pageSizeSpin.setValue(self._page_size)
        self.refreshBtn = QPushButton(self.tr("Actualiser"))
        bottom.addWidget(self.pageSpin)
        bottom.addWidget(self.pageSizeSpin)
        bottom.addWidget(self.refreshBtn)
        layout.addLayout(bottom)

        self.searchEdit.textChanged.connect(self._load)
        self.refreshBtn.clicked.connect(self._load)
        self.pageSpin.valueChanged.connect(self._on_page_change)
        self.pageSizeSpin.valueChanged.connect(self._on_page_size_change)
        self.addBtn.clicked.connect(self._add)
        self.editBtn.clicked.connect(self._edit)
        self.delBtn.clicked.connect(self._delete)

    def _query(self):
        base = "SELECT id, name_fr, name_ar, phone, email FROM partners WHERE kind='supplier'"
        params = []
        q = self.searchEdit.text().strip()
        if q:
            base += " AND (name_fr LIKE ? OR name_ar LIKE ? OR phone LIKE ? OR email LIKE ?)"
            like = f\"%{q}%\"
            params.extend([like, like, like, like])
        base += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([self._page_size, (self._page - 1) * self._page_size])
        return base, params

    def _load(self) -> None:
        sql, params = self._query()
        rows = self.db.query(sql, params)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["name_fr"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["name_ar"]))
            self.table.setItem(r, 3, QTableWidgetItem(row["phone"]))
            self.table.setItem(r, 4, QTableWidgetItem(row["email"]))
        self.table.resizeColumnsToContents()

    @Slot()
    def _on_page_change(self, val: int) -> None:
        self._page = max(1, val)
        self._load()

    @Slot()
    def _on_page_size_change(self, val: int) -> None:
        self._page_size = val
        self._load()

    def _current_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return int(self.table.item(indexes[0].row(), 0).text())

    @Slot()
    def _add(self) -> None:
        name_fr, name_ar = "Fournisseur", "????"
        self.db.execute("INSERT INTO partners (kind, name_fr, name_ar) VALUES ('supplier', ?, ?);", (name_fr, name_ar))
        self._load()

    @Slot()
    def _edit(self) -> None:
        cid = self._current_id()
        if not cid:
            return
        self.db.execute("UPDATE partners SET name_fr=name_fr||' *' WHERE id=?;", (cid,))
        self._load()

    @Slot()
    def _delete(self) -> None:
        cid = self._current_id()
        if not cid:
            return
        if QMessageBox.question(self, self.tr("Confirmer"), self.tr("Supprimer ce fournisseur ?")) != QMessageBox.Yes:
            return
        self.db.execute("DELETE FROM partners WHERE id=?;", (cid,))
        self._load()

