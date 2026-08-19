from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.audit_middleware import AuditMiddleware
from app.routers import requirements, test_cases, executions, deviations, phases, audit


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
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuditMiddleware)

app.include_router(phases.router, prefix="/phases", tags=["Phases"])
app.include_router(requirements.router, prefix="/requirements", tags=["Requirements"])
app.include_router(test_cases.router, prefix="/test-cases", tags=["Test Cases"])
app.include_router(executions.router, prefix="/executions", tags=["Executions"])
app.include_router(deviations.router, prefix="/deviations", tags=["Deviations"])
app.include_router(audit.router, prefix="/audit-log", tags=["Audit Log"])


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "data_boundary": "All data is synthetic and non-confidential. Not for regulated use.",
    }


async def _count(db, sql: str) -> int:
    row = await (await db.execute(sql)).fetchone()
    return row[0]


@app.get("/summary", tags=["Summary"])
async def summary(request: Request):
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
