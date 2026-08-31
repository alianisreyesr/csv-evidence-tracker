from app.scoring import classify_deviation_risk, score_requirement_risk
from datetime import datetime, timezone, timedelta


def recent():
    return datetime.now(timezone.utc).isoformat()


def old():
    return (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()


def test_critical_severity_scores_high():
    result = classify_deviation_risk("Critical", "Open", recent())
    assert result["score"] >= 3
    assert result["classification"] == "High"


def test_minor_recent_no_owner_medium():
    result = classify_deviation_risk("Minor", "Open", recent(), assigned_to=None)
    assert result["score"] >= 1


def test_minor_recent_assigned_low():
    result = classify_deviation_risk("Minor", "Open", recent(), assigned_to="ana.reyes")
    assert result["classification"] == "Low"
    assert result["score"] <= 1


def test_overdue_adds_score():
    base = classify_deviation_risk("Minor", "Open", recent(), assigned_to="ana.reyes")
    overdue = classify_deviation_risk("Minor", "Open", old(), assigned_to="ana.reyes")
    assert overdue["score"] > base["score"]


def test_recurrence_adds_score():
    without = classify_deviation_risk("Minor", "Open", recent(), recurrence=False, assigned_to="a")
    with_rec = classify_deviation_risk("Minor", "Open", recent(), recurrence=True, assigned_to="a")
    assert with_rec["score"] > without["score"]


def test_contributing_reasons_returned():
    result = classify_deviation_risk("Critical", "Open", old(), recurrence=True)
    assert len(result["contributing_reasons"]) > 0


def test_resolved_deviation_not_penalized_for_overdue():
    result = classify_deviation_risk("Minor", "Resolved", old(), assigned_to="a")
    reasons_text = " ".join(result["contributing_reasons"])
    assert "Overdue" not in reasons_text


# ---------------------------------------------------------------------------
# score_requirement_risk — S x P x D formal requirement risk assessment
# ---------------------------------------------------------------------------
def test_requirement_risk_is_pure_product():
    result = score_requirement_risk(severity=3, probability=4, detectability=2)
    assert result["score"] == 24


def test_requirement_risk_low_tier_boundary():
    # Highest score still classified Low: 2*2*2=8 -> Low; 2*2*3=12? check
    # exact boundary values instead of derived products.
    assert score_requirement_risk(1, 1, 1)["level"] == "Low"
    assert score_requirement_risk(2, 2, 2)["score"] == 8
    assert score_requirement_risk(2, 2, 2)["level"] == "Low"


def test_requirement_risk_medium_tier_boundary():
    result = score_requirement_risk(3, 3, 1)  # score 9
    assert result["score"] == 9
    assert result["level"] == "Medium"


def test_requirement_risk_high_tier_boundary():
    result = score_requirement_risk(4, 4, 2)  # score 32
    assert result["score"] == 32
    assert result["level"] == "High"


def test_requirement_risk_critical_tier_boundary():
    result = score_requirement_risk(5, 5, 3)  # score 75
    assert result["score"] == 75
    assert result["level"] == "Critical"


def test_requirement_risk_lowest_and_highest_possible():
    assert score_requirement_risk(1, 1, 1)["score"] == 1
    highest = score_requirement_risk(5, 5, 5)
    assert highest["score"] == 125
    assert highest["level"] == "Critical"
