"""Shared pytest fixtures and command-line options."""

from __future__ import annotations

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from utils.config import FrameworkConfig, load_config
from utils.driver_factory import get_driver
from utils.logger import get_logger


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add framework runtime overrides from command line."""
    parser.addoption("--base-url", action="store", default=None, help="Override base URL")
    parser.addoption("--browser", action="store", default=None, help="Browser: chrome|firefox")
    parser.addoption("--headless", action="store_true", help="Run browser in headless mode")


@pytest.fixture(scope="session")
def config(pytestconfig: pytest.Config) -> FrameworkConfig:
    """Load and optionally override framework config for current run."""
    loaded = load_config()
    base_url = pytestconfig.getoption("--base-url") or loaded.base_url
    browser = pytestconfig.getoption("--browser") or loaded.browser
    headless_override = pytestconfig.getoption("--headless")

    return FrameworkConfig(
        base_url=base_url.rstrip("/"),
        browser=browser.strip().lower(),
        headless=headless_override or loaded.headless,
        implicit_wait=loaded.implicit_wait,
        explicit_wait=loaded.explicit_wait,
        window_width=loaded.window_width,
        window_height=loaded.window_height,
        log_level=loaded.log_level,
    )


@pytest.fixture(scope="function")
def driver(config: FrameworkConfig) -> WebDriver:
    """Set up Selenium driver and tear it down after each test."""
    logger = get_logger("driver_fixture", config.log_level)
    logger.info("Starting driver for browser: %s", config.browser)
    web_driver = get_driver(config)
    try:
        yield web_driver
    finally:
        logger.info("Closing browser")
        web_driver.quit()


@pytest.fixture(scope="function")
def selenium_driver(driver: WebDriver) -> WebDriver:
    """Alias fixture for teams preferring explicit Selenium naming."""
    return driver
