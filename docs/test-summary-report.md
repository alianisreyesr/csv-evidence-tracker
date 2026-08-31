# Test Summary Report

**System:** CSV Evidence Tracker
**Report ID:** TSR-001
**Version:** 2.0
**Date:** 2026-08-31
**Author:** Portfolio Project — Synthetic GxP Demo
**Status:** Final — reviewed and re-executed against the running application

> ⚠️ Portfolio project. All data is synthetic. This report is not part of a validated GxP system.

> **Version 2.0 note:** Version 1.0 (2026-08-26) of this report was written
> without actually executing the PQ protocol or the full automated test
> suite against the current code — several claimed PASS results (RTM CSV
> export, root-cause enforcement on Critical deviations, a two-step
> investigation workflow) described capabilities that did not exist yet,
> and 9 of the 57 automated tests could not even run due to an httpx API
> change. Version 2.0 corrects this: every result below reflects an actual
> run on 2026-08-31, and §5 documents what was fixed to make the earlier
> claims true rather than just rewriting the claims.

---

## 1. Executive Summary

The CSV Evidence Tracker system's automated test suite (57 tests) passes in full, with 85% backend coverage. The PQ protocol (`docs/pq-test-protocol.md`, v2.0) was re-executed live against a running instance and all 8 steps pass. Several gaps between documented and implemented behavior were found during this review and fixed rather than left as documentation drift (see §5). One documented capability from the original protocol — requirement/test-case authoring and formal risk assessment via the API — is **not implemented** and is now tracked as an open item instead of a false PASS claim.

---

## 2. Validation Phase Results

| Phase | Evidence | Tests | Pass | Fail | Status |
|---|---|---|---|---|---|
| Automated suite (`pytest`) | `tests/` (15 modules) | 57 | 57 | 0 | ✅ COMPLETE |
| Performance Qualification (PQ) | `docs/pq-test-protocol.md` v2.0, executed live | 8 | 8 | 0 | ✅ COMPLETE |
| Backend coverage | `pytest --cov=app --cov-fail-under=70` | — | 85% | — | ✅ ABOVE GATE |

IQ/OQ as separate numbered protocols (IQ-001, OQ-001…016) referenced in
v1.0 of this report were not independently re-verified as standalone
documents in this review; the behaviors they describe (RBAC, audit trail,
timestamps, validation) are covered by the automated suite and the PQ run
above. Treat the v1.0 IQ/OQ phase table as superseded by this one.

---

## 3. URS Coverage

| URS ID | Requirement | Risk Level | Evidence | Status |
|---|---|---|---|---|
| URS-001 | Role-Based Access Control | 🔴 HIGH | `tests/test_auth_roles.py` (13 tests) | ✅ PASS |
| URS-002 | Audit Trail — Automatic & Immutable | 🟡 MEDIUM | `tests/test_audit_trail.py`; PQ Steps 7–8 | ✅ PASS |
| URS-003 | Deviation Lifecycle | 🔴 HIGH | `tests/test_deviation_lifecycle.py`, `test_deviations.py`; PQ Steps 2–5 | ✅ PASS |
| URS-004 | Data Completeness Validation | 🔴 HIGH | `tests/test_validation.py` | ✅ PASS |
| URS-005 | Timestamping & Timezone | 🔴 HIGH | `tests/test_timestamps.py` — **fixed this review**, see §5 | ✅ PASS |
| URS-006 | Secure JWT Authentication | 🟡 MEDIUM | `tests/test_auth_roles.py` | ✅ PASS |
| URS-007 | RTM Export | 🟡 MEDIUM | `GET /rtm/export` — **implemented this review**, see §5; `tests/test_export.py`; PQ Step 6 | ✅ PASS |
| URS-008 | Risk-Based Severity Classification | 🔴 HIGH | `app/scoring.py`; root-cause gate on Critical resolve — **implemented this review**, see §5; PQ Step 4 | ✅ PASS |
| URS-009 | Data Retention & Non-Repudiation | 🟡 MEDIUM | Admin audit-log deletion self-logged — **fixed this review**, see §5; PQ Step 8 | ✅ PASS |
| URS-010 | System Health & Version Visibility | 🟢 LOW | `tests/test_health.py` | ✅ PASS |

**URS Coverage: 10/10 (100%)**

---

## 4. Regulatory Alignment

