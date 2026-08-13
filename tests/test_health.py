import pytest


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "data_boundary" in data


@pytest.mark.asyncio
async def test_summary(client):
    r = await client.get("/summary")
    assert r.status_code == 200
    data = r.json()
    assert "requirements" in data
    assert "test_cases" in data
    assert "open_deviations" in data
    assert "test_coverage_pct" in data
