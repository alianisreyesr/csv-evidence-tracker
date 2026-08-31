"""
OQ-009 — Missing title returns 422
OQ-010 — Missing severity returns 422
OQ-015 — Critical deviation without root_cause returns 422 on resolve
URS: URS-004, URS-008
Risk Score: 24 (HIGH)

Verifies input validation for deviation records per ALCOA+ (Complete)
and ICH Q9 risk-based severity classification.
"""
import pytest
from httpx import AsyncClient

from tests.auth_helpers import auth_headers
from tests.auth_helpers import login as _login


@pytest.mark.asyncio
async def test_missing_title(client: AsyncClient):
    """OQ-009: POST /deviations without title returns HTTP 422."""
    headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    payload = {
        "description": "No title provided",
        "severity": "Minor",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    resp = await client.post("/deviations", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_missing_severity(client: AsyncClient):
    """OQ-010: POST /deviations without severity returns HTTP 422."""
    headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    payload = {
        "title": "No Severity Deviation",
        "description": "Missing severity field",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    resp = await client.post("/deviations", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_critical_requires_root_cause(client: AsyncClient):
    """OQ-015: Resolving a Critical deviation without root_cause returns 422."""
    a_headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    q_headers = auth_headers(await _login(client, "qa_reviewer01", "QAReview01!"))

    # Create Critical deviation
    payload = {
        "title": "Critical No Root Cause",
        "description": "Critical severity test",
        "severity": "Critical",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    create_resp = await client.post("/deviations", json=payload, headers=a_headers)
    dev_id = create_resp.json()["id"]

    # Move to Under Investigation first — resolving requires it (OQ-008)
    status_resp = await client.patch(
        f"/deviations/{dev_id}/status",
        json={"status": "Under Investigation"},
        headers=q_headers,
    )
    assert status_resp.status_code == 200

    # Attempt resolve with an otherwise-valid payload but no root_cause
    resolve_resp = await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={
            "actor": "qa_reviewer01",
            "resolution_notes": "Attempting to close without a root cause.",
            "root_cause": "",
        },
        headers=q_headers,
    )
    assert resolve_resp.status_code == 422
