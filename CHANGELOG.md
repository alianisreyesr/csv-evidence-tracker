# Changelog

All notable changes to this project are documented here.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Full FastAPI application with requirements, RTM, test-case/execution, phase, deviation, and audit-oriented routes.
- Synthetic portfolio-safe datasets and SQLite-backed persistence.
- React/Vite reviewer interface for dashboard, traceability, test execution, deviations, and audit review.
- Automated pytest suite covering API health, requirements, phases, deviations, scoring, and audit behavior.
- GitHub Actions CI with backend coverage enforcement and frontend production-build validation.
- Docker Compose and Nginx-based local full-stack execution.
- Portfolio-safety, validation-boundary, architecture, regulatory-reference, review-checklist, and implementation documentation.

### Changed
- Updated GitHub Actions to current Node 24-compatible action generations.
- CI now uses least-privilege `contents: read` permissions.
- CI now enforces a minimum 70% backend coverage threshold and verifies that the frontend builds successfully.

### Release blockers for 1.0.0
- Commit a frontend package-manager lockfile and switch CI from `npm install` to `npm ci` for reproducible dependency resolution.
- Confirm the hardened CI is green on the release candidate branch.
- Record exact backend test count and coverage from CI in the README/release evidence.
- Verify Docker Compose quick-start commands against the release candidate.
- Create final v1.0.0 release notes and tag only after the evidence above is complete.

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
