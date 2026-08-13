# CSV Evidence Tracker

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-20232A?style=flat&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-audit%20trail-003B57?style=flat&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/status-in%20development-yellow?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

**GxP · CSV · 21 CFR Part 11 · ALCOA+ · GAMP 5 · IQ/OQ/PQ · Requirements Traceability**

*A portfolio-safe, full-stack prototype for Computer System Validation evidence management*

</div>

---

> **⚠️ Data boundary:** Every record, requirement, test result, and scenario in this repository is entirely fictional and synthetic. This project contains no proprietary information from any employer, client, or regulated system. It is not validated software and must not be used for actual regulated quality decisions.

---

## Overview

In regulated pharmaceutical and biotech environments, **Computer System Validation (CSV)** requires formal documentation that every system requirement has been tested and the evidence is traceable — from specification through qualification. This prototype models that process as a data engineering problem:

- **Requirements Traceability Matrix (RTM):** Link every user requirement to a test case and a result
- **IQ/OQ/PQ Test Execution Log:** Record test execution with actor, timestamp, pass/fail, and evidence reference
- **Deviation Log:** Capture and track test failures with risk classification and resolution path
- **Immutable Audit Trail:** Every data mutation is appended to a tamper-evident log (21 CFR Part 11 / ALCOA+)

**Why this matters:** Regulatory agencies (FDA, EMA) require audit-ready evidence that systems were validated per documented protocols. A Quality Data Engineer must understand how to model, store, and surface this evidence — not just document it in Word files.

---

## What It Demonstrates

| Capability | Implementation |
|---|---|
| **Requirements traceability** | RTM linking URS → test cases → execution results |
| **Validation lifecycle** | IQ / OQ / PQ phases with phase-gating logic |
| **Test execution tracking** | Pass/fail with actor, timestamp, evidence reference |
| **Deviation management** | Failure capture, risk classification, CAPA linkage |
| **Audit trail (21 CFR Part 11)** | Append-only log; actor + timestamp on every mutation |
| **Data pipeline** | Synthetic CSV seeds → SQLite with schema constraints |
| **API design** | FastAPI + Pydantic, structured responses, rate limiting |
| **Reviewer dashboard** | React + Vite — RTM view, test queue, deviation tracker |

---

## Architecture

```text
┌─────────────────────┐
│  Synthetic Seed Data │  ← URS, test cases, protocols (all fictional)
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  SQLite Database                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ requirements│  │  test_cases  │  │ phases  │ │
│  └──────┬──────┘  └──────┬───────┘  └────┬────┘ │
│         │                │               │      │
│  ┌──────▼────────────────▼───────────────▼────┐ │
│  │            test_executions (RTM)            │ │
│  └──────────────────┬──────────────────────────┘ │
│                     │                             │
│  ┌──────────────────▼──────────────────────────┐ │
│  │   deviations (failures → CAPA linkage)      │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │   audit_log (append-only, tamper-evident)   │ │
│  └─────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │     FastAPI Layer     │
         │  + AuditMiddleware    │
         └──────┬─────────┬──────┘
                │         │
   ┌────────────▼──┐  ┌───▼──────────┐
   │ React Dashboard│  │ /docs Swagger│
   │ (RTM + queue) │  │  (API UI)    │
   └───────────────┘  └──────────────┘
```

---

## Data Model

### Core Tables

```sql
-- User Requirements
requirements (id, code, title, description, category, priority, phase, status, created_at)

-- Test Cases linked to requirements (RTM)
test_cases (id, requirement_id, code, title, description, test_type, expected_result, created_at)

-- Validation Phases (IQ / OQ / PQ)
phases (id, name, description, status, started_at, completed_at)

-- Test Execution Records
test_executions (
    id, test_case_id, phase_id,
    executed_by, executed_at,     -- ALCOA+ Who + When
    result,                       -- PASS / FAIL / BLOCKED / NOT_RUN
    actual_result, evidence_ref,  -- What was observed + where is the evidence
    notes
)

-- Deviation Log (failures → investigation → resolution)
deviations (
    id, execution_id,
    title, description,
    severity,             -- Critical / Major / Minor
    risk_classification,  -- Impact on validation integrity
    status,               -- Open / Under Investigation / Resolved / Accepted
    capa_ref,             -- Reference to corrective action
    created_at, resolved_at
)

-- Immutable Audit Log (21 CFR Part 11 / ALCOA+)
audit_log (
    id, actor, action, table_affected, record_id,
    previous_value, new_value,
    ip_address, user_agent,
    created_at  -- UTC, server-generated
)
```

