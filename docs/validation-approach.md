# Validation Approach

> This document describes the design philosophy of the CSV Evidence Tracker.
> All scenarios and data are synthetic and fictional.

## What is Computer System Validation (CSV)?

CSV is a formal process required by FDA regulations (21 CFR Part 11, 21 CFR Part 820) and international standards (GAMP 5) to demonstrate that a computerized system consistently does what it is designed to do in a regulated environment.

The validation lifecycle typically follows:

```
User Requirements Specification (URS)
          ↓
Functional Specification (FS)
          ↓
Installation Qualification (IQ)  — Is the system installed correctly?
          ↓
Operational Qualification (OQ)   — Does the system operate as specified?
          ↓
Performance Qualification (PQ)   — Does the system perform reliably under real conditions?
          ↓
Ongoing Monitoring + Change Control
```

## What This Prototype Models

This system demonstrates the **data engineering** side of CSV evidence management:

1. **Requirements management** — Structured storage and status tracking of URS items
2. **Traceability** — Every test case links to a requirement (RTM); every execution links to a test case
3. **Evidence recording** — ALCOA+ compliant test execution log (Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available)
4. **Deviation tracking** — Failures are captured, classified by severity, and tracked to resolution
5. **Audit trail** — All data mutations are appended to a tamper-evident log per 21 CFR Part 11

## ALCOA+ Principles Applied

| Principle | Implementation |
|---|---|
| **Attributable** | `executed_by` and `actor` fields required on all records |
| **Legible** | Structured text fields with validation constraints |
| **Contemporaneous** | `executed_at` is UTC, server-generated at time of POST |
| **Original** | Source data preserved in `test_executions`; audit log is append-only |
| **Accurate** | Schema constraints enforce valid values (result, severity, status) |
| **Complete** | Required fields enforced at API and DB level |
| **Consistent** | UTC timestamps throughout; no client-supplied timestamps |
| **Enduring** | SQLite WAL mode; audit_log rows are never deleted |
| **Available** | API endpoints expose all records with filtering |

## What This Does NOT Model

- Real validated software — this is a portfolio artifact only
- Formal change control procedures
- Electronic signature (21 CFR Part 11 §11.50)
- Role-based access control
- Integration with LIMS, ERP, or EDMS systems

See [IMPROVEMENTS.md](../IMPROVEMENTS.md) for planned enhancements.
