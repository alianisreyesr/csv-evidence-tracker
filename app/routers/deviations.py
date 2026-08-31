"""
deviations.py
=============
REST endpoints for CSV deviation management.

Role enforcement (GAMP 5 / 21 CFR Part 11):
  - Any authenticated user  : create and read deviations
  - QA Reviewer or Admin    : resolve / approve a deviation
"""
from __future__ import annotations

import json

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from app.database import get_db
from app.models import DeviationCreate, DeviationResolve, DeviationStatusUpdate, Deviation
from app.auth import UserRole
from app.dependencies import require_role, get_current_user
from app.scoring import classify_deviation_risk
from datetime import datetime, timezone

# Statuses PATCH /{id}/resolve may transition out of. A deviation can be
# resolved straight from Open, or after an optional Under Investigation
# step via PATCH /{id}/status — both are valid QA workflows here.
RESOLVABLE_FROM = {"Open", "Under Investigation"}

router = APIRouter()


def _deserialize(row: dict) -> dict:
    data = dict(row)
    reasons = data.get("contributing_reasons")
    data["contributing_reasons"] = json.loads(reasons) if reasons else None
    return data


@router.post("", response_model=Deviation, status_code=201)
async def create_deviation(
    body: DeviationCreate,
    _user=Depends(get_current_user),   # any authenticated role
):
    """Create a new deviation record. Requires authentication.

    risk_classification/risk_score are always computed server-side via
    classify_deviation_risk() — the explainable rule engine this project
    exists to demonstrate — rather than trusted from the client, so a
    caller can't just assert their own severity rating.
    """
    now = datetime.now(timezone.utc).isoformat()
    risk = classify_deviation_risk(
        severity=body.severity,
        status="Open",
        created_at=now,
        assigned_to=body.assigned_to,
    )
    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO deviations
                (execution_id, title, description, severity, risk_classification,
                 risk_score, contributing_reasons, assigned_to, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)
            """,
            (
                body.execution_id,
                body.title,
                body.description,
                body.severity,
                risk["classification"],
                risk["score"],
                json.dumps(risk["contributing_reasons"]),
                body.assigned_to,
                now,
            ),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (cursor.lastrowid,)
        )).fetchone()
    return _deserialize(dict(row))


@router.get("", response_model=list[Deviation])
async def list_deviations(
    status: Optional[str] = Query(None),
    _user=Depends(get_current_user),
):
    """Return deviation records, optionally filtered by status. Requires authentication."""
    async with get_db() as db:
        if status:
            rows = await (await db.execute(
                "SELECT * FROM deviations WHERE status = ? ORDER BY created_at DESC", (status,)
            )).fetchall()
        else:
            rows = await (await db.execute("SELECT * FROM deviations ORDER BY created_at DESC")).fetchall()
    return [_deserialize(dict(r)) for r in rows]


@router.get("/{deviation_id}", response_model=Deviation)
async def get_deviation(deviation_id: int, _user=Depends(get_current_user)):
    """Return a single deviation by ID. Requires authentication."""
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Deviation {deviation_id} not found.")
    return _deserialize(dict(row))


@router.patch("/{deviation_id}/status", response_model=Deviation)
async def update_deviation_status(
    deviation_id: int,
    body: DeviationStatusUpdate,
    _user=Depends(require_role(UserRole.qa_reviewer, UserRole.admin)),  # QA+ only
):
    """
    Move a deviation from Open into Under Investigation, ahead of resolving it.
    Restricted to QA Reviewer and Admin roles (21 CFR Part 11 §11.10(d)).
    """
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Deviation {deviation_id} not found.")
        if dict(row)["status"] != "Open":
            raise HTTPException(
                status_code=409,
                detail="Only an Open deviation can move to Under Investigation.",
            )

        await db.execute(
            "UPDATE deviations SET status = ? WHERE id = ? AND status = 'Open'",
            (body.status, deviation_id),
        )
        await db.commit()
        updated = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
    return _deserialize(dict(updated))


@router.patch("/{deviation_id}/resolve", response_model=Deviation)
async def resolve_deviation(
    deviation_id: int,
    body: DeviationResolve,
    _user=Depends(require_role(UserRole.qa_reviewer, UserRole.admin)),  # QA+ only
):
    """
    Resolve or accept-with-risk a deviation. Valid from Open or, after an
    optional PATCH /{id}/status step, from Under Investigation. Rejected
    with 409 once a deviation is already in a terminal state.
    Restricted to QA Reviewer and Admin roles (21 CFR Part 11 §11.10(d)).

    OQ-015 / URS-008 (ICH Q9 risk-based control): a Critical deviation
    cannot be resolved without a documented root_cause — severity alone
    doesn't justify closing the highest-risk records on a resolution note.
    """
    async with get_db() as db:
        row = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Deviation {deviation_id} not found.")
        current = dict(row)
        if current["status"] not in RESOLVABLE_FROM:
            raise HTTPException(status_code=409, detail="Deviation is already resolved.")
        if current["severity"] == "Critical" and not (body.root_cause or "").strip():
            raise HTTPException(
                status_code=422,
                detail="root_cause is required to resolve a Critical deviation.",
            )

        resolved_at = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """
            UPDATE deviations
            SET status = ?, capa_ref = ?, resolved_at = ?, resolution_notes = ?, root_cause = ?
            WHERE id = ? AND status IN ('Open', 'Under Investigation')
            """,
            (body.status, body.capa_ref, resolved_at, body.resolution_notes, body.root_cause, deviation_id),
        )
        await db.commit()
        updated = await (await db.execute(
            "SELECT * FROM deviations WHERE id = ?", (deviation_id,)
        )).fetchone()
    return _deserialize(dict(updated))
