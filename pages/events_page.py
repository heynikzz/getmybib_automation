"""Page object for events listing and event detail navigation."""

from __future__ import annotations

import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from locators.events_page_locators import EventsPageLocators
from pages.base_page import BasePage
from pages.registration_page import RegistrationPage
from utils.config import FrameworkConfig
from utils.event_classifier import needs_category_page


class EventsPage(BasePage):
    EXPECTED_LIVE_EVENTS = 19
    CATEGORY_STEP_CITIES = ("delhi", "mumbai", "bangalore", "bengaluru")

    def __init__(self, driver: WebDriver, config: FrameworkConfig | None = None) -> None:
        super().__init__(driver, config)

    def events_listing_url(self) -> str:
        base = self.config.base_url if self.config else "https://getmybib.com"
        return f"{base.rstrip('/')}/events"

    def go_to_events_listing(self) -> None:
        self.open(self.config.base_url if self.config else "https://getmybib.com")
        if self.is_visible(EventsPageLocators.VIEW_ALL_EVENTS_BUTTON):
            self.click(EventsPageLocators.VIEW_ALL_EVENTS_BUTTON)
        self.wait_for_events_grid()

    def wait_for_events_grid(self) -> None:
        self.wait.until(lambda _: len(self.find_all(EventsPageLocators.EVENT_CARD)) > 0)

    def get_total_event_count(self) -> int:
        text = self.get_text(EventsPageLocators.RESULTS_INFO)
        match = re.search(r"(\d+)\s+Events?", text, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    def get_visible_event_count(self) -> int:
        return len(self.find_all(EventsPageLocators.EVENT_CARD))

    def get_event_titles_on_page(self) -> list[str]:
        return [
            element.text.strip()
            for element in self.find_all(EventsPageLocators.EVENT_TITLE)
            if element.text.strip()
        ]

    def get_pagination_pages(self) -> list[int]:
        pages: list[int] = []
        for button in self.find_all(EventsPageLocators.PAGE_NUMBER_BUTTONS):
            label = button.text.strip()
            if label.isdigit():
                pages.append(int(label))
        return sorted(set(pages))

    def go_to_page(self, page_number: int) -> None:
        for button in self.find_all(EventsPageLocators.PAGE_NUMBER_BUTTONS):
            if button.text.strip() == str(page_number):
                self.click_element(button)
                self.wait_for_events_grid()
                return
        raise RuntimeError(f"Pagination page {page_number} was not found.")

    def open_event_at_index(self, index: int) -> str:
        cards = self.find_all(EventsPageLocators.EVENT_CARD)
        if index < 0 or index >= len(cards):
            raise IndexError(f"Event index {index} is out of range (found {len(cards)} cards).")
        title = self._get_card_title(cards[index])
        self.click_element(cards[index])
        self.wait_for_event_detail()
        return title

    def return_to_listing(self, page_number: int = 1) -> None:
        self.open(self.events_listing_url())
        self.wait_for_events_grid()
        if page_number > 1:
            self.go_to_page(page_number)

    def wait_for_event_detail(self) -> None:
        self.wait.until(lambda d: "/description" in d.current_url.lower())
        self.wait.until(lambda d: "id=" in d.current_url.lower())
        self.wait.until(lambda _: len(self.find_all(EventsPageLocators.SELECT_TICKETS_BUTTON)) > 0)

    def is_event_detail_open(self) -> bool:
        url = self.driver.current_url.lower()
        return "/description" in url and "id=" in url

    def click_select_tickets(self, event_title: str) -> None:
        button = self._get_visible_select_tickets_button()
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        self.driver.execute_script("arguments[0].click();", button)
        self._complete_booking_entry_step(event_title)

    def _complete_booking_entry_step(self, event_title: str) -> None:
        self.wait.until(
            lambda d: "/category" in d.current_url.lower() or "/register" in d.current_url.lower()
        )
        if self.is_category_page_open():
            RegistrationPage(self.driver, self.config).select_available_wave_ticket()
        self.wait.until(lambda d: "/register" in d.current_url.lower())

    def is_category_page_open(self) -> bool:
        return "/category" in self.driver.current_url.lower()

    def is_tickets_page_open(self) -> bool:
        return "/register" in self.driver.current_url.lower()

    def complete_booking_flow(self, event_title: str) -> None:
        RegistrationPage(self.driver, self.config).complete_booking_flow(event_title)

    def is_final_booking_step_reached(self) -> bool:
        return RegistrationPage(self.driver, self.config).is_final_step_reached()

    def _get_visible_select_tickets_button(self) -> WebElement:
        self.wait.until(lambda _: len(self.find_all(EventsPageLocators.SELECT_TICKETS_BUTTON)) > 0)
        for button in reversed(self.find_all(EventsPageLocators.SELECT_TICKETS_BUTTON)):
            if button.is_displayed():
                return button
        raise RuntimeError("Select Tickets button was not visible.")

    def _get_card_title(self, card: WebElement) -> str:
        titles = card.find_elements(*EventsPageLocators.EVENT_TITLE)
        if titles and titles[0].text.strip():
            return titles[0].text.strip()
        return card.text.strip().split("\n")[0]
