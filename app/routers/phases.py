from fastapi import APIRouter
from app.database import get_db
from app.models import Phase
from typing import List

router = APIRouter()


@router.get("", response_model=List[Phase])
async def list_phases():
    async with get_db() as db:
        rows = await (await db.execute("SELECT * FROM phases ORDER BY id")).fetchall()
    return [dict(r) for r in rows]


@router.get("/{phase_id}", response_model=Phase)
async def get_phase(phase_id: int):
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM phases WHERE id=?", (phase_id,))).fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Phase not found")
    return dict(row)
