"""Static task data for easy spam classification."""

TASK_ID = "easy_spam_classification"
TASK_TYPE = "spam_classification"
ALLOWED_ACTIONS = ["classify"]
INSTRUCTIONS = (
    "Classify each email as spam or not_spam. "
    "Return exactly one label: spam or not_spam."
)

SAMPLES = [
    {
        "email_subject": "You've won a $500 gift card",
        "email_body": "Claim your reward now. Click this link and enter your card details.",
        "expected_label": "spam",
    },
    {
        "email_subject": "Project meeting moved to 3 PM",
        "email_body": "Please join the team sync at 3 PM today in Conference Room B.",
        "expected_label": "not_spam",
    },
    {
        "email_subject": "Final notice: account suspension",
        "email_body": "Your account will be suspended unless you verify your password immediately.",
        "expected_label": "spam",
    },
]

TASK_DATA = {
    "task_id": TASK_ID,
    "task_type": TASK_TYPE,
    "allowed_actions": ALLOWED_ACTIONS,
    "instructions": INSTRUCTIONS,
    "samples": SAMPLES,
}
