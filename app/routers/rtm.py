from fastapi import APIRouter
from app.database import get_db

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
