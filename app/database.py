import aiosqlite
import csv
from pathlib import Path
from contextlib import asynccontextmanager

DB_PATH = Path("data/csv_tracker.db")
DATA_DIR = Path("data")


@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def init_db():
    schema = Path("sql/schema.sql").read_text()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(schema)
        await db.commit()
        await _seed_if_empty(db)


async def _seed_if_empty(db):
    count = (await (await db.execute("SELECT COUNT(*) FROM requirements")).fetchone())[0]
    if count > 0:
        return

    for table, file in [
        ("phases", "phases.csv"),
        ("requirements", "requirements.csv"),
        ("test_cases", "test_cases.csv"),
        ("test_executions", "test_executions.csv"),
        ("deviations", "deviations.csv"),
    ]:
        path = DATA_DIR / file
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            continue
        cols = ", ".join(rows[0].keys())
        placeholders = ", ".join(["?"] * len(rows[0]))
        await db.executemany(
            f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})",
            [list(r.values()) for r in rows],
        )
    await db.commit()
