"""Authentication router — POST /auth/login returns a Bearer JWT."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from pydantic import BaseModel

from app.auth import (
    DUMMY_PASSWORD_HASH,
    SYNTHETIC_USERS,
    UserRole,
    create_access_token,
    decode_token,
    oauth2_scheme,
    verify_password,
)

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    full_name: str


@router.post(
    "/login",
    response_model=Token,
    summary="Obtain a Bearer JWT",
    description=(
        "Authenticate with a synthetic portfolio user. "
        "Credentials are hard-coded for demonstration — not for production use. "
        "Available users: analyst01 / qa_reviewer01 / admin01."
    ),
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = SYNTHETIC_USERS.get(form_data.username)
    # Verify against the placeholder hash even on an unknown username so a
    # bad username and a bad password take the same amount of time.
    password_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
    if not user or not verify_password(form_data.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": form_data.username, "role": user["role"].value})
    return Token(
        access_token=token,
        token_type="bearer",
        role=user["role"],
        full_name=user["full_name"],
    )


@router.get("/me", summary="Return current authenticated user info")
async def me(token: str = Depends(oauth2_scheme)):
    data = decode_token(token)
    user = SYNTHETIC_USERS.get(data.username, {})
    return {
        "username": data.username,
        "role": data.role,
        "full_name": user.get("full_name", ""),
    }
