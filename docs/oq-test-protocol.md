# Operational Qualification (OQ) Test Protocol

**System:** CSV Evidence Tracker  
**Protocol ID:** OQ-001  
**Version:** 1.0  
**Date:** 2026-08-26  
**Author:** Portfolio Project — Synthetic GxP Demo  
**Status:** Executed (simulated)

> ⚠️ Portfolio project. All data is synthetic. This protocol is not part of a validated GxP system.

---

## 1. Purpose

This OQ protocol verifies that the CSV Evidence Tracker system functions correctly under normal and boundary conditions for all high-risk URS requirements. It covers role-based access, audit trail integrity, deviation lifecycle enforcement, input validation, timestamp handling, JWT authentication, RTM export, and severity classification.

---

## 2. Scope

All functional requirements in the URS (URS-001 through URS-009). URS-010 (health check) is covered in the IQ protocol.

---

## 3. Pre-Conditions

- System deployed via `docker compose up`
- Database migrated (all tables present)
- Test users pre-created: `analyst_user`, `qa_reviewer_user`, `admin_user`
- All tests run via `pytest tests/` from project root

---

## 4. Test Cases

### OQ-001 — Analyst Cannot Resolve Deviation
| Field | Value |
|---|---|
| **URS** | URS-001 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_auth_roles.py::test_analyst_cannot_resolve` |
| **Steps** | 1. Authenticate as `analyst_user` → get JWT. 2. POST `/deviations` to create a deviation. 3. PATCH `/deviations/{id}/resolve` with Analyst JWT. |
| **Expected** | HTTP 403 Forbidden |
| **Actual** | HTTP 403 Forbidden |
| **Result** | ✅ PASS |

---

### OQ-002 — Analyst Cannot Delete Audit Log
| Field | Value |
|---|---|
| **URS** | URS-001, URS-002, URS-009 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_auth_roles.py::test_analyst_cannot_delete_audit_log` |
| **Steps** | 1. Authenticate as `analyst_user`. 2. DELETE `/audit-log/{id}` with Analyst JWT. |
| **Expected** | HTTP 403 Forbidden |
| **Actual** | HTTP 403 Forbidden |
| **Result** | ✅ PASS |

---

### OQ-003 — QA Reviewer Cannot Delete Audit Log
| Field | Value |
|---|---|
| **URS** | URS-001 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_auth_roles.py::test_qa_reviewer_cannot_delete_audit_log` |
| **Steps** | 1. Authenticate as `qa_reviewer_user`. 2. DELETE `/audit-log/{id}`. |
| **Expected** | HTTP 403 Forbidden |
| **Actual** | HTTP 403 Forbidden |
| **Result** | ✅ PASS |

---

### OQ-004 — Admin Can Delete Audit Log
| Field | Value |
|---|---|
| **URS** | URS-001, URS-009 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_auth_roles.py::test_admin_can_delete_audit_log` |
| **Steps** | 1. Authenticate as `admin_user`. 2. DELETE `/audit-log/{id}`. |
| **Expected** | HTTP 200 OK |
| **Actual** | HTTP 200 OK |
| **Result** | ✅ PASS |

---

### OQ-005 — Audit Entry Created on Deviation Create
| Field | Value |
|---|---|
| **URS** | URS-002 |
| **Risk Score** | 10 (MEDIUM) |
| **Test File** | `tests/test_audit_trail.py::test_audit_created_on_deviation_create` |
| **Steps** | 1. POST `/deviations` with valid payload. 2. GET `/audit-log`. |
| **Expected** | Audit entry with `action=CREATE`, `user_id`, `timestamp` |
| **Actual** | Entry exists with all required fields |
| **Result** | ✅ PASS |

---

### OQ-006 — Audit Entry Created on Deviation Resolve
| Field | Value |
|---|---|
| **URS** | URS-002, URS-003 |
| **Risk Score** | 10 (MEDIUM) |
| **Test File** | `tests/test_audit_trail.py::test_audit_on_resolve` |
| **Steps** | 1. Create deviation. 2. Resolve as QA Reviewer. 3. Check audit log. |
| **Expected** | Entry with `action=RESOLVE`, actor ID, timestamp |
| **Actual** | Entry exists |
| **Result** | ✅ PASS |

---

### OQ-007 — Valid State Transitions
| Field | Value |
|---|---|
| **URS** | URS-003 |
| **Risk Score** | 18 (HIGH) |
| **Test File** | `tests/test_deviation_lifecycle.py::test_valid_state_transitions` |
| **Steps** | 1. Create deviation (state=open). 2. Move to under_review. 3. Move to resolved. |
| **Expected** | State updates correctly; audit entry per transition |
| **Actual** | All transitions succeed; audit entries present |
| **Result** | ✅ PASS |

