from fastapi import APIRouter, HTTPException, Query
from app.database import get_db
from app.models import Requirement
from typing import List, Optional

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


@router.get("/{req_id}", response_model=Requirement)
async def get_requirement(req_id: int):
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM requirements WHERE id=?", (req_id,))).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Requirement not found")
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
