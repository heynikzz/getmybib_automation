"""Login functionality tests using LoginPage POM."""

import pytest

from pages.login_page import LoginPage
from utils.config import FrameworkConfig


def test_login_success(driver, config: FrameworkConfig) -> None:
    """Verify user can login with valid credentials."""
    login_page = LoginPage(driver, config)

    login_page.open_url()
    login_page.login(username="standard_user", password="secret_sauce")

    assert login_page.is_inventory_page_visible(), "Inventory page should be visible after login."


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("invalid_user", "wrong_password"),
        ("standard_user", "wrong_password"),
        ("locked_out_user", "secret_sauce"),
    ],
)
def test_login_invalid_credentials_shows_error(
    driver, config: FrameworkConfig, username: str, password: str
) -> None:
    """Verify login error appears for invalid credentials."""
    login_page = LoginPage(driver, config)

    login_page.open_url()
    login_page.login(username=username, password=password)

    error_text = login_page.get_login_error()
    assert "Epic sadface" in error_text, "Expected login error message was not shown."
