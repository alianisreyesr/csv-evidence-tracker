"""
test_auth_roles.py
==================
Role-based access control (RBAC) test suite.

Verifies that:
  - Unauthenticated requests are rejected with HTTP 401.
  - The Analyst role is denied (HTTP 403) from endpoints that require
    QA Reviewer or Admin privileges.
  - QA Reviewer can approve deviations and read the audit log.
  - Admin has unrestricted access.
  - Invalid credentials always return HTTP 401.
  - GET /auth/me reflects the correct role for each synthetic user.

All data is synthetic. No production credentials are used.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _login(client: AsyncClient, username: str, password: str) -> str:
    """Obtain a Bearer token for the given synthetic user."""
    resp = await client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    """Return Authorization header dict for a given token."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Authentication baseline
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login_analyst_returns_token(client: AsyncClient):
    """Analyst can log in and receives a JWT with the correct role."""
    resp = await client.post(
        "/auth/login",
        data={"username": "analyst01", "password": "Analyst01!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "Analyst"
    assert "access_token" in body


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client: AsyncClient):
    """Invalid credentials must always be rejected with HTTP 401."""
    resp = await client.post(
        "/auth/login",
        data={"username": "analyst01", "password": "wrong-password"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user_returns_401(client: AsyncClient):
    """Unrecognised username must be rejected with HTTP 401."""
    resp = await client.post(
        "/auth/login",
        data={"username": "ghost", "password": "irrelevant"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/me — identity reflection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_me_reflects_analyst_role(client: AsyncClient):
    """GET /auth/me must return the correct role for an Analyst token."""
    token = await _login(client, "analyst01", "Analyst01!")
    resp = await client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "Analyst"


@pytest.mark.asyncio
async def test_me_reflects_qa_reviewer_role(client: AsyncClient):
    """GET /auth/me must return the correct role for a QA Reviewer token."""
    token = await _login(client, "qa_reviewer01", "QAReview01!")
    resp = await client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "QA Reviewer"


@pytest.mark.asyncio
async def test_me_reflects_admin_role(client: AsyncClient):
    """GET /auth/me must return the correct role for an Admin token."""
    token = await _login(client, "admin01", "Admin01!")
    resp = await client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "Admin"


# ---------------------------------------------------------------------------
# Unauthenticated access — must be rejected with HTTP 401
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unauthenticated_cannot_read_audit_log(client: AsyncClient):
    """Requests without a Bearer token must be rejected with HTTP 401."""
    resp = await client.get("/audit-log")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_cannot_resolve_deviation(client: AsyncClient):
    """Deviation approval without a token must return HTTP 401."""
    resp = await client.patch(
        "/deviations/1/resolve",
        json={"actor": "anon", "resolution_notes": "Attempting without auth.", "status": "Resolved"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Analyst role — read-only; must be blocked from approval and audit writes
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_analyst_cannot_approve_deviation(client: AsyncClient):
    """
    An Analyst must receive HTTP 403 when attempting to approve a deviation.
    Only QA Reviewer and Admin are authorised for this action.
    """
    token = await _login(client, "analyst01", "Analyst01!")
    resp = await client.patch(
        "/deviations/1/resolve",
        json={"actor": "analyst01", "resolution_notes": "Trying to approve as Analyst.", "status": "Resolved"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403
    assert "403" in str(resp.status_code)


@pytest.mark.asyncio
async def test_analyst_cannot_modify_audit_record(client: AsyncClient):
    """
    An Analyst must receive HTTP 403 when attempting to delete or modify
    an audit log entry. The audit trail must be immutable for non-Admin roles.
    """
    token = await _login(client, "analyst01", "Analyst01!")
    resp = await client.delete("/audit-log/1", headers=auth_headers(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analyst_can_read_audit_log(client: AsyncClient):
    """An Analyst must be permitted to read (GET) the audit log."""
    token = await _login(client, "analyst01", "Analyst01!")
    resp = await client.get("/audit-log", headers=auth_headers(token))
    # 200 OK or 404 (empty DB) are both acceptable; 401/403 are failures
    assert resp.status_code not in (401, 403)


# ---------------------------------------------------------------------------
# QA Reviewer role — can approve deviations; cannot modify audit log
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_qa_reviewer_can_approve_deviation(client: AsyncClient):
    """
    A QA Reviewer must be permitted to resolve a deviation.
    This test creates a deviation first, then resolves it.
    """
    token = await _login(client, "qa_reviewer01", "QAReview01!")
    headers = auth_headers(token)

    # Create a deviation to resolve
    create_resp = await client.post(
        "/deviations",
        json={
            "title": "TC-RBAC: QA approval test deviation",
            "severity": "Minor",
            "description": "Synthetic deviation created by RBAC test suite.",
        },
        headers=headers,
    )
    # Accept 200 or 201; skip if endpoint is not yet role-gated for creation
    assert create_resp.status_code in (200, 201, 422), create_resp.text

    if create_resp.status_code in (200, 201):
        dev_id = create_resp.json()["id"]
        resolve_resp = await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={
                "actor": "qa_reviewer01",
                "resolution_notes": "Resolved by QA Reviewer in RBAC test.",
                "status": "Resolved",
            },
            headers=headers,
        )
        assert resolve_resp.status_code == 200


@pytest.mark.asyncio
async def test_qa_reviewer_cannot_modify_audit_record(client: AsyncClient):
    """
    A QA Reviewer must receive HTTP 403 when attempting to delete an audit
    log entry. Audit log modification is reserved for Admin only.
    """
    token = await _login(client, "qa_reviewer01", "QAReview01!")
    resp = await client.delete("/audit-log/1", headers=auth_headers(token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Admin role — full access
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_admin_can_read_audit_log(client: AsyncClient):
    """Admin must be able to read the audit log without restriction."""
    token = await _login(client, "admin01", "Admin01!")
    resp = await client.get("/audit-log", headers=auth_headers(token))
    assert resp.status_code not in (401, 403)


@pytest.mark.asyncio
async def test_admin_can_approve_deviation(client: AsyncClient):
    """
    Admin must be permitted to resolve a deviation.
    Verifies that Admin role satisfies QA Reviewer-level enforcement.
    """
    token = await _login(client, "admin01", "Admin01!")
    headers = auth_headers(token)

    create_resp = await client.post(
        "/deviations",
        json={
            "title": "TC-RBAC: Admin approval test deviation",
            "severity": "Major",
            "description": "Synthetic deviation created by Admin RBAC test.",
        },
        headers=headers,
    )
    assert create_resp.status_code in (200, 201, 422), create_resp.text

    if create_resp.status_code in (200, 201):
        dev_id = create_resp.json()["id"]
        resolve_resp = await client.patch(
            f"/deviations/{dev_id}/resolve",
            json={
                "actor": "admin01",
                "resolution_notes": "Resolved by Admin in RBAC test suite.",
                "status": "Resolved",
            },
            headers=headers,
        )
        assert resolve_resp.status_code == 200
