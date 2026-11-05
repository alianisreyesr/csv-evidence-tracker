"""Tests for the /test-cases router."""
import pytest

from tests.auth_helpers import auth_headers, login


async def _h(client, user="analyst01", pw="Analyst01!"):
    return auth_headers(await login(client, user, pw))


def _case(**overrides):
    body = {
        "requirement_id": 1,
        "code": "TC-NEW-001",
        "title": "A brand new test case",
        "description": "desc",
        "test_type": "Functional",
        "expected_result": "It works",
    }
    body.update(overrides)
    return body


@pytest.mark.asyncio
async def test_create_test_case_success(client):
    r = await client.post("/test-cases", json=_case(), headers=await _h(client))
    assert r.status_code == 201
    data = r.json()
    assert data["code"] == "TC-NEW-001"
    assert data["requirement_code"]


@pytest.mark.asyncio
async def test_create_test_case_requires_auth(client):
    r = await client.post("/test-cases", json=_case())
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_test_case_unknown_requirement(client):
    r = await client.post("/test-cases", json=_case(requirement_id=99999), headers=await _h(client))
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_create_test_case_duplicate_code(client):
    h = await _h(client)
    assert (await client.post("/test-cases", json=_case(), headers=h)).status_code == 201
    r = await client.post("/test-cases", json=_case(), headers=h)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_create_test_case_invalid_type(client):
    r = await client.post("/test-cases", json=_case(test_type="Bogus"), headers=await _h(client))
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_test_cases_and_filters(client):
    h = await _h(client)
    allc = (await client.get("/test-cases", headers=h)).json()
    assert allc
    req_id = allc[0]["requirement_id"]

    by_req = (await client.get(f"/test-cases?requirement_id={req_id}", headers=h)).json()
    assert by_req and all(c["requirement_id"] == req_id for c in by_req)

    phase = allc[0]["requirement_phase"]
    by_phase = (await client.get(f"/test-cases?phase={phase}", headers=h)).json()
    assert by_phase and all(c["requirement_phase"] == phase for c in by_phase)

    both = (await client.get(f"/test-cases?phase={phase}&requirement_id={req_id}", headers=h)).json()
    assert both


@pytest.mark.asyncio
async def test_get_test_case_with_executions(client):
    h = await _h(client)
    ex = await client.post(
        "/executions",
        json={"test_case_id": 1, "phase_id": 1, "executed_by": "analyst01", "result": "PASS"},
        headers=h,
    )
    assert ex.status_code == 201
    r = await client.get("/test-cases/1", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["test_case"]["id"] == 1
    assert len(body["executions"]) >= 1


@pytest.mark.asyncio
async def test_get_test_case_not_found(client):
    r = await client.get("/test-cases/99999", headers=await _h(client))
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_summary_endpoint(client):
    r = await client.get("/summary", headers=await _h(client))
    assert r.status_code == 200
    assert "requirements" in r.json()
