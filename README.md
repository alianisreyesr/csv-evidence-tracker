# CSV Evidence Tracker

Portfolio-safe Computer System Validation (CSV) evidence-tracking prototype built with Python, FastAPI, React, SQLite, Docker, and Nginx. It demonstrates risk-aware requirements traceability, IQ/OQ/PQ test execution workflows, deviation lifecycle handling, and an audit-trail concept using synthetic data only.

> **Portfolio boundary:** This educational prototype is not a validated production system and must not be used for real GxP records, electronic signatures, or regulated quality decisions.

## Why this project

Regulated teams need clear, reviewable links between user requirements, risk, testing evidence, deviations, and release decisions. This project models those links in one application while keeping the dataset safe for public portfolio review.

## Capabilities

- Requirements and risk-aware traceability
- Requirements Traceability Matrix (RTM) from requirement to test evidence
- IQ/OQ/PQ test queue and execution status
- Deviation logging, investigation, follow-up, and closure workflows
- Append-oriented audit-log concept for meaningful actions
- Synthetic seed data, local Docker environment, and CI workflow

## Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React, Vite, Tailwind CSS | Dashboard and quality-workflow views |
| API | Python, FastAPI | Business logic and API endpoints |
| Data | SQLite | Local prototype persistence |
| Runtime | Docker Compose, Nginx | Local multi-service environment and reverse proxy |

See [architecture documentation](docs/architecture.md) for additional detail.

## Run locally

### Prerequisites

- Docker Desktop with Docker Compose

### Start

```bash
docker compose up --build
```

Open the frontend at `http://localhost:5173`. API documentation is available at `http://localhost:8000/docs` when the API service is running.

## Safe data handling

All requirements, test cases, execution results, deviations, names, and dates are synthetic. The repository contains no proprietary, patient, manufacturing, employer, or regulated production records.

## Portfolio walkthrough

- [3–5 minute demo guide](docs/PORTFOLIO_DEMO.md)
- [Validation boundary](docs/VALIDATION_BOUNDARY.md)
- [Review checklist](docs/REVIEW_CHECKLIST.md)
- [Validation approach](docs/validation-approach.md)

## Validation and compliance boundary

This application illustrates CSV and data-integrity concepts. It does **not** establish compliance with 21 CFR Part 11, EU Annex 11, GAMP 5, or any organization-specific quality system. A real deployment would require a formal intended-use assessment, risk assessment, validated lifecycle deliverables, security controls, controlled audit trails, electronic-signature controls where applicable, and quality-system governance.

## License

For educational and portfolio use. Adapt only after an organization completes its own intended-use, risk, validation, security, and quality-system processes.
