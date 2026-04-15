"""Page object for login functionality."""

from __future__ import annotations

from locators.login_page_locators import LoginPageLocators
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Actions and assertions for the login page."""

    def open_url(self, url: str | None = None) -> None:
        """Open login page URL from argument or framework config."""
        target_url = url or (self.config.base_url if self.config else None)
        if not target_url:
            raise ValueError("URL is required when BasePage config is not provided.")
        self.open(target_url)

    def login(self, username: str, password: str) -> None:
        self.send_keys(LoginPageLocators.USERNAME_INPUT, username)
        self.send_keys(LoginPageLocators.PASSWORD_INPUT, password)
        self.click(LoginPageLocators.LOGIN_BUTTON)

    # Backward-compatible alias for existing tests.
    def open_login_page(self) -> None:
        self.open_url()

    def is_inventory_page_visible(self) -> bool:
        return self.is_visible(LoginPageLocators.INVENTORY_CONTAINER)

    def get_login_error(self) -> str:
        return self.get_text(LoginPageLocators.LOGIN_ERROR)