| Regulation / Standard | Controls Implemented |
|---|---|
| **21 CFR Part 11 §11.10(d)** | RBAC enforced at router level; JWT authentication |
| **21 CFR Part 11 §11.10(e)** | Immutable audit trail; every mutating action logged with actor + timestamp, including the admin-delete path itself (see §5) |
| **ALCOA+ (Attributable)** | Actor resolved from the verified JWT (`AuditMiddleware._actor_from_request`), not a spoofable header |
| **ALCOA+ (Contemporaneous)** | Timestamps generated server-side in UTC at time of action — now consistently timezone-aware across every insert path, see §5 |
| **ALCOA+ (Original)** | No UPDATE on audit log entries; Analyst/QA cannot delete |
| **ALCOA+ (Complete)** | Required fields enforced via Pydantic validation (HTTP 422 on missing); Critical deviations additionally require a documented `root_cause` to resolve |
| **ALCOA+ (Enduring)** | Admin deletes are themselves logged — genuinely true as of this review, see §5 |
| **ICH Q9** | Risk scoring applied to deviations at creation; Critical severity requires root-cause documentation before closure |
| **GAMP 5 Category 4** | Custom-configured application with IQ/OQ/PQ documentation; PQ re-executed live for this report |

---

## 5. Findings From This Review

Executing the PQ protocol against the running application (rather than
writing the report from the protocol text) surfaced the following, all
fixed in this review:

| Finding | Fix |
|---|---|
| 9 of 57 tests could not run: `AsyncClient(app=app, ...)` — an httpx shortcut removed in the pinned httpx version | Switched to `ASGITransport` via the shared `client` fixture |
| Those same 5 test files logged in with stale users (`analyst`/`qa_reviewer`/`admin`) against a nonexistent `/auth/token` endpoint | Corrected to the real synthetic users (`analyst01` etc.) and `/auth/login` |
| Audit-log entries written by the generic middleware had no timezone offset (SQLite column default, not the app's own UTC-aware inserts) | `AuditMiddleware` now sets `created_at` explicitly via `datetime.now(timezone.utc).isoformat()` |
| `DELETE /audit-log/{id}` was never itself logged — `AuditMiddleware` skips all `/audit-log` paths to avoid logging routine reads | The endpoint now writes its own `DELETE_AUDIT_ENTRY` row (actor, deleted-record snapshot, UTC timestamp) |
| "Critical deviation requires root_cause" (OQ-015/URS-008) had no implementation — no `root_cause` field existed at all | Added the column, the field, and a 422 check in `PATCH /deviations/{id}/resolve` |
| `Under Investigation` was reachable in the schema's `CHECK` constraint but no endpoint could ever set it | Added `PATCH /deviations/{id}/status` as an optional pre-resolve step |
| `GET /rtm/export` (URS-007, claimed as CSV export) did not exist — only `GET /rtm` (JSON) did | Implemented `GET /rtm/export`, Admin-gated, CSV |
| `ruff>=0.5` (unpinned) resolves to a linter version with a much broader default rule set than the code was written against, so CI's lint step could fail with zero code changes to this repo | Added `ruff.toml` pinning the rule selection |

None of these were cosmetic — each closed a gap between a documented,
claimed-passing control and what the code actually did.

---

## 6. Open Items

| Item | Description | Priority | Status |
|---|---|---|---|
| OI-001 | PQ video demo (2 min screen recording) | MEDIUM | Open |
| OI-002 | Mermaid architecture diagram in README | LOW | Open — verify against current README |
| OI-003 | GitHub Actions CI/CD workflow | HIGH | ✅ Done — `.github/workflows/ci.yml`, `codeql.yml` exist and gate on lint/type-check/test/coverage/frontend build/Docker smoke test |
| OI-004 | Requirement and test-case authoring via the API (`POST /requirements`, `POST /test-cases`) does not exist; requirements/test cases are currently read-only, seeded from CSV | MEDIUM | ✅ Done — `POST /requirements` (Analyst+) and `POST /test-cases` (Analyst+) implemented, audited via `AuditMiddleware`, covered by `tests/test_requirements.py` |
| OI-005 | Formal risk-assessment endpoint (`POST /requirements/{id}/risk`, S×P×D scoring) referenced in v1.0 of the PQ protocol does not exist | MEDIUM | ✅ Done — `POST /requirements/{id}/risk` (QA Reviewer+) implemented in `app/scoring.py`/`app/routers/requirements.py`, persisted on `requirements`, surfaced in `GET /requirements` and `GET /rtm`; covered by `tests/test_scoring.py` and `tests/test_requirements.py`. Not re-verified via a live PQ re-run — see `docs/pq-test-protocol.md` post-2.0 note. |

---

## 7. Validation Conclusion

The CSV Evidence Tracker system's deviation-lifecycle, audit-trail, RBAC,
and RTM-export controls are implemented, tested, and were verified live
against a running instance as part of this review — not just asserted in
documentation. Requirement and test-case authoring plus formal risk
assessment remain read-only/unimplemented and are tracked as open items
rather than claimed complete.

The system is approved for portfolio demonstration. It is not approved for use in regulated production environments.

---

**Prepared by:** Portfolio Project
**Review date:** 2026-08-31
**Next review:** At each major version release, or before any claim in this report is repeated without re-running the suite it's based on

---

*All business data is synthetic. This report demonstrates CSV validation documentation skills for portfolio purposes.*
