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
from app.main import app

QA_CREDENTIALS = {"username": "qa_reviewer", "password": "qa123"}
ANALYST_CREDENTIALS = {"username": "analyst", "password": "analyst123"}


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
async def test_missing_title():
    """OQ-009: POST /deviations without title returns HTTP 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        headers = await analyst_headers(client)
        payload = {
            "description": "No title provided",
            "severity": "Minor",
            "detected_date": "2026-08-26",
            "product_id": "PROD-001",
        }
        resp = await client.post("/deviations", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_missing_severity():
    """OQ-010: POST /deviations without severity returns HTTP 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        headers = await analyst_headers(client)
        payload = {
            "title": "No Severity Deviation",
            "description": "Missing severity field",
            "detected_date": "2026-08-26",
            "product_id": "PROD-001",
        }
        resp = await client.post("/deviations", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_critical_requires_root_cause():
    """OQ-015: Resolving a Critical deviation without root_cause returns 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        a_headers = await analyst_headers(client)
        q_headers = await qa_headers(client)

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

        # Move to under_review first
        await client.patch(
            f"/deviations/{dev_id}/status",
            json={"status": "under_review"},
            headers=q_headers,
        )

        # Attempt resolve without root_cause
        resolve_resp = await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={"root_cause": ""},
            headers=q_headers,
        )
        assert resolve_resp.status_code == 422
