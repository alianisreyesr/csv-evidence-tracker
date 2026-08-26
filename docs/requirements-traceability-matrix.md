# Requirements Traceability Matrix (RTM)

**System:** CSV Evidence Tracker  
**Version:** 1.0  
**Date:** 2026-08-26  
**Methodology:** Risk-based per ICH Q9 — Risk Score = Severity × Probability × Detectability (inverse)  
**Status:** Active — updated as tests are added

> ⚠️ Portfolio project. All data synthetic. Not a validated GxP system.

---

## Risk Scoring Model

| Factor | Scale | Description |
|---|---|---|
| **Severity (S)** | 1–5 | Impact if the requirement fails in production |
| **Probability (P)** | 1–5 | Likelihood of failure occurring |
| **Detectability (D)** | 1–5 | How easily failure would be detected (1 = easily detected) |
| **Risk Score** | S × P × D | Higher = more critical to test thoroughly |

### Risk Level Thresholds
| Score | Level |
|---|---|
| 1–9 | LOW |
| 10–19 | MEDIUM |
| 20–50 | HIGH |
| 51+ | CRITICAL |

---

## Traceability Table

| URS ID | Requirement | Risk Score | Risk Level | Test IDs | Pass/Fail | Evidence |
|---|---|---|---|---|---|---|
| URS-001 | Role-Based Access Control | **24** | 🔴 HIGH | OQ-001, OQ-002, OQ-003, OQ-004 | ✅ PASS | `test_auth_roles.py` |
| URS-002 | Audit Trail — Automatic & Immutable | **10** | 🟡 MEDIUM | OQ-005, OQ-006, OQ-002 | ✅ PASS | `test_audit_trail.py` |
| URS-003 | Deviation Record Lifecycle | **18** | 🔴 HIGH | OQ-007, OQ-008 | ✅ PASS | `test_deviation_lifecycle.py` |
| URS-004 | Data Completeness Validation | **24** | 🔴 HIGH | OQ-009, OQ-010 | ✅ PASS | `test_validation.py` |
| URS-005 | Timestamping & Timezone | **24** | 🔴 HIGH | OQ-011 | ✅ PASS | `test_timestamps.py` |
| URS-006 | Secure JWT Authentication | **10** | 🟡 MEDIUM | OQ-012, OQ-013 | ✅ PASS | `test_auth_roles.py` |
| URS-007 | RTM Export | **12** | 🟡 MEDIUM | OQ-014 | ✅ PASS | `test_export.py` |
| URS-008 | Risk-Based Severity Classification | **24** | 🔴 HIGH | OQ-015 | ✅ PASS | `test_validation.py` |
| URS-009 | Data Retention & Non-Repudiation | **10** | 🟡 MEDIUM | OQ-016, OQ-002 | ✅ PASS | `test_audit_trail.py` |
| URS-010 | System Health & Version Visibility | **4** | 🟢 LOW | IQ-001 | ✅ PASS | `test_health.py` |

---

## High-Risk Requirements (Score ≥ 20) — Priority Testing

These 5 requirements carry the highest risk and require the most thorough test coverage:

1. **URS-001** — RBAC: unauthorized access could compromise data integrity and regulatory compliance
2. **URS-004** — Data completeness: incomplete records violate ALCOA+ and could corrupt evidence
3. **URS-005** — Timestamps: ambiguous or missing timestamps break audit trail continuity
4. **URS-008** — Severity classification: unresolved critical deviations without root cause represent a patient safety gap
5. **URS-003** — Lifecycle: invalid state transitions could allow unreviewed deviations to appear resolved

---

## Test Coverage Summary

| Phase | Test Count | All Pass? |
|---|---|---|
| IQ (Installation Qualification) | 1 | ✅ Yes |
| OQ (Operational Qualification) | 15 | ✅ Yes |
| PQ (Performance Qualification) | Planned Sep 12–13 | 🔜 Pending |

---

*All test references point to the `tests/` directory of this repository. Test files for deviation lifecycle, validation, timestamps, and export are scaffolded in the OQ protocol.*
