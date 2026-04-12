"""Script entry point for running the Email Triage API server."""

from __future__ import annotations

import argparse

import uvicorn


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run("server:app", host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(host=args.host, port=args.port)
