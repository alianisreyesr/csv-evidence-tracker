# CSV Evidence Tracker

A portfolio-safe Computer System Validation (CSV) evidence tracker demonstrating requirements traceability, IQ/OQ/PQ test execution, deviation logging, and an audit-trail-oriented workflow using Python, FastAPI, React, SQLite, and synthetic data.

## Portfolio safety

This repository uses **synthetic, non-production data only**. It is a portfolio prototype, not a validated GxP system, and is not a substitute for approved procedures, validation documentation, production controls, or regulated decision-making. See [Portfolio Safety and Intended Use](docs/PORTFOLIO_SAFETY.md).

## What it demonstrates

- Requirements-to-test traceability
- Illustrative IQ/OQ/PQ execution workflows
- Deviation logging and review-oriented evidence
- Audit-trail concepts and structured recordkeeping
- A clear boundary between a technical prototype and validated production software

## Technology

- Python and FastAPI
- React frontend
- SQLite for local demonstration data
- Docker Compose and Nginx for local containerized setup
- Synthetic test and example data

## Local setup

```bash
git clone https://github.com/alianisreyesr/csv-evidence-tracker.git
cd csv-evidence-tracker
docker compose up --build
```

Review the project files and environment configuration before running locally. Never use production, proprietary, personal, or regulated records.

## Governance principles demonstrated

- Synthetic-data boundary for public demonstrations
- Traceability from requirements through test evidence
- Reviewable records and audit-trail-oriented design
- Human oversight and explicit prototype limitations

## Contributing

Use the issue and pull-request templates to document validation, data safety, and governance considerations.

## Security

See [SECURITY.md](SECURITY.md) for responsible disclosure and repository safety guidance.
