import time
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import aiosqlite
from pathlib import Path

from fastapi import HTTPException

from app.auth import decode_token

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}
# POST /executions writes its own richer audit_log entry (see
# app/routers/executions.py) using the same JWT-verified actor this
# middleware would otherwise log — skip it here to avoid a duplicate row.
SELF_LOGGED_PATHS = {"/executions"}
DB_PATH = Path("data/csv_tracker.db")


def _actor_from_request(request: Request) -> str:
    """Resolve the audit actor from the verified JWT, not a client header.

    A bearer token is present on every mutating route this middleware
    covers (they all require authentication), so this is the caller's
    real, verified identity rather than an unauthenticated, spoofable
    ``X-Actor`` header. Falls back to that header only when no valid
    token is present, which should only happen on requests that end up
    401ing anyway.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
        try:
            return decode_token(token).username
        except HTTPException:
            pass
    return request.headers.get("X-Actor", "unknown")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        if (
            request.method in MUTATING_METHODS
            and request.url.path not in EXCLUDED_PATHS
            and request.url.path not in SELF_LOGGED_PATHS
            and not request.url.path.startswith("/audit-log")
        ):
            actor = _actor_from_request(request)
            try:
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute(
                        """
                        INSERT INTO audit_log
                            (actor, action, ip_address, user_agent, status_code, latency_ms, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            actor,
                            f"{request.method} {request.url.path}",
                            request.client.host if request.client else None,
                            request.headers.get("user-agent"),
                            response.status_code,
                            latency_ms,
                            # Explicit, timezone-aware UTC timestamp — the column's
                            # DEFAULT (datetime('now','utc')) produces a naive
                            # string with no offset, which breaks the ALCOA+
                            # Contemporaneous guarantee every other insert in this
                            # codebase (deviations, test_executions) already keeps.
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    await db.commit()
            except Exception:
                pass  # Never block a request due to audit failure

        return response
