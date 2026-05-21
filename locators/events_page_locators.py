"""Locators for the events listing and event detail pages."""

from selenium.webdriver.common.by import By


class EventsPageLocators:
    VIEW_ALL_EVENTS_BUTTON = (By.CSS_SELECTOR, "button[class*='cards_viewAllEvents']")
    EVENT_CARD = (By.CSS_SELECTOR, "div[class*='filterDetailsCards_card__']")
    EVENT_TITLE = (By.CSS_SELECTOR, "h3[class*='filterDetailsCards_eventTitle__']")
    RESULTS_INFO = (By.CSS_SELECTOR, "[class*='filterDetailsCards_resultsInfo__']")
    PAGE_NUMBER_BUTTONS = (By.CSS_SELECTOR, "li[class*='filterDetailsCards_page_number_li__']")
    SELECT_TICKETS_BUTTON = (By.CSS_SELECTOR, "button[class*='eventInfo_select_tickets_btn']")
    CATEGORY_SELECT_TICKET_BUTTON = (
        By.CSS_SELECTOR,
        "button[class*='category_selectTicketButton']",
    )
    TICKET_ADD_BUTTON = (By.CSS_SELECTOR, "button[class*='register_addOnlyButton']")
