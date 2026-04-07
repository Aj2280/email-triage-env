"""
email_triage_env.py — Core OpenEnv environment for Email Triage.

Implements reset(), step(), and state() following the OpenEnv spec.
"""
import uuid
from typing import Optional

from models import TriageAction, EmailObservation, TriageState, StepResult
from server.tasks import get_random_email, get_email_by_id, run_grader


class EmailTriageEnvironment:
    """
    OpenEnv-compatible Email Triage environment.

    An AI agent receives emails one at a time and must triage them:
      - task_easy:   classify into a category
      - task_medium: classify + assign priority + route to department
      - task_hard:   full triage + draft a short response

    Each episode runs for max_steps steps. A new email is presented
    at each step. The agent can optionally change the task_id per step.
    """

    MAX_STEPS = 10

    def __init__(self):
        self._state = TriageState()
        self._current_email: Optional[dict] = None
        self._step_seed = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def reset(self, task_id: str = "task_easy", seed: Optional[int] = None) -> EmailObservation:
        """Initialise a new episode and return the first observation."""
        self._step_seed = seed if seed is not None else 0
        email = get_random_email(seed=self._step_seed)
        self._current_email = email

        self._state = TriageState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            current_task_id=task_id,
            current_email_id=email["email_id"],
            total_reward=0.0,
            max_steps=self.MAX_STEPS,
            done=False,
        )

        return self._make_observation(feedback="Episode started. Triage the email.", score=0.0)

    def step(self, action: TriageAction) -> StepResult:
        """Submit a triage action, evaluate with the grader, return result."""
        if self._state.done:
            obs = self._make_observation(
                feedback="Episode is already done. Call reset() to start a new episode.",
                score=0.0,
            )
            return StepResult(observation=obs, reward=0.0, done=True)

        # Run grader
        score, feedback = run_grader(
            task_id=action.task_id,
            action=action.model_dump(),
            email=self._current_email,
        )

        # Update state
        self._state.step_count += 1
        self._state.total_reward += score
        self._state.current_task_id = action.task_id

        # Advance to next email
        self._step_seed += 1
        next_email = get_random_email(seed=self._step_seed)
        self._current_email = next_email
        self._state.current_email_id = next_email["email_id"]

        # Check termination
        done = self._state.step_count >= self.MAX_STEPS
        self._state.done = done

        obs = self._make_observation(feedback=feedback, score=score, done=done)
        return StepResult(
            observation=obs,
            reward=score,
            done=done,
            info={
                "episode_id": self._state.episode_id,
                "step_count": self._state.step_count,
                "total_reward": round(self._state.total_reward, 3),
            },
        )

    def state(self) -> TriageState:
        """Return the current internal environment state."""
        return self._state

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_observation(
        self, feedback: str = "", score: float = 0.0, done: bool = False
    ) -> EmailObservation:
        email = self._current_email
        return EmailObservation(
            email_id=email["email_id"],
            subject=email["subject"],
            body=email["body"],
            sender=email["sender"],
            received_at=email["received_at"],
            task_id=self._state.current_task_id,
            feedback=feedback,
            score=score,
            done=done,
        )
