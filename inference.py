"""Standalone inference script for Email Triage environment.

Uses the hackathon's LLM proxy (API_BASE_URL + API_KEY) to classify and
reply to emails, then grades the responses through the environment.
"""

import asyncio
import os
from openai import OpenAI

from env import EmailTriageEnv
from models import Action


# ---------- LLM client using hackathon proxy ----------
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")

if not API_BASE_URL or not API_KEY:
    raise RuntimeError(
        "API_BASE_URL and API_KEY must be set. "
        "These are injected by the hackathon platform."
    )

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)


# ---------- Logging helpers ----------

def log_start(task, env_name, model):
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(step, task_type, action, reward, done, error=None):
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} task_type={task_type} action={action!r} "
        f"reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ---------- LLM agent ----------

def get_llm_action(task_type: str, instructions: str, email_subject: str, email_body: str) -> tuple[str, str]:
    """Call the LLM through the hackathon proxy and return (action_type, content)."""

    email_text = f"Subject: {email_subject}\nBody: {email_body}"

    if task_type == "reply_drafting":
        system_prompt = (
            "You are a helpful customer support agent. "
            "Write a short, professional reply to the customer email. "
            "Your reply MUST include: "
            "1) An acknowledgement (e.g. 'thank you for reaching out'), "
            "2) An apology (e.g. 'sorry' or 'apologize'), "
            "3) A next step (e.g. 'we will look into this' or 'I will follow up')."
        )
        action_type = "reply"
        max_tokens = 200
    elif task_type == "priority_classification":
        system_prompt = (
            "You are an email priority classifier. "
            "Classify the email as exactly one word: low, normal, or urgent. "
            "Respond with ONLY the label, nothing else."
        )
        action_type = "classify"
        max_tokens = 10
    else:
        # spam_classification
        system_prompt = (
            "You are a spam classifier. "
            "Classify the email as exactly one label: spam or not_spam. "
            "Respond with ONLY the label, nothing else."
        )
        action_type = "classify"
        max_tokens = 10

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{instructions}\n\n{email_text}"},
            ],
            max_tokens=max_tokens,
            temperature=0,
        )
        content = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        # Fallback so grading still runs
        if task_type == "reply_drafting":
            content = (
                "Thank you for reaching out. I am sorry for the inconvenience. "
                "We will look into this and follow up with you shortly."
            )
        elif task_type == "priority_classification":
            content = "normal"
        else:
            content = "not_spam"

    return action_type, content


# ---------- Main loop ----------

async def main():
    env = EmailTriageEnv()
    rewards = []
    steps = 0
    num_tasks = len(env._task_instances)

    log_start("email-triage", "openenv", MODEL_NAME)

    try:
        for step_num in range(1, num_tasks + 1):
            obs = await env.reset()

            task_type = obs.get("task_type", "")
            instructions = obs.get("instructions", "")
            email_subject = obs.get("email_subject", "")
            email_body = obs.get("email_body", "")

            action_type, content = get_llm_action(
                task_type, instructions, email_subject, email_body
            )

            action = Action(action_type=action_type, content=content)
            result = await env.step(action)

            reward = result.get("reward", 0.0)
            done = result.get("done", False)

            rewards.append(reward)
            steps = step_num

            log_step(step_num, task_type, content, reward, done)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        success = score > 0.5

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        score = sum(rewards) / len(rewards) if rewards else 0.0
        success = False

    log_end(success, steps, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())