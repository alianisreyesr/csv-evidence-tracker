import pytest


@pytest.mark.asyncio
async def test_list_deviations(client):
    r = await client.get("/deviations")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for d in data:
        assert "risk_score" in d
        assert "risk_classification" in d
        assert "contributing_reasons" in d


@pytest.mark.asyncio
async def test_filter_deviations_by_status(client):
    r = await client.get("/deviations?status=Open")
    assert r.status_code == 200
    for d in r.json():
        assert d["status"] == "Open"


@pytest.mark.asyncio
async def test_create_deviation(client):
    r = await client.post(
        "/deviations",
        json={
            "title": "Test deviation for portfolio",
            "description": "Synthetic test entry",
            "severity": "Minor",
        },
        headers={"X-Actor": "test.user"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "Open"
    assert data["severity"] == "Minor"
    assert "risk_score" in data


@pytest.mark.asyncio
async def test_create_deviation_missing_severity(client):
    r = await client.post(
        "/deviations",
        json={"title": "Missing severity"},
        headers={"X-Actor": "test.user"},
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_resolve_deviation(client):
    create = await client.post(
        "/deviations",
        json={"title": "To be resolved", "severity": "Major"},
        headers={"X-Actor": "test.user"},
    )
    dev_id = create.json()["id"]
    r = await client.post(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "Resolved in synthetic test run.", "status": "Resolved"},
        headers={"X-Actor": "test.user"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "Resolved"


@pytest.mark.asyncio
async def test_resolve_already_resolved(client):
    create = await client.post(
        "/deviations",
        json={"title": "Double resolve test", "severity": "Minor"},
        headers={"X-Actor": "test.user"},
    )
    dev_id = create.json()["id"]
    await client.post(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "First resolution.", "status": "Resolved"},
        headers={"X-Actor": "test.user"},
    )
    r = await client.post(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "Trying again.", "status": "Resolved"},
        headers={"X-Actor": "test.user"},
    )
    assert r.status_code == 400
