from fastapi import APIRouter, HTTPException, Header, Query
from app.database import get_db
from app.models import DeviationCreate, DeviationResolve, Deviation
from app.scoring import classify_deviation_risk
from typing import List, Optional
from datetime import datetime, timezone
import json

router = APIRouter()


@router.get("")
async def list_deviations(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    sql = "SELECT * FROM deviations WHERE 1=1"
    params = []
    if status:
        sql += " AND status=?"
        params.append(status)
    if severity:
        sql += " AND severity=?"
        params.append(severity)
    sql += " ORDER BY created_at DESC"
    async with get_db() as db:
        rows = await (await db.execute(sql, params)).fetchall()

    result = []
    for r in rows:
        d = dict(r)
        risk = classify_deviation_risk(
            severity=d["severity"],
            status=d["status"],
            created_at=d["created_at"],
            assigned_to=d.get("assigned_to"),
        )
        d["risk_score"] = risk["score"]
        d["risk_classification"] = risk["classification"]
        d["contributing_reasons"] = risk["contributing_reasons"]
        result.append(d)
    return result


@router.get("/{dev_id}")
async def get_deviation(dev_id: int):
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM deviations WHERE id=?", (dev_id,))).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Deviation not found")
    d = dict(row)
    risk = classify_deviation_risk(
        severity=d["severity"],
        status=d["status"],
        created_at=d["created_at"],
        assigned_to=d.get("assigned_to"),
    )
    d.update(risk)
    return d


@router.post("", status_code=201)
async def create_deviation(
    body: DeviationCreate,
    x_actor: str = Header(...),
):
    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        cur = await db.execute(
            """
            INSERT INTO deviations
                (execution_id, title, description, severity, risk_classification,
                 status, assigned_to, created_at)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (body.execution_id, body.title, body.description, body.severity,
             body.risk_classification, "Open", body.assigned_to, now),
        )
        dev_id = cur.lastrowid
        await db.execute(
            "INSERT INTO audit_log (actor, action, table_affected, record_id, new_value, created_at) VALUES (?,?,?,?,?,?)",
            (x_actor, "CREATE_DEVIATION", "deviations", dev_id, json.dumps(body.model_dump()), now),
        )
        await db.commit()
        row = await (await db.execute("SELECT * FROM deviations WHERE id=?", (dev_id,))).fetchone()
    d = dict(row)
    risk = classify_deviation_risk(
        severity=d["severity"], status=d["status"],
        created_at=d["created_at"], assigned_to=d.get("assigned_to")
    )
    d.update(risk)
    return d


@router.post("/{dev_id}/resolve")
async def resolve_deviation(
    dev_id: int,
    body: DeviationResolve,
    x_actor: str = Header(...),
):
    now = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM deviations WHERE id=?", (dev_id,))).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Deviation not found")
        d = dict(row)
        if d["status"] in ("Resolved", "Accepted with Risk"):
            raise HTTPException(status_code=400, detail="Deviation is already resolved.")

        await db.execute(
            "UPDATE deviations SET status=?, capa_ref=?, resolved_at=? WHERE id=?",
            (body.status, body.capa_ref, now, dev_id),
        )
        await db.execute(
            """
            INSERT INTO audit_log
                (actor, action, table_affected, record_id, previous_value, new_value, created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                x_actor, "RESOLVE_DEVIATION", "deviations", dev_id,
                json.dumps({"status": d["status"]}),
                json.dumps({"status": body.status, "capa_ref": body.capa_ref,
                            "resolution_notes": body.resolution_notes}),
                now,
            ),
        )
        await db.commit()
    return {"id": dev_id, "status": body.status, "resolved_at": now, "actor": x_actor}
