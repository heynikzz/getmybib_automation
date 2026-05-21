"""Classify GetMyBib live events for booking-flow rules."""

from __future__ import annotations

from enum import Enum

TWO_DAY_CITIES = ("delhi", "mumbai", "bangalore", "bengaluru")


class EventFamily(Enum):
    GOAT = "goat"
    DEVILS_CIRCUIT = "devils_circuit"
    YODDHA = "yoddha"
    UNKNOWN = "unknown"


def classify_event(title: str) -> EventFamily:
    normalized = title.lower()
    if "g.o.a.t" in normalized or "goat" in normalized:
        return EventFamily.GOAT
    if "yoddha" in normalized:
        return EventFamily.YODDHA
    if "devils circuit" in normalized:
        return EventFamily.DEVILS_CIRCUIT
    return EventFamily.UNKNOWN


def needs_category_page(title: str) -> bool:
    normalized = title.lower()
    if classify_event(title) not in (EventFamily.DEVILS_CIRCUIT, EventFamily.YODDHA):
        return False
    return any(city in normalized for city in TWO_DAY_CITIES)


def expected_participant_forms(title: str, page_text: str = "") -> int:
    family = classify_event(title)
    combined = f"{title} {page_text}".lower()
    if family == EventFamily.GOAT:
        return 4
    if family == EventFamily.DEVILS_CIRCUIT:
        return 1
    if family == EventFamily.YODDHA:
        if "double" in combined:
            return 2
        return 1
    return 1
