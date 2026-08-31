import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.dependencies import Admin_Only

router = APIRouter()


@router.get("")
async def get_rtm():
    """
    Requirements Traceability Matrix:
    Returns all requirements with their linked test cases and latest execution result.
    """
    async with get_db() as db:
        reqs = await (await db.execute("SELECT * FROM requirements ORDER BY id")).fetchall()
        result = []
        for req in reqs:
            r = dict(req)
            cases = await (await db.execute(
                "SELECT * FROM test_cases WHERE requirement_id=? ORDER BY id",
                (req["id"],),
            )).fetchall()
            test_list = []
            for tc in cases:
                t = dict(tc)
                latest = await (await db.execute(
                    "SELECT * FROM test_executions WHERE test_case_id=? ORDER BY executed_at DESC LIMIT 1",
                    (tc["id"],),
                )).fetchone()
                t["latest_execution"] = dict(latest) if latest else None
                test_list.append(t)
            r["test_cases"] = test_list
            r["total_tests"] = len(test_list)
            executed = [t for t in test_list if t["latest_execution"]]
            r["executed_count"] = len(executed)
            passed = [t for t in executed if t["latest_execution"]["result"] == "PASS"]
            r["passed_count"] = len(passed)
            r["coverage_pct"] = round(len(executed) / len(test_list) * 100, 1) if test_list else 0
            result.append(r)
    return result


@router.get("/export")
async def export_rtm_csv(_user=Admin_Only):
    """
    URS-007 — Export the Requirements Traceability Matrix as CSV.

    One row per (requirement, test case) pair, with the latest execution
    result flattened in — the same evidence GET /rtm returns as nested
    JSON, in the tabular form an auditor expects to attach to a validation
    package. Requirements with no test cases yet still get one row so
    coverage gaps are visible in the export, not silently dropped.

    Restricted to Admin (21 CFR Part 11 §11.10(d)) since an RTM export is
    itself a piece of validation evidence.
    """
    data = await get_rtm()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "requirement_code", "requirement_title", "priority", "phase", "requirement_status",
        "test_case_code", "test_case_title", "expected_result",
        "latest_result", "executed_by", "executed_at",
    ])
    for req in data:
        test_cases = req["test_cases"]
        if not test_cases:
            writer.writerow([
                req["code"], req["title"], req["priority"], req["phase"], req["status"],
                "", "", "", "NOT_RUN", "", "",
            ])
            continue
        for tc in test_cases:
            latest = tc["latest_execution"]
            writer.writerow([
                req["code"], req["title"], req["priority"], req["phase"], req["status"],
                tc["code"], tc["title"], tc["expected_result"],
                latest["result"] if latest else "NOT_RUN",
                latest["executed_by"] if latest else "",
                latest["executed_at"] if latest else "",
            ])

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rtm_export.csv"},
    )
