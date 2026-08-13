import pytest
from app.scoring import classify_deviation_risk
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
