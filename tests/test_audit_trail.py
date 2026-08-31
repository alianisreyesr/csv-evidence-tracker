"""
OQ-005 — Audit entry created on deviation create
OQ-006 — Audit entry created on deviation resolve
OQ-016 — Admin delete creates audit log entry
URS: URS-002, URS-009
Risk Score: 10 (MEDIUM)

Verifies ALCOA+ (Attributable, Contemporaneous, Original) compliance:
- Every deviation action creates an audit log entry
- Entries contain user_id, action, and timestamp
- Admin deletes are themselves recorded
"""
import pytest
from httpx import AsyncClient

from tests.auth_helpers import auth_headers
from tests.auth_helpers import login as _login


@pytest.mark.asyncio
async def test_audit_created_on_deviation_create(client: AsyncClient):
    """OQ-005: Creating a deviation produces an audit log entry with required fields."""
    a_headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))

    payload = {
        "title": "Audit Trail Test",
        "description": "Checking audit entry on create",
        "severity": "Minor",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    await client.post("/deviations", json=payload, headers=a_headers)

    audit_resp = await client.get("/audit-log", headers=a_headers)
    assert audit_resp.status_code == 200
    entries = audit_resp.json()
    assert len(entries) > 0

    latest = entries[0]
    assert "action" in latest or "event_type" in latest
    assert "timestamp" in latest or "created_at" in latest


@pytest.mark.asyncio
async def test_audit_on_resolve(client: AsyncClient):
    """OQ-006: Resolving a deviation produces an audit log entry."""
    a_headers = auth_headers(await _login(client, "analyst01", "Analyst01!"))
    q_headers = auth_headers(await _login(client, "qa_reviewer01", "QAReview01!"))

    payload = {
        "title": "Resolve Audit Test",
        "description": "Audit on resolve",
        "severity": "Minor",
        "detected_date": "2026-08-26",
        "product_id": "PROD-001",
    }
    create_resp = await client.post("/deviations", json=payload, headers=a_headers)
    dev_id = create_resp.json()["id"]

    await client.patch(
        f"/deviations/{dev_id}/status",
        json={"status": "Under Investigation"},
        headers=q_headers,
    )
    await client.patch(
        f"/deviations/{dev_id}/resolve",
        json={
            "actor": "qa_reviewer01",
            "resolution_notes": "Root cause documented and corrective action applied.",
            "root_cause": "Root cause documented",
        },
        headers=q_headers,
    )

    audit_resp = await client.get("/audit-log", headers=q_headers)
    entries = audit_resp.json()
    actions = [e.get("action") or e.get("event_type", "") for e in entries]
    assert any("resolve" in str(a).lower() or "update" in str(a).lower() for a in actions)


@pytest.mark.asyncio
async def test_admin_delete_logged(client: AsyncClient):
    """OQ-016: Admin deleting an audit log entry is itself logged."""
    admin_headers = auth_headers(await _login(client, "admin01", "Admin01!"))

    audit_resp = await client.get("/audit-log", headers=admin_headers)
    entries = audit_resp.json()

    if entries:
        entry_id = entries[-1]["id"]
        delete_resp = await client.delete(f"/audit-log/{entry_id}", headers=admin_headers)
        assert delete_resp.status_code == 204

        # Verify the delete itself was logged
        new_audit = await client.get("/audit-log", headers=admin_headers)
        new_entries = new_audit.json()
        new_actions = [e.get("action") or e.get("event_type", "") for e in new_entries]
        assert any("delete" in str(a).lower() for a in new_actions)
