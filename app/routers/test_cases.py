from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from typing import Optional

router = APIRouter()


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
