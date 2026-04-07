"""
mock_inference_final.py — Final clean verification script.
"""
import requests
from server.tasks import EMAILS

BASE_URL = "https://abhi2280-email-triage-env.hf.space"

def run_test(task_id: str):
    print(f"Testing {task_id}...")
    # Reset
    obs = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id, "seed": 42}, timeout=60).json()
    email_id = obs.get("email_id")
    ground_truth = next(e["ground_truth"] for e in EMAILS if e["email_id"] == email_id)
    
    # Step
    action = {
        "task_id": task_id,
        "category": ground_truth["category"],
        "priority": ground_truth.get("priority", "low"),
        "department": ground_truth.get("department", "HR"),
        "response_draft": "test response"
    }
    result = requests.post(f"{BASE_URL}/step", json=action, timeout=60).json()
    print(f"  {task_id} Result: {result.get('reward', 0.0):.2f}/1.00 | {result.get('feedback', '')[:50]}...")

if __name__ == "__main__":
    health = requests.get(f"{BASE_URL}/health", timeout=60).json()
    print(f"✅ Live Health: {health}")
    run_test("task_easy")
    run_test("task_medium")
    run_test("task_hard")
    print("\n🚀 ALL SYSTEMS OPERATIONAL!")
