"""
deviations.py
=============
REST endpoints for CSV deviation management.

Role enforcement (GAMP 5 / 21 CFR Part 11):
  - Any authenticated user  : create and read deviations
  - QA Reviewer or Admin    : resolve / approve a deviation
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.models import DeviationCreate, DeviationResolve, Deviation
from app.auth import UserRole
from app.dependencies import require_role, get_current_user
from datetime import datetime, timezone

router = APIRouter()


@router.post("", response_model=Deviation, status_code=201)
async def create_deviation(
    body: DeviationCreate,
    _user=Depends(get_current_user),   # any authenticated role
):
    """Create a new deviation record. Requires authentication."""
    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO deviations
                (execution_id, title, description, severity, risk_classification,
                 assigned_to, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Open', ?)
            """,
            (
                body.execution_id,
                body.title,
                body.description,
                body.severity,
                body.risk_classification,
                body.assigned_to,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (cursor.lastrowid,)
        )).fetchone()
    return dict(row)


@router.get("", response_model=list[Deviation])
async def list_deviations(_user=Depends(get_current_user)):
    """Return all deviation records. Requires authentication."""
    async with get_db() as db:
        rows = await (await db.execute("SELECT * FROM deviations ORDER BY created_at DESC")).fetchall()
    return [dict(r) for r in rows]


@router.get("/{deviation_id}", response_model=Deviation)
async def get_deviation(deviation_id: int, _user=Depends(get_current_user)):
    """Return a single deviation by ID. Requires authentication."""
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Deviation {deviation_id} not found.")
    return dict(row)


@router.patch("/{deviation_id}/resolve", response_model=Deviation)
async def resolve_deviation(
    deviation_id: int,
    body: DeviationResolve,
    _user=Depends(require_role(UserRole.qa_reviewer, UserRole.admin)),  # QA+ only
):
    """
    Resolve or accept-with-risk a deviation.
    Restricted to QA Reviewer and Admin roles (21 CFR Part 11 §11.10(d)).
    """
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Deviation {deviation_id} not found.")
        if dict(row)["status"] != "Open":
            raise HTTPException(status_code=409, detail="Deviation is already resolved.")

        resolved_at = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """
            UPDATE deviations
            SET status = ?, capa_ref = ?, resolved_at = ?
            WHERE id = ?
            """,
            (body.status, body.capa_ref, resolved_at, deviation_id),
        )
        await db.commit()
        updated = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
    return dict(updated)
