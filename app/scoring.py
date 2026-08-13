from typing import Optional
from datetime import datetime, timezone


def classify_deviation_risk(
    severity: str,
    status: str,
    created_at: str,
    recurrence: bool = False,
    assigned_to: Optional[str] = None,
) -> dict:
    """
    Explainable, rule-based risk classification for deviations.
    Returns score, classification, and list of contributing reasons.
    Score is additive and transparent — not a black-box model.
    """
    score = 0
    reasons = []

    if severity == "Critical":
        score += 3
        reasons.append("Severity is Critical (+3)")
    elif severity == "Major":
        score += 2
        reasons.append("Severity is Major (+2)")

    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created).days
        if age_days > 30 and status not in ("Resolved", "Accepted with Risk"):
            score += 2
            reasons.append(f"Overdue — open for {age_days} days (+2)")
    except Exception:
        pass

    if not assigned_to:
        score += 1
        reasons.append("No owner assigned (+1)")

    if recurrence:
        score += 1
        reasons.append("Recurrence flag set (+1)")

    if score >= 5:
        classification = "High"
    elif score >= 2:
        classification = "Medium"
    else:
        classification = "Low"

    return {
        "score": score,
        "classification": classification,
        "contributing_reasons": reasons,
    }
