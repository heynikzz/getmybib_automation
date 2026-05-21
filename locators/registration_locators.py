"""Locators for the multi-step registration/booking flow."""

from selenium.webdriver.common.by import By


class RegistrationLocators:
    NEXT_BUTTON = (By.XPATH, "//button[normalize-space()='Next']")
    SAVE_BUTTON = (By.XPATH, "//button[normalize-space()='Save']")
    ADD_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Add' or contains(@class,'register_add')]",
    )
    CATEGORY_SELECT_TICKET = (By.CSS_SELECTOR, "button[class*='category_selectTicketButton']")
    MUI_OPTION = (By.CSS_SELECTOR, "li[role='option']")
