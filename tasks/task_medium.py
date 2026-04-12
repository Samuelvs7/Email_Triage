"""Static task data for medium priority classification."""

TASK_ID = "medium_priority_classification"
TASK_TYPE = "priority_classification"
ALLOWED_ACTIONS = ["classify"]
INSTRUCTIONS = (
    "Classify each email priority as low, normal, or urgent. "
    "Return exactly one label: low, normal, or urgent."
)

SAMPLES = [
    {
        "email_subject": "Weekly newsletter draft",
        "email_body": "No rush. Please review the draft by the end of this week.",
        "expected_label": "low",
    },
    {
        "email_subject": "Invoice question",
        "email_body": "Can you clarify line item 4 when you have a moment today?",
        "expected_label": "normal",
    },
    {
        "email_subject": "Production outage affecting customers",
        "email_body": "Service is down for multiple users. Need immediate support.",
        "expected_label": "urgent",
    },
]

TASK_DATA = {
    "task_id": TASK_ID,
    "task_type": TASK_TYPE,
    "allowed_actions": ALLOWED_ACTIONS,
    "instructions": INSTRUCTIONS,
    "samples": SAMPLES,
}
