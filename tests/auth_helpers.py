"""Shared auth helpers for tests — obtain a Bearer JWT for a synthetic user."""
from __future__ import annotations

from httpx import AsyncClient


async def login(client: AsyncClient, username: str, password: str) -> str:
    """Obtain a Bearer token for the given synthetic user."""
    resp = await client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    """Return Authorization header dict for a given token."""
    return {"Authorization": f"Bearer {token}"}
