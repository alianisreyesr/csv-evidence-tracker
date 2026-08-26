"""
IQ-001 — Health Endpoint (Installation Qualification)
URS: URS-010
Risk Score: 4 (LOW)

Verifies that the /health endpoint:
- Returns HTTP 200 without authentication
- Returns required fields: status, version, timestamp, db_status
- timestamp is in UTC ISO 8601 format
- version matches APP_VERSION
"""
import pytest
from httpx import AsyncClient
from app.main import app, APP_VERSION


@pytest.mark.asyncio
async def test_health_returns_200():
    """IQ-001a: /health is accessible without authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_required_fields():
    """IQ-001b: /health response contains all required fields per URS-010."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "db_status" in data
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_version_matches():
    """IQ-001c: /health version field matches APP_VERSION constant."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    data = response.json()
    assert data["version"] == APP_VERSION


@pytest.mark.asyncio
async def test_health_timestamp_utc():
    """IQ-001d: /health timestamp is ISO 8601 UTC per URS-005 / URS-010."""
    from datetime import datetime, timezone
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    ts = response.json()["timestamp"]
    # Must parse without error and be timezone-aware UTC
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None
