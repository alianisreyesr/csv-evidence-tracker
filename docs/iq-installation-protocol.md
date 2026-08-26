# Installation Qualification (IQ) Protocol

**System:** CSV Evidence Tracker  
**Protocol ID:** IQ-001  
**Version:** 1.0  
**Date:** 2026-08-26  
**Author:** Portfolio Project — Synthetic GxP Demo  
**Status:** Executed (simulated)

> ⚠️ Portfolio project. All data is synthetic. This protocol is not part of a validated GxP system.

---

## 1. Purpose

This IQ protocol verifies that the CSV Evidence Tracker system is correctly installed and configured in the target environment. It covers Docker-based deployment, database migration, environment variable configuration, and the system health check endpoint.

Successful IQ execution is a prerequisite for proceeding to Operational Qualification (OQ).

---

## 2. Scope

- Docker Compose deployment
- Database initialization and migration
- Environment variable configuration
- Health check endpoint (`GET /health`)
- Application version verification

---

## 3. Pre-Installation Checklist

| Item | Requirement | Verified |
|---|---|---|
| Docker Engine | ≥ 24.0 installed | ✅ |
| Docker Compose | ≥ 2.20 installed | ✅ |
| Git | Repository cloned from `github.com/alianisreyesr/csv-evidence-tracker` | ✅ |
| `.env` file | Created from `.env.example` with `SECRET_KEY`, `DATABASE_URL` | ✅ |
| Ports | 80 (nginx), 8000 (API), 5432 (DB) available | ✅ |

---

## 4. Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | JWT signing secret (min 32 chars) | `change-me-in-production` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+aiosqlite:///./csv_tracker.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token TTL | `60` |
| `APP_VERSION` | Application version (auto-set in code) | `1.3.0` |

---

## 5. Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/alianisreyesr/csv-evidence-tracker.git
cd csv-evidence-tracker

# 2. Copy environment file
cp .env.example .env
# Edit .env and set SECRET_KEY to a secure value

# 3. Start all services
docker compose up --build -d

# 4. Verify services are running
docker compose ps
# Expected: api, db, frontend, nginx all showing "Up"

# 5. Run database migrations
docker compose exec api alembic upgrade head
# Expected: "INFO [alembic.runtime.migration] Running upgrade ..."

# 6. Verify health endpoint
curl http://localhost/health
# Expected: {"status": "ok", "version": "1.3.0", "db_status": "ok", ...}
```

---

## 6. IQ Test Cases

### IQ-001 — Health Endpoint Returns 200 with Version
| Field | Value |
|---|---|
| **URS** | URS-010 |
| **Risk Score** | 4 (LOW) |
| **Test File** | `tests/test_health.py` |
| **Command** | `curl http://localhost/health` |
| **Expected** | HTTP 200, JSON with `status: ok`, `version: 1.3.0`, `timestamp` (UTC), `db_status: ok` |
| **Actual** | HTTP 200, all fields present |
| **Result** | ✅ PASS |

### IQ-002 — Database Connectivity
| Field | Value |
|---|---|
| **URS** | URS-010 |
| **Risk Score** | 4 (LOW) |
| **Command** | `docker compose exec db psql -U postgres -c "SELECT 1;"` |
| **Expected** | Returns `1` (connection successful) |
| **Actual** | Connection successful |
| **Result** | ✅ PASS |

### IQ-003 — Database Migrations Applied
| Field | Value |
|---|---|
| **URS** | URS-002, URS-003 |
| **Risk Score** | 10 (MEDIUM) |
| **Command** | `docker compose exec api alembic current` |
| **Expected** | Current migration head applied; all tables exist (`deviations`, `audit_log`, `users`) |
| **Actual** | All tables present |
| **Result** | ✅ PASS |

### IQ-004 — API Documentation Accessible
| Field | Value |
|---|---|
| **URS** | NFR-003 |
| **Risk Score** | 2 (LOW) |
| **Command** | `curl http://localhost/docs` |
| **Expected** | HTTP 200, Swagger UI rendered |
| **Actual** | HTTP 200 |
| **Result** | ✅ PASS |

### IQ-005 — Reproducible from Clean Clone
| Field | Value |
|---|---|
| **URS** | NFR-003 |
| **Risk Score** | 4 (LOW) |
| **Steps** | `git clone` → `cp .env.example .env` → `docker compose up --build -d` → `/health` |
| **Expected** | Full system operational with no manual steps beyond env file |
| **Actual** | System operational |
| **Result** | ✅ PASS |

---

## 7. IQ Summary

| Total Tests | Pass | Fail |
|---|---|---|
| 5 | 5 | 0 |

**IQ Conclusion:** The system is correctly installed. All installation verification tests passed. The system is approved to proceed to Operational Qualification (OQ).

---

*Protocol executed as simulated portfolio evidence. All business data is synthetic.*
