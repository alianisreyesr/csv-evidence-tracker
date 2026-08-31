import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends

from app.database import get_db
from app.models import TestCaseCreate
from app.auth import UserRole
from app.dependencies import require_role

router = APIRouter()


@router.post("", status_code=201)
async def create_test_case(
    body: TestCaseCreate,
    _user=Depends(require_role(UserRole.analyst, UserRole.qa_reviewer, UserRole.admin)),
):
    """Author a new test case linked to a requirement. Requires Analyst role or above.

    `code` must be unique (e.g. TC-OQ-011); `requirement_id` must reference
    an existing requirement — both violations return a 4xx rather than a
    raw database error, matching the pattern in requirements.py.
    """
    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        req = await (await db.execute(
            "SELECT id FROM requirements WHERE id=?", (body.requirement_id,)
        )).fetchone()
        if not req:
            raise HTTPException(
                status_code=422, detail=f"Requirement {body.requirement_id} does not exist."
            )
        try:
            cursor = await db.execute(
                """
                INSERT INTO test_cases
                    (requirement_id, code, title, description, test_type, expected_result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    body.requirement_id,
                    body.code,
                    body.title,
                    body.description,
                    body.test_type,
                    body.expected_result,
                    now,
                ),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail=f"Test case code '{body.code}' already exists.")
        await db.commit()
        row = await (await db.execute(
            """
            SELECT tc.*, r.code AS requirement_code, r.title AS requirement_title,
                   r.phase AS requirement_phase
            FROM test_cases tc
            JOIN requirements r ON r.id = tc.requirement_id
            WHERE tc.id = ?
            """,
            (cursor.lastrowid,),
        )).fetchone()
    return dict(row)


@router.get("")
async def list_test_cases(
    phase: Optional[str] = Query(None),
    requirement_id: Optional[int] = Query(None),
):
    sql = """
        SELECT tc.*, r.code AS requirement_code, r.title AS requirement_title,
               r.phase AS requirement_phase
        FROM test_cases tc
        JOIN requirements r ON r.id = tc.requirement_id
        WHERE 1=1
    """
    params = []
    if requirement_id:
        sql += " AND tc.requirement_id=?"
        params.append(requirement_id)
    if phase:
        sql += " AND r.phase=?"
        params.append(phase)
    sql += " ORDER BY tc.id"
    async with get_db() as db:
        rows = await (await db.execute(sql, params)).fetchall()
    return [dict(r) for r in rows]


@router.get("/{case_id}")
async def get_test_case(case_id: int):
    async with get_db() as db:
        row = await (await db.execute(
            """
            SELECT tc.*, r.code AS requirement_code, r.title AS requirement_title,
                   r.phase AS requirement_phase
            FROM test_cases tc
            JOIN requirements r ON r.id = tc.requirement_id
            WHERE tc.id=?
            """,
            (case_id,),
        )).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Test case not found")
        executions = await (await db.execute(
            "SELECT * FROM test_executions WHERE test_case_id=? ORDER BY executed_at DESC",
            (case_id,),
        )).fetchall()
    return {"test_case": dict(row), "executions": [dict(e) for e in executions]}
