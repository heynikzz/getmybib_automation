"""Base page with common Selenium actions and waits."""

from __future__ import annotations

from typing import Optional

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import FrameworkConfig
from utils.logger import get_logger


Locator = tuple[str, str]


class BasePage:
    """Shared operations for all page objects."""

    def __init__(self, driver: WebDriver, config: Optional[FrameworkConfig] = None) -> None:
        """Initialize page with Selenium driver and optional framework config."""
        self.driver = driver
        self.config = config
        explicit_wait = config.explicit_wait if config else 10
        log_level = config.log_level if config else "INFO"
        self.wait = WebDriverWait(driver, explicit_wait)
        self.logger = get_logger(self.__class__.__name__, log_level)

    def open(self, url: str) -> None:
        self.logger.info("Navigating to URL: %s", url)
        try:
            self.driver.get(url)
        except WebDriverException as exc:
            self.logger.exception("Failed to open URL: %s", url)
            raise RuntimeError(f"Unable to navigate to URL: {url}") from exc

    def wait_for_element(self, locator: Locator) -> WebElement:
        """Wait until an element is visible and return it."""
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException as exc:
            self.logger.exception("Element not visible within timeout: %s", locator)
            raise TimeoutException(f"Element not visible within timeout: {locator}") from exc

    def wait_for_clickable(self, locator: Locator) -> WebElement:
        """Wait until an element is clickable and return it."""
        try:
            return self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException as exc:
            self.logger.exception("Element not clickable within timeout: %s", locator)
            raise TimeoutException(f"Element not clickable within timeout: {locator}") from exc

    def click(self, locator: Locator) -> None:
        """Click an element after waiting for it to be clickable."""
        self.logger.info("Clicking element: %s", locator)
        try:
            self.wait_for_clickable(locator).click()
        except (TimeoutException, WebDriverException) as exc:
            self.logger.exception("Failed to click element: %s", locator)
            raise RuntimeError(f"Unable to click element: {locator}") from exc

    def send_keys(self, locator: Locator, text: str, clear: bool = True) -> None:
        """Send text to an input element."""
        self.logger.info("Sending text to element: %s", locator)
        try:
            element = self.wait_for_element(locator)
            if clear:
                element.clear()
            element.send_keys(text)
        except (TimeoutException, WebDriverException) as exc:
            self.logger.exception("Failed to type into element: %s", locator)
            raise RuntimeError(f"Unable to send keys to element: {locator}") from exc

    def get_text(self, locator: Locator) -> str:
        """Get visible text from an element."""
        self.logger.info("Getting text from element: %s", locator)
        try:
            return self.wait_for_element(locator).text
        except (TimeoutException, WebDriverException) as exc:
            self.logger.exception("Failed to get text from element: %s", locator)
            raise RuntimeError(f"Unable to get text from element: {locator}") from exc

    # Backward-compatible aliases for existing page objects/tests.
    def wait_for_visible(self, locator: Locator) -> WebElement:
        return self.wait_for_element(locator)

    def type_text(self, locator: Locator, text: str, clear: bool = True) -> None:
        self.send_keys(locator, text, clear=clear)

    def is_visible(self, locator: Locator) -> bool:
        try:
            self.wait_for_element(locator)
            return True
        except TimeoutException:
            return False

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def click_element(self, element: WebElement) -> None:
        self.logger.info("Clicking web element: %s", element.tag_name)
        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)
