# Case study: executable CSV evidence traceability

## Problem

Validation evidence becomes difficult to audit when requirements, test cases, executions, deviations, and approvals are maintained as disconnected documents.

## Users and outcome

Validation engineers connect requirements to IQ/OQ/PQ-style tests, executors record results, and reviewers inspect coverage and deviations. The prototype makes missing links and incomplete evidence visible through one workflow.

## Engineering decisions

- FastAPI enforces evidence relationships and exposes a documented API.
- React provides a reviewer-facing traceability experience.
- SQLite and synthetic seed records keep the demo deterministic and portfolio-safe.
- CI verifies backend coverage, frontend builds, and a Docker Compose smoke path.

## Evidence

The repository includes architecture, validation-boundary, safety, regulatory-reference, demo, and screenshot documentation together with automated tests and CI.

## Boundary

The records are demonstration evidence, not approved validation deliverables. Production use would require controlled identities, signatures where applicable, approved procedures, validated infrastructure, formal release records, and organizational quality governance.
