# Architecture — CSV Evidence Tracker

> For portfolio use only. All data is synthetic and non-confidential.

## Components

| Component | Technology | Purpose |
|---|---|---|
| Backend API | FastAPI + Python 3.11 | REST endpoints, business logic, audit middleware |
| Database | SQLite (WAL mode) | Structured storage with FK constraints |
| Frontend | React + Vite | Reviewer dashboard — RTM, test queue, deviation tracker |
| Seed Data | CSV (synthetic) | Fictional requirements, test cases, execution records |
| CI | GitHub Actions | Runs test suite on every push and PR |
| Container | Docker + Compose | One-command local setup |

## Data Flow

1. Synthetic CSVs are loaded into SQLite on first start
2. FastAPI serves data via structured endpoints with Pydantic validation
3. All mutating requests are intercepted by `AuditMiddleware` → logged to `audit_log`
4. Review actions (test execution, deviation resolution) also generate explicit audit events
5. React dashboard consumes the API via `/api` proxy (Vite dev) or direct URL (production)

## Audit Trail Design

The `audit_log` table is the core compliance artifact:
- **Append-only:** No UPDATE or DELETE is ever issued against this table
- **Server-generated timestamps:** `created_at` is set by the server in UTC, never by the client
- **Actor required:** Every mutation requires an `actor` identifier (API header)
- **Dual logging:** Explicit review events + `AuditMiddleware` for all mutating HTTP requests
