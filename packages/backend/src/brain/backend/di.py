from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import Depends

from .config import BackendSettings, settings


@lru_cache()
def get_settings() -> BackendSettings:
    return settings


def get_logger(settings: BackendSettings = Depends(get_settings)) -> logging.Logger:
    return logging.getLogger("brain.backend")
