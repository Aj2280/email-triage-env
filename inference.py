"""
inference.py — Baseline inference script for the Email Triage OpenEnv environment.

Runs the LLM agent against all 3 tasks (easy / medium / hard) and prints
reproducible scores. Uses the OpenAI client as required by the hackathon spec.

Required environment variables:
  API_BASE_URL  — LLM API endpoint (e.g. https://api.openai.com/v1)
  MODEL_NAME    — Model identifier (e.g. gpt-4o-mini)
  HF_TOKEN      — Hugging Face / API key

Usage:
  python inference.py
  python inference.py --base-url http://localhost:8000   # point at local server
"""
import os
import json
import argparse
import requests
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")

TASKS = ["task_easy", "task_medium", "task_hard"]
EPISODES_PER_TASK = 3   # kept low to stay within the 20-min runtime limit
SEED_BASE = 42

# ── OpenAI client ─────────────────────────────────────────────────────────────

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN or "sk-placeholder",
)


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_system_prompt(task_id: str) -> str:
    base = (
        "You are an expert email triage agent. "
        "You will receive an email (subject, body, sender) and must triage it.\n\n"
        "Always respond with a valid JSON object and nothing else.\n"
    )

    if task_id == "task_easy":
        return base + (
            "Your JSON must have exactly this key:\n"
            "  category: one of [spam, urgent, normal, promotional]\n\n"
            "Example: {\"category\": \"urgent\"}"
        )
    elif task_id == "task_medium":
        return base + (
            "Your JSON must have exactly these keys:\n"
            "  category:   one of [spam, urgent, normal, promotional]\n"
            "  priority:   one of [low, medium, high, critical]\n"
            "  department: one of [HR, IT, Sales, Support, Finance]\n\n"
            "Example: {\"category\": \"urgent\", \"priority\": \"critical\", \"department\": \"IT\"}"
        )
    else:  # task_hard
        return base + (
            "Your JSON must have exactly these keys:\n"
            "  category:        one of [spam, urgent, normal, promotional]\n"
            "  priority:        one of [low, medium, high, critical]\n"
            "  department:      one of [HR, IT, Sales, Support, Finance]\n"
            "  response_draft:  a short (1-3 sentence) response or action summary\n\n"
            "Example: {\n"
            "  \"category\": \"urgent\",\n"
            "  \"priority\": \"critical\",\n"
            "  \"department\": \"IT\",\n"
            "  \"response_draft\": \"Escalating to on-call IT engineer immediately. "
            "Will update you within 15 minutes.\"\n"
            "}"
        )


def build_user_prompt(obs: dict) -> str:
    return (
        f"From:    {obs['sender']}\n"
        f"Subject: {obs['subject']}\n\n"
        f"{obs['body']}\n\n"
        "Please triage this email."
    )


# ── LLM call ─────────────────────────────────────────────────────────────────

def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """Call the LLM and parse its JSON response."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=300,
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Environment helpers ───────────────────────────────────────────────────────

def env_reset(base_url: str, task_id: str, seed: int) -> dict:
    r = requests.post(
        f"{base_url}/reset",
        json={"task_id": task_id, "seed": seed},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def env_step(base_url: str, action: dict) -> dict:
    r = requests.post(f"{base_url}/step", json=action, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_task(base_url: str, task_id: str, num_episodes: int) -> dict:
    """Run num_episodes episodes for a given task_id and return score summary."""
    episode_rewards = []

    for ep in range(num_episodes):
        seed = SEED_BASE + ep
        obs = env_reset(base_url, task_id, seed)
        total_reward = 0.0
        steps = 0

        print(f"  Episode {ep+1}/{num_episodes} — email: '{obs['subject'][:60]}'", flush=True)
        print(f"[START] task={task_id}", flush=True)

        while not obs.get("done", False):
            system_prompt = build_system_prompt(task_id)
            user_prompt   = build_user_prompt(obs)

            try:
                llm_output = call_llm(system_prompt, user_prompt)
            except Exception as e:
                print(f"    ⚠️  LLM parse error: {e}. Using fallback.", flush=True)
                llm_output = {"category": "normal"}

            action = {"task_id": task_id, **llm_output}
            result = env_step(base_url, action)

            reward  = result.get("reward", 0.0)
            total_reward += reward
            steps += 1
            obs = result.get("observation", {})

            print(f"    Step {steps} → reward={reward:.2f} | {obs.get('feedback','')[:80]}", flush=True)
            print(f"[STEP] step={steps} reward={reward}", flush=True)

            if result.get("done", False):
                break

        # Calculate and clamp the final score for the [END] block (strictly between 0 and 1)
        final_score = round(min(max(total_reward / max(steps, 1), 0.01), 0.99), 2)
        print(f"[END] task={task_id} score={final_score} steps={steps}", flush=True)
        episode_rewards.append(final_score)

    avg = sum(episode_rewards) / len(episode_rewards)
    return {
        "task_id": task_id,
        "episodes": num_episodes,
        "episode_avg_rewards": [round(r, 4) for r in episode_rewards],
        "mean_score": round(avg, 4),
    }


def main():
    parser = argparse.ArgumentParser(description="Email Triage baseline inference")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("ENV_BASE_URL", "http://localhost:8000"),
        help="Base URL of the running environment server",
    )
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    print(f"\n{'='*60}", flush=True)
    print(f" Email Triage — Baseline Inference", flush=True)
    print(f" Model:   {MODEL_NAME}", flush=True)
    print(f" Env URL: {base_url}", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Verify server is up
    health = requests.get(f"{base_url}/health", timeout=10)
    health.raise_for_status()
    print(f"✅ Server healthy: {health.json()}\n", flush=True)

    all_results = []
    for task_id in TASKS:
        print(f"\n── Task: {task_id} {'─'*40}", flush=True)
        result = run_task(base_url, task_id, EPISODES_PER_TASK)
        all_results.append(result)
        print(f"  ✅ Mean score: {result['mean_score']:.4f}", flush=True)

    # Summary
    print(f"\n{'='*60}", flush=True)
    print(" FINAL SCORES", flush=True)
    print(f"{'='*60}", flush=True)
    overall = []
    for r in all_results:
        print(f"  {r['task_id']:<15} → {r['mean_score']:.4f}  (episodes: {r['episodes']})", flush=True)
        overall.append(r["mean_score"])
    print(f"{'─'*60}", flush=True)
    print(f"  {'OVERALL MEAN':<15} → {sum(overall)/len(overall):.4f}", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Save results to file
    output = {
        "model": MODEL_NAME,
        "env_url": base_url,
        "tasks": all_results,
        "overall_mean": round(sum(overall) / len(overall), 4),
    }
    with open("inference_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to inference_results.json", flush=True)


if __name__ == "__main__":
    main()
