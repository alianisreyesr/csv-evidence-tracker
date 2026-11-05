"""Tests for the /executions router (list filters and recording)."""
import pytest

from tests.auth_helpers import auth_headers, login


async def _h(client):
    return auth_headers(await login(client, "analyst01", "Analyst01!"))


def _payload(**overrides):
    body = {
        "test_case_id": 1,
        "phase_id": 1,
        "executed_by": "analyst01",
        "result": "PASS",
        "actual_result": "As expected",
        "evidence_ref": "EV-001",
        "notes": "n/a",
    }
    body.update(overrides)
    return body


@pytest.mark.asyncio
async def test_record_execution_requires_auth(client):
    r = await client.post("/executions", json=_payload())
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_record_execution_success_and_audit_actor(client):
    h = await _h(client)
    r = await client.post("/executions", json=_payload(), headers=h)
    assert r.status_code == 201
    body = r.json()
    assert body["result"] == "PASS"
    assert body["test_case_id"] == 1
    assert body["executed_at"]

    admin = auth_headers(await login(client, "admin01", "Admin01!"))
    log = await client.get("/audit-log", headers=admin)
    assert log.status_code == 200
    entries = [e for e in log.json() if e["action"] == "EXECUTE_TEST"]
    assert entries and entries[0]["actor"] == "analyst01"


@pytest.mark.asyncio
async def test_record_execution_unknown_test_case(client):
    r = await client.post("/executions", json=_payload(test_case_id=99999), headers=await _h(client))
    assert r.status_code == 404
    assert "Test case" in r.json()["detail"]


@pytest.mark.asyncio
async def test_record_execution_unknown_phase(client):
    r = await client.post("/executions", json=_payload(phase_id=99999), headers=await _h(client))
    assert r.status_code == 404
    assert "Phase" in r.json()["detail"]


@pytest.mark.asyncio
async def test_record_execution_invalid_result(client):
    r = await client.post("/executions", json=_payload(result="MAYBE"), headers=await _h(client))
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_list_executions_filters(client):
    h = await _h(client)
    await client.post("/executions", json=_payload(result="PASS", phase_id=1), headers=h)
    await client.post("/executions", json=_payload(result="FAIL", phase_id=2), headers=h)

    everything = (await client.get("/executions", headers=h)).json()
    assert len(everything) >= 2

    fails = (await client.get("/executions?result=FAIL", headers=h)).json()
    assert fails and all(e["result"] == "FAIL" for e in fails)

    phase2 = (await client.get("/executions?phase_id=2", headers=h)).json()
    assert phase2 and all(e["phase_id"] == 2 for e in phase2)

    both = (await client.get("/executions?result=PASS&phase_id=1", headers=h)).json()
    assert both and all(e["result"] == "PASS" and e["phase_id"] == 1 for e in both)

    none = (await client.get("/executions?result=BLOCKED&phase_id=3", headers=h)).json()
    assert none == []
