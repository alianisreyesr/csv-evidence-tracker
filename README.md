# CSV Evidence Tracker

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-20232A?style=flat&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-audit%20trail-003B57?style=flat&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

**GxP · CSV · 21 CFR Part 11 · ALCOA+ · Requirements Traceability · IQ/OQ/PQ**

*A portfolio-safe Computer System Validation (CSV) evidence tracker*

[Quick Start](#quick-start) · [Architecture](docs/architecture.md) · [Regulatory References](docs/REGULATORY_REFERENCES.md) · [Portfolio Safety](docs/PORTFOLIO_SAFETY.md) · [Validation Boundary](docs/VALIDATION_BOUNDARY.md)

</div>

---

> **⚠️ Data Boundary:** Every record is entirely fictional/synthetic. This repository contains no proprietary information, employer data, or regulated records. It is **not** validated software and must not be used for regulated quality decisions.

---

## What This Is

A full-stack prototype that demonstrates how a Quality / CSV professional approaches **evidence collection and traceability** in a regulated environment:

- Requirements → Test Cases → Executions (IQ / OQ / PQ)
- Deviation logging linked to test evidence
- Append-oriented audit trail concepts aligned with 21 CFR Part 11 and ALCOA+
- Clear separation between a technical demonstration and a validated production system

**Built with:** Python · FastAPI · React (Vite) · SQLite · Docker Compose · Nginx

---

## Skills Demonstrated

| Domain | What This Project Shows |
|--------|-------------------------|
| **Requirements Traceability** | RTM linking requirements → test cases → executions |
| **IQ / OQ / PQ Workflows** | Phase-based test execution and status tracking |
| **Deviation Management** | Logging, scoring, and review-oriented deviation records |
| **Audit Trail Concepts** | Structured, reviewable records with actor and timestamp awareness |
| **API Engineering** | FastAPI routers, Pydantic models, clean separation of concerns |
| **Frontend for Reviewers** | React dashboard (Dashboard, RTM, Test Queue, Deviations, Audit Log) |
| **Containerization** | Docker + docker-compose + Nginx reverse proxy |
| **Documentation Discipline** | Portfolio safety, validation boundary, **FDA/MHRA/PIC/S/EU references**, architecture, review checklist |

---

## Architecture (high level)

```text
┌────────────────────┐
│  Synthetic CSVs    │  ← requirements, test cases, executions, deviations, phases
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐     ┌──────────────────────────┐
│  SQLite + schema   │────▶│  FastAPI routers         │
│  (constraints)     │     │  requirements · rtm      │
└────────────────────┘     │  test_cases · executions │
                           │  phases · deviations     │
                           │  audit                   │
                           └────────────┬─────────────┘
                                        │
              ┌─────────────────────────┼──────────────────┐
              ▼                         ▼                  ▼
   ┌──────────────────┐      ┌──────────────────┐  ┌─────────────┐
   │  React Frontend  │      │  Audit-oriented  │  │  /docs      │
   │  (Vite + Tailwind)│     │  evidence views  │  │  (Swagger)  │
   └──────────────────┘      └──────────────────┘  └─────────────┘
```

See [docs/architecture.md](docs/architecture.md) · [docs/validation-approach.md](docs/validation-approach.md) · [docs/REGULATORY_REFERENCES.md](docs/REGULATORY_REFERENCES.md).

---

## Quick Start

### Option A — Docker (recommended)

```bash
git clone https://github.com/alianisreyesr/csv-evidence-tracker.git
cd csv-evidence-tracker
docker compose up --build
```

- Frontend / app: check the ports defined in `docker-compose.yml` and `nginx`
- API docs: typically available via the FastAPI service (`/docs`)

### Option B — Local (Python + Node)

```bash
# Backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install && npm run dev
```

> Never load production, proprietary, personal, or regulated data into this prototype.

---

## Main Capabilities

| Area | Endpoints / Views |
|------|-------------------|
| Requirements | List / detail of requirements |
| RTM | Requirements ↔ Test Cases traceability |
| Test Cases & Executions | IQ/OQ/PQ execution tracking |
| Phases | Validation phase status |
| Deviations | Deviation log + risk-oriented views |
| Audit | Reviewable audit-oriented log |

Interactive OpenAPI docs are available when the API is running (`/docs` and `/redoc`).

---

## Repository Structure

```text
csv-evidence-tracker/
├── app/                  # FastAPI application
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── scoring.py
│   ├── audit_middleware.py
│   └── routers/
├── frontend/
├── data/
├── sql/
├── docs/                 # safety, architecture, REGULATORY_REFERENCES, checklists
├── tests/
├── nginx/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Portfolio Safety & Governance

- **Synthetic data only** — [docs/PORTFOLIO_SAFETY.md](docs/PORTFOLIO_SAFETY.md)
- **Validation boundary** — [docs/VALIDATION_BOUNDARY.md](docs/VALIDATION_BOUNDARY.md)
- **Regulatory context (FDA, MHRA, PIC/S, EU, CSA)** — [docs/REGULATORY_REFERENCES.md](docs/REGULATORY_REFERENCES.md)
- Review checklist — [docs/REVIEW_CHECKLIST.md](docs/REVIEW_CHECKLIST.md)

This is a **learning and portfolio artifact**. A real validated system would additionally require formal IQ/OQ/PQ protocols, approved SOPs, change control, role-based access, and controlled environments.

---

## Related Portfolio Project

| Project | Focus |
|---------|--------|
| [Quality Deviation Risk Monitor](https://github.com/alianisreyesr/quality-deviation-risk-monitor) | Explainable risk scoring, append-only audit trail, reviewer queue |

---

## Contributing & Security

- Use the issue and pull-request templates (they include data-safety and governance prompts).
- See [SECURITY.md](SECURITY.md) for responsible disclosure guidance.

---

<div align="center">

**Built by [Alianis Reyes-Reyes](https://www.linkedin.com/in/alianis-reyes-reyes/)**

Information Systems @ UPRM · Former Eli Lilly Intern

*Every design decision asks: would this evidence still be trustworthy under inspection?*

</div>
