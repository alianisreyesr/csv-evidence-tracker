"""
OQ-007 — Valid State Transitions
OQ-008 — Invalid Direct Transition Rejected
URS: URS-003
Risk Score: 18 (HIGH)

Verifies that deviation records follow the enforced lifecycle:
  open → under_review → resolved

And that invalid transitions (open → resolved) are rejected with HTTP 422.
"""
import pytest
from httpx import AsyncClient
from app.main import app

ANALYST_CREDENTIALS = {"username": "analyst", "password": "analyst123"}
QA_CREDENTIALS = {"username": "qa_reviewer", "password": "qa123"}


async def get_token(client, credentials):
    resp = await client.post("/auth/token", data=credentials)
    return resp.json()["access_token"]


async def analyst_headers(client):
    token = await get_token(client, ANALYST_CREDENTIALS)
    return {"Authorization": f"Bearer {token}"}


async def qa_headers(client):
    token = await get_token(client, QA_CREDENTIALS)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_valid_state_transitions():
    """OQ-007: open → under_review → resolved transitions are accepted."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        a_headers = await analyst_headers(client)
        q_headers = await qa_headers(client)

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

        # Move to under_review
        review_resp = await client.patch(
            f"/deviations/{dev_id}/status",
            json={"status": "under_review"},
            headers=q_headers,
        )
        assert review_resp.status_code == 200
        assert review_resp.json()["status"] == "under_review"

        # Resolve
        resolve_resp = await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={"root_cause": "Test root cause", "corrective_action": "Fixed"},
            headers=q_headers,
        )
        assert resolve_resp.status_code == 200


@pytest.mark.asyncio
async def test_invalid_direct_resolve():
    """OQ-008: open → resolved directly is rejected (HTTP 422)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        a_headers = await analyst_headers(client)
        q_headers = await qa_headers(client)

        payload = {
            "title": "Direct Resolve Test",
            "description": "Should not go directly to resolved",
            "severity": "Minor",
            "detected_date": "2026-08-26",
            "product_id": "PROD-001",
        }
        create_resp = await client.post("/deviations", json=payload, headers=a_headers)
        dev_id = create_resp.json()["id"]

        # Attempt to resolve directly from open
        resolve_resp = await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={"root_cause": "Bypass attempt"},
            headers=q_headers,
        )
        assert resolve_resp.status_code == 422
