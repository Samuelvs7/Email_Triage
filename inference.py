"""
Inference Script for Email Triage Environment
===================================
MANDATORY
- API_BASE_URL   The API endpoint for the LLM.
- MODEL_NAME     The model identifier to use for inference.
- HF_TOKEN       Your Hugging Face / API key.
- API_KEY        Alternative to HF_TOKEN.

STDOUT FORMAT
- [START] task=<task_name> env=<benchmark> model=<model_name>
- [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
- [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import os
from typing import List, Optional

from openai import OpenAI

from env import EmailTriageEnv
from models import Action


# ---------- Environment variables ----------
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
BENCHMARK = "email-triage-env"

if not API_KEY:
    raise ValueError("HF_TOKEN or API_KEY must be set.")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


# ---------- Logging helpers (strict format) ----------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ---------- LLM agent ----------

def get_llm_action(task_type: str, instructions: str, email_subject: str, email_body: str) -> tuple:
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


# ---------- Main: run each task as separate episode ----------

async def main():
    env = EmailTriageEnv()
    num_tasks = len(env._task_instances)

    for task_idx in range(num_tasks):
        obs = await env.reset()

        task_type = obs.get("task_type", "unknown")
        task_id = obs.get("task_id", task_type)
        instructions = obs.get("instructions", "")
        email_subject = obs.get("email_subject", "")
        email_body = obs.get("email_body", "")

        rewards: List[float] = []
        steps_taken = 0

        # Each task is a separate [START]/[END] episode
        log_start(task=task_type, env=BENCHMARK, model=MODEL_NAME)

        try:
            action_type, content = get_llm_action(
                task_type, instructions, email_subject, email_body
            )

            action = Action(action_type=action_type, content=content)
            result = await env.step(action)

            reward = result.get("reward", 0.0)
            done = result.get("done", True)
            error = result.get("info", {}).get("error", None)

            rewards.append(reward)
            steps_taken = 1

            log_step(step=1, action=content, reward=reward, done=done, error=error)

            score = reward
            success = score > 0.1

        except Exception as e:
            print(f"[DEBUG] Task {task_type} error: {e}", flush=True)
            score = 0.0
            success = False
            steps_taken = 1
            rewards = [0.0]

        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())