"""Quick smoke test: one event through checkout."""

from pages.events_page import EventsPage
from utils.config import FrameworkConfig


def test_first_event_completes_booking(driver, config: FrameworkConfig) -> None:
    events_page = EventsPage(driver, config)
    events_page.go_to_events_listing()
    title = events_page.open_event_at_index(0)
    events_page.click_select_tickets(title)
    events_page.complete_booking_flow(title)
    assert events_page.is_final_booking_step_reached()
