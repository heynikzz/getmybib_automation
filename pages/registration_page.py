"""Page object for the multi-step event registration/booking flow."""

from __future__ import annotations

import re
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select, WebDriverWait

from locators.registration_locators import RegistrationLocators
from pages.base_page import BasePage
from utils import random_data
from utils.event_classifier import EventFamily, classify_event, expected_participant_forms


class RegistrationPage(BasePage):
    UNAVAILABLE_WAVE_KEYWORDS = ("sold out", "full", "closed", "unavailable", "not available")
    PLACEHOLDER_VALUE_HINTS = (
        "enter text",
        "enter email",
        "enter contact",
        "select from",
        "select ",
        "choose ",
    )

    def __init__(self, driver: WebDriver, config=None) -> None:
        super().__init__(driver, config)
        explicit = config.explicit_wait if config else 10
        self.long_wait = WebDriverWait(driver, explicit * 4)
        self._label_cache: list[tuple[str, WebElement, WebElement]] | None = None
        self._fields_filled_this_pass: set[str] = set()
        self._current_event_title = ""

    def complete_booking_flow(self, event_title: str) -> None:
        self.logger.info("Starting booking flow for: %s", event_title)
        self._current_event_title = event_title
        if self.is_category_page_open():
            self.select_available_wave_ticket()
        self._wait_for_register_or_attendees()
        self._complete_register_ticket_step()
        self._complete_attendees_step(event_title)
        self.click_next_when_enabled()
        self._skip_addon_step()
        self._advance_to_checkout()
        if not self.is_checkout_page():
            raise RuntimeError(
                f"Checkout page was not reached for '{event_title}': {self.driver.current_url}"
            )

    def select_available_wave_ticket(self) -> None:
        self.wait.until(lambda d: "/category" in d.current_url.lower())
        time.sleep(0.5)
        self.long_wait.until(lambda _: bool(self._visible_category_ticket_buttons()))
        for prefer_singles in (True, False):
            for index, button in enumerate(self._visible_category_ticket_buttons()):
                if self._wave_is_unavailable(button):
                    continue
                if prefer_singles and self._wave_is_doubles(button):
                    continue
                self.logger.info("Selecting wave ticket at index %s", index)
                self._js_click(button)
                time.sleep(1)
                try:
                    self.wait.until(lambda d: "/register" in d.current_url.lower())
                    return
                except TimeoutException:
                    pass
        raise RuntimeError("Could not select an available wave ticket on the category page.")

    def _complete_register_ticket_step(self) -> None:
        if "/attendees" in self.driver.current_url.lower():
            return
        self.long_wait.until(self._register_page_ready)
        add_button = self.long_wait.until(self._first_clickable_add_button)
        self._js_click(add_button)
        time.sleep(0.5)
        self.click_next_when_enabled()

    def _complete_attendees_step(self, event_title: str) -> None:
        self.wait.until(
            lambda d: "/attendees" in d.current_url.lower() or self.get_participant_tabs()
        )
        time.sleep(0.5)
        tabs = self.get_participant_tabs()
        form_count = len(tabs) if tabs else expected_participant_forms(
            event_title, self.driver.find_element(By.TAG_NAME, "body").text
        )
        self.logger.info("Filling %s participant form(s) for %s", form_count, event_title)
        self._current_event_title = event_title
        if tabs:
            for name, tab in tabs[:form_count]:
                self.logger.info("Saving participant: %s", name)
                self._js_click(tab)
                time.sleep(0.3)
                self._fill_form_then_save(name)
        else:
            for index in range(form_count):
                self._fill_form_then_save(str(index))
        if not self._is_next_enabled():
            self.logger.info("Next still disabled — re-saving forms.")
            if tabs:
                for name, tab in tabs[:form_count]:
                    self._js_click(tab)
                    time.sleep(0.3)
                    self._fill_form_then_save(name)
        self._wait_for_next_enabled()

    def _fill_form_then_save(self, participant_key: str) -> None:
        self.fill_visible_form(participant_key, self._current_event_title)
        self.click_save_when_ready()
        time.sleep(1)

    def fill_visible_form(self, participant_key: str = "0", event_title: str = "") -> None:
        self._fields_filled_this_pass = set()
        self._label_cache = None
        self._build_label_cache()
        try:
            self._fill_form_fields_in_order(participant_key, event_title)
        finally:
            self._label_cache = None

    def _fill_form_fields_in_order(self, participant_key: str, event_title: str) -> None:
        family = classify_event(event_title)
        if family == EventFamily.GOAT:
            self._fill_goat_field_order(participant_key)
        elif family == EventFamily.YODDHA:
            self._fill_yoddha_field_order(participant_key)
        else:
            self._fill_devils_circuit_field_order(participant_key)
        self._ensure_radio_groups_selected()

    def _fill_goat_field_order(self, participant_key: str) -> None:
        self._fill_by_label_match(lambda t: "full name" in t, participant_key)
        self._fill_by_label_match(
            lambda t: ("contact no" in t or t == "contact") and "emergency" not in t, participant_key
        )
        self._fill_by_label_match(lambda t: "email" in t and "emergency" not in t, participant_key)
        self._fill_gender_field()
        self._fill_by_label_match(
            lambda t: "date of birth" in t
            or ("birth" in t and "emergency" not in t and "contact" not in t),
            participant_key,
            is_date=True,
        )
        self._fill_shirt_or_vest_field()
        self._fill_state_field()
        self._fill_by_label_match(lambda t: "city" in t and "emergency" not in t, participant_key)
        self._fill_by_label_match(lambda t: "instagram" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact name" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact number" in t, participant_key)

    def _fill_devils_circuit_field_order(self, participant_key: str) -> None:
        self._fill_by_label_match(lambda t: "full name" in t, participant_key)
        self._fill_by_label_match(lambda t: "email" in t and "emergency" not in t, participant_key)
        self._fill_by_label_match(
            lambda t: ("contact no" in t or t == "contact") and "emergency" not in t, participant_key
        )
        self._fill_gender_field()
        self._fill_by_label_match(
            lambda t: "date of birth" in t
            or ("birth" in t and "emergency" not in t and "contact" not in t),
            participant_key,
            is_date=True,
        )
        self._fill_shirt_or_vest_field()
        self._fill_state_field()
        self._fill_by_label_match(lambda t: "city" in t and "emergency" not in t, participant_key)
        self._fill_by_label_match(lambda t: "instagram" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact name" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact number" in t, participant_key)

    def _fill_yoddha_field_order(self, participant_key: str) -> None:
        self._fill_by_label_match(lambda t: "full name" in t, participant_key)
        self._fill_by_label_match(lambda t: "email" in t and "emergency" not in t, participant_key)
        self._fill_by_label_match(
            lambda t: ("contact no" in t or t == "contact") and "emergency" not in t, participant_key
        )
        self._fill_by_label_match(
            lambda t: "date of birth" in t
            or ("birth" in t and "emergency" not in t and "contact" not in t),
            participant_key,
            is_date=True,
        )
        self._fill_gender_field()
        self._fill_shirt_or_vest_field()
        self._fill_state_field()
        self._fill_by_label_match(lambda t: "city" in t and "emergency" not in t, participant_key)
        self._fill_by_label_match(
            lambda t: "train" in t or "where do you" in t, participant_key
        )
        self._fill_by_label_match(lambda t: "instagram" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact name" in t, participant_key)
        self._fill_by_label_match(lambda t: "emergency contact number" in t, participant_key)

    def _build_label_cache(self) -> list[tuple[str, WebElement, WebElement]]:
        if self._label_cache is not None:
            return self._label_cache
        option_labels = {"male", "female", "m", "l", "xl", "xxl", "s", "xs"}
        entries: list[tuple[str, WebElement, WebElement, int]] = []
        seen: set[str] = set()
        for label in self.driver.find_elements(By.TAG_NAME, "label"):
            if not label.is_displayed():
                continue
            raw = (label.text or "").strip()
            if not raw or re.fullmatch(r"Participant \d+", raw):
                continue
            clean = raw.lower().rstrip("*").strip()
            if clean in option_labels:
                continue
            key = f"{label.location['y']}:{clean}"
            if key in seen:
                continue
            seen.add(key)
            container = self._find_field_container(label)
            if container:
                entries.append((clean, label, container, label.location["y"]))
        entries.sort(key=lambda item: item[3])
        self._label_cache = [(a, b, c) for a, b, c, _ in entries]
        return self._label_cache

    def _find_label_and_container(self, matcher) -> tuple[WebElement | None, WebElement | None]:
        for clean, label, container in self._build_label_cache():
            if matcher(clean):
                return label, container
        return None, None

    def _fill_by_label_match(
        self, matcher, participant_key: str, *, is_date: bool = False
    ) -> None:
        label, container = self._find_label_and_container(matcher)
        if not container:
            return
        if is_date:
            self._fill_date_in_row(container)
            return
        label_text = (label.text or "").strip() if label else ""
        self._fill_text_inputs_in_row(container, label_text, participant_key)

    def _fill_gender_field(self) -> None:
        _label, container = self._find_label_and_container(
            lambda t: "gender" in t and "emergency" not in t
        )
        if container and not self._click_option_in_container(container, ("Male", "Female")):
            self._fill_radio_in_row(container)

    def _fill_shirt_or_vest_field(self) -> None:
        _label, container = self._find_label_and_container(
            lambda t: any(w in t for w in ("t - shirt", "t-shirt", "vest size", "shirt size"))
            and "emergency" not in t
        )
        if container and not self._click_option_in_container(
            container, ("M", "L", "S", "XL", "XXL")
        ):
            self._fill_radio_in_row(container)

    def _fill_state_field(self) -> None:
        _label, container = self._find_label_and_container(
            lambda t: "state" in t and "city" not in t and "emergency" not in t
        )
        if container:
            self._select_dropdown_in_control(container)
            time.sleep(0.3)

    def _fill_text_inputs_in_row(
        self, row: WebElement, label_text: str, participant_key: str
    ) -> None:
        for field in row.find_elements(
            By.CSS_SELECTOR,
            "input:not([type='hidden']):not([type='radio']):not([type='checkbox']):not([type='submit']), textarea",
        ):
            if field.is_displayed():
                self._fill_input_element(field, label_text, participant_key)

    def _fill_date_in_row(self, row: WebElement) -> None:
        for field in row.find_elements(By.CSS_SELECTOR, "input"):
            if not field.is_displayed() or self._already_filled(field):
                continue
            placeholder = (field.get_attribute("placeholder") or "").lower()
            if "dd" in placeholder or "birth" in placeholder:
                self._type_into_field(field, "01/01/1990")
                field.send_keys(Keys.TAB)
                self._mark_filled(field)

    def _fill_input_element(self, field: WebElement, label_text: str, participant_key: str) -> None:
        if self._already_filled(field):
            return
        field_type = (field.get_attribute("type") or "text").lower()
        if field_type in ("radio", "checkbox", "hidden", "submit", "button"):
            return
        if not self._field_needs_value(field, label_text):
            return
        value = random_data.value_for_label(label_text, participant_key)
        if value:
            self._type_into_field(field, value)
            self._mark_filled(field)

    def _field_needs_value(self, field: WebElement, label_text: str) -> bool:
        current = (field.get_attribute("value") or "").strip()
        if not current:
            return True
        lower = current.lower()
        if any(h in lower for h in self.PLACEHOLDER_VALUE_HINTS):
            return True
        ll = label_text.lower()
        if "email" in ll and "@" not in current:
            return True
        if "contact" in ll and len(re.sub(r"\D", "", current)) < 10:
            return True
        return False

    def _ensure_radio_groups_selected(self) -> None:
        seen: set[str] = set()
        for _c, _l, container in self._build_label_cache():
            for radio in container.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
                if not radio.is_displayed():
                    continue
                name = radio.get_attribute("name") or self._field_key(radio)
                if name in seen or radio.is_selected():
                    seen.add(name)
                    continue
                seen.add(name)
                self._js_click(radio)
                break

    def _fill_radio_in_row(self, row: WebElement) -> None:
        for radio in row.find_elements(By.CSS_SELECTOR, "input[type='radio']"):
            if radio.is_displayed() and not radio.is_selected():
                self._js_click(radio)
                self._mark_filled(radio)
                return

    def _click_option_in_container(self, container: WebElement, options: tuple[str, ...]) -> bool:
        for option in options:
            for element in container.find_elements(
                By.XPATH, f".//*[normalize-space()='{option}']"
            ):
                if element.is_displayed():
                    self._js_click(element)
                    return True
        return False

    def _find_field_container(self, label: WebElement) -> WebElement | None:
        for xpath in (
            "./ancestor::div[contains(@class,'accordianFormInput')][1]",
            "./ancestor::div[contains(@class,'MuiFormControl')][1]",
            "./parent::*",
        ):
            try:
                return label.find_element(By.XPATH, xpath)
            except Exception:
                continue
        return None

    def _select_dropdown_in_control(self, control: WebElement) -> bool:
        for combobox in control.find_elements(By.CSS_SELECTOR, "[role='combobox']"):
            if combobox.is_displayed() and not self._already_filled(combobox):
                self._select_mui_option(combobox)
                self._mark_filled(combobox)
                return True
        for select_el in control.find_elements(By.TAG_NAME, "select"):
            if select_el.is_displayed() and not self._already_filled(select_el):
                if self._select_first_valid_option(select_el):
                    self._mark_filled(select_el)
                    return True
        return False

    def _select_first_valid_option(self, select_el: WebElement) -> bool:
        dropdown = Select(select_el)
        for index, option in enumerate(dropdown.options):
            text = (option.text or "").strip().lower()
            if not text or any(w in text for w in ("select", "choose", "from here")):
                continue
            dropdown.select_by_index(index)
            return True
        return False

    def _select_mui_option(self, combobox: WebElement) -> None:
        self._js_click(combobox)
        time.sleep(0.4)
        options = [
            o
            for o in self.driver.find_elements(*RegistrationLocators.MUI_OPTION)
            if o.is_displayed() and (o.text or "").strip()
        ]
        if options:
            self._js_click(options[1] if len(options) > 1 else options[0])
        time.sleep(0.2)

    def click_save_when_ready(self) -> None:
        try:
            button = self.wait.until(self._save_button_enabled)
        except TimeoutException:
            button = self.long_wait.until(self._save_button_visible)
        self._js_click(button)

    def click_next_when_enabled(self) -> bool:
        try:
            button = self.wait.until(self._next_button_enabled)
            self._js_click(button)
            time.sleep(1)
            return True
        except TimeoutException:
            return False

    def get_participant_tabs(self) -> list[tuple[str, WebElement]]:
        tabs: list[tuple[str, WebElement]] = []
        seen: set[str] = set()
        for element in self.driver.find_elements(
            By.XPATH, "//*[starts-with(normalize-space(text()), 'Participant ')]"
        ):
            label = (element.text or "").strip()
            if not re.fullmatch(r"Participant \d+", label):
                continue
            if element.is_displayed() and label not in seen:
                seen.add(label)
                tabs.append((label, element))
        return sorted(tabs, key=lambda item: int(item[0].split()[-1]))

    def is_checkout_page(self) -> bool:
        url = self.driver.current_url.lower()
        if any(p in url for p in ("/checkout", "/payment", "/summary")):
            return True
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        return any(w in body for w in ("checkout", "pay now", "proceed to pay", "order summary"))

    def is_final_step_reached(self) -> bool:
        return self.is_checkout_page()

    def is_category_page_open(self) -> bool:
        return "/category" in self.driver.current_url.lower()

    def _skip_addon_step(self) -> None:
        if "/addon" in self.driver.current_url.lower():
            self.logger.info("Skipping addon step")
            self.click_next_when_enabled()

    def _advance_to_checkout(self) -> None:
        if self.is_checkout_page():
            return
        for _ in range(3):
            if self.is_checkout_page():
                return
            if self._is_next_enabled():
                self.click_next_when_enabled()
                time.sleep(1)
        self.long_wait.until(lambda _: self.is_checkout_page())

    def _wait_for_register_or_attendees(self) -> None:
        self.long_wait.until(
            lambda d: "/register" in d.current_url.lower() or "/attendees" in d.current_url.lower()
        )
        time.sleep(1)

    def _wait_for_next_enabled(self) -> None:
        if self._is_next_enabled():
            return
        self.long_wait.until(self._next_button_enabled)

    def _is_next_enabled(self) -> bool:
        return any(
            b.is_displayed() and b.is_enabled()
            for b in self.driver.find_elements(*RegistrationLocators.NEXT_BUTTON)
        )

    def _save_button_enabled(self, driver: WebDriver) -> WebElement:
        for button in driver.find_elements(*RegistrationLocators.SAVE_BUTTON):
            if button.is_displayed() and button.is_enabled():
                return button
        raise TimeoutException("Save is not enabled yet.")

    def _save_button_visible(self, driver: WebDriver) -> WebElement:
        for button in driver.find_elements(*RegistrationLocators.SAVE_BUTTON):
            if button.is_displayed():
                return button
        raise TimeoutException("Save button is not visible yet.")

    def _register_page_ready(self, driver: WebDriver) -> bool:
        if "/attendees" in driver.current_url.lower():
            return True
        if "/register" not in driver.current_url.lower():
            return False
        return self._find_add_button(driver) is not None

    def _find_add_button(self, driver: WebDriver) -> WebElement | None:
        for button in driver.find_elements(*RegistrationLocators.ADD_BUTTON):
            if button.is_displayed() and button.is_enabled() and button.text.strip().lower() == "add":
                return button
        for button in driver.find_elements(By.CSS_SELECTOR, "button[class*='register_add']"):
            if button.is_displayed() and button.is_enabled():
                return button
        return None

    def _first_clickable_add_button(self, driver: WebDriver) -> WebElement:
        button = self._find_add_button(driver)
        if button:
            return button
        raise TimeoutException("No clickable Add button found on the register page.")

    def _next_button_enabled(self, driver: WebDriver) -> WebElement:
        for button in driver.find_elements(*RegistrationLocators.NEXT_BUTTON):
            if button.is_displayed() and button.is_enabled():
                return button
        raise TimeoutException("Next button is not enabled yet.")

    def _visible_category_ticket_buttons(self) -> list[WebElement]:
        return [b for b in self.find_all(RegistrationLocators.CATEGORY_SELECT_TICKET) if b.is_displayed()]

    def _wave_is_unavailable(self, button: WebElement) -> bool:
        try:
            section = button.find_element(
                By.XPATH,
                "./ancestor::*[contains(@class,'category') or contains(@class,'wave')][1]",
            )
            text = (section.text or "").lower()
        except Exception:
            text = (button.text or "").lower()
        return any(k in text for k in self.UNAVAILABLE_WAVE_KEYWORDS)

    def _wave_is_doubles(self, button: WebElement) -> bool:
        try:
            section = button.find_element(
                By.XPATH,
                "./ancestor::*[contains(@class,'category') or contains(@class,'wave')][1]",
            )
            text = (section.text or "").lower()
        except Exception:
            text = (button.text or "").lower()
        return "double" in text

    def _field_key(self, field: WebElement) -> str:
        fid = field.get_attribute("id")
        if fid:
            return f"id:{fid}"
        name = field.get_attribute("name")
        if name:
            return f"name:{name}"
        return f"ref:{id(field)}"

    def _already_filled(self, field: WebElement) -> bool:
        return self._field_key(field) in self._fields_filled_this_pass

    def _mark_filled(self, field: WebElement) -> None:
        self._fields_filled_this_pass.add(self._field_key(field))

    def _type_into_field(self, field: WebElement, value: str) -> None:
        self._js_click(field)
        try:
            field.clear()
        except Exception:
            pass
        field.send_keys(value)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            field,
        )

    def _js_click(self, element: WebElement) -> None:
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)
