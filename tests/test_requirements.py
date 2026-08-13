import pytest


@pytest.mark.asyncio
async def test_list_requirements(client):
    r = await client.get("/requirements")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_filter_requirements_by_phase(client):
    r = await client.get("/requirements?phase=OQ")
    assert r.status_code == 200
    for item in r.json():
        assert item["phase"] == "OQ"


@pytest.mark.asyncio
async def test_get_requirement_by_id(client):
    r = await client.get("/requirements/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


@pytest.mark.asyncio
async def test_requirement_not_found(client):
    r = await client.get("/requirements/9999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_requirement_test_cases(client):
    r = await client.get("/requirements/1/test-cases")
    assert r.status_code == 200
    data = r.json()
    assert "requirement" in data
    assert "test_cases" in data
