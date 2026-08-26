"""
audit.py
========
REST endpoints for the append-only audit log.

Role enforcement (21 CFR Part 11 §11.10(e) / ALCOA+ Original principle):
  - Any authenticated user : read the audit log
  - Admin only             : delete a specific audit entry
                             (intentionally restricted; use with extreme caution)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.models import AuditEntry
from app.auth import UserRole
from app.dependencies import require_role, get_current_user

router = APIRouter()


@router.get("", response_model=list[AuditEntry])
async def list_audit_log(
    _user=Depends(get_current_user),  # any authenticated role
):
    """Return all audit log entries in reverse chronological order."""
    async with get_db() as db:
        rows = await (await db.execute(
            "SELECT * FROM audit_log ORDER BY created_at DESC"
        )).fetchall()
    return [dict(r) for r in rows]


@router.get("/{entry_id}", response_model=AuditEntry)
async def get_audit_entry(entry_id: int, _user=Depends(get_current_user)):
    """Return a single audit log entry by ID. Requires authentication."""
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM audit_log WHERE id = ?", (entry_id,)
        )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Audit entry {entry_id} not found.")
    return dict(row)


@router.delete("/{entry_id}", status_code=204)
async def delete_audit_entry(
    entry_id: int,
    _user=Depends(require_role(UserRole.admin)),  # Admin only
):
    """
    Delete a specific audit log entry.
    Restricted to Admin role only (ALCOA+ Original principle).
    This endpoint exists to support test validation; use with caution.
    """
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT id FROM audit_log WHERE id = ?", (entry_id,)
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Audit entry {entry_id} not found.")
        await db.execute("DELETE FROM audit_log WHERE id = ?", (entry_id,))
        await db.commit()
