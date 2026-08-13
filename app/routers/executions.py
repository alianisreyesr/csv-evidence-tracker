from fastapi import APIRouter, HTTPException, Header, Query
from app.database import get_db
from app.models import ExecutionCreate, Execution
from typing import List, Optional
from datetime import datetime, timezone
import json

router = APIRouter()


@router.get("", response_model=List[Execution])
async def list_executions(
    result: Optional[str] = Query(None),
    phase_id: Optional[int] = Query(None),
):
    sql = "SELECT * FROM test_executions WHERE 1=1"
    params = []
    if result:
        sql += " AND result=?"
        params.append(result)
    if phase_id:
        sql += " AND phase_id=?"
        params.append(phase_id)
    sql += " ORDER BY executed_at DESC"
    async with get_db() as db:
        rows = await (await db.execute(sql, params)).fetchall()
    return [dict(r) for r in rows]


@router.post("", response_model=Execution, status_code=201)
async def record_execution(
    body: ExecutionCreate,
    x_actor: str = Header(..., description="Identifier of the person recording the execution"),
):
    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        tc = await (await db.execute("SELECT id FROM test_cases WHERE id=?", (body.test_case_id,))).fetchone()
        if not tc:
            raise HTTPException(status_code=404, detail="Test case not found")
        ph = await (await db.execute("SELECT id FROM phases WHERE id=?", (body.phase_id,))).fetchone()
        if not ph:
            raise HTTPException(status_code=404, detail="Phase not found")

        cur = await db.execute(
            """
            INSERT INTO test_executions
                (test_case_id, phase_id, executed_by, executed_at, result,
                 actual_result, evidence_ref, notes, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (body.test_case_id, body.phase_id, x_actor, now,
             body.result, body.actual_result, body.evidence_ref, body.notes, now),
        )
        exec_id = cur.lastrowid

        await db.execute(
            """
            INSERT INTO audit_log (actor, action, table_affected, record_id, new_value, created_at)
            VALUES (?,?,?,?,?,?)
            """,
            (x_actor, "EXECUTE_TEST", "test_executions", exec_id,
             json.dumps({"test_case_id": body.test_case_id, "result": body.result}), now),
        )
        await db.commit()

        row = await (await db.execute("SELECT * FROM test_executions WHERE id=?", (exec_id,))).fetchone()
    return dict(row)
