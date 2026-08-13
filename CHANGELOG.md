# Changelog

All notable changes to this project are documented here.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Planned
- SQLite schema implementation (`sql/schema.sql`)
- Synthetic seed data CSV files
- FastAPI application scaffold (`app/main.py`)
- Requirements and test case endpoints
- Test execution recording with ALCOA+ audit trail
- Deviation log and resolution tracking
- RTM export endpoint
- React reviewer dashboard
- Automated test suite
- GitHub Actions CI
- Docker support

---

## [0.1.0] — 2026-08-13

### Added
- Initial project scaffold
- Data model design: `requirements`, `test_cases`, `test_executions`, `deviations`, `audit_log`
- SQL schema (`sql/schema.sql`) with ALCOA+ aligned constraints
- Dockerfile and docker-compose.yml
- Architecture documentation (`docs/architecture.md`)
- Validation approach documentation (`docs/validation-approach.md`)
- `.gitignore` for Python, Node, SQLite, and environment files
- `requirements.txt` with FastAPI, Pydantic, pytest stack
