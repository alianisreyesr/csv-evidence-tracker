import pytest

from tests.auth_helpers import auth_headers, login


@pytest.mark.asyncio
async def test_list_deviations(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.get("/deviations", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for d in data:
        assert "risk_score" in d
        assert "risk_classification" in d
        assert "contributing_reasons" in d


@pytest.mark.asyncio
async def test_filter_deviations_by_status(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.get("/deviations?status=Open", headers=headers)
    assert r.status_code == 200
    for d in r.json():
        assert d["status"] == "Open"


@pytest.mark.asyncio
async def test_create_deviation(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/deviations",
        json={
            "title": "Test deviation for portfolio",
            "description": "Synthetic test entry",
            "severity": "Minor",
        },
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "Open"
    assert data["severity"] == "Minor"
    # risk_score/risk_classification are computed server-side by the
    # explainable rule engine (app/scoring.py), not accepted from the client.
    assert data["risk_score"] is not None
    assert data["risk_classification"] in ("Low", "Medium", "High")
    assert isinstance(data["contributing_reasons"], list)


@pytest.mark.asyncio
async def test_create_deviation_missing_severity(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/deviations",
        json={"title": "Missing severity"},
        headers=headers,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_resolve_deviation(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    create = await client.post(
        "/deviations",
        json={"title": "To be resolved", "severity": "Major"},
        headers=headers,
    )
    dev_id = create.json()["id"]
    r = await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "Resolved in synthetic test run.", "status": "Resolved"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "Resolved"
    # resolution_notes must actually persist, not be silently discarded.
    assert body["resolution_notes"] == "Resolved in synthetic test run."


@pytest.mark.asyncio
async def test_resolve_already_resolved(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    create = await client.post(
        "/deviations",
        json={"title": "Double resolve test", "severity": "Minor"},
        headers=headers,
    )
    dev_id = create.json()["id"]
    await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "First resolution.", "status": "Resolved"},
        headers=headers,
    )
    r = await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={"actor": "test.user", "resolution_notes": "Trying again.", "status": "Resolved"},
        headers=headers,
    )
    # The route raises 409 Conflict for "already resolved" (see
    # app/routers/deviations.py); this test previously asserted 400, but
    # never actually exercised the real endpoint (it POSTed to a PATCH-only
    # route with no auth, so it always failed before reaching this check).
    assert r.status_code == 409
