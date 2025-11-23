from __future__ import annotations

from pathlib import Path

from PySide6 import QtUiTools
from PySide6.QtCore import QFile, QIODevice, Slot, QDate
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from app.core.db import Database
from app.core.i18n import I18n
from app.core.settings import AppSettings
from app.core.logger import get_logger

from app.views.modules.customers import CustomersView
from app.views.modules.products import ProductsView
from app.views.modules.sales import SalesView
from app.views.modules.stock import StockView
from app.views.modules.purchases import PurchasesView
from app.views.modules.payments import PaymentsView
from app.views.modules.cash import CashView
from app.views.modules.suppliers import SuppliersView
from app.views.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    def __init__(self, db: Database, i18n: I18n, settings: AppSettings, current_user: dict, signals, base_dir: Path, parent=None):
        super().__init__(parent)
        self.db = db
        self.i18n = i18n
        self.settings = settings
        self.current_user = current_user
        self.base_dir = base_dir
        self.logger = get_logger(__name__)
        self._load_ui()
        self._wire()
        self._setup_modules()
        signals.languageChanged.connect(self._retranslate)
        self.statusBar().showMessage(self.tr("Connect? en tant que {user} ({role})").format(user=current_user["username"], role=current_user["role"]))

    def _load_ui(self) -> None:
        ui_path = Path(__file__).resolve().parents[1] / "ui" / "main.ui"
        file = QFile(str(ui_path))
        file.open(QIODevice.ReadOnly)
        loader = QtUiTools.QUiLoader()
        window = loader.load(file, self)
        file.close()

        self.setCentralWidget(window.centralWidget())
        self.setMenuBar(window.menuBar())
        self.setStatusBar(window.statusBar())

        # Resolve needed widgets/actions
        self.navTree = window.findChild(type(self), "navTree") or window.findChild(object, "navTree")
        self.stack = window.findChild(type(self), "stack") or window.findChild(object, "stack")
        self.actionBackup: QAction = window.findChild(QAction, "actionBackup")
        self.actionRestore: QAction = window.findChild(QAction, "actionRestore")
        self.actionSettings: QAction = window.findChild(QAction, "actionSettings")
        self.actionQuit: QAction = window.findChild(QAction, "actionQuit")
        self.actionLangFr: QAction = window.findChild(QAction, "actionLangFr")
        self.actionLangAr: QAction = window.findChild(QAction, "actionLangAr")
        self.actionAbout: QAction = window.findChild(QAction, "actionAbout")
        self.setWindowTitle(window.windowTitle())

    def _wire(self) -> None:
        self.actionQuit.triggered.connect(self.close)
        self.actionLangFr.triggered.connect(lambda: self.i18n.set_language("fr"))
        self.actionLangAr.triggered.connect(lambda: self.i18n.set_language("ar"))
        self.actionAbout.triggered.connect(self._about)
        self.actionBackup.triggered.connect(self._backup)
        self.actionRestore.triggered.connect(self._restore)
        self.actionSettings.triggered.connect(self._open_settings)
        self.navTree.itemClicked.connect(self._on_nav_clicked)

    def _setup_modules(self) -> None:
        # Add module pages
        self.modules = {
            "Clients": CustomersView(self.db, self),
            "Fournisseurs": SuppliersView(self.db, self),
            "Produits": ProductsView(self.db, self),
            "Stock": StockView(self.db, self),
            "Devis": SalesView(self.db, self, kind="quote"),
            "BL": SalesView(self.db, self, kind="delivery"),
            "Factures": SalesView(self.db, self, kind="invoice"),
            "Achats": PurchasesView(self.db, self),
            "Paiements": PaymentsView(self.db, self),
            "Caisse": CashView(self.db, self),
        }
        for name, widget in self.modules.items():
            self.stack.addWidget(widget)

    @Slot()
    def _about(self) -> None:
        QMessageBox.information(self, self.tr("? propos"), self.tr("Gestion Commerciale\nVersion 0.1.0"))

    @Slot()
    def _backup(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Choisir le fichier de sauvegarde"), f"backup-{QDate.currentDate().toString('yyyyMMdd')}.db", self.tr("SQLite (*.db)"))
        if not path:
            return
        try:
            src = self.db.path
            Path(path).write_bytes(Path(src).read_bytes())
            QMessageBox.information(self, self.tr("Succ?s"), self.tr("Sauvegarde termin?e"))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Erreur"), str(e))

    @Slot()
    def _restore(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.tr("S?lectionner la sauvegarde"), "", self.tr("SQLite (*.db)"))
        if not path:
            return
        try:
            Path(self.db.path).write_bytes(Path(path).read_bytes())
            QMessageBox.information(self, self.tr("Succ?s"), self.tr("Restauration termin?e. Red?marrez l'application."))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Erreur"), str(e))

    @Slot()
    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.db, self.settings, self)
        dlg.exec()

    @Slot()
    def _on_nav_clicked(self, item, column) -> None:
        name = item.text(0)
        widget = self.modules.get(name)
        if widget:
            self.stack.setCurrentWidget(widget)

    def _retranslate(self) -> None:
        # Widgets created from .ui will retranslate automatically
        pass

