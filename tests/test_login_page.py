"""Smoke test to validate login page loads."""

from pages.login_page import LoginPage
from utils.config import FrameworkConfig


def test_login_page_loads(driver, config: FrameworkConfig) -> None:
    login_page = LoginPage(driver, config)
    login_page.open_login_page()

    assert "getmybib.com" in driver.current_url.lower(), "Login page URL did not load as expected."
