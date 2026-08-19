# CSV Evidence Tracker Implementation Roadmap

> **Authorship:** This roadmap was designed and created by Alianis Reyes Reyes for the CSV Evidence Tracker portfolio project. It distinguishes the current demonstration implementation from proposed future enhancements.

## Purpose

This roadmap keeps the portfolio documentation accurate by separating implemented functionality from the target CSV evidence-tracking model. It does not represent a production validation plan.

## Current Demonstration Implementation

The current repository includes a FastAPI backend, React frontend, SQLite persistence, Docker Compose deployment assets, audit middleware, risk-scoring logic, and automated tests covering health, requirements, phases, deviations, audit behavior, and scoring.

| Area | Current Demonstration Capability |
|---|---|
| Requirements | Requirement-oriented records and API behavior are represented and covered by tests. |
| Test lifecycle | Phase and test-oriented workflow behavior is represented and covered by tests. |
| Deviations | Demonstration deviation handling is represented and covered by tests. |
| Audit trail | Audit-middleware behavior and audit-oriented records are represented and covered by tests. |
| Risk scoring | Demonstration scoring logic is implemented and tested. |
| User interface | React user interface is delivered through the containerized application architecture. |
| Data scope | The project is restricted to synthetic, non-sensitive demonstration data. |

## Proposed Target Model

The following structures are documented in `data-dictionary.md` and `entity-lifecycle-flow.md` as proposed extensions. They must not be described as implemented until corresponding migrations, models, API routes, UI workflows, tests, and documentation are present.

| Proposed Capability | Intended Outcome | Suggested Completion Evidence |
|---|---|---|
| User and role model | Demonstrate role-aware actions for authors, testers, reviewers, and approvers. | User table/model, authorization rules, seed users, tests, and UI role indicators. |
| Requirement-to-test traceability | Link each requirement to one or more test cases. | Association table, traceability API, matrix UI, and coverage tests. |
| Risk assessment | Relate hazards, mitigations, and residual risk to requirements. | Risk model, scoring rules, API/UI workflow, and risk-calculation tests. |
| Controlled test cases | Version test procedures separately from their executions. | Test-case model, version snapshot, approval status, and regression tests. |
| Test execution records | Preserve the actual result, executor, timestamps, and retest history. | Execution model, workflow rules, evidence links, and lifecycle tests. |
| Evidence management | Attach synthetic evidence metadata and integrity hashes. | Evidence model, attachment/reference policy, checksum validation, and tests. |
| Approval workflow | Capture demonstration review and approval decisions. | Approval model, role checks, immutable decision records, and tests. |
| Expanded audit events | Record state transitions for all controlled entities. | Append-only event policy, before/after state capture, and audit tests. |

## Recommended Delivery Sequence

1. Implement the requirement-to-test traceability relationship and a traceability matrix view.
2. Add versioned test cases and immutable test-execution snapshots.
3. Add evidence metadata, including synthetic-data flags and optional SHA-256 checksums.
4. Add risk assessment fields and risk-score calculation tied to requirements.
5. Add a demonstration approval workflow with clearly labeled non-production limitations.
6. Expand audit coverage for controlled lifecycle transitions.
7. Update the data dictionary, architecture diagram, screenshots, README, and test suite after each completed increment.

## Completion Criteria

A proposed capability is considered implemented only when all of the following are complete:

- Database persistence or clearly defined storage behavior.
- Backend model and API behavior.
- Frontend workflow or documented API-only interface.
- Automated tests for successful, invalid, and boundary cases.
- Audit-event behavior where the workflow changes controlled data.
- Documentation updated to remove the `Proposed` label.

## Portfolio Safety

All roadmap items remain portfolio demonstrations. They must use synthetic data and must not be represented as a validated production system, electronic-signature solution, or evidence of compliance with 21 CFR Part 11.
