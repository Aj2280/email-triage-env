""" app.py — FastAPI server exposing the OpenEnv HTTP endpoints.
Endpoints:
  POST /reset → Start a new episode
  POST /step → Submit a triage action
  GET /state → Inspect current environment state
  GET /health → Health check (required by OpenEnv validator)
"""

import sys
import os

# Make sure parent directory (project root) is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

from models import TriageAction, EmailObservation, TriageState, StepResult
from server.email_triage_env import EmailTriageEnvironment

app = FastAPI(
    title="Email Triage OpenEnv",
    description=(
        "A real-world OpenEnv environment where AI agents learn to triage emails — "
        "categorising, prioritising, and routing them to the correct department."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single global environment instance (sufficient for hackathon scope)
env = EmailTriageEnvironment()

# ── Request schemas ───────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task_easy"
    seed: Optional[int] = None

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    """Landing page for the Email Triage OpenEnv environment."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📧 Email Triage — OpenEnv</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { max-width: 700px; padding: 40px; text-align: center; }
            h1 { font-size: 2.5rem; margin-bottom: 10px; color: #fff; }
            .subtitle { font-size: 1.1rem; color: #a0a0c0; margin-bottom: 30px; }
            .badge { display: inline-block; background: #4caf50; color: #fff; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-bottom: 30px; }
            .endpoints { background: rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; text-align: left; margin-bottom: 24px; backdrop-filter: blur(10px); }
            .endpoints h3 { color: #90caf9; margin-bottom: 14px; font-size: 1rem; }
            .ep { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 0.95rem; }
            .ep:last-child { border-bottom: none; }
            .method { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 700; min-width: 50px; text-align: center; }
            .get { background: #1b5e20; color: #a5d6a7; }
            .post { background: #e65100; color: #ffcc80; }
            .path { color: #fff; font-family: monospace; }
            .desc { color: #999; margin-left: auto; font-size: 0.85rem; }
            .tasks { background: rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; text-align: left; backdrop-filter: blur(10px); }
            .tasks h3 { color: #90caf9; margin-bottom: 14px; font-size: 1rem; }
            .task-row { padding: 6px 0; font-size: 0.9rem; }
            .task-name { color: #ffcc80; font-family: monospace; font-weight: 600; }
            a.btn { display: inline-block; margin-top: 24px; padding: 12px 28px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s; }
            a.btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📧 Email Triage</h1>
            <p class="subtitle">OpenEnv Environment — AI agents learn to triage emails</p>
            <span class="badge">✅ Running — v1.0.0</span>

            <div class="endpoints">
                <h3>API Endpoints</h3>
                <div class="ep"><span class="method get">GET</span> <span class="path">/health</span> <span class="desc">Health check</span></div>
                <div class="ep"><span class="method post">POST</span> <span class="path">/reset</span> <span class="desc">Start new episode</span></div>
                <div class="ep"><span class="method post">POST</span> <span class="path">/step</span> <span class="desc">Submit triage action</span></div>
                <div class="ep"><span class="method get">GET</span> <span class="path">/state</span> <span class="desc">Inspect environment</span></div>
            </div>

            <div class="tasks">
                <h3>Task Difficulty Tiers</h3>
                <div class="task-row"><span class="task-name">task_easy</span> — Classify category (spam/urgent/normal/promotional)</div>
                <div class="task-row"><span class="task-name">task_medium</span> — Category + Priority + Department routing</div>
                <div class="task-row"><span class="task-name">task_hard</span> — Full triage + draft response</div>
            </div>

            <a href="/docs" class="btn">📖 Interactive API Docs</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    """Health check — must return 200 for the OpenEnv validator."""
    return {"status": "ok", "environment": "email-triage-env", "version": "1.0.0"}

@app.post("/reset", response_model=EmailObservation)
def reset(req: ResetRequest = ResetRequest()):
    """
    Reset the environment and start a new episode.
    Parameters:
      task_id: Which task to use — task_easy | task_medium | task_hard
      seed: Optional random seed for reproducibility
    """
    valid_tasks = {"task_easy", "task_medium", "task_hard"}
    if req.task_id not in valid_tasks:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid task_id '{req.task_id}'. Must be one of {valid_tasks}",
        )

    obs = env.reset(task_id=req.task_id, seed=req.seed)
    return obs

@app.post("/step", response_model=StepResult)
def step(action: TriageAction):
    """
    Submit a triage action and receive the next observation + reward.
    The agent should populate fields based on the current task:
      task_easy → category only
      task_medium → category + priority + department
      task_hard → category + priority + department + response_draft
    """
    result = env.step(action)
    return result

@app.get("/state", response_model=TriageState)
def state():
    """Return the current internal state of the environment."""
    return env.state()

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    """Main entry point for the server, used by the [project.scripts] in pyproject.toml."""
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
