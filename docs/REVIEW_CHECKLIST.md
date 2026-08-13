# Review Checklist

## Scope and data

- [ ] README identifies the application as a portfolio prototype.
- [ ] All data is synthetic; no proprietary, patient, manufacturing, employee, or regulated records are included.
- [ ] Intended use is limited to demonstration, learning, and portfolio review.

## Traceability

- [ ] Each requirement has a unique identifier.
- [ ] Requirement-to-test links are inspectable in the RTM.
- [ ] Uncovered requirements or incomplete execution evidence are visible as gaps.
- [ ] Requirement, test, and execution status terminology is consistent.

## Test execution

- [ ] IQ/OQ/PQ records clearly display phase and status.
- [ ] Outcomes distinguish pass, fail, blocked, and not-run states where applicable.
- [ ] Failed or blocked tests can be associated with a deviation or follow-up action.

## Deviations

- [ ] Each deviation has an identifier, description, severity or impact field, owner, and lifecycle status.
- [ ] Investigation and follow-up context are available before closure.
- [ ] Open deviations are visually distinguishable from closed records.

## Auditability

- [ ] Audit-log examples identify an action, timestamp, and affected object.
- [ ] The UI and documentation do not claim immutable, compliant, or production-grade audit trails.
- [ ] The validation boundary is visible to reviewers.

## Portfolio quality

- [ ] Local setup steps are reproducible.
- [ ] Screens and labels avoid real-company, product, or personal data.
- [ ] The demo narrative accurately states capabilities and limitations.
- [ ] Portfolio language matches `VALIDATION_BOUNDARY.md`.