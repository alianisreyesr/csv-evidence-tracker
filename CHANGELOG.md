# Changelog

All notable changes to this project are documented here.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Fixed — PQ execution review (2026-08-31)

Live-executing the PQ protocol surfaced several gaps between documented and
actual behavior; each was fixed and re-verified against the running app
rather than left as a documentation claim:

- **Broken test infrastructure**: `tests/test_timestamps.py`,
  `test_validation.py`, `test_deviation_lifecycle.py`, `test_audit_trail.py`,
  and `test_export.py` used `AsyncClient(app=app, ...)`, an httpx shortcut
  removed in the httpx version this project already pins — those 9 tests
  could not execute at all. Fixed to use `ASGITransport` via the shared
  `client` fixture (matching `test_auth_roles.py`/`test_health.py`).
- **Stale credentials**: the same five files logged in as `analyst`/`qa_reviewer`/
  `admin` against `/auth/token` — neither the users nor the endpoint exist;
  the real synthetic users are `analyst01`/`qa_reviewer01`/`admin01` against
  `/auth/login`. Fixed to match `tests/auth_helpers.py`.
- **Audit trail timestamps missing timezone**: `AuditMiddleware`'s generic
  audit-log insert relied on SQLite's `datetime('now','utc')` column
  default, which returns a naive string with no UTC offset — every
  middleware-logged action (everything except `POST /executions`, which
  sets its own timestamp) failed the ALCOA+ *Contemporaneous* timestamp
  check. Now sets `created_at` explicitly via
  `datetime.now(timezone.utc).isoformat()`, consistent with the rest of
  the codebase.
- **Admin audit-log deletion was not itself logged**: `AuditMiddleware`
  intentionally skips every `/audit-log` path to avoid logging routine
  reads — which also meant `DELETE /audit-log/{id}` went unrecorded,
  contradicting the documented ALCOA+ *Enduring* / "no silent data loss"
  claim. `DELETE /audit-log/{id}` now writes its own `DELETE_AUDIT_ENTRY`
  audit row (actor, deleted record snapshot, UTC timestamp) — the same
  self-logging pattern `app/routers/executions.py` already used.
- **"Critical deviation requires root_cause" (OQ-015/URS-008) was never
  implemented**: no `root_cause` column or field existed. Added a
  `root_cause` column, a `root_cause` field on `DeviationResolve`/`Deviation`,
  and a check in `PATCH /deviations/{id}/resolve` rejecting (422) a Critical
  deviation resolved without one.
- **`Under Investigation` was a dead status**: the schema's `CHECK` constraint
  allowed it, but no endpoint could ever set it. Added
  `PATCH /deviations/{id}/status` (QA Reviewer/Admin) as an optional
  Open → Under Investigation step ahead of resolving.
- **`GET /rtm/export` did not exist** (URS-007 claimed a CSV export; `GET /rtm`
  returns JSON only). Added `GET /rtm/export` (Admin-only), flattening the
  same RTM data into one CSV row per requirement/test-case pair.
- **`ruff.toml` added**: pins the linter's rule selection so CI stays
  deterministic across ruff version upgrades, independent of this repo's
  code (see `ruff.toml` for why).

### Planned
- `POST /requirements`, `POST /test-cases`, and a risk-assessment endpoint
  (`POST /requirements/{id}/risk`, S×P×D scoring) do not exist yet —
  requirements and test cases are currently read-only, seeded from CSV.
  `docs/pq-test-protocol.md` previously described these as implemented
  and passing; that was inaccurate and has been corrected. Tracked as a
  real gap, not a documentation nit.
- Frontend dependency modernization and bundle-size optimization.
- Additional API tests for execution, RTM, and test-case routes.

---

## [1.0.0] — 2026-08-19

### Added
- Full FastAPI application with requirements, RTM, test-case/execution, phase, deviation, and audit-oriented routes.
- Synthetic portfolio-safe datasets and SQLite-backed persistence.
- React/Vite reviewer interface for dashboard, traceability, test execution, deviations, and audit review.
- Explainable rule-based deviation risk scoring.
- Automated pytest suite with a 70% minimum backend coverage gate.
- Reproducible frontend dependency resolution through `frontend/package-lock.json` and `npm ci`.
- GitHub Actions full-stack CI with backend tests, frontend production build, and Docker Compose smoke validation.
- Docker Compose deployment with FastAPI, React/Nginx frontend, and Nginx reverse proxy.
- Portfolio-safety, validation-boundary, architecture, regulatory-reference, review-checklist, and implementation documentation.

### Changed
- Updated GitHub Actions to current Node 24-compatible v7 action generations.
- CI uses least-privilege `contents: read` permissions.
- Frontend API client and reviewer views now match the implemented backend routes and response schemas.
- Deviation create/list/read responses use consistent risk fields.
- Critical deviations classify as High risk while preserving the existing Major/Minor thresholds.
- SQLite runtime paths are configurable for container execution.
- Frontend container builds with Node 22 and the committed lockfile.
- Nginx reverse-proxy configuration delegates SPA fallback to the frontend container.

### Fixed
- Corrected asynchronous SQLite reads in the summary endpoint.
- Registered the RTM router in the FastAPI application.
- Corrected audit-log and deviation-resolution frontend routes and methods.
- Added required `X-Actor` headers for auditable frontend mutations.
- Corrected test execution phase mapping between the UI and backend.
- Removed an invalid Nginx named-location `proxy_pass` that prevented the reverse proxy from starting.

### Verified release evidence
- 27/27 backend tests passed on GitHub Actions.
- Backend statement coverage: 79.37% (required minimum: 70%).
- React/Vite production build passed from the committed lockfile using `npm ci`.
- Docker Compose configuration and image builds passed.
- Docker Compose stack reached healthy state for API, frontend, and reverse proxy.
- Smoke checks passed through Nginx for the SPA, `/health`, `/api/summary`, `/api/phases`, `/api/test-cases`, `/api/deviations`, `/api/audit-log`, and `/api/rtm`.

### Safety boundary
- All bundled data is synthetic and non-confidential.
- This is a portfolio/learning artifact, not validated software and not intended for regulated production decisions.

---

## [0.1.0] — 2026-08-13

### Added
- Initial project scaffold.
- Data model design: `requirements`, `test_cases`, `test_executions`, `deviations`, `audit_log`.
- SQL schema (`sql/schema.sql`) with ALCOA+-aligned constraints.
- Dockerfile and docker-compose.yml.
- Architecture documentation (`docs/architecture.md`).
- Validation approach documentation (`docs/validation-approach.md`).
- `.gitignore` for Python, Node, SQLite, and environment files.
- `requirements.txt` with FastAPI, Pydantic, and pytest stack.
