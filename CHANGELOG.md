# Changelog

All notable changes to this project are documented here.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
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
