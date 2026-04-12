"""Pydantic models for the Email Triage OpenEnv environment."""

from typing import Literal

from pydantic import BaseModel


class Observation(BaseModel):
    task_id: str
    task_type: str
    email_subject: str
    email_body: str
    allowed_actions: list[str]
    instructions: str


class Action(BaseModel):
    action_type: Literal["classify", "reply"]
    content: str


class Reward(BaseModel):
    score: float
    reason: str
