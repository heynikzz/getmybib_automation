"""Factory for initializing and configuring Selenium WebDriver instances."""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from utils.config import FrameworkConfig


def create_chrome_driver(headless: bool = False, implicit_wait: int = 10) -> webdriver.Chrome:
    """Create a Chrome WebDriver instance using ChromeDriverManager."""
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if headless:
        chrome_options.add_argument("--headless=new")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    if headless:
        # Headless mode does not support maximize reliably across environments.
        driver.set_window_size(1920, 1080)
    else:
        driver.maximize_window()

    driver.implicitly_wait(implicit_wait)
    return driver


def _build_chrome_driver(config: FrameworkConfig) -> webdriver.Chrome:
    driver = create_chrome_driver(headless=config.headless, implicit_wait=config.implicit_wait)
    if config.headless:
        driver.set_window_size(config.window_width, config.window_height)
    return driver


def _build_firefox_driver(config: FrameworkConfig) -> webdriver.Firefox:
    firefox_options = FirefoxOptions()
    if config.headless:
        firefox_options.add_argument("--headless")

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.set_window_size(config.window_width, config.window_height)
    return driver


def get_driver(config: FrameworkConfig) -> webdriver.Remote:
    """Instantiate a driver based on configured browser."""
    if config.browser == "chrome":
        driver = _build_chrome_driver(config)
    elif config.browser == "firefox":
        driver = _build_firefox_driver(config)
        driver.implicitly_wait(config.implicit_wait)
    else:
        raise ValueError(f"Unsupported browser: {config.browser}. Use chrome or firefox.")

    return driver
