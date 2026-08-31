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

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.models import AuditEntry
from app.auth import UserRole, TokenData
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
    user: TokenData = Depends(require_role(UserRole.admin)),  # Admin only
):
    """
    Delete a specific audit log entry.
    Restricted to Admin role only (ALCOA+ Original principle).
    This endpoint exists to support test validation; use with caution.

    The deletion is itself recorded as a new audit_log row (ALCOA+ Enduring
    — no silent data loss). AuditMiddleware skips every /audit-log request
    to avoid logging routine reads, so a deletion under this same prefix
    needs its own explicit entry, the same pattern app/routers/executions.py
    uses for its self-logged write.
    """
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM audit_log WHERE id = ?", (entry_id,)
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Audit entry {entry_id} not found.")
        deleted = dict(row)
        await db.execute("DELETE FROM audit_log WHERE id = ?", (entry_id,))
        await db.execute(
            """
            INSERT INTO audit_log (actor, action, table_affected, record_id, previous_value, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user.username,
                "DELETE_AUDIT_ENTRY",
                "audit_log",
                entry_id,
                json.dumps(deleted, default=str),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()
