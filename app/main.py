from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.audit_middleware import AuditMiddleware
from app.routers import requirements, test_cases, executions, deviations, phases, audit, rtm
from app.routers import auth_router

APP_VERSION = "1.3.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="CSV Evidence Tracker",
    description=(
        "Portfolio-safe Computer System Validation (CSV) evidence tracker. "
        "All data is synthetic and non-confidential. "
        "Not for use in regulated production environments."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(phases.router, prefix="/phases", tags=["Phases"])
app.include_router(requirements.router, prefix="/requirements", tags=["Requirements"])
app.include_router(test_cases.router, prefix="/test-cases", tags=["Test Cases"])
app.include_router(executions.router, prefix="/executions", tags=["Executions"])
app.include_router(deviations.router, prefix="/deviations", tags=["Deviations"])
app.include_router(audit.router, prefix="/audit-log", tags=["Audit Log"])
app.include_router(rtm.router, prefix="/rtm", tags=["Traceability"])


# ---------------------------------------------------------------------------
# Platform endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health():
    """
    IQ-001 — Liveness probe.
    Returns application version, UTC timestamp, DB status, and data boundary notice.
    This endpoint is unauthenticated per URS-010.
    """
    from app.database import get_db
    db_status = "unknown"
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
            db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_status": db_status,
        "data_boundary": "All data is synthetic and non-confidential. Not for regulated use.",
    }


async def _count(db, sql: str) -> int:
    row = await (await db.execute(sql)).fetchone()
    return row[0]


@app.get("/summary", tags=["Summary"])
async def summary(request: Request):
    """Return aggregate validation progress metrics across all phases."""
    from app.database import get_db
    async with get_db() as db:
        total_reqs = await _count(db, "SELECT COUNT(*) FROM requirements")
        total_tests = await _count(db, "SELECT COUNT(*) FROM test_cases")
        passed = await _count(db, "SELECT COUNT(*) FROM test_executions WHERE result='PASS'")
        failed = await _count(db, "SELECT COUNT(*) FROM test_executions WHERE result='FAIL'")
        blocked = await _count(db, "SELECT COUNT(*) FROM test_executions WHERE result='BLOCKED'")
        open_devs = await _count(db, "SELECT COUNT(*) FROM deviations WHERE status != 'Resolved'")
        total_exec = await _count(db, "SELECT COUNT(*) FROM test_executions")
        coverage_pct = round((total_exec / total_tests * 100), 1) if total_tests else 0
    return {
        "requirements": total_reqs,
        "test_cases": total_tests,
        "executions": {"total": total_exec, "passed": passed, "failed": failed, "blocked": blocked},
        "test_coverage_pct": coverage_pct,
        "open_deviations": open_devs,
    }
