# Data Integrity Controls — ALCOA+

> **Scope:** This document describes how the CSV Evidence Tracker enforces each  
> ALCOA+ principle at the application layer. All data is synthetic and  
> non-confidential. This system is **not** validated for use in a regulated  
> production environment.

---

## Background

ALCOA+ is the data integrity framework referenced by the FDA (21 CFR Part 11),  
EMA, and GAMP 5. It requires that records be **A**ttributable, **L**egible,  
**C**ontemporaneous, **O**riginal, and **A**ccurate — plus the extended attributes  
Complete, Consistent, Enduring, and Available.

This tracker demonstrates each principle through concrete backend controls.

---

## ALCOA+ Principle Mapping

### A — Attributable

> *Every record must identify who created or modified it, and when.*

| Control | Implementation | File |
|---|---|---|
| JWT identity injected on every write | `get_current_user` dependency resolves the actor from the Bearer token before any state change is persisted | `app/auth.py` |
| `actor` field on audit entries | `AuditMiddleware` captures `TokenData.username` and writes it to `audit_log.actor` for every mutating request | `app/audit_middleware.py` |
| Role attribution | `audit_log` stores the HTTP method, endpoint, and status code so reviewers know what action was taken and under which role | `app/audit_middleware.py` |

**Regulatory reference:** 21 CFR Part 11 §11.10(e) — audit trails shall capture the date and time of operator entries.

---

### L — Legible

> *Records must be readable and understandable for the lifetime of the record.*

| Control | Implementation | File |
|---|---|---|
| Structured JSON responses | All API responses are typed Pydantic models serialised to JSON; no free-text blobs | `app/models.py` |
| ISO 8601 timestamps | All `created_at`, `executed_at`, and `resolved_at` fields are stored and returned as UTC ISO 8601 strings | `app/database.py` |
| Human-readable status enums | Result and severity fields use constrained string enums (`PASS`, `FAIL`, `BLOCKED`, `Critical`, `Major`, `Minor`) | `app/models.py` |
| OpenAPI documentation | FastAPI auto-generates `/docs` (Swagger UI) and `/redoc` so every field is self-documenting | `app/main.py` |

**Regulatory reference:** GAMP 5 (2nd ed.) Appendix D1 — data must remain legible throughout the retention period.

---

### C — Contemporaneous

> *Records must be created at the time the activity occurs.*

| Control | Implementation | File |
|---|---|---|
| Server-side UTC timestamps | `executed_at` and `created_at` are set by the database layer using `datetime.utcnow()` at insert time — clients cannot supply these values | `app/routers/executions.py` |
| Audit middleware timestamp | `AuditMiddleware` records the request timestamp before the endpoint handler runs, preventing post-hoc manipulation | `app/audit_middleware.py` |
| No client-supplied date fields | `ExecutionCreate`, `DeviationCreate`, and `DeviationResolve` models do not expose timestamp fields — all are server-generated | `app/models.py` |

**Regulatory reference:** 21 CFR Part 11 §11.10(e) — computer-generated, time-stamped audit trails.

---

### O — Original

> *The first recorded result must be preserved; corrections must not obscure the original.*

| Control | Implementation | File |
|---|---|---|
| Append-only audit log | `audit_log` has no `UPDATE` or `DELETE` route; the Admin-only delete endpoint is intentionally absent from the current router to demonstrate immutability | `app/routers/audit.py` |
| Deviation status transitions | Deviations move through a one-way state machine (`Open → Resolved / Accepted with Risk`); prior state is captured in the audit log before transition | `app/routers/deviations.py` |
| Previous-value capture | `audit_log.previous_value` stores the serialised prior state of any modified record | `app/audit_middleware.py` |

**Regulatory reference:** 21 CFR Part 11 §11.10(k)(2) — records shall not be deleted or overwritten without audit trail capture.

---

### A — Accurate

> *Records must be correct, truthful, and a complete representation of the observation.*

| Control | Implementation | File |
|---|---|---|
| Pydantic input validation | All request bodies are validated by Pydantic v2 before hitting the database; invalid payloads return `422 Unprocessable Entity` | `app/models.py` |
| Enum-constrained result fields | `result` is constrained to `PASS \| FAIL \| BLOCKED \| NOT_RUN`; free-text results are rejected | `app/models.py` |
| Severity constraint | `severity` is constrained to `Critical \| Major \| Minor` | `app/models.py` |
| Foreign-key enforcement | SQLite `PRAGMA foreign_keys = ON` is set on every connection to prevent orphaned test executions or deviations | `app/database.py` |

**Regulatory reference:** GAMP 5 (2nd ed.) Chapter 6 — data accuracy must be maintained through system lifecycle.

---

## Extended Attributes (+)

### Complete

Every execution record requires `test_case_id`, `phase_id`, `executed_by`, and `result`.  
Optional fields (`actual_result`, `evidence_ref`, `notes`) are nullable but always  
returned in responses so consumers can detect absence explicitly.

### Consistent

The Requirement → Test Case → Execution → Deviation chain is enforced by relational  
foreign keys. The `/rtm` endpoint exposes the full traceability matrix to verify  
requirement-to-test consistency at any point in time.

### Enduring

Data is persisted in an SQLite file (`data/tracker.db`) with no time-to-live or  
auto-purge logic. The file can be backed up as a binary artifact. For production  
deployments, migration to PostgreSQL with point-in-time recovery is recommended.

### Available

The `/health` liveness endpoint and the `/summary` dashboard endpoint allow operators  
to verify system availability and data completeness without requiring database access.

---

## Role-to-Control Matrix

The following table maps each ALCOA+ control to the role required to perform the action.

| Action | Analyst | QA Reviewer | Admin |
|---|:---:|:---:|:---:|
| Submit test execution | ✅ | ✅ | ✅ |
| Read audit log | ✅ | ✅ | ✅ |
| Approve / resolve deviation | ❌ | ✅ | ✅ |
| Modify audit log entry | ❌ | ❌ | ✅ |
| Read RTM | ✅ | ✅ | ✅ |
| Create deviation | ✅ | ✅ | ✅ |

Role enforcement is implemented via `app/dependencies.py` (`require_role()`) and  
covered by the test suite in `tests/test_auth_roles.py`.

---

## Regulatory References

| Standard | Relevant Section | Topic |
|---|---|---|
| 21 CFR Part 11 | §11.10(a) | Validation of systems |
| 21 CFR Part 11 | §11.10(e) | Audit trails |
| 21 CFR Part 11 | §11.10(d) | Access controls |
| 21 CFR Part 11 | §11.10(k) | Record retention |
| GAMP 5 (2nd ed.) | Appendix D1 | Data integrity principles |
| GAMP 5 (2nd ed.) | Chapter 6 | System lifecycle controls |
| EMA/INS/GMP/04873 | Section 4 | ALCOA+ data integrity |

---

*Document owner: Portfolio project — Alianis Reyes Reyes*  
*Last updated: 2026-08-26*  
*Classification: Non-confidential / Portfolio demonstration*
