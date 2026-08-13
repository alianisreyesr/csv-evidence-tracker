import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import aiosqlite
from pathlib import Path

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
DB_PATH = Path("data/csv_tracker.db")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        if (
            request.method in MUTATING_METHODS
            and request.url.path not in EXCLUDED_PATHS
            and not request.url.path.startswith("/audit-log")
        ):
            actor = request.headers.get("X-Actor", "unknown")
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute(
                        """
                        INSERT INTO audit_log
                            (actor, action, ip_address, user_agent, status_code, latency_ms)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            actor,
                            f"{request.method} {request.url.path}",
                            request.client.host if request.client else None,
                            request.headers.get("user-agent"),
                            response.status_code,
                            latency_ms,
                        ),
                    )
                    await db.commit()
            except Exception:
                pass  # Never block a request due to audit failure

        return response
