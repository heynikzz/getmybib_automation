"""Configuration management for automation framework."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from config.settings import SETTINGS


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / ".env"

# Load environment values once at import time.
load_dotenv(dotenv_path=ENV_FILE, override=False)


def _to_bool(value: str | None, default: bool = False) -> bool:
    """Convert string-ish values to a boolean."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _to_int(value: str | None, default: int) -> int:
    """Convert a string value to integer with fallback."""
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class FrameworkConfig:
    """Strongly-typed runtime settings."""

    base_url: str
    browser: str
    headless: bool
    implicit_wait: int
    explicit_wait: int
    window_width: int
    window_height: int
    log_level: str


def load_config() -> FrameworkConfig:
    """Build framework configuration from environment values."""
    return FrameworkConfig(
        base_url=os.getenv("BASE_URL", SETTINGS.base_url).rstrip("/"),
        browser=os.getenv("BROWSER", SETTINGS.browser).strip().lower(),
        headless=_to_bool(os.getenv("HEADLESS"), default=SETTINGS.headless),
        implicit_wait=_to_int(os.getenv("IMPLICIT_WAIT"), default=SETTINGS.implicit_wait),
        explicit_wait=_to_int(os.getenv("EXPLICIT_WAIT"), default=SETTINGS.timeout),
        window_width=_to_int(os.getenv("WINDOW_WIDTH"), default=1920),
        window_height=_to_int(os.getenv("WINDOW_HEIGHT"), default=1080),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
    )
