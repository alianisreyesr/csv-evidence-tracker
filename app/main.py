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


@app.get("/summary", tags=["Summary"])
async def summary(request: Request):
    from app.database import get_db
    async with get_db() as db:
        total_reqs = (await db.execute("SELECT COUNT(*) FROM requirements")).fetchone()[0]
        total_tests = (await db.execute("SELECT COUNT(*) FROM test_cases")).fetchone()[0]
        passed = (await db.execute("SELECT COUNT(*) FROM test_executions WHERE result='PASS'")).fetchone()[0]
        failed = (await db.execute("SELECT COUNT(*) FROM test_executions WHERE result='FAIL'")).fetchone()[0]
        blocked = (await db.execute("SELECT COUNT(*) FROM test_executions WHERE result='BLOCKED'")).fetchone()[0]
        open_devs = (await db.execute("SELECT COUNT(*) FROM deviations WHERE status != 'Resolved'")).fetchone()[0]
        total_exec = (await db.execute("SELECT COUNT(*) FROM test_executions")).fetchone()[0]
        coverage_pct = round((total_exec / total_tests * 100), 1) if total_tests else 0
    return {
        "requirements": total_reqs,
        "test_cases": total_tests,
        "executions": {"total": total_exec, "passed": passed, "failed": failed, "blocked": blocked},
        "test_coverage_pct": coverage_pct,
        "open_deviations": open_devs,
    }
