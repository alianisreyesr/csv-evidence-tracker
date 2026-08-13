from fastapi import APIRouter, Query
from app.database import get_db
from app.models import AuditEntry
from typing import List, Optional

router = APIRouter()


@router.get("", response_model=List[AuditEntry])
async def get_audit_log(
    actor: Optional[str] = Query(None),
    table_affected: Optional[str] = Query(None),
    record_id: Optional[int] = Query(None),
    limit: int = Query(100, le=500),
):
    sql = "SELECT * FROM audit_log WHERE 1=1"
    params = []
    if actor:
        sql += " AND actor=?"
        params.append(actor)
    if table_affected:
        sql += " AND table_affected=?"
        params.append(table_affected)
    if record_id:
        sql += " AND record_id=?"
        params.append(record_id)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    async with get_db() as db:
        rows = await (await db.execute(sql, params)).fetchall()
    return [dict(r) for r in rows]
