"""
tasks.py — Email dataset and graders for the Email Triage environment.

3 tasks with increasing difficulty:
  task_easy   → Categorize only                         (score 0.0 / 1.0)
  task_medium → Categorize + Priority + Department      (score 0.0–1.0, partial credit)
  task_hard   → Full triage + response draft quality    (score 0.0–1.0, partial credit)
"""
import random
from typing import Optional

# ── Email Dataset ─────────────────────────────────────────────────────────────

EMAILS = [
    {
        "email_id": "e001",
        "sender": "alice@company.com",
        "received_at": "2025-04-01T09:00:00Z",
        "subject": "Congratulations! You've won $1,000,000",
        "body": (
            "Dear user, you have been selected as our lucky winner. "
            "Click this link to claim your prize immediately. "
            "Hurry, offer expires in 24 hours!"
        ),
        "ground_truth": {
            "category": "spam",
            "priority": "low",
            "department": "IT",          # IT handles spam/security
            "response_keywords": ["ignore", "spam", "block", "filter", "report"],
        },
    },
    {
        "email_id": "e002",
        "sender": "ceo@bigclient.com",
        "received_at": "2025-04-01T09:15:00Z",
        "subject": "URGENT: Production server is down — need immediate fix",
        "body": (
            "Hi team, our production server has been down for the past 30 minutes. "
            "We are losing $5,000 per minute. Please escalate this immediately and "
            "have your on-call engineer contact me at once."
        ),
        "ground_truth": {
            "category": "urgent",
            "priority": "critical",
            "department": "IT",
            "response_keywords": ["escalate", "engineer", "contact", "fix", "priority", "immediately"],
        },
    },
    {
        "email_id": "e003",
        "sender": "promo@shoppingsite.com",
        "received_at": "2025-04-01T09:30:00Z",
        "subject": "50% off sale — this weekend only!",
        "body": (
            "Shop our biggest sale of the year. Get 50% off all electronics, "
            "clothing, and home goods. Use code SAVE50 at checkout. "
            "Valid Saturday and Sunday only."
        ),
        "ground_truth": {
            "category": "promotional",
            "priority": "low",
            "department": "Sales",
            "response_keywords": ["unsubscribe", "noted", "promotional", "archived"],
        },
    },
    {
        "email_id": "e004",
        "sender": "john.doe@company.com",
        "received_at": "2025-04-01T10:00:00Z",
        "subject": "Leave application for next week",
        "body": (
            "Hi, I would like to apply for annual leave from April 7th to April 11th. "
            "I have completed all my pending tasks. Please let me know if this is approved."
        ),
        "ground_truth": {
            "category": "normal",
            "priority": "medium",
            "department": "HR",
            "response_keywords": ["approved", "HR", "leave", "forward", "acknowledge"],
        },
    },
    {
        "email_id": "e005",
        "sender": "vendor@supplierco.com",
        "received_at": "2025-04-01T10:30:00Z",
        "subject": "Invoice #4521 — Payment overdue",
        "body": (
            "Dear accounts team, we noticed that invoice #4521 for $12,400 "
            "issued on March 1st is now 30 days overdue. Please process this payment "
            "at your earliest convenience to avoid late fees."
        ),
        "ground_truth": {
            "category": "urgent",
            "priority": "high",
            "department": "Finance",
            "response_keywords": ["payment", "process", "invoice", "finance", "accounts"],
        },
    },
    {
        "email_id": "e006",
        "sender": "newsletter@techdigest.com",
        "received_at": "2025-04-01T11:00:00Z",
        "subject": "This week in tech: AI breakthroughs and more",
        "body": (
            "Welcome to this week's Tech Digest. Top stories: OpenAI releases GPT-5, "
            "Meta open-sources a new model, and a startup raises $200M for quantum computing. "
            "Read the full stories on our website."
        ),
        "ground_truth": {
            "category": "promotional",
            "priority": "low",
            "department": "IT",
            "response_keywords": ["noted", "archived", "unsubscribe", "newsletter"],
        },
    },
    {
        "email_id": "e007",
        "sender": "new.hire@company.com",
        "received_at": "2025-04-01T11:30:00Z",
        "subject": "Laptop setup issues — cannot access internal systems",
        "body": (
            "Hi, I just joined the company today and my laptop is not letting me log in "
            "to the internal portal. I tried resetting my password but the IT help page "
            "is also not loading. Could someone help me set this up?"
        ),
        "ground_truth": {
            "category": "normal",
            "priority": "high",
            "department": "IT",
            "response_keywords": ["IT support", "ticket", "help", "reset", "contact IT"],
        },
    },
    {
        "email_id": "e008",
        "sender": "prospect@startup.io",
        "received_at": "2025-04-01T12:00:00Z",
        "subject": "Interested in your enterprise plan",
        "body": (
            "Hello, we are a 200-person startup and are evaluating your enterprise plan "
            "for our entire team. Could someone from your sales team reach out to schedule "
            "a demo? We are ready to move quickly."
        ),
        "ground_truth": {
            "category": "normal",
            "priority": "high",
            "department": "Sales",
            "response_keywords": ["demo", "sales team", "schedule", "enterprise", "contact"],
        },
    },
]


def get_random_email(seed: Optional[int] = None) -> dict:
    """Return a random email from the dataset."""
    rng = random.Random(seed)
    return rng.choice(EMAILS)


def get_email_by_id(email_id: str) -> Optional[dict]:
    for e in EMAILS:
        if e["email_id"] == email_id:
            return e
    return None


# ── Graders ───────────────────────────────────────────────────────────────────

