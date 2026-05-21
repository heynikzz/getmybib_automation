"""Random test data for dynamic registration forms."""

from __future__ import annotations

import random
import string


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_name(participant_key: str = "") -> str:
    suffix = participant_key.replace("participant", "").strip() or random_string(3)
    return f"Test User {suffix.title()} {random_string(4).title()}"


def random_email(participant_key: str = "") -> str:
    suffix = participant_key.replace(" ", "").lower().replace("participant", "") or random_string(4)
    return f"test.{suffix}.{random_string(5)}@example.com"


def random_phone() -> str:
    return f"98{random.randint(10000000, 99999999)}"


def value_for_label(label: str, participant_key: str = "") -> str:
    label_lower = label.lower().strip().rstrip("*").strip()
    if "email" in label_lower or "e-mail" in label_lower:
        return random_email(participant_key)
    if "contact no" in label_lower or label_lower == "contact":
        return random_phone()
    if "mobile" in label_lower or "phone" in label_lower:
        return random_phone()
    if "contact number" in label_lower or ("number" in label_lower and "emergency" in label_lower):
        return random_phone()
    if "full name" in label_lower:
        return random_name(participant_key)
    if "emergency contact name" in label_lower:
        return f"Emergency {random_string(4).title()}"
    if "instagram" in label_lower:
        return f"testuser{random_string(5)}"
    if "train" in label_lower or "where do you" in label_lower:
        return random.choice(["Mumbai", "Delhi", "Pune", "Hyderabad", "Bengaluru"])
    if "state" in label_lower:
        return ""
    if "city" in label_lower:
        return random.choice(["Mumbai", "Delhi", "Bengaluru", "Pune", "Hyderabad", "Chennai"])
    if "date" in label_lower or "birth" in label_lower or "dob" in label_lower:
        return "01/01/1990"
    if "name" in label_lower:
        return random_name(participant_key)
    if "contact" in label_lower:
        return random_phone()
    return f"Auto {random_string(8)}"


def value_for_input(
    input_type: str,
    placeholder: str = "",
    label: str = "",
    participant_key: str = "",
) -> str:
    combined = f"{label} {placeholder}".lower()
    if not combined.strip():
        if input_type.lower() == "email":
            return random_email(participant_key)
        if input_type.lower() == "tel":
            return random_phone()
        return f"Test {random_string(6)}"
    return value_for_label(combined, participant_key)
