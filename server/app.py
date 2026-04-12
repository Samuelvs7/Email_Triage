"""Compatibility app module for OpenEnv validation tooling."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import uvicorn

ROOT_SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"

if not ROOT_SERVER_PATH.exists():
    raise FileNotFoundError(f"Expected root server module at {ROOT_SERVER_PATH}")

spec = importlib.util.spec_from_file_location("email_triage_root_server", ROOT_SERVER_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load root server module from {ROOT_SERVER_PATH}")

root_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_server)

app = root_server.app


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.host == "0.0.0.0" and args.port == 8000:
        main()
    else:
        main(host=args.host, port=args.port)
