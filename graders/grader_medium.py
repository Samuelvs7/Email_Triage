"""Grader for medium priority classification."""


def _normalize_label(value: str) -> str:
    normalized = (value or "").strip().lower()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = "".join(ch for ch in normalized if ch.isalnum() or ch == "_")
    return normalized.strip("_")


def grade_medium(action_content: str, expected_label: str) -> dict[str, float | str]:
    """Grade low/normal/urgent with exact normalized match."""
    predicted = _normalize_label(action_content)
    expected = _normalize_label(expected_label)

    if predicted == expected:
        return {"score": 0.99, "reason": "correct label"}

    return {"score": 0.01, "reason": f"expected '{expected}', got '{predicted or 'empty'}'"}
