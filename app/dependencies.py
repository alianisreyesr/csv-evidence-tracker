"""Role enforcement dependencies — use require_role() on any endpoint."""
from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from app.auth import TokenData, UserRole, get_current_user


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Factory that returns a FastAPI dependency enforcing role membership.

    Usage:
        @router.post("/approve")
        async def approve(user=Depends(require_role(UserRole.qa_reviewer, UserRole.admin))):
            ...
    """
    async def _check(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role}' is not authorised for this action. "
                    f"Required: {[r.value for r in allowed_roles]}"
                ),
            )
        return current_user

    return _check


# ---------------------------------------------------------------------------
# Convenience shortcuts
# ---------------------------------------------------------------------------
Any_Authenticated = Depends(get_current_user)
Analyst_Or_Above = Depends(require_role(UserRole.analyst, UserRole.qa_reviewer, UserRole.admin))
QA_Or_Above = Depends(require_role(UserRole.qa_reviewer, UserRole.admin))
Admin_Only = Depends(require_role(UserRole.admin))
