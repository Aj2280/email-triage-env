---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
---

# 📧 Email Triage — OpenEnv Environment

A real-world OpenEnv environment where AI agents learn to triage emails:
**categorise → prioritise → route → respond.**

Built for the **Meta × PyTorch × Scaler OpenEnv Hackathon**.

> [!IMPORTANT]
> **Status: Phase 1 & Phase 2 PASSED** ✅
> This environment is fully compliant with the Phase 2 agentic evaluation requirements, including mandatory structured output parsing and score range validation.

---

## 🎯 Environment Description

Agents interact with an inbox of realistic business emails and must triage each one through three tasks of increasing difficulty.

| Task | What the agent must do | Reward Range |
|------|----------------------|-----------|
| `task_easy` | Classify category only: `spam / urgent / normal / promotional` | (0.0, 1.0) |
| `task_medium` | Category + Priority + Department routing | (0.0, 1.0) |
| `task_hard` | Full triage + write a short response draft | (0.0, 1.0) |

---

## 🏆 Scoring & Compliance (Phase 2)

To ensure compatibility with the automated evaluator, the following scoring rules are enforced:
- **Strict Range**: All rewards and episode scores are clamped strictly between 0 and 1 (typically **0.01 to 0.99**) to satisfy the hackathon validator's `strictly within (0, 1)` check.
- **Partial Credit**: `task_medium` and `task_hard` award partial credit for "off-by-one" priority levels and keyword matches in responses.

---

## 📋 Mandatory Structured Output

The `inference.py` script must print the following blocks to `stdout` for the Phase 2 parser to correctly grade the agent:

```text
[START] task=task_id
[STEP] step=N reward=X
[END] task=task_id score=Y steps=N
```
*Note: All output blocks include `flush=True` to ensure real-time parsing.*

---

## 🚀 Setup & Run

### Local (without Docker)

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Docker (Hackathon Stable)
We use a specific base image to ensure registry stability on remote runners:

```bash
docker build -t email-triage-env .
docker run -p 8000:8000 email-triage-env
```

### Verify it works

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" \
     -d '{"task_id": "task_easy", "seed": 42}'
```

---

## 🤖 Run Baseline Inference

```bash
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
export HF_TOKEN=your_key_here

# Start the environment server first, then:
python inference.py --base-url http://localhost:8000
```

---

## 📁 Project Structure

```
email_triage_env/
├── openenv.yaml          # OpenEnv spec (interface, action/obs space)
├── models.py             # Typed Pydantic models for API
├── inference.py          # Baseline agent with structured output [START/STEP/END]
├── requirements.txt      # Minimal dependency set
├── Dockerfile            # Python 3.10-slim-bullseye build
└── server/
    ├── app.py            # FastAPI entry point
    ├── email_triage_env.py  # Core state management
    └── tasks.py          # Graders (with 0.01-0.99 score clamping)
```

---

## 🔧 Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | LLM API endpoint (e.g., OpenRouter or HF Router) |
| `MODEL_NAME` | Model identifier (e.g., meta-llama/Llama-3-8B) |
| `HF_TOKEN` | Hugging Face Access Token |

---

## ☁️ Deployment

This project is optimized for deployment as a **Hugging Face Docker Space**. Ensure you set the `HF_TOKEN` in the Space settings as a Secret for the inference script to access protected models.
