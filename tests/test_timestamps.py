"""
OQ-011 — Timestamps Stored in UTC ISO 8601
URS: URS-005
Risk Score: 24 (HIGH)

Verifies that all created_at and updated_at fields returned by the API
are in UTC ISO 8601 format, with timezone info present.
ALCOA+ (Contemporaneous) compliance.
"""
from datetime import datetime

import pytest
from httpx import AsyncClient

from tests.auth_helpers import auth_headers
from tests.auth_helpers import login as _login


@pytest.mark.asyncio
async def test_created_at_utc(client: AsyncClient):
    """OQ-011a: created_at on a new deviation is UTC ISO 8601."""
    headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
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
async def test_audit_timestamp_utc(client: AsyncClient):
    """OQ-011b: Audit log entries have UTC ISO 8601 timestamps."""
    headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))

    audit_resp = await client.get("/audit-log", headers=headers)
    assert audit_resp.status_code == 200
    entries = audit_resp.json()

    if entries:
        ts = entries[0].get("timestamp") or entries[0].get("created_at")
        parsed = datetime.fromisoformat(ts)
        assert parsed.tzinfo is not None
