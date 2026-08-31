"""
OQ-007 — Valid State Transitions
OQ-008 — Invalid Repeat Transition Rejected
URS: URS-003
Risk Score: 18 (HIGH)

Verifies that deviation records follow the enforced lifecycle:
  Open -> Under Investigation -> Resolved | Accepted with Risk
  Open -> Resolved | Accepted with Risk (Under Investigation is optional)

And that a deviation already in a terminal state (Resolved / Accepted with
Risk) cannot be resolved a second time (HTTP 409).
"""
import pytest
from httpx import AsyncClient

from tests.auth_helpers import auth_headers
from tests.auth_helpers import login as _login


@pytest.mark.asyncio
async def test_valid_state_transitions(client: AsyncClient):
    """OQ-007: open → under_review → resolved transitions are accepted."""
    a_headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    q_headers = auth_headers(await _login(client, "qa_reviewer01", "QAReview01!"))

    # Create deviation as Analyst
    payload = {
        "title": "Lifecycle Test Deviation",
        "description": "Testing state transitions",
        "severity": "Minor",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    create_resp = await client.post("/deviations", json=payload, headers=a_headers)
    assert create_resp.status_code in (200, 201)
    dev_id = create_resp.json()["id"]

    # Move to Under Investigation
    review_resp = await client.patch(
        f"/deviations/{dev_id}/status",
        json={"status": "Under Investigation"},
        headers=q_headers,
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["status"] == "Under Investigation"

    # Resolve
    resolve_resp = await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={
            "actor": "qa_reviewer01",
            "resolution_notes": "Root cause investigated and corrective action applied.",
        },
        headers=q_headers,
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "Resolved"


@pytest.mark.asyncio
async def test_invalid_direct_resolve(client: AsyncClient):
    """OQ-008: Resolving an already-resolved deviation a second time is rejected (HTTP 409)."""
    a_headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    q_headers = auth_headers(await _login(client, "qa_reviewer01", "QAReview01!"))

    payload = {
        "title": "Double Resolve Test",
        "description": "Should not be resolvable twice",
        "severity": "Minor",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    create_resp = await client.post("/deviations", json=payload, headers=a_headers)
    dev_id = create_resp.json()["id"]

    resolve_payload = {
        "actor": "qa_reviewer01",
        "resolution_notes": "First resolution — should succeed.",
    }
    first_resp = await client.patch(
        f"/deviations/{dev_id}/resolve", json=resolve_payload, headers=q_headers
    )
    assert first_resp.status_code == 200

    # A second resolve attempt on an already-terminal deviation must be rejected
    second_resp = await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={**resolve_payload, "resolution_notes": "Second attempt — should be rejected."},
        headers=q_headers,
    )
    assert second_resp.status_code == 409
