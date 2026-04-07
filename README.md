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

Built for the **Meta × PyTorch × Scaler OpenEnv Hackathon **.

---

## 🎯 Environment Description

Agents interact with an inbox of realistic business emails and must triage each
one through three tasks of increasing difficulty.

| Task | What the agent must do | Max score |
|------|----------------------|-----------|
| `task_easy` | Classify category only: `spam / urgent / normal / promotional` | 1.0 |
| `task_medium` | Category + Priority (`low/medium/high/critical`) + Department (`HR/IT/Sales/Support/Finance`) | 1.0 |
| `task_hard` | Full triage + write a short response draft | 1.0 |

---

## 🔌 Action & Observation Spaces

### Action (`POST /step`)

```json
{
  "task_id":        "task_easy | task_medium | task_hard",
  "category":       "spam | urgent | normal | promotional",
  "priority":       "low | medium | high | critical",
  "department":     "HR | IT | Sales | Support | Finance",
  "response_draft": "Short action summary or reply (task_hard only)"
}
```

### Observation (returned by `/reset` and `/step`)

```json
{
  "email_id":    "e002",
  "subject":     "URGENT: Production server is down",
  "body":        "Hi team, our production server...",
  "sender":      "ceo@bigclient.com",
  "received_at": "2025-04-01T09:15:00Z",
  "task_id":     "task_easy",
  "feedback":    "✅ Correct! Category 'urgent' matches expected 'urgent'.",
  "score":       1.0,
  "done":        false
}
```

---

## 🏆 Reward Function

**task_easy** — binary: `1.0` if category correct, `0.0` otherwise.

**task_medium** — partial credit:
- Category correct → +0.40
- Priority correct → +0.30 (off-by-one → +0.15)
- Department correct → +0.30

**task_hard** — partial credit:
- Category → +0.30
- Priority → +0.20 (off-by-one → +0.10)
- Department → +0.20
- Response draft keyword quality → up to +0.30

---

## 🚀 Setup & Run

### Local (without Docker)

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Docker

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
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=your_key_here

# Start the environment server first, then:
python inference.py --base-url http://localhost:8000
```

Results are saved to `inference_results.json`.

---

## 📋 OpenEnv Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Health check |
| `POST` | `/reset`  | Start new episode |
| `POST` | `/step`   | Submit triage action |
| `GET`  | `/state`  | Inspect current state |

---

## 📁 Project Structure

```
email_triage_env/
├── openenv.yaml          # OpenEnv spec
├── models.py             # Typed Action / Observation / State
├── inference.py          # Baseline inference script
├── requirements.txt
├── Dockerfile
├── README.md
└── server/
    ├── app.py            # FastAPI server
    ├── email_triage_env.py  # Core environment logic
    └── tasks.py          # Email dataset + graders
```

---

## 🔧 Required Environment Variables (for inference)

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | LLM API endpoint |
| `MODEL_NAME` | Model identifier |
| `HF_TOKEN` | Hugging Face / API key |

---

## ☁️ Deployment to Hugging Face Spaces

This environment is fully containerized and ready to be deployed as a Docker Space on Hugging Face:
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set the Space name (e.g., `email-triage-env`).
3. Select **Docker** as the Space SDK and choose the **Blank** Docker template.
4. Clone the space repository and copy all these project files into it.
5. Commit and push the files. Hugging Face will automatically build the `Dockerfile` and expose the API on port `8000`.
