import os
import sys
from app.app import run_app


def main() -> int:
    # Ensure working directory at project root for data paths
    os.environ.setdefault("QT_API", "pyside6")
    return run_app()


if __name__ == "__main__":
    sys.exit(main())

