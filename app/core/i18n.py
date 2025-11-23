from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QLocale, QTranslator, Qt, QSettings
from PySide6.QtWidgets import QApplication


class I18n:
    def __init__(self, base_dir: Path, app: QApplication, signals) -> None:
        self.base_dir = Path(base_dir)
        self.app = app
        self.translator = QTranslator()
        self.settings = QSettings()
        self.signals = signals

    def load_saved_locale(self) -> None:
        lang = self.settings.value("ui/lang", "fr", type=str)
        self.set_language(lang)

    def set_language(self, lang_code: str) -> None:
        # Remove previous translator
        self.app.removeTranslator(self.translator)
        qm_path = self.base_dir / "app" / "translations" / f"{lang_code}.qm"
        if qm_path.exists():
            self.translator.load(str(qm_path))
            self.app.installTranslator(self.translator)
        # Set layout direction for RTL language
        if lang_code.startswith("ar"):
            self.app.setLayoutDirection(Qt.RightToLeft)
        else:
            self.app.setLayoutDirection(Qt.LeftToRight)
        self.settings.setValue("ui/lang", lang_code)
        self.signals.languageChanged.emit()

