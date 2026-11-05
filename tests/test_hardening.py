"""Security hardening: auth on reads, JWT-derived resolver, secret check,
audit middleware behaviour, and CSV formula neutralisation."""
import csv
import io
import logging
import sqlite3

import pytest

from app.auth import DEFAULT_DEV_SECRET, resolve_secret_key
from tests.auth_helpers import auth_headers, login

PROTECTED_GETS = [
    "/phases", "/phases/1", "/requirements", "/requirements/1",
    "/requirements/1/test-cases", "/test-cases", "/test-cases/1",
    "/executions", "/rtm",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", PROTECTED_GETS)
async def test_read_endpoints_require_auth(client, path):
    assert (await client.get(path)).status_code == 401
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    assert (await client.get(path, headers=headers)).status_code == 200


def test_secret_default_rejected_outside_dev():
    with pytest.raises(RuntimeError):
        resolve_secret_key(None, "production")
    with pytest.raises(RuntimeError):
        resolve_secret_key(DEFAULT_DEV_SECRET, "production")
    assert resolve_secret_key("a-private-value", "production") == "a-private-value"
    assert resolve_secret_key(None, "development") == DEFAULT_DEV_SECRET


@pytest.mark.asyncio
async def test_resolver_taken_from_jwt(client, patch_db_path):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    dev = (await client.post(
        "/deviations", json={"title": "Resolver attribution", "severity": "Minor"},
        headers=headers)).json()
    r = await client.patch(
        f"/deviations/{dev['id']}/resolve",
        json={"actor": "someone.else", "resolution_notes": "Resolved with attribution.",
              "status": "Resolved"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["resolved_by"] == "qa_reviewer01"
    con = sqlite3.connect(patch_db_path)
    assert con.execute("SELECT resolved_by FROM deviations WHERE id=?", (dev["id"],)).fetchone()[0] == "qa_reviewer01"


@pytest.mark.asyncio
async def test_audit_uses_database_path_and_logs_failures(client, patch_db_path, caplog):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    # Written to the configured DB (database.DB_PATH), not a hard-coded path.
    await client.post("/deviations", json={"title": "Audit path check", "severity": "Minor"}, headers=headers)
    con = sqlite3.connect(patch_db_path)
    assert con.execute("SELECT COUNT(*) FROM audit_log WHERE action='POST /deviations'").fetchone()[0] == 1

    # A failing audit write must be logged, not swallowed silently.
    con.execute("DROP TABLE audit_log")
    con.commit()
    with caplog.at_level(logging.ERROR, logger="app.audit_middleware"):
        r = await client.post("/deviations", json={"title": "Audit failure check", "severity": "Minor"}, headers=headers)
    assert r.status_code == 201  # the request itself is not blocked
    assert any("Failed to write audit_log" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_rtm_export_neutralises_formulas(client):
    admin = auth_headers(await login(client, "admin01", "Admin01!"))
    r = await client.post(
        "/requirements",
        json={"code": "URS-999", "title": "=HYPERLINK(\"http://evil\",\"x\")", "priority": "High"},
        headers=admin,
    )
    assert r.status_code == 201, r.text
    export = await client.get("/rtm/export", headers=admin)
    rows = list(csv.DictReader(io.StringIO(export.text)))
    titles = [row["requirement_title"] for row in rows if row["requirement_code"] == "URS-999"]
    assert titles == ["'=HYPERLINK(\"http://evil\",\"x\")"]
    assert not any(row["requirement_title"].startswith("=") for row in rows)
