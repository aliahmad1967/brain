"""Desktop application entry point and main window shell."""

import logging
import sys

from brain.core import settings
from PySide6.QtWidgets import QApplication, QMainWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window shell for the Brain desktop application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(settings.app_name)
        self.resize(1024, 768)


def main() -> None:
    """Bootstrap and start the PySide6 desktop application."""
    # Ensure data directory structures are created
    settings.ensure_dirs()

    logging.basicConfig(level=logging.INFO)
    logger.info("Starting %s desktop application shell...", settings.app_name)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
