"""Locators for the login page."""

from selenium.webdriver.common.by import By


class LoginPageLocators:
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    INVENTORY_CONTAINER = (By.ID, "inventory_container")
    LOGIN_ERROR = (By.CSS_SELECTOR, "[data-test='error']")