def grade_easy(action: dict, ground_truth: dict) -> tuple[float, str]:
    """
    task_easy: Score purely on correct category classification.
    Returns (score, feedback).
    """
    predicted = action.get("category", "").lower()
    expected = ground_truth["category"].lower()

    if predicted == expected:
        return 1.0, f"✅ Correct! Category '{predicted}' matches expected '{expected}'."
    else:
        return 0.0, f"❌ Incorrect. Predicted '{predicted}' but expected '{expected}'."


def grade_medium(action: dict, ground_truth: dict) -> tuple[float, str]:
    """
    task_medium: Partial credit across category (40%), priority (30%), department (30%).
    """
    score = 0.0
    feedback_parts = []

    # Category — 40%
    pred_cat = action.get("category", "").lower()
    exp_cat = ground_truth["category"].lower()
    if pred_cat == exp_cat:
        score += 0.4
        feedback_parts.append(f"✅ Category correct ({pred_cat})")
    else:
        feedback_parts.append(f"❌ Category wrong (got '{pred_cat}', expected '{exp_cat}')")

    # Priority — 30%
    pred_pri = (action.get("priority") or "").lower()
    exp_pri = ground_truth["priority"].lower()
    if pred_pri == exp_pri:
        score += 0.3
        feedback_parts.append(f"✅ Priority correct ({pred_pri})")
    else:
        # Partial credit for adjacent priority levels
        priority_order = ["low", "medium", "high", "critical"]
        if pred_pri in priority_order and exp_pri in priority_order:
            diff = abs(priority_order.index(pred_pri) - priority_order.index(exp_pri))
            if diff == 1:
                score += 0.15
                feedback_parts.append(f"⚠️ Priority off by one (got '{pred_pri}', expected '{exp_pri}') — partial credit")
            else:
                feedback_parts.append(f"❌ Priority wrong (got '{pred_pri}', expected '{exp_pri}')")
        else:
            feedback_parts.append(f"❌ Priority invalid or wrong (got '{pred_pri}', expected '{exp_pri}')")

    # Department — 30%
    pred_dep = (action.get("department") or "")
    exp_dep = ground_truth["department"]
    if pred_dep == exp_dep:
        score += 0.3
        feedback_parts.append(f"✅ Department correct ({pred_dep})")
    else:
        feedback_parts.append(f"❌ Department wrong (got '{pred_dep}', expected '{exp_dep}')")

    return round(score, 2), " | ".join(feedback_parts)


def grade_hard(action: dict, ground_truth: dict) -> tuple[float, str]:
    """
    task_hard: Full triage including response_draft quality.
    Category (30%) + Priority (20%) + Department (20%) + Response quality (30%).
    """
    score = 0.0
    feedback_parts = []

    # Category — 30%
    pred_cat = (action.get("category") or "").lower()
    exp_cat = ground_truth["category"].lower()
    if pred_cat == exp_cat:
        score += 0.3
        feedback_parts.append(f"✅ Category ({pred_cat})")
    else:
        feedback_parts.append(f"❌ Category (got '{pred_cat}', expected '{exp_cat}')")

    # Priority — 20%
    pred_pri = (action.get("priority") or "").lower()
    exp_pri = ground_truth["priority"].lower()
    if pred_pri == exp_pri:
        score += 0.2
        feedback_parts.append(f"✅ Priority ({pred_pri})")
    else:
        priority_order = ["low", "medium", "high", "critical"]
        if pred_pri in priority_order and exp_pri in priority_order:
            diff = abs(priority_order.index(pred_pri) - priority_order.index(exp_pri))
            if diff == 1:
                score += 0.1
                feedback_parts.append(f"⚠️ Priority off by one (partial)")
            else:
                feedback_parts.append(f"❌ Priority (got '{pred_pri}', expected '{exp_pri}')")
        else:
            feedback_parts.append(f"❌ Priority invalid")

    # Department — 20%
    pred_dep = (action.get("department") or "")
    exp_dep = ground_truth["department"]
    if pred_dep == exp_dep:
        score += 0.2
        feedback_parts.append(f"✅ Department ({pred_dep})")
    else:
        feedback_parts.append(f"❌ Department (got '{pred_dep}', expected '{exp_dep}')")

    # Response draft — 30%
    response = (action.get("response_draft") or "").lower()
    keywords = ground_truth["response_keywords"]
    if response:
        matched = [kw for kw in keywords if kw.lower() in response]
        keyword_score = min(len(matched) / max(len(keywords), 1), 1.0) * 0.3
        score += keyword_score
        if matched:
            feedback_parts.append(
                f"✅ Response draft OK — matched keywords: {matched} (+{round(keyword_score, 2)})"
            )
        else:
            feedback_parts.append("⚠️ Response draft present but no expected keywords matched")
    else:
        feedback_parts.append("❌ Response draft missing (required for task_hard)")

    return round(score, 2), " | ".join(feedback_parts)


def run_grader(task_id: str, action: dict, email: dict) -> tuple[float, str]:
    """Dispatch to the right grader based on task_id."""
    gt = email["ground_truth"]
    
    if task_id == "task_easy":
        raw_score, feedback = grade_easy(action, gt)
    elif task_id == "task_medium":
        raw_score, feedback = grade_medium(action, gt)
    elif task_id == "task_hard":
        raw_score, feedback = grade_hard(action, gt)
    else:
        raw_score, feedback = 0.0, f"Unknown task_id: {task_id}"

    # Scaler Phase 2 Requirement: Scores must be strictly between 0 and 1 (not 0.0 or 1.0)
    clamped_score = round(min(max(raw_score, 0.01), 0.99), 2)
    
    return clamped_score, feedback
