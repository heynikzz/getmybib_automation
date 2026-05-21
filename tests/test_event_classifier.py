"""Unit tests for event booking rules."""

from utils.event_classifier import EventFamily, classify_event, expected_participant_forms, needs_category_page


def test_classify_events() -> None:
    assert classify_event("G.O.A.T. Run Delhi NCR") == EventFamily.GOAT
    assert classify_event("Maruti Suzuki Arena Devils Circuit Pune 2026-27") == EventFamily.DEVILS_CIRCUIT
    assert classify_event("S3: The Yoddha Race - Mumbai") == EventFamily.YODDHA


def test_category_page_cities() -> None:
    assert needs_category_page("S3: The Yoddha Race - Mumbai") is True
    assert needs_category_page("Maruti Suzuki Arena Devils Circuit Chandigarh 2026-27") is False


def test_participant_form_counts() -> None:
    assert expected_participant_forms("G.O.A.T. Run Delhi NCR") == 4
    assert expected_participant_forms("Maruti Suzuki Arena Devils Circuit Pune 2026-27") == 1
    assert expected_participant_forms("S3: The Yoddha Race - Hyderabad") == 1
    assert expected_participant_forms("S3: The Yoddha Race - Mumbai", "Wave Doubles 7:00 AM") == 2
