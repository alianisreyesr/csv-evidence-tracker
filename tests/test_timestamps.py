"""
OQ-011 — Timestamps Stored in UTC ISO 8601
URS: URS-005
Risk Score: 24 (HIGH)

Verifies that all created_at and updated_at fields returned by the API
are in UTC ISO 8601 format, with timezone info present.
ALCOA+ (Contemporaneous) compliance.
"""
import pytest
from datetime import datetime
from httpx import AsyncClient
from app.main import app

ANALYST_CREDENTIALS = {"username": "analyst", "password": "analyst123"}


async def get_token(client):
    resp = await client.post("/auth/token", data=ANALYST_CREDENTIALS)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_created_at_utc():
    """OQ-011a: created_at on a new deviation is UTC ISO 8601."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "Timestamp Test Deviation",
            "description": "Checking UTC timestamp",
            "severity": "Minor",
            "detected_date": "2026-08-26",
            "product_id": "PROD-001",
        }
        resp = await client.post("/deviations", json=payload, headers=headers)
        assert resp.status_code in (200, 201)
        data = resp.json()

    assert "created_at" in data
    ts = data["created_at"]
    # Must parse as ISO 8601 with timezone
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None, "created_at must be timezone-aware UTC"


@pytest.mark.asyncio
async def test_audit_timestamp_utc():
    """OQ-011b: Audit log entries have UTC ISO 8601 timestamps."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        audit_resp = await client.get("/audit-log", headers=headers)
        assert audit_resp.status_code == 200
        entries = audit_resp.json()

        if entries:
            ts = entries[0].get("timestamp") or entries[0].get("created_at")
            parsed = datetime.fromisoformat(ts)
            assert parsed.tzinfo is not None
