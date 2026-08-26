# Learning Log — CSV Evidence Tracker

**Author:** Portfolio Project  
**Last Updated:** 2026-08-26  
**Purpose:** Document key decisions, regulatory rationale, risk reasoning, and lessons learned during development of the CSV Evidence Tracker portfolio project.

---

## Entry 001 — 2026-08-26 · RBAC Design Decisions

### Decision
Implemented three roles: Analyst, QA Reviewer, and Admin. Used FastAPI dependency injection (`require_role()`) at the router level rather than inside business logic.

### Why
Router-level enforcement means the access control is always applied regardless of how the endpoint is called internally. This is consistent with the defense-in-depth principle in GAMP 5 and reduces the risk of a developer accidentally bypassing a permission check by calling a helper function directly.

### Regulatory Basis
21 CFR Part 11 §11.10(d) requires that access to computer systems be limited to authorized individuals. Enforcing at the transport layer (router) rather than the service layer is a stronger control.

### Risk Considered
If roles were checked inside the service layer, a future refactor could introduce a code path that bypasses the check. Router-level enforcement eliminates this risk class entirely.

---

## Entry 002 — 2026-08-26 · Audit Trail Immutability

### Decision
Audit log entries have no UPDATE or DELETE endpoints exposed to Analyst or QA Reviewer roles. Admin DELETE is permitted but is itself logged.

### Why
ALCOA+ requires that original records be preserved (Original, Enduring). A mutable audit log would fail a 21 CFR Part 11 inspection because entries could be altered after the fact, destroying the chain of evidence.

### What I Learned
The regulatory intent is not just "don't delete data" but "prove that the data hasn't been changed." This is why even the Admin delete action is logged — so there is always a record of what happened to the audit trail itself.

### Risk Considered
Risk Score URS-002: 10 (MEDIUM). Severity is 5 (maximum) because a compromised audit trail is a critical GxP failure. Detectability is 1 (easy to detect via test) which reduces the overall score — but the severity alone justifies strong controls.

---

## Entry 003 — 2026-08-26 · Risk Scoring Model

### Decision
Used a 1–5 scale for Severity, Probability, and Detectability. Risk Score = S × P × D where lower Detectability means easier to catch (so lower score = less risk at same severity).

### Why
This is the standard FMEA-inspired model used in ICH Q9 and referenced in GAMP 5 Appendix O. The Detectability axis is inverted (1 = easy to detect, 5 = hard to detect) to reflect that a failure that is hard to detect is more dangerous.

### Alternative Considered
Used a simple 3-tier (High/Medium/Low) classification without numeric scoring. Rejected because numeric scores allow prioritization across requirements and are more defensible in an audit context.

### Key Insight
URS-001 (RBAC), URS-004 (completeness), URS-005 (timestamps), and URS-008 (severity classification) all score 24/HIGH — not because they are likely to fail, but because their failure impact (Severity=4–5) multiplied by moderate detectability makes them the highest-priority testing targets. This is exactly how a QA engineer thinks when writing a validation plan.

---

## Entry 004 — 2026-08-26 · URS vs. Functional Requirements

### What I Learned
A URS (User Requirements Specification) is written from the user/business perspective: *what the system must do* and *why it matters to quality or compliance*. It is not the same as a technical specification. The acceptance criteria in a URS should be testable without knowing how the system is implemented.

### Example
URS-001 says: "A user with Analyst role receives HTTP 403 when attempting to resolve a deviation." This is testable from the outside (black-box) and does not depend on whether roles are stored in a database, a config file, or a JWT claim.

### Regulatory Basis
GAMP 5 Chapter 6 defines URS as the foundation of the V-model: URS → Functional Spec → Design Spec → Test Protocols. Writing the URS first forces you to define "done" before writing code.

---

## Entry 005 — 2026-08-26 · RTM as a Living Document

### Decision
The RTM is maintained as both a `.csv` (machine-readable) and a `.md` (human-readable) file. Both are committed to the repository and updated with each sprint.

### Why
The CSV format allows programmatic generation and validation (e.g., a script could verify that every URS ID has at least one test row and that all test results are PASS). The Markdown format is readable in GitHub and serves as the human-facing evidence document that a hiring manager or QA director would review.

### Next Steps
- Add a GitHub Actions workflow that reads the RTM CSV and fails the build if any row has `pass_fail=FAIL` or is missing a test reference
- This would demonstrate continuous validation in a CI/CD pipeline — a differentiator for Quality Data Engineer roles

---

*This log is updated with each development sprint. It demonstrates regulatory reasoning, not just coding decisions — the difference between a developer and a CSV Analyst.*
