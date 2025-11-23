import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QLocale, QTranslator, Qt, Signal, QObject
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication

from app.core.i18n import I18n
from app.core.db import Database
from app.core.migrations import MigrationManager
from app.core.settings import AppSettings
from app.views.login import LoginDialog
from app.views.main_window import MainWindow
from app.core.logger import init_logging, get_logger
from app.core.auth import ensure_bootstrap_admin
from app.core.utils import ensure_runtime_assets


class AppSignals(QObject):
    languageChanged = Signal()


signals = AppSignals()


def run_app() -> int:
    # Application bootstrap
    app = QApplication(sys.argv)
    app.setOrganizationName("AgenticSoft")
    app.setApplicationName("Gestion Commerciale")
    app.setApplicationVersion("0.1.0")

    init_logging()
    logger = get_logger(__name__)

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = Path(os.getenv("APP_DATA_DIR", base_dir / "data"))
    data_dir.mkdir(parents=True, exist_ok=True)

    ensure_runtime_assets(base_dir)

    # i18n
    i18n = I18n(base_dir=base_dir, app=app, signals=signals)
    i18n.load_saved_locale()

    # DB + migrations
    db_path = data_dir / "app.db"
    db = Database(db_path)
    migrator = MigrationManager(db=db, migrations_dir=base_dir / "app" / "migrations")
    migrator.apply_pending_migrations()

    # Settings
    settings = AppSettings(db=db)
    settings.ensure_defaults()

    # Auth bootstrap
    ensure_bootstrap_admin(db)

    # Login
    login = LoginDialog(db=db, i18n=i18n, signals=signals)
    if login.exec() != LoginDialog.Accepted:
        return 0
    user = login.get_authenticated_user()
    if not user:
        return 0

    # Font that supports Arabic for UI
    app.setFont(QFont("Noto Naskh Arabic", 10))

    # Main window
    window = MainWindow(db=db, i18n=i18n, settings=settings, current_user=user, signals=signals, base_dir=base_dir)
    window.setWindowIcon(QIcon(str(base_dir / "app" / "assets" / "icons" / "app.png")))
    window.resize(1280, 800)
    window.show()

    logger.info("Application started")
    return app.exec()

