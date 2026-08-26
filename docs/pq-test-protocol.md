# Performance Qualification (PQ) Protocol

**System:** CSV Evidence Tracker  
**Protocol ID:** PQ-001  
**Version:** 1.0  
**Date:** 2026-08-26  
**Author:** Portfolio Project — Synthetic GxP Demo  
**Status:** Executed (simulated)

> ⚠️ Portfolio project. All data is synthetic. This protocol is not part of a validated GxP system.

---

## 1. Purpose

This PQ protocol demonstrates that the CSV Evidence Tracker system performs its intended functions correctly under realistic operating conditions, executing a complete end-to-end validation workflow from requirement creation through QA review and RTM export.

PQ is the final validation phase and provides the evidence that the system is suitable for its intended use per GAMP 5 and 21 CFR Part 11.

---

## 2. PQ Scenario — End-to-End Validation Workflow

**Scenario:** A QA team validates a new CSV system for electronic batch records. They must:
1. Define requirements
2. Assess risk
3. Execute test cases
4. Record a deviation
5. Resolve with root cause
6. QA Reviewer approves
7. Export RTM as evidence

---

## 3. PQ Test Steps

### Step 1 — Requirement Entry (URS-004)
| Field | Value |
|---|---|
| **Actor** | Analyst |
| **Action** | POST `/requirements` with title, description, urs_id, acceptance_criteria |
| **Expected** | HTTP 201, requirement stored with ID |
| **Actual** | HTTP 201, `req_id: REQ-001` returned |
| **Result** | ✅ PASS |

### Step 2 — Risk Assessment (URS-008)
| Field | Value |
|---|---|
| **Actor** | QA Reviewer |
| **Action** | POST `/requirements/{id}/risk` with severity=4, probability=3, detectability=2 |
| **Expected** | Risk score = 24, risk_level = HIGH |
| **Actual** | `risk_score: 24`, `risk_level: HIGH` |
| **Result** | ✅ PASS |

### Step 3 — Test Case Creation
| Field | Value |
|---|---|
| **Actor** | Analyst |
| **Action** | POST `/test-cases` linked to REQ-001 |
| **Expected** | Test case created with status `pending` |
| **Actual** | HTTP 201, `tc_id: TC-001` |
| **Result** | ✅ PASS |

### Step 4 — Test Execution
| Field | Value |
|---|---|
| **Actor** | Analyst |
| **Action** | POST `/executions` for TC-001 with result=PASS, evidence=\"Screenshot attached\" |
| **Expected** | Execution recorded; audit log entry created |
| **Actual** | HTTP 201, audit entry present |
| **Result** | ✅ PASS |

### Step 5 — Deviation Recording (URS-003)
| Field | Value |
|---|---|
| **Actor** | Analyst |
| **Action** | POST `/deviations` with title, description, severity=Major, product_id |
| **Expected** | Deviation created with status=open; audit entry with action=CREATE |
| **Actual** | HTTP 201, `status: open`, audit entry present |
| **Result** | ✅ PASS |

### Step 6 — QA Review and Resolution (URS-001, URS-008)
| Field | Value |
|---|---|
| **Actor** | QA Reviewer |
| **Action** | PATCH `/deviations/{id}/status` to `under_review`, then PATCH `/deviations/{id}/resolve` with root_cause populated |
| **Expected** | Status transitions enforced; resolution logged |
| **Actual** | Both transitions succeed; audit entries created |
| **Result** | ✅ PASS |

### Step 7 — RTM Export (URS-007)
| Field | Value |
|---|---|
| **Actor** | Admin |
| **Action** | GET `/rtm/export` |
| **Expected** | CSV file with all requirements, risk scores, test results, pass/fail status |
| **Actual** | Valid CSV returned with all columns |
| **Result** | ✅ PASS |

### Step 8 — Audit Trail Completeness (URS-002)
| Field | Value |
|---|---|
| **Actor** | Admin |
| **Action** | GET `/audit-log` |
| **Expected** | Entries present for all actions in Steps 1–7: CREATE, EXECUTE, RESOLVE, EXPORT |
| **Actual** | All action types present with user_id and UTC timestamp |
| **Result** | ✅ PASS |

---

## 4. PQ Summary

| Phase Step | Actor | Result |
|---|---|---|
| Requirement entry | Analyst | ✅ PASS |
| Risk assessment | QA Reviewer | ✅ PASS |
| Test case creation | Analyst | ✅ PASS |
| Test execution | Analyst | ✅ PASS |
| Deviation recording | Analyst | ✅ PASS |
| QA review and resolution | QA Reviewer | ✅ PASS |
| RTM export | Admin | ✅ PASS |
| Audit trail completeness | Admin | ✅ PASS |

**Total Steps: 8 | Pass: 8 | Fail: 0**

**PQ Conclusion:** The system successfully executes the complete validation workflow under realistic operating conditions. All three user roles performed their designated functions. The audit trail is complete and attributable. The RTM export provides machine-readable traceability evidence. The system is qualified for its intended portfolio demonstration use.

---

*Protocol executed as simulated portfolio evidence. All business data is synthetic.*
