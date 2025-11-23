import logging
from pathlib import Path

_LOGGER_INITIALIZED = False


def init_logging() -> None:
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(logs_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    _LOGGER_INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