---

## API Endpoints (Planned)

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Service state + data boundary confirmation |
| `/requirements` | GET/POST | List or create requirements |
| `/requirements/{id}` | GET | Requirement detail with linked test cases (RTM view) |
| `/test-cases` | GET/POST | List or create test cases |
| `/test-cases/{id}/execute` | POST | Record test execution with actor, result, evidence ref |
| `/phases` | GET | IQ/OQ/PQ phases and completion status |
| `/deviations` | GET/POST | Deviation log with status filter |
| `/deviations/{id}/resolve` | POST | Record resolution or CAPA reference |
| `/rtm` | GET | Full Requirements Traceability Matrix export |
| `/audit-log` | GET | Immutable audit trail, newest-first |
| `/summary` | GET | Counts: total reqs, test coverage %, open deviations |

---

## Repository Structure

```text
csv-evidence-tracker/
├── app/
│   ├── main.py               ← FastAPI app entry point
│   ├── database.py           ← SQLite connection + seed loader
│   ├── models.py             ← Pydantic models
│   ├── routers/
│   │   ├── requirements.py
│   │   ├── test_cases.py
│   │   ├── executions.py
│   │   ├── deviations.py
│   │   ├── phases.py
│   │   └── audit.py
│   ├── audit_middleware.py   ← Logs all mutating HTTP requests
│   └── scoring.py            ← Deviation risk classification rules
├── data/
│   ├── requirements.csv      ← Synthetic URS (fictional)
│   ├── test_cases.csv        ← Synthetic test cases
│   ├── executions.csv        ← Synthetic execution records
│   └── deviations.csv        ← Synthetic deviation log
├── frontend/                 ← Vite + React dashboard
│   ├── src/
│   │   ├── pages/
│   │   │   ├── RTMView.jsx       ← Traceability matrix
│   │   │   ├── TestQueue.jsx     ← Pending executions
│   │   │   ├── DeviationLog.jsx  ← Deviation tracker
│   │   │   └── AuditLog.jsx
│   │   └── components/
├── sql/
│   ├── schema.sql            ← Full DDL with constraints
│   └── indexes.sql
├── tests/
│   ├── test_requirements.py
│   ├── test_executions.py
│   ├── test_deviations.py
│   ├── test_audit.py
│   └── test_rtm.py
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   └── validation-approach.md
├── CHANGELOG.md
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Roadmap

- [x] Project scaffold and data model design
- [ ] SQLite schema implementation
- [ ] Synthetic seed data generation (CSV → SQLite)
- [ ] FastAPI backend — requirements and test case endpoints
- [ ] FastAPI backend — execution recording with audit trail
- [ ] FastAPI backend — deviation log and resolution
- [ ] RTM export endpoint (JSON + CSV)
- [ ] React dashboard — RTM view
- [ ] React dashboard — test execution queue
- [ ] React dashboard — deviation tracker
- [ ] Automated test suite
- [ ] GitHub Actions CI
- [ ] Docker support

---

## Related Portfolio Projects

| Project | Focus | Repo |
|---|---|---|
| **Quality Deviation Risk Monitor** | Risk scoring, explainable prioritization, audit trail | [→ View](https://github.com/alianisreyesr/quality-deviation-risk-monitor) |
| **Student Assembly Registration** | Role-based access, institutional validation, PHP + MySQL | *In progress* |

---

<div align="center">

**Built by [Alianis Reyes-Reyes](https://www.linkedin.com/in/alianis-reyes-reyes/)** — Information Systems @ UPRM · Former Eli Lilly Intern

*Building trusted systems from data to decision.*

</div>
