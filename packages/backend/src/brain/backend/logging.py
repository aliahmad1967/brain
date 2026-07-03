from __future__ import annotations

import logging
import sys
from logging import Logger

from .config import BackendSettings

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(settings: BackendSettings) -> Logger:
    settings.ensure_dirs()

    if not logging.getLogger().handlers:
        handlers = [logging.StreamHandler(sys.stdout)]

        if settings.log_file:
            file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT))
            handlers.append(file_handler)

        logging.basicConfig(
            level=settings.log_level.upper(),
            format=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT,
            handlers=handlers,
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())

    backend_logger = logging.getLogger("brain.backend")
    backend_logger.setLevel(settings.log_level.upper())
    backend_logger.debug("Backend logging configured")

    return backend_logger
