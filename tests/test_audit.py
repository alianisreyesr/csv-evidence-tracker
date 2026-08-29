import pytest

from tests.auth_helpers import auth_headers, login


@pytest.mark.asyncio
async def test_audit_log_exists(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.get("/audit-log", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_audit_entry_created_on_deviation(client):
    # The audit actor is now the verified JWT identity, not a client
    # X-Actor header — a header can no longer forge attribution.
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    await client.post(
        "/deviations",
        json={"title": "Audit trail test deviation", "severity": "Major"},
        headers={**headers, "X-Actor": "spoofed.actor"},
    )
    r = await client.get("/audit-log", headers=headers)
    assert r.status_code == 200
    entries = r.json()
    assert any(e["actor"] == "analyst01" for e in entries)
    assert not any(e["actor"] == "spoofed.actor" for e in entries)


@pytest.mark.asyncio
async def test_audit_log_no_delete(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.delete("/audit-log", headers=headers)
    assert r.status_code == 405


@pytest.mark.asyncio
async def test_audit_log_no_put(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.put("/audit-log", json={}, headers=headers)
    assert r.status_code == 405
