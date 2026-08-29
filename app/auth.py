"""Authentication helpers — JWT encode/decode and current-user dependency."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config (portfolio-safe defaults — override via env in Docker)
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-not-for-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
class UserRole(str, Enum):
    analyst = "Analyst"
    qa_reviewer = "QA Reviewer"
    admin = "Admin"


# ---------------------------------------------------------------------------
# Token payload
# ---------------------------------------------------------------------------
class TokenData(BaseModel):
    username: str
    role: UserRole


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Timing-safe (bcrypt's own constant-time compare) verification."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


# A hash of a value nobody can type, used as the comparison target for an
# unknown username so login() always does one bcrypt verify regardless of
# whether the username exists — avoids leaking valid usernames via timing.
DUMMY_PASSWORD_HASH = hash_password("no-such-user-placeholder")


# ---------------------------------------------------------------------------
# Synthetic user store (portfolio — no real credentials)
# ---------------------------------------------------------------------------
# Passwords are bcrypt-hashed even though these are synthetic/demo accounts:
# storing them in plaintext with a non-constant-time `==` compare (the prior
# implementation) is exactly the pattern a careful reviewer would flag, so
# the portfolio piece demonstrates the real practice instead of skipping it.
SYNTHETIC_USERS: dict[str, dict] = {
    "analyst01": {
        "password_hash": hash_password("Analyst01!"),
        "role": UserRole.analyst,
        "full_name": "Ana Analyst",
    },
    "qa_reviewer01": {
        "password_hash": hash_password("QAReview01!"),
        "role": UserRole.qa_reviewer,
        "full_name": "Quinn Reviewer",
    },
    "admin01": {
        "password_hash": hash_password("Admin01!"),
        "role": UserRole.admin,
        "full_name": "Alex Admin",
    },
}


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")
        role: str = payload.get("role", "")
        if not username or not role:
            raise credentials_exc
        return TokenData(username=username, role=UserRole(role))
    except (JWTError, ValueError):
        raise credentials_exc


# ---------------------------------------------------------------------------
# FastAPI dependency — injects current authenticated user
# ---------------------------------------------------------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return decode_token(token)
