"""Static task data for hard reply drafting."""

TASK_ID = "hard_support_reply"
TASK_TYPE = "reply_drafting"
ALLOWED_ACTIONS = ["reply"]
INSTRUCTIONS = (
    "Write a short customer support reply. "
    "Include acknowledgement, apology, and next step."
)

SAMPLES = [
    {
        "email_subject": "Order delayed for over a week",
        "email_body": (
            "Hi support, my order was supposed to arrive last Friday and there "
            "has been no update. Can someone help?"
        ),
        "expected_keywords": ["acknowledgement", "apology", "next step"],
    }
]

TASK_DATA = {
    "task_id": TASK_ID,
    "task_type": TASK_TYPE,
    "allowed_actions": ALLOWED_ACTIONS,
    "instructions": INSTRUCTIONS,
    "samples": SAMPLES,
}