---

### OQ-008 — Invalid Direct Transition Rejected
| Field | Value |
|---|---|
| **URS** | URS-003 |
| **Risk Score** | 18 (HIGH) |
| **Test File** | `tests/test_deviation_lifecycle.py::test_invalid_direct_resolve` |
| **Steps** | 1. Create deviation (state=open). 2. Attempt PATCH to resolved directly. |
| **Expected** | HTTP 422 Unprocessable Entity |
| **Actual** | HTTP 422 |
| **Result** | ✅ PASS |

---

### OQ-009 — Missing Required Field Returns 422
| Field | Value |
|---|---|
| **URS** | URS-004 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_validation.py::test_missing_title` |
| **Steps** | 1. POST `/deviations` without `title`. |
| **Expected** | HTTP 422 with field-level error |
| **Actual** | HTTP 422 |
| **Result** | ✅ PASS |

---

### OQ-010 — Missing Severity Returns 422
| Field | Value |
|---|---|
| **URS** | URS-004 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_validation.py::test_missing_severity` |
| **Steps** | 1. POST `/deviations` without `severity`. |
| **Expected** | HTTP 422 |
| **Actual** | HTTP 422 |
| **Result** | ✅ PASS |

---

### OQ-011 — Timestamps Stored in UTC ISO 8601
| Field | Value |
|---|---|
| **URS** | URS-005 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_timestamps.py::test_created_at_utc` |
| **Steps** | 1. POST `/deviations`. 2. GET `/deviations/{id}`. 3. Assert `created_at` ends with `Z` or `+00:00`. |
| **Expected** | UTC ISO 8601 timestamp |
| **Actual** | UTC format confirmed |
| **Result** | ✅ PASS |

---

### OQ-012 — Unauthenticated Request Returns 401
| Field | Value |
|---|---|
| **URS** | URS-006 |
| **Risk Score** | 10 (MEDIUM) |
| **Test File** | `tests/test_auth_roles.py::test_no_token_returns_401` |
| **Steps** | 1. GET `/deviations` with no Authorization header. |
| **Expected** | HTTP 401 Unauthorized |
| **Actual** | HTTP 401 |
| **Result** | ✅ PASS |

---

### OQ-013 — Expired Token Returns 401
| Field | Value |
|---|---|
| **URS** | URS-006 |
| **Risk Score** | 10 (MEDIUM) |
| **Test File** | `tests/test_auth_roles.py::test_expired_token_returns_401` |
| **Steps** | 1. Generate token with past expiry. 2. GET `/deviations`. |
| **Expected** | HTTP 401 Unauthorized |
| **Actual** | HTTP 401 |
| **Result** | ✅ PASS |

---

### OQ-014 — RTM CSV Export
| Field | Value |
|---|---|
| **URS** | URS-007 |
| **Risk Score** | 12 (MEDIUM) |
| **Test File** | `tests/test_export.py::test_rtm_csv_export` |
| **Steps** | 1. Authenticate as Admin. 2. GET `/export/rtm`. |
| **Expected** | HTTP 200, Content-Type: text/csv, valid columns |
| **Actual** | HTTP 200, CSV returned |
| **Result** | ✅ PASS |

---

### OQ-015 — Critical Deviation Requires Root Cause
| Field | Value |
|---|---|
| **URS** | URS-008 |
| **Risk Score** | 24 (HIGH) |
| **Test File** | `tests/test_validation.py::test_critical_requires_root_cause` |
| **Steps** | 1. Create deviation with `severity=Critical`. 2. PATCH to resolve with empty `root_cause`. |
| **Expected** | HTTP 422 Unprocessable Entity |
| **Actual** | HTTP 422 |
| **Result** | ✅ PASS |

---

### OQ-016 — Admin Delete Creates Audit Log Entry
| Field | Value |
|---|---|
| **URS** | URS-009 |
| **Risk Score** | 10 (MEDIUM) |
| **Test File** | `tests/test_audit_trail.py::test_admin_delete_logged` |
| **Steps** | 1. Admin deletes a deviation. 2. GET `/audit-log`. |
| **Expected** | Entry with `action=DELETE`, Admin user ID, timestamp |
| **Actual** | Entry exists |
| **Result** | ✅ PASS |

---

## 5. OQ Summary

| Total Tests | Pass | Fail | Pending |
|---|---|---|---|
| 16 | 16 | 0 | 0 |

**OQ Conclusion:** All operational qualification test cases passed. The system demonstrates correct behavior for all high-risk and medium-risk URS requirements under normal and negative test conditions.

---

*Protocol executed as simulated portfolio evidence. All business data is synthetic.*
