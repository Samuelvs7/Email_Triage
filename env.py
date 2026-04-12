"""Async OpenEnv-style environment for Email Triage."""

from __future__ import annotations

from typing import Any

from graders.grader_easy import grade_easy
from graders.grader_hard import grade_hard
from graders.grader_medium import grade_medium
from models import Action, Observation, Reward
from tasks.task_easy import TASK_DATA as EASY_TASK
from tasks.task_hard import TASK_DATA as HARD_TASK
from tasks.task_medium import TASK_DATA as MEDIUM_TASK


class EmailTriageEnv:
    """Minimal deterministic environment for Email Triage tasks."""

    def __init__(self) -> None:
        self._task_instances = self._build_task_instances()
        self._next_task_index = 0

        self._current_task: dict[str, Any] | None = None
        self._done = True
        self._last_action: Action | None = None
        self._last_reward: Reward | None = None

    @staticmethod
    def _build_task_instances() -> list[dict[str, Any]]:
        datasets = [EASY_TASK, MEDIUM_TASK, HARD_TASK]
        instances: list[dict[str, Any]] = []

        for dataset in datasets:
            for sample_idx, sample in enumerate(dataset["samples"]):
                instances.append(
                    {
                        "task_id": dataset["task_id"],
                        "task_type": dataset["task_type"],
                        "allowed_actions": dataset["allowed_actions"],
                        "instructions": dataset["instructions"],
                        "sample_index": sample_idx,
                        "email_subject": sample["email_subject"],
                        "email_body": sample["email_body"],
                        "expected_label": sample.get("expected_label"),
                        "expected_keywords": sample.get("expected_keywords", []),
                    }
                )

        return instances

    def _current_observation(self) -> Observation:
        if self._current_task is None:
            return Observation(
                task_id="",
                task_type="",
                email_subject="",
                email_body="",
                allowed_actions=[],
                instructions="No active task. Call reset() first.",
            )

        return Observation(
            task_id=self._current_task["task_id"],
            task_type=self._current_task["task_type"],
            email_subject=self._current_task["email_subject"],
            email_body=self._current_task["email_body"],
            allowed_actions=self._current_task["allowed_actions"],
            instructions=self._current_task["instructions"],
        )

    async def reset(self) -> dict[str, Any]:
        """Load the next task instance and return its observation."""
        task = self._task_instances[self._next_task_index % len(self._task_instances)]
        self._next_task_index += 1

        self._current_task = task
        self._done = False
        self._last_action = None
        self._last_reward = None

        observation = self._current_observation()
        return observation.model_dump()

    async def step(self, action: Action | dict[str, Any]) -> dict[str, Any]:
        """Validate action, grade it, and end the episode."""
        if self._current_task is None:
            reward = Reward(score=0.0, reason="No active task. Call reset() first.")
            return {
                "state": self._current_observation().model_dump(),
                "reward": reward.score,
                "done": True,
                "info": {"error": "missing_active_task", "reason": reward.reason},
            }

        if self._done:
            reward = self._last_reward or Reward(score=0.0, reason="Episode already done.")
            return {
                "state": self._current_observation().model_dump(),
                "reward": reward.score,
                "done": True,
                "info": {"error": "episode_already_done", "reason": reward.reason},
            }

        parsed_action = self._validate_action(action)
        if isinstance(parsed_action, dict):
            reward = Reward(score=0.0, reason=parsed_action["error"])
            self._last_reward = reward
            self._done = True
            return {
                "state": self._current_observation().model_dump(),
                "reward": reward.score,
                "done": True,
                "info": {"error": "invalid_action", "reason": reward.reason},
            }

        self._last_action = parsed_action
        result = self._grade_action(parsed_action)
        reward = Reward(score=float(result["score"]), reason=str(result["reason"]))
        self._last_reward = reward
        self._done = True

        info: dict[str, Any] = {
            "task_id": self._current_task["task_id"],
            "task_type": self._current_task["task_type"],
            "sample_index": self._current_task["sample_index"],
        }

        expected_label = self._current_task.get("expected_label")
        if expected_label is not None:
            info["expected_label"] = expected_label

        expected_keywords = self._current_task.get("expected_keywords")
        if expected_keywords:
            info["expected_keywords"] = expected_keywords

        return {
            "state": self._current_observation().model_dump(),
            "reward": reward.score,
            "done": True,
            "info": {**info, "reason": reward.reason},
        }

    def _validate_action(self, action: Action | dict[str, Any]) -> Action | dict[str, str]:
        try:
            parsed = action if isinstance(action, Action) else Action.model_validate(action)
        except Exception as exc:  # noqa: BLE001 - keep validation path simple
            return {"error": f"Invalid action payload: {exc}"}

        allowed_actions = self._current_task["allowed_actions"]
        if parsed.action_type not in allowed_actions:
            allowed = ", ".join(allowed_actions)
            return {"error": f"Invalid action_type '{parsed.action_type}'. Allowed: {allowed}."}

        if not parsed.content.strip():
            return {"error": "Action content must be non-empty."}

        return parsed

    def _grade_action(self, action: Action) -> dict[str, float | str]:
        task_type = self._current_task["task_type"]

        if task_type == "spam_classification":
            expected_label = self._current_task["expected_label"]
            return grade_easy(action.content, expected_label)

        if task_type == "priority_classification":
            expected_label = self._current_task["expected_label"]
            return grade_medium(action.content, expected_label)

        if task_type == "reply_drafting":
            return grade_hard(action.content)

        return {"score": 0.0, "reason": f"Unsupported task_type '{task_type}'."}

    async def state(self) -> dict[str, Any]:
        """Expose internal state for debugging."""
        return {
            "has_active_task": self._current_task is not None,
            "done": self._done,
            "next_task_index": self._next_task_index,
            "current_task_id": self._current_task["task_id"] if self._current_task else None,
            "current_task_type": self._current_task["task_type"] if self._current_task else None,
            "current_sample_index": self._current_task["sample_index"] if self._current_task else None,
            "last_action": self._last_action.model_dump() if self._last_action else None,
            "last_reward": self._last_reward.model_dump() if self._last_reward else None,
        }
