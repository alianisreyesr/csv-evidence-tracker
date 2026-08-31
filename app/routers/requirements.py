"""
requirements.py
================
REST endpoints for user requirements (URS).

Role enforcement (GAMP 5 / 21 CFR Part 11):
  - Any authenticated user        : read requirements
  - Analyst, QA Reviewer or Admin : author a new requirement
  - QA Reviewer or Admin          : perform the formal S x P x D risk
                                     assessment on a requirement
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from app.database import get_db
from app.models import Requirement, RequirementCreate, RequirementRisk
from app.auth import UserRole
from app.dependencies import require_role
from app.scoring import score_requirement_risk

router = APIRouter()


@router.get("", response_model=List[Requirement])
async def list_requirements(
    phase: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
):
    sql = "SELECT * FROM requirements WHERE 1=1"
    params = []
    if phase:
        sql += " AND phase=?"
        params.append(phase)
    if status:
        sql += " AND status=?"
        params.append(status)
    if priority:
        sql += " AND priority=?"
        params.append(priority)
    sql += " ORDER BY id"
    async with get_db() as db:
        rows = await (await db.execute(sql, params)).fetchall()
    return [dict(r) for r in rows]


@router.post("", response_model=Requirement, status_code=201)
async def create_requirement(
    body: RequirementCreate,
    _user=Depends(require_role(UserRole.analyst, UserRole.qa_reviewer, UserRole.admin)),
):
    """Author a new requirement. Requires Analyst role or above.

    `code` must be unique (e.g. URS-011) — a duplicate returns 409, the
    same conflict semantics used elsewhere in this codebase for unique
    business keys.
    """
    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        try:
            cursor = await db.execute(
                """
                INSERT INTO requirements
                    (code, title, description, category, priority, phase, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    body.code,
                    body.title,
                    body.description,
                    body.category,
                    body.priority,
                    body.phase,
                    body.status,
                    now,
                ),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail=f"Requirement code '{body.code}' already exists.")
        await db.commit()
        row = await (await db.execute(
            "SELECT * FROM requirements WHERE id = ?", (cursor.lastrowid,)
        )).fetchone()
    return dict(row)


@router.get("/{req_id}", response_model=Requirement)
async def get_requirement(req_id: int):
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM requirements WHERE id=?", (req_id,))).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return dict(row)


@router.post("/{req_id}/risk", response_model=Requirement)
async def assess_requirement_risk(
    req_id: int,
    body: RequirementRisk,
    _user=Depends(require_role(UserRole.qa_reviewer, UserRole.admin)),  # QA+ only
):
    """
    Formal S x P x D risk assessment for a requirement (ICH Q9 FMEA-style).

    risk_score/risk_level are always computed server-side via
    score_requirement_risk() — the same explainable-scoring principle
    classify_deviation_risk() applies to deviations — rather than trusted
    from the client. Restricted to QA Reviewer and Admin roles, matching
    the review-authority pattern used for deviation resolution
    (21 CFR Part 11 §11.10(d)).
    """
    async with get_db() as db:
        existing = await (await db.execute(
            "SELECT * FROM requirements WHERE id=?", (req_id,)
        )).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Requirement not found")

        risk = score_requirement_risk(
            severity=body.severity,
            probability=body.probability,
            detectability=body.detectability,
        )
        assessed_at = datetime.now(timezone.utc).isoformat()
        await db.execute(
            """
            UPDATE requirements
            SET risk_severity = ?, risk_probability = ?, risk_detectability = ?,
                risk_score = ?, risk_level = ?, risk_assessed_by = ?, risk_assessed_at = ?
            WHERE id = ?
            """,
            (
                body.severity,
                body.probability,
                body.detectability,
                risk["score"],
                risk["level"],
                body.assessed_by,
                assessed_at,
                req_id,
            ),
        )
        await db.commit()
        row = await (await db.execute(
            "SELECT * FROM requirements WHERE id = ?", (req_id,)
        )).fetchone()
    return dict(row)


@router.get("/{req_id}/test-cases")
async def get_requirement_test_cases(req_id: int):
    async with get_db() as db:
        req = await (await db.execute("SELECT * FROM requirements WHERE id=?", (req_id,))).fetchone()
        if not req:
            raise HTTPException(status_code=404, detail="Requirement not found")
        cases = await (await db.execute(
            "SELECT * FROM test_cases WHERE requirement_id=? ORDER BY id", (req_id,)
        )).fetchall()
    return {"requirement": dict(req), "test_cases": [dict(c) for c in cases]}
