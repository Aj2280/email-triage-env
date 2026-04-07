"""
models.py — Typed Pydantic models for the Email Triage OpenEnv environment.
Defines Action, Observation, and State following the OpenEnv spec.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ── Action ────────────────────────────────────────────────────────────────────

class TriageAction(BaseModel):
    """Action submitted by the agent for email triage."""
    task_id: Literal["task_easy", "task_medium", "task_hard"] = Field(
        ..., description="Which task the agent is solving"
    )
    category: Literal["spam", "urgent", "normal", "promotional"] = Field(
        ..., description="Email category classification"
    )
    priority: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        None, description="Priority level (required for task_medium and task_hard)"
    )
    department: Optional[Literal["HR", "IT", "Sales", "Support", "Finance"]] = Field(
        None, description="Target department for routing (required for task_medium and task_hard)"
    )
    response_draft: Optional[str] = Field(
        None, description="Short response or action summary (required for task_hard)"
    )


# ── Observation ───────────────────────────────────────────────────────────────

class EmailObservation(BaseModel):
    """Observation returned to the agent after reset() or step()."""
    email_id: str = Field(..., description="Unique ID of the current email")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body text")
    sender: str = Field(..., description="Sender email address")
    received_at: str = Field(..., description="ISO timestamp of email receipt")
    task_id: str = Field(..., description="Current task the agent should solve")
    feedback: str = Field("", description="Feedback from the grader after a step")
    score: float = Field(0.0, description="Score awarded in the last step (0.0–1.0)")
    done: bool = Field(False, description="Whether the episode has ended")


# ── State ─────────────────────────────────────────────────────────────────────

class TriageState(BaseModel):
    """Internal environment state (exposed via GET /state)."""
    episode_id: str = Field("", description="Current episode identifier")
    step_count: int = Field(0, description="Number of steps taken in this episode")
    current_task_id: str = Field("task_easy", description="Active task")
    current_email_id: str = Field("", description="Active email ID")
    total_reward: float = Field(0.0, description="Cumulative reward this episode")
    max_steps: int = Field(10, description="Max steps allowed per episode")
    done: bool = Field(False, description="Whether episode is finished")


# ── Step Result ───────────────────────────────────────────────────────────────

class StepResult(BaseModel):
    """Full response returned by POST /step."""
    observation: EmailObservation
    reward: float
    done: bool
    info: dict = Field(default_factory=dict)
