import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pathlib import Path

# Use a temp DB for tests
TEST_DB = Path("data/test_tracker.db")


@pytest.fixture(autouse=True)
def patch_db_path(monkeypatch, tmp_path):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr("app.database.DB_PATH", test_db)
    monkeypatch.setattr("app.audit_middleware.DB_PATH", test_db)
    monkeypatch.setattr("app.routers.executions.get_db", _patched_get_db(test_db))
    return test_db


def _patched_get_db(path):
    import aiosqlite
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def get_db():
        async with aiosqlite.connect(path) as db:
            db.row_factory = aiosqlite.Row
            await db.execute("PRAGMA foreign_keys=ON")
            yield db
    return get_db


@pytest_asyncio.fixture
async def client():
    from app.main import app
    from app.database import init_db
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
