# CSV Evidence Tracker

<div align="center">

[![CI](https://github.com/alianisreyesr/csv-evidence-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/alianisreyesr/csv-evidence-tracker/actions/workflows/ci.yml)
[![CodeQL](https://github.com/alianisreyesr/csv-evidence-tracker/actions/workflows/codeql.yml/badge.svg)](https://github.com/alianisreyesr/csv-evidence-tracker/actions/workflows/codeql.yml)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![API](https://img.shields.io/badge/API-v1.3.0-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-20232A?style=flat&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-evidence%20store-003B57?style=flat&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

**GxP · CSV · ALCOA+ · RBAC · Full-Stack Auth · Requirements Traceability · IQ/OQ/PQ**

*A portfolio-safe full-stack prototype for traceable validation evidence.*

[Screenshots](#portfolio-preview) · [Quick Start](#quick-start) · [Demo flow](#demo-flow) · [Case study](docs/CASE_STUDY.md) · [Demo guide](docs/PORTFOLIO_DEMO.md) · [Architecture](docs/architecture.md) · [Validation Boundary](docs/VALIDATION_BOUNDARY.md) · [Data Integrity Controls](docs/data-integrity-controls.md)

</div>

---

> **Data boundary:** All bundled records are fictional/synthetic. This repository contains no proprietary, employer, patient, personal, or regulated production data. It is **not validated software** and must not be used to make regulated quality decisions.

## Portfolio preview

| Validation dashboard | Requirements traceability matrix |
|---|---|
| ![Synthetic validation evidence dashboard](docs/assets/dashboard.png) | ![Synthetic requirements traceability matrix](docs/assets/rtm.png) |

See the [case study](docs/CASE_STUDY.md) for the business problem, users, decisions, evidence, and production boundary.

## Why this project exists

Computer System Validation work is not just about storing requirements or test results. The evidence needs to remain **traceable, reviewable, attributable, and reproducible**.

CSV Evidence Tracker demonstrates that workflow as an executable system:

```mermaid
flowchart LR
    REQ[Requirement] --> TC[Test Case]
    TC --> EX[Execution]
    EX --> DEV[Deviation]
    DEV --> AUD[Audit Evidence]
    REQ -.->|Requirements Traceability| AUD
```

It combines a reviewer-facing UI with JWT authentication, role-based access control, structured SQLite persistence, explainable deviation risk scoring, CI checks, and a containerized deployment path — all visible end-to-end through the browser.

## What it demonstrates

| Area | Evidence in the repository |
|---|---|
| Requirements traceability | RTM linking requirements to test cases and latest executions |
| IQ / OQ / PQ workflow | Phase-aware test evidence and execution records |
| Deviation management | Create, review, resolve, CAPA reference, and explainable risk classification |
| **Role-based access control** | **JWT authentication with Analyst / QA Reviewer / Admin roles enforced at the router level (21 CFR Part 11 §11.10(d))** |
| **Full-stack auth integration** | **React LoginPage · AuthContext · ProtectedRoute · role badge visible in the UI sidebar** |
| **ALCOA+ data integrity** | **Each principle mapped to its implementation control — see [data-integrity-controls.md](docs/data-integrity-controls.md)** |
| Audit concepts | Actor-aware, append-oriented audit records; read-only for Analyst, delete restricted to Admin |
| API engineering | FastAPI routers, Pydantic schemas, SQLite persistence, health/summary endpoints |
| Reviewer experience | React/Vite dashboard, RTM, test queue, deviations, phases, and audit views |
| Reproducible builds | Committed npm lockfile, `npm ci`, GitHub Actions coverage gate |
| Runtime verification | Docker Compose build/start/health + reverse-proxy smoke tests in CI |
| Governance | Explicit portfolio-safety and validation-boundary documentation |

## CI/CD Pipeline

Every commit to `main` and every pull request triggers a three-stage pipeline:

| Stage | What it checks | Gate |
|---|---|---|
| **Backend** | `ruff` lint · `mypy` type-check · `pytest` with ≥70% coverage | ❌ Blocks merge if coverage < 70% |
| **Frontend** | `npm ci` reproducible install · Vite production build | ❌ Blocks merge if build fails |
| **Docker** | `docker compose up --build` · `/health` smoke test · Swagger docs accessible | ❌ Blocks merge if stack fails to start |
| **CodeQL** | Python + JavaScript security scanning (weekly + on push) | Advisory |

## Authentication & Role-Based Access Control

v1.1.0 introduced JWT-based authentication and three roles aligned with a typical CSV review workflow. v1.2.0 closes the loop by integrating the auth flow into the React/Vite UI.

| Role | Permissions |
|---|---|
| **Analyst** | Submit executions · Read deviations · Read audit log |
| **QA Reviewer** | All Analyst permissions + approve / resolve deviations |
| **Admin** | All QA Reviewer permissions + delete audit log entries |

Role enforcement is applied at the FastAPI dependency layer via `require_role()` in `app/dependencies.py`. No endpoint bypass is possible without a valid JWT signed by the server secret.

```bash
# Obtain a token (synthetic portfolio credentials)
curl -X POST http://localhost/api/auth/login \
  -d "username=qa_reviewer01&password=QAReview01!"

# Use the token on a protected endpoint
curl -H "Authorization: Bearer <token>" \
  http://localhost/api/deviations
```

All RBAC controls are covered by the automated test suite in [`tests/test_auth_roles.py`](tests/test_auth_roles.py) (13 test cases, including explicit 401 and 403 negative tests).

## Frontend Authentication

v1.2.0 integrates the JWT auth flow directly into the React/Vite reviewer interface:

| Component | Location | Responsibility |
|---|---|---|
| `AuthContext` | `src/context/AuthContext.jsx` | Global token + user state; `login()`, `logout()`, sessionStorage persistence |
| `LoginPage` | `src/pages/LoginPage.jsx` | Login form with one-click role selector for portfolio demos |
| `ProtectedRoute` | `src/components/ProtectedRoute.jsx` | Redirects unauthenticated users to `/login`; preserves intended destination |
| `RoleBadge` | `src/components/RoleBadge.jsx` | Color-coded role pill displayed in the sidebar |

The sidebar footer permanently shows the authenticated user's full name, username, and role badge. A **Sign out** button clears the session and returns to the login screen.

```
Analyst      → blue pill   🔵
QA Reviewer  → purple pill 🟣
Admin        → amber pill  🟡
```

Session is stored in `sessionStorage` — survives page refresh, cleared when the tab is closed (portfolio-appropriate scope; a production system would use secure HttpOnly cookies and a token-refresh endpoint).

## Demo flow

After `docker compose up --build`, open `http://localhost/`:

1. The app redirects to `/login` (all routes are protected)
2. Click one of the **role quick-select buttons** to pre-fill credentials — no docs needed
3. Sign in → land on `/dashboard` with the role badge visible in the sidebar
4. Navigate to **Deviations** and attempt to resolve one — only QA Reviewer / Admin can
5. Navigate to **Audit Log** and attempt to delete an entry — only Admin can
6. Click **Sign out** → session cleared, back to `/login`

## Verified evidence

The release candidate is validated by GitHub Actions rather than README-only claims:

- **Backend tests passing** with a **70% minimum coverage gate**
- **13 RBAC-specific tests** covering unauthenticated, forbidden, and authorised scenarios
- Frontend dependencies installed reproducibly with **`npm ci`**
- React/Vite production build passing
- Docker Compose configuration validated and service images built from scratch
- API, frontend, and reverse proxy reach healthy state
- Reverse-proxy smoke checks pass for all public and authenticated routes

The synthetic seed dataset contains **12 requirements, 21 test cases, and 18 recorded executions**. Those are demonstration records, not production validation evidence.

## Architecture

```mermaid
flowchart TD
    SEED[Synthetic CSV seed data]
    DB[(SQLite evidence store)]
    AUTH["JWT Auth layer\nAnalyst · QA Reviewer · Admin"]
    API["FastAPI API\nrequirements · RTM\ntests · executions\nphases · deviations\naudit · summary"]
    NGINX["Nginx reverse proxy\n/api/* → FastAPI\n/* → frontend"]
    UI["React/Vite reviewer interface\nLoginPage · ProtectedRoute\nRole badge · Dashboard · RTM\nDeviations · Audit Log"]

    SEED --> DB
    DB --> API
    AUTH -->|require_role()| API
    API -->|/api/*| NGINX
    NGINX --> UI
    UI -->|POST /auth/login| AUTH
```

See [architecture](docs/architecture.md), [validation approach](docs/validation-approach.md), [regulatory references](docs/REGULATORY_REFERENCES.md), and [data integrity controls](docs/data-integrity-controls.md).

## Quick Start

### Docker Compose — recommended

Prerequisites: Docker with Compose support.

```bash
git clone https://github.com/alianisreyesr/csv-evidence-tracker.git
cd csv-evidence-tracker
docker compose up --build
```

Then open:

- Application + Login: `http://localhost/`
- Health check: `http://localhost/health`
- API docs (Swagger UI): `http://localhost/docs`

Stop the stack with:

```bash
docker compose down
```

### Local development

```bash
# Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Run tests locally:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

## Core API surface

| Endpoint | Purpose | Min. Role |
|---|---|---|
| `POST /auth/login` | Obtain Bearer JWT | — |
| `GET /auth/me` | Current user identity | Any authenticated |
| `GET /health` | Runtime health + version + DB status | — |
| `GET /summary` | Validation evidence summary | — |
| `GET /phases` | IQ/OQ/PQ phase state | Any authenticated |
| `GET /requirements` | Requirements evidence | Any authenticated |
| `GET /test-cases` | Test cases + requirement context | Any authenticated |
| `GET/POST /executions` | Test execution evidence | Any authenticated |
| `GET/POST /deviations` | Deviation workflow + explainable risk | Any authenticated |
| `PATCH /deviations/{id}/resolve` | Controlled resolution action | **QA Reviewer / Admin** |
| `GET /audit-log` | Reviewable audit trail | Any authenticated |
| `DELETE /audit-log/{id}` | Remove audit entry | **Admin only** |
| `GET /rtm` | Requirements traceability matrix | Any authenticated |
| `GET /rtm/export` | RTM export as CSV | **Admin** |

## Explainable deviation risk

Deviation risk is intentionally rule-based rather than opaque. The API returns:

- `risk_score`
- `risk_classification`
- `contributing_reasons`

Critical severity is classified as High, while recurrence, overdue state, severity, and ownership contribute transparent score reasons. This makes reviewer decisions inspectable in a portfolio context.

## Repository structure

```mermaid
flowchart TB
  R["csv-evidence-tracker"]
  R --> A["app — FastAPI application and scoring"]
  A --> AR["routers — requirements, tests, deviations, audit, RTM, and auth"]
  R --> F["frontend — React and Vite reviewer UI"]
  F --> FC["context/ — AuthContext"]
  F --> FP["pages/ — LoginPage + app pages"]
  F --> FM["components/ — ProtectedRoute · RoleBadge · Layout"]
  R --> D["data — synthetic CSV seed records"]
  R --> S["sql — SQLite schema"]
  R --> O["docs — architecture, safety, ALCOA+ controls, and validation boundary"]
  R --> T["tests — backend automated tests incl. RBAC suite"]
  R --> N["nginx — integrated reverse proxy"]
  R --> G[".github/workflows — CI (backend · frontend · Docker) + CodeQL"]
  R --> P["Docker and changelog files"]
```

## Validation and regulatory boundary

This project demonstrates engineering and evidence-management concepts relevant to regulated environments, but it does **not** claim to be a validated GxP system.

A production implementation would require substantially more, including approved procedures, controlled infrastructure, formal validation deliverables, identity/access controls, electronic-signature controls where applicable, backup/recovery qualification, security controls, change control, operational monitoring, and organization-specific quality governance.

Reference documents:

- [Portfolio Safety](docs/PORTFOLIO_SAFETY.md)
- [Validation Boundary](docs/VALIDATION_BOUNDARY.md)
- [Regulatory References](docs/REGULATORY_REFERENCES.md)
- [Review Checklist](docs/REVIEW_CHECKLIST.md)
- [Data Integrity Controls (ALCOA+)](docs/data-integrity-controls.md)

## Engineering notes

**v1.3.0** adds the full CI/CD pipeline (backend lint/test/coverage · frontend build · Docker smoke test · CodeQL), IQ/OQ/PQ protocols, and the complete test suite scaffold covering all URS.

**v1.2.0** integrates the JWT auth flow into the React/Vite UI: `LoginPage` with one-click role selector for demos, `AuthContext` for global token state with sessionStorage persistence, `ProtectedRoute` for route-level access control, and a `RoleBadge` component in the sidebar. The full RBAC story is now visible end-to-end through the browser without reading documentation.

**v1.1.0** added JWT-based RBAC with role enforcement at the router level, a 13-test RBAC suite, and full ALCOA+ documentation mapping each principle to its implementation.

---

## Regulated Portfolio Ecosystem

| Project | Domain Focus | Status |
|---|---|---|
| **[Quality Deviation Risk Monitor](https://github.com/alianisreyesr/quality-deviation-risk-monitor)** | Deviation prioritization & explainable risk scoring | ✅ Active · 112 tests |
| **[GxP Change Control](https://github.com/alianisreyesr/gxp-change-control)** | Controlled change lifecycle & approvals | ✅ Active · 68 tests |
| **[Data Integrity Case File](https://github.com/alianisreyesr/data-integrity-case-file)** | ALCOA+ investigation, CAPA readiness, local AI triage | ✅ Active |
| **[CSA Assurance Planner](https://github.com/alianisreyesr/csa-assurance-planner)** | Risk-based software assurance planning, FDA CSA alignment | ✅ Active |
| **[GxP Batch Data Pipeline](https://github.com/alianisreyesr/gxp-batch-data-pipeline)** | Batch manufacturing pipeline — DuckDB · dbt · quality gates | ✅ Active · 12 tests |

---

<div align="center">

**Built by [Alianis Reyes-Reyes](https://www.linkedin.com/in/alianis-reyes-reyes/)**

Information Systems @ UPRM · Eli Lilly Tech@Lilly Alumni

*Every design decision asks: would this evidence still be trustworthy under inspection?*

</div>
