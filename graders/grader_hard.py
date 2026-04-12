"""Grader for hard reply drafting."""

import string

WEIGHTS = {
    "acknowledgement": 0.4,
    "apology": 0.3,
    "next_step": 0.3,
}

KEYWORDS = {
    "acknowledgement": [
        "acknowledgement",
        "acknowledgment",
        "thank you for reaching out",
        "thanks for reaching out",
        "we received",
        "i understand",
        "we understand",
        "acknowledge",
    ],
    "apology": [
        "sorry",
        "apologize",
        "apology",
        "regret",
    ],
    "next_step": [
        "next step",
        "we will",
        "i will",
        "follow up",
        "update you",
        "look into this",
        "investigate",
    ],
}


def _normalize_text(value: str) -> str:
    normalized = (value or "").lower()
    translator = str.maketrans({char: " " for char in string.punctuation})
    normalized = normalized.translate(translator)
    return " ".join(normalized.split())


def _has_any_keyword(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def grade_hard(action_content: str) -> dict[str, float | str]:
    """Grade reply text using deterministic keyword-based weights."""
    text = _normalize_text(action_content)

    acknowledgement_hit = _has_any_keyword(text, KEYWORDS["acknowledgement"])
    apology_hit = _has_any_keyword(text, KEYWORDS["apology"])
    next_step_hit = _has_any_keyword(text, KEYWORDS["next_step"])

    score = 0.0
    if acknowledgement_hit:
        score += WEIGHTS["acknowledgement"]
    if apology_hit:
        score += WEIGHTS["apology"]
    if next_step_hit:
        score += WEIGHTS["next_step"]

    # Clamp to strict (0, 1) range — validator rejects exact 0.0 or 1.0
    score = round(score, 2)
    score = max(0.01, min(0.99, score))

    parts = []
    parts.append("acknowledgement: yes" if acknowledgement_hit else "acknowledgement: no")
    parts.append("apology: yes" if apology_hit else "apology: no")
    parts.append("next_step: yes" if next_step_hit else "next_step: no")

    return {"score": score, "reason": ", ".join(parts)}
