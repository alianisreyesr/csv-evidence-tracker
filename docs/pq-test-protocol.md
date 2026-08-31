# Performance Qualification (PQ) Protocol

**System:** CSV Evidence Tracker
**Protocol ID:** PQ-001
**Version:** 2.0
**Date:** 2026-08-31
**Author:** Portfolio Project — Synthetic GxP Demo
**Status:** Executed live against a running local instance (`uvicorn`, SQLite, this repo's actual routes)

> ⚠️ Portfolio project. All data is synthetic. This protocol is not part of a validated GxP system.

> **Version 2.0 note:** Version 1.0 of this protocol described a broader
> workflow (requirement entry, S×P×D risk assessment) that was never
> implemented in the API — only seeded, read-only reference data exists for
> requirements and test cases. Version 2.0 documents the workflow this
> system **actually** exposes, executed end-to-end, with real request/
> response evidence rather than idealized "Expected = Actual" rows. See
> `docs/test-summary-report.md` §5 for the gap that removal leaves open.

---

## 1. Purpose

This PQ protocol demonstrates that the CSV Evidence Tracker system performs its intended functions correctly under realistic operating conditions, executing a complete end-to-end validation workflow: test execution against a seeded requirement, deviation recording, QA investigation and resolution, RTM export, and audit trail verification.

PQ is the final validation phase and provides the evidence that the system is suitable for its intended use per GAMP 5 and 21 CFR Part 11.

---

## 2. PQ Scenario — End-to-End Validation Workflow

**Scenario:** A QA team executes a test case against a seeded requirement, records a Critical deviation from the failure, investigates it, resolves it with a documented root cause, exports the RTM as evidence, and confirms the audit trail captured every step — including that an admin deletion of an audit entry is itself logged.

Executed against `URS-001 / TC-IQ-001` (seeded requirement/test case) — no requirement- or test-case-authoring endpoints exist to originate new ones (see Version 2.0 note above).

---

## 3. PQ Test Steps

Every step below was executed with `curl` against a live `uvicorn` instance on 2026-08-31. Request/response bodies are abbreviated; full JSON is reproducible via `docs/demo-walkthrough.md` if one is added, or by re-running the commands shown.

### Step 1 — Test Execution (URS-001 / TC-IQ-001)
| Field | Value |
|---|---|
| **Actor** | Analyst (`analyst01`) |
| **Action** | `POST /executions` `{test_case_id: 1, phase_id: 1, result: "FAIL", ...}` |
| **Expected** | HTTP 201; execution recorded; self-logged audit entry (`EXECUTE_TEST`) |
| **Actual** | HTTP 201, `id: 19`, `executed_at: 2026-08-31T20:23:25.841648+00:00` |
| **Result** | ✅ PASS |

### Step 2 — Deviation Recording (URS-003)
| Field | Value |
|---|---|
| **Actor** | Analyst (`analyst01`) |
| **Action** | `POST /deviations` `{execution_id: 19, severity: "Critical", ...}` |
| **Expected** | HTTP 201; server computes `risk_score`/`risk_classification` — not client-supplied; `status: "Open"` |
| **Actual** | HTTP 201, `id: 4`, `risk_score: 3`, `risk_classification: "High"`, `contributing_reasons: ["Severity is Critical (+3)"]`, `status: "Open"` |
| **Result** | ✅ PASS |

### Step 3 — Move to Under Investigation (URS-003)
| Field | Value |
|---|---|
| **Actor** | QA Reviewer (`qa_reviewer01`) |
| **Action** | `PATCH /deviations/4/status` `{status: "Under Investigation"}` |
| **Expected** | HTTP 200; status transitions from Open |
| **Actual** | HTTP 200, `status: "Under Investigation"` |
| **Result** | ✅ PASS |

### Step 4 — Resolve Without Root Cause Rejected (OQ-015 / URS-008)
| Field | Value |
|---|---|
| **Actor** | QA Reviewer (`qa_reviewer01`) |
| **Action** | `PATCH /deviations/4/resolve` with `resolution_notes` but no `root_cause`, on a **Critical** deviation |
| **Expected** | HTTP 422 — a Critical deviation cannot be resolved without a documented root cause |
| **Actual** | HTTP 422, `{"detail":"root_cause is required to resolve a Critical deviation."}` |
| **Result** | ✅ PASS |

### Step 5 — QA Resolution With Root Cause (URS-001, URS-008)
| Field | Value |
|---|---|
| **Actor** | QA Reviewer (`qa_reviewer01`) |
| **Action** | `PATCH /deviations/4/resolve` with `root_cause`, `resolution_notes`, `capa_ref` |
| **Expected** | HTTP 200; `status: "Resolved"`; `resolved_at` server-generated UTC |
| **Actual** | HTTP 200, `status: "Resolved"`, `root_cause: "Session token TTL miscalculated on server clock drift"`, `resolved_at: 2026-08-31T20:23:39.618356+00:00` |
| **Result** | ✅ PASS |

### Step 6 — RTM CSV Export, Admin-Gated (URS-007)
| Field | Value |
|---|---|
| **Actor** | Admin (`admin01`) vs. Analyst (`analyst01`) |
| **Action** | `GET /rtm/export` |
| **Expected** | Admin: HTTP 200, `text/csv`, one row per requirement/test-case pair. Analyst: HTTP 403. |
| **Actual** | Admin: HTTP 200, `content-type: text/csv`, 21 data rows + header. Analyst: HTTP 403, `{"detail":"Role 'UserRole.analyst' is not authorised..."}` |
| **Result** | ✅ PASS |

### Step 7 — Audit Trail Completeness (URS-002, URS-009)
| Field | Value |
|---|---|
| **Actor** | Admin (`admin01`) |
| **Action** | `GET /audit-log` |
| **Expected** | Entries for every mutating step above (`EXECUTE_TEST`, `POST /deviations`, `PATCH /deviations/4/status`, both `PATCH /deviations/4/resolve` attempts — including the rejected one), each with `actor` and a UTC-offset `created_at` |
| **Actual** | All present, newest-first, e.g. `PATCH /deviations/4/resolve \| qa_reviewer01 \| 2026-08-31T20:23:39.621109+00:00` — including the 422-rejected attempt at `20:23:39.608173+00:00` |
| **Result** | ✅ PASS |

### Step 8 — Admin Deletion Is Itself Logged (OQ-016, ALCOA+ Enduring)
| Field | Value |
|---|---|
| **Actor** | Admin (`admin01`) |
| **Action** | `DELETE /audit-log/{id}` on the oldest entry |
| **Expected** | HTTP 204; a new `DELETE_AUDIT_ENTRY` entry recorded with the deleted row's actor and a UTC timestamp — not a silent deletion |
| **Actual** | HTTP 204; next `GET /audit-log` shows `DELETE_AUDIT_ENTRY \| admin01 \| record_id: 1 \| 2026-08-31T20:23:55.361017+00:00` as the newest entry |
| **Result** | ✅ PASS |

---

## 4. PQ Summary

| Step | Actor | Result |
|---|---|---|
| Test execution | Analyst | ✅ PASS |
| Deviation recording | Analyst | ✅ PASS |
| Move to Under Investigation | QA Reviewer | ✅ PASS |
| Resolve rejected without root cause (Critical) | QA Reviewer | ✅ PASS |
| Resolve with root cause | QA Reviewer | ✅ PASS |
| RTM CSV export, Admin-gated | Admin / Analyst | ✅ PASS |
| Audit trail completeness | Admin | ✅ PASS |
| Admin deletion self-logged | Admin | ✅ PASS |

**Total Steps: 8 | Pass: 8 | Fail: 0**

**PQ Conclusion:** The system executes the deviation lifecycle — test failure → deviation → investigation → resolution with a required root cause on Critical severity — end-to-end, with a complete, attributable, UTC-timestamped audit trail, including self-logged administrative deletions. RTM export is correctly Admin-gated. Requirements and test-case authoring, and a formal risk-assessment endpoint, are **not** implemented; that scope reduction from v1.0 is intentional and documented, not silently dropped — see `docs/test-summary-report.md` §5 (Open Items).

---

*Protocol executed live against a running instance on 2026-08-31. All business data is synthetic.*
