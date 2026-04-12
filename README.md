---
title: Email Triage Environment Server
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
base_path: /web
tags:
  - openenv
---

# Email Triage OpenEnv

A minimal, deterministic OpenEnv-style environment for email triage tasks.
The environment supports three task types:
- spam classification
- priority classification
- customer-support reply drafting

## Real-World Use

Email triage is a common workflow in support, operations, and internal helpdesk teams.
This project simulates practical agent behavior such as:
- identifying likely spam quickly
- prioritizing urgent messages first
- drafting consistent support replies with required communication elements

## Tasks

1. Easy: Spam Classification
- Input: one email subject/body
- Output: `spam` or `not_spam`
- Action type: `classify`

2. Medium: Priority Classification
- Input: one email subject/body
- Output: `low`, `normal`, or `urgent`
- Action type: `classify`

3. Hard: Reply Drafting
- Input: one support email
- Output: short support reply
- Action type: `reply`

## Scoring Logic

- Easy grader: exact normalized label match (`spam` vs `not_spam`)
- Medium grader: exact normalized label match (`low` / `normal` / `urgent`)
- Hard grader: deterministic keyword checklist scoring
- acknowledgement = `0.4`
- apology = `0.3`
- next step = `0.3`
- final score is clamped to `[0.0, 1.0]`

## Setup (Local)

1. Create and activate a virtual environment.
```bash
python -m venv .venv
```

2. Install dependencies.
```bash
pip install -r requirements.txt
```

3. Run the API server.
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

4. Verify endpoints.
```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/reset
curl http://127.0.0.1:8000/state
```

5. Run baseline inference (optional).
```bash
python inference.py
```

## Docker Usage

1. Build image.
```bash
docker build -t email-triage-env .
```

2. Run container.
```bash
docker run --rm -p 7860:7860 email-triage-env
```

3. Check health.
```bash
curl http://127.0.0.1:7860/health
```

## Deploy to Hugging Face Spaces

1. Create a new Space on Hugging Face.
- Space SDK: `Docker`
- Visibility: public or private as needed

2. Push this repository contents to the Space repo.
- Include at minimum: `Dockerfile`, `requirements.txt`, source files, and `openenv.yaml`

3. Ensure the server starts from the Docker CMD.
- Current CMD runs: `uvicorn server:app --host 0.0.0.0 --port ${PORT:-7860}`

4. After build completes, open the Space URL and verify:
- `/health` returns status `healthy`
- `/reset`, `/step`, and `/state` respond successfully
