import pytest


@pytest.mark.asyncio
async def test_audit_log_exists(client):
    r = await client.get("/audit-log")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_audit_entry_created_on_deviation(client):
    await client.post(
        "/deviations",
        json={"title": "Audit trail test deviation", "severity": "Major"},
        headers={"X-Actor": "audit.tester"},
    )
    r = await client.get("/audit-log?actor=audit.tester")
    assert r.status_code == 200
    entries = r.json()
    assert any(e["actor"] == "audit.tester" for e in entries)


@pytest.mark.asyncio
async def test_audit_log_no_delete(client):
    r = await client.delete("/audit-log")
    assert r.status_code == 405


@pytest.mark.asyncio
async def test_audit_log_no_put(client):
    r = await client.put("/audit-log", json={})
    assert r.status_code == 405
