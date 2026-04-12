"""Minimal client helper for Email Triage environment endpoints."""

from __future__ import annotations

from typing import Any

import requests


class EmailTriageClient:
    """Small HTTP client for reset/step/state endpoints."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def reset(self) -> dict[str, Any]:
        return self._request("POST", "/reset", json={})

    def step(self, action_type: str, content: str) -> dict[str, Any]:
        payload = {"action_type": action_type, "content": content}
        return self._request("POST", "/step", json=payload)

    def state(self) -> dict[str, Any]:
        return self._request("GET", "/state")

    def _request(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        response = requests.request(
            method=method,
            url=f"{self.base_url}{path}",
            json=json,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
