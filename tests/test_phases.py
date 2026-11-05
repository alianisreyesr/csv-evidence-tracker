import pytest

from tests.auth_helpers import auth_headers, login


async def _h(client):
    return auth_headers(await login(client, "analyst01", "Analyst01!"))


@pytest.mark.asyncio
async def test_list_phases(client):
    r = await client.get("/phases", headers=await _h(client))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    names = [p["name"] for p in data]
    assert "IQ" in names
    assert "OQ" in names
    assert "PQ" in names


@pytest.mark.asyncio
async def test_get_phase_by_id(client):
    r = await client.get("/phases/1", headers=await _h(client))
    assert r.status_code == 200
    assert r.json()["name"] == "IQ"


@pytest.mark.asyncio
async def test_phase_not_found(client):
    r = await client.get("/phases/999", headers=await _h(client))
    assert r.status_code == 404
