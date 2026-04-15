"""Central Selenium framework settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeleniumSettings:
    """Base framework configuration for browser runs."""

    base_url: str = "https://getmybib.com"
    timeout: int = 10
    browser: str = "chrome"
    headless: bool = False
    implicit_wait: int = 0


SETTINGS = SeleniumSettings()
