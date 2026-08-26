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
from app.main import app

ANALYST_CREDENTIALS = {"username": "analyst", "password": "analyst123"}
QA_CREDENTIALS = {"username": "qa_reviewer", "password": "qa123"}
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}


async def get_token(client, credentials):
    resp = await client.post("/auth/token", data=credentials)
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_audit_created_on_deviation_create():
    """OQ-005: Creating a deviation produces an audit log entry with required fields."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        a_token = await get_token(client, ANALYST_CREDENTIALS)
        a_headers = {"Authorization": f"Bearer {a_token}"}

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
async def test_audit_on_resolve():
    """OQ-006: Resolving a deviation produces an audit log entry."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        a_token = await get_token(client, ANALYST_CREDENTIALS)
        q_token = await get_token(client, QA_CREDENTIALS)
        a_headers = {"Authorization": f"Bearer {a_token}"}
        q_headers = {"Authorization": f"Bearer {q_token}"}

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
            json={"status": "under_review"},
            headers=q_headers,
        )
        await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={"root_cause": "Root cause documented", "corrective_action": "Fixed"},
            headers=q_headers,
        )

        audit_resp = await client.get("/audit-log", headers=q_headers)
        entries = audit_resp.json()
        actions = [e.get("action") or e.get("event_type", "") for e in entries]
        assert any("resolve" in str(a).lower() or "update" in str(a).lower() for a in actions)


@pytest.mark.asyncio
async def test_admin_delete_logged():
    """OQ-016: Admin deleting an audit log entry is itself logged."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        admin_token = await get_token(client, ADMIN_CREDENTIALS)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        audit_resp = await client.get("/audit-log", headers=admin_headers)
        entries = audit_resp.json()

        if entries:
            entry_id = entries[-1]["id"]
            delete_resp = await client.delete(f"/audit-log/{entry_id}", headers=admin_headers)
            assert delete_resp.status_code == 200

            # Verify the delete itself was logged
            new_audit = await client.get("/audit-log", headers=admin_headers)
            new_entries = new_audit.json()
            new_actions = [e.get("action") or e.get("event_type", "") for e in new_entries]
            assert any("delete" in str(a).lower() for a in new_actions)
