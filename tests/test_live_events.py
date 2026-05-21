"""End-to-end live event booking flow tests."""

from pages.events_page import EventsPage
from utils.config import FrameworkConfig


def test_all_live_events_complete_booking_flow(driver, config: FrameworkConfig) -> None:
    events_page = EventsPage(driver, config)
    events_page.go_to_events_listing()

    total_events = events_page.get_total_event_count()
    assert total_events == EventsPage.EXPECTED_LIVE_EVENTS, (
        f"Expected {EventsPage.EXPECTED_LIVE_EVENTS} live events, found {total_events}."
    )

    completed: list[str] = []
    pages = events_page.get_pagination_pages() or [1]

    for page_number in pages:
        events_page.go_to_page(page_number)
        visible_count = events_page.get_visible_event_count()

        for index in range(visible_count):
            title = events_page.open_event_at_index(index)
            assert events_page.is_event_detail_open(), f"Event '{title}' did not open detail page."
            events_page.click_select_tickets(title)
            assert events_page.is_tickets_page_open(), f"Event '{title}' did not reach register flow."
            events_page.complete_booking_flow(title)
            assert events_page.is_final_booking_step_reached(), (
                f"Event '{title}' did not reach checkout."
            )
            completed.append(title)
            events_page.return_to_listing(page_number)

    assert len(completed) == EventsPage.EXPECTED_LIVE_EVENTS
    assert len(set(completed)) == EventsPage.EXPECTED_LIVE_EVENTS
