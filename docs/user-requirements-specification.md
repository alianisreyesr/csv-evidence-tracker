# User Requirements Specification (URS)

**System:** CSV Evidence Tracker  
**Version:** 1.0  
**Date:** 2026-08-26  
**Author:** Portfolio Project — Synthetic GxP Demo  
**Status:** Approved (simulated)

> ⚠️ This is a portfolio project. All data is synthetic. This document is not part of a validated GxP system.

---

## 1. Purpose

This URS defines the verifiable functional and regulatory requirements for the CSV Evidence Tracker system, a web-based tool for managing CSV validation evidence, audit trails, and deviation records in a simulated pharmaceutical quality environment.

---

## 2. Scope

The system covers:
- User authentication and role-based access control
- Deviation record creation, review, and resolution
- Immutable audit trail generation
- Requirements Traceability Matrix (RTM) export
- Data integrity enforcement (ALCOA+)

---

## 3. User Requirements

### URS-001 — Role-Based Access Control
**Statement:** The system shall restrict access to sensitive operations based on user role. Analysts may create and view records. QA Reviewers may additionally resolve deviations. Admins have full access including audit log deletion.  
**Acceptance Criteria:** A user with Analyst role receives HTTP 403 when attempting to resolve a deviation or delete an audit log entry.  
**Regulatory Basis:** 21 CFR Part 11 §11.10(d) — Access controls; GAMP 5 Category 4.

---

### URS-002 — Audit Trail — Automatic and Immutable
**Statement:** The system shall automatically record every create, update, and delete action on deviation records, including the user identity, timestamp, action type, and before/after values. Audit log entries shall not be modifiable by Analyst or QA Reviewer roles.  
**Acceptance Criteria:** After any deviation action, an audit log entry exists with `user_id`, `action`, `timestamp`, and `record_id`. Attempts to delete audit log entries as Analyst or QA Reviewer return HTTP 403.  
**Regulatory Basis:** 21 CFR Part 11 §11.10(e) — Audit trails; ALCOA+ (Attributable, Contemporaneous, Original).

---

### URS-003 — Deviation Record Lifecycle
**Statement:** The system shall support deviation records progressing through defined states: `open → under_review → resolved`. State transitions shall be logged and shall enforce valid transitions only.  
**Acceptance Criteria:** A deviation cannot transition from `open` directly to `resolved`. Each transition is recorded in the audit log with actor and timestamp.  
**Regulatory Basis:** GAMP 5 §10 — Deviation and CAPA management.

---

### URS-004 — Data Completeness Validation
**Statement:** The system shall reject deviation records that are missing required fields: `title`, `description`, `severity`, `detected_date`, and `product_id`.  
**Acceptance Criteria:** POST `/deviations` with a missing required field returns HTTP 422 with a field-level error message.  
**Regulatory Basis:** ALCOA+ (Complete); FDA Data Integrity Guidance 2018.

---

### URS-005 — Timestamping and Timezone Handling
**Statement:** All timestamps recorded by the system shall use UTC and include both date and time with second-level precision. The system shall not accept or store ambiguous local times.  
**Acceptance Criteria:** All `created_at`, `updated_at`, and audit `timestamp` fields are stored and returned in ISO 8601 UTC format (e.g., `2026-08-26T20:00:00Z`).  
**Regulatory Basis:** ALCOA+ (Contemporaneous); 21 CFR Part 11 §11.10(e).

---

### URS-006 — Secure Authentication with JWT
**Statement:** The system shall authenticate users via signed JWT tokens. Tokens shall expire after a defined period. Unauthenticated requests to protected endpoints shall be rejected.  
**Acceptance Criteria:** A request to any protected endpoint without a valid JWT returns HTTP 401. A token older than the configured expiry is rejected with HTTP 401.  
**Regulatory Basis:** 21 CFR Part 11 §11.10(d) — Identity authentication.

---

### URS-007 — RTM Export
**Statement:** The system shall provide an export of the Requirements Traceability Matrix in CSV format, mapping each URS to its associated test cases, risk score, and pass/fail status.  
**Acceptance Criteria:** GET `/export/rtm` returns a valid CSV file with columns: `urs_id`, `requirement`, `risk_score`, `test_id`, `test_result`, `evidence_ref`.  
**Regulatory Basis:** GAMP 5 Appendix M — Traceability; FDA Process Validation 2011.

---

### URS-008 — Risk-Based Severity Classification
**Statement:** The system shall classify each deviation by severity (`Critical`, `Major`, `Minor`) and shall prevent resolution of Critical deviations without a mandatory root cause field populated.  
**Acceptance Criteria:** Attempting to resolve a deviation with `severity=Critical` and empty `root_cause` returns HTTP 422.  
**Regulatory Basis:** ICH Q9 — Quality Risk Management; GAMP 5 §7.

---

### URS-009 — Data Retention and Non-Repudiation
**Statement:** The system shall retain all deviation records and their complete audit history for the lifetime of the application. No hard-delete operation shall be available to non-Admin users. Admin deletes shall themselves be logged.  
**Acceptance Criteria:** After Admin deletes a deviation, an audit log entry of type `DELETE` exists for that record with the Admin's user ID and timestamp.  
**Regulatory Basis:** 21 CFR Part 11 §11.10(e); ALCOA+ (Enduring).

---

### URS-010 — System Health and Version Visibility
**Statement:** The system shall expose a health check endpoint returning the application version, database connectivity status, and current UTC timestamp. This endpoint shall be accessible without authentication.  
**Acceptance Criteria:** GET `/health` returns HTTP 200 with JSON containing `version`, `status: ok`, and `timestamp` in UTC.  
**Regulatory Basis:** GAMP 5 IQ — Installation Qualification; FDA 21 CFR Part 11 §11.10(a).

---

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-001 | Security | All endpoints except `/health` and `/auth/token` require valid JWT |
| NFR-002 | Performance | API responses for list endpoints shall return within 2 seconds for up to 1,000 records |
| NFR-003 | Reproducibility | The full system shall be deployable via `docker compose up` with no manual steps |
| NFR-004 | Traceability | Every functional requirement shall be linked to at least one test case in the RTM |

---

*Document generated as part of a portfolio CSV validation project. All business data is synthetic.*
