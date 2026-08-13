import pytest


@pytest.mark.asyncio
async def test_list_phases(client):
    r = await client.get("/phases")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    names = [p["name"] for p in data]
    assert "IQ" in names
    assert "OQ" in names
    assert "PQ" in names


@pytest.mark.asyncio
async def test_get_phase_by_id(client):
    r = await client.get("/phases/1")
    assert r.status_code == 200
    assert r.json()["name"] == "IQ"


@pytest.mark.asyncio
async def test_phase_not_found(client):
    r = await client.get("/phases/999")
    assert r.status_code == 404
