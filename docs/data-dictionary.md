# CSV Evidence Tracker Data Dictionary

> **Authorship:** This data dictionary was designed and created by Alianis Reyes Reyes for the CSV Evidence Tracker portfolio project. It documents the current demonstration data model and proposed lifecycle extensions using synthetic data only.

## Conventions

- Primary keys are represented as `id` unless otherwise noted.
- Foreign keys use the `<entity>_id` naming convention.
- Timestamps should be stored in UTC using ISO 8601-compatible datetime values.
- Enumerated values are controlled lists for demonstration purposes.
- Records and values described here must contain fictional, non-sensitive data only.

## User

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique user identifier. |
| `username` | String | Yes | Unique login or demonstration user name. |
| `display_name` | String | Yes | Name shown in the application. |
| `email` | String | No | Synthetic contact value, if used. |
| `role` | Enum | Yes | `ADMIN`, `AUTHOR`, `TESTER`, `REVIEWER`, `APPROVER`, or `READ_ONLY`. |
| `is_active` | Boolean | Yes | Indicates whether the user may access the demonstration application. |
| `created_at` | Datetime | Yes | Record creation timestamp. |
| `updated_at` | Datetime | Yes | Last update timestamp. |

## Requirement

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique requirement identifier. |
| `requirement_key` | String | Yes | Human-readable unique identifier, such as `URS-001`. |
| `title` | String | Yes | Short requirement title. |
| `description` | Text | Yes | Requirement statement and acceptance intent. |
| `category` | Enum | Yes | `FUNCTIONAL`, `DATA_INTEGRITY`, `SECURITY`, `COMPLIANCE`, or `REPORTING`. |
| `priority` | Enum | Yes | `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`. |
| `status` | Enum | Yes | `DRAFT`, `APPROVED`, `IMPLEMENTED`, `VERIFIED`, or `RETIRED`. |
| `version` | String | Yes | Controlled record version. |
| `source_reference` | String | No | Reference to the fictional source document or request. |
| `owner_id` | Foreign key | Yes | References `User.id`. |
| `created_at` | Datetime | Yes | Record creation timestamp. |
| `updated_at` | Datetime | Yes | Last update timestamp. |

## Risk Assessment

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique risk assessment identifier. |
| `risk_key` | String | Yes | Human-readable identifier, such as `RA-001`. |
| `requirement_id` | Foreign key | Yes | References `Requirement.id`. |
| `hazard_description` | Text | Yes | Description of the potential harm or concern. |
| `failure_mode` | Text | Yes | How the requirement or control could fail. |
| `potential_impact` | Text | Yes | Potential effect of the failure. |
| `severity` | Integer | Yes | Impact rating, typically 1–5. |
| `probability` | Integer | Yes | Likelihood rating, typically 1–5. |
| `detectability` | Integer | Yes | Detection rating, typically 1–5. |
| `risk_score` | Integer | Yes | Derived score, for example severity × probability × detectability. |
| `risk_level` | Enum | Yes | `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. |
| `mitigation` | Text | No | Planned or implemented control. |
| `residual_risk_score` | Integer | No | Score after mitigation. |
| `residual_risk_level` | Enum | No | Residual risk classification. |
| `status` | Enum | Yes | `DRAFT`, `ASSESSED`, `MITIGATED`, or `ACCEPTED`. |
| `assessed_by_id` | Foreign key | No | References `User.id`. |
| `assessed_at` | Datetime | No | Assessment completion timestamp. |

## Test Case

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique test case identifier. |
| `test_case_key` | String | Yes | Human-readable identifier, such as `OQ-TRACE-001`. |
| `title` | String | Yes | Test case title. |
| `objective` | Text | Yes | Verification objective. |
| `test_level` | Enum | Yes | `IQ`, `OQ`, or `PQ`. |
| `preconditions` | Text | No | Conditions required before execution. |
| `test_steps` | JSON or Text | Yes | Ordered test procedure. |
| `expected_result` | Text | Yes | Expected verification outcome. |
| `status` | Enum | Yes | `DRAFT`, `IN_REVIEW`, `APPROVED`, `READY`, or `RETIRED`. |
| `version` | String | Yes | Controlled test-case version. |
| `author_id` | Foreign key | Yes | References `User.id`. |
| `reviewer_id` | Foreign key | No | References `User.id`. |
| `created_at` | Datetime | Yes | Record creation timestamp. |
| `updated_at` | Datetime | Yes | Last update timestamp. |

## Requirement-Test Case Traceability

| Field | Type | Required | Description |
|---|---|---:|---|
| `requirement_id` | Foreign key | Yes | References `Requirement.id`. |
| `test_case_id` | Foreign key | Yes | References `TestCase.id`. |
| `coverage_type` | Enum | Yes | `PRIMARY` or `SUPPORTING`. |
| `rationale` | Text | No | Reason for the traceability link. |

## Test Execution

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique execution identifier. |
| `execution_key` | String | Yes | Human-readable identifier, such as `TE-2026-001`. |
| `test_case_id` | Foreign key | Yes | References `TestCase.id`. |
| `test_case_version_snapshot` | String or JSON | Yes | Version or snapshot of the procedure executed. |
| `environment` | String | Yes | Demonstration environment, such as `DEMO-LOCAL`. |
| `status` | Enum | Yes | `NOT_RUN`, `IN_PROGRESS`, `PASSED`, `FAILED`, `BLOCKED`, or `NOT_APPLICABLE`. |
| `actual_result` | Text | No | Observed execution result. |
| `execution_notes` | Text | No | Supplemental execution details. |
| `deviation_reference` | String | No | Synthetic deviation identifier, if applicable. |
| `deviation_summary` | Text | No | Summary of the nonconformance or exception. |
| `executed_by_id` | Foreign key | No | References `User.id`. |
| `started_at` | Datetime | No | Execution start timestamp. |
| `completed_at` | Datetime | No | Execution completion timestamp. |

## Evidence

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique evidence identifier. |
| `evidence_key` | String | Yes | Human-readable identifier, such as `EV-001`. |
| `evidence_type` | Enum | Yes | `SCREENSHOT`, `LOG_EXPORT`, `REPORT`, `TEST_DATA`, `ATTACHMENT`, or `LINK`. |
| `file_name` | String | No | File name or display label. |
| `storage_reference` | String | Yes | File path, URI, or application reference. |
| `content_type` | String | No | MIME type when applicable. |
| `checksum_sha256` | String | No | SHA-256 hash used to demonstrate evidence integrity. |
| `description` | Text | Yes | Explanation of the evidence content and relevance. |
| `status` | Enum | Yes | `DRAFT`, `ATTACHED`, `REVIEWED`, `ACCEPTED`, or `REJECTED`. |
| `test_execution_id` | Foreign key | No | References `TestExecution.id`. |
| `requirement_id` | Foreign key | No | References `Requirement.id`. |
| `risk_assessment_id` | Foreign key | No | References `RiskAssessment.id`. |
| `uploaded_by_id` | Foreign key | Yes | References `User.id`. |
| `uploaded_at` | Datetime | Yes | Evidence attachment timestamp. |
| `is_synthetic` | Boolean | Yes | Must be `true` within this portfolio project. |

## Approval

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique approval identifier. |
| `approval_key` | String | Yes | Human-readable approval identifier. |
| `entity_type` | Enum | Yes | `REQUIREMENT`, `RISK_ASSESSMENT`, `TEST_CASE`, `TEST_EXECUTION`, or `EVIDENCE`. |
| `entity_id` | Integer or UUID | Yes | Identifier of the controlled entity being reviewed. |
| `approval_type` | Enum | Yes | `REVIEW`, `APPROVAL`, `REJECTION`, or `RISK_ACCEPTANCE`. |
| `decision` | Enum | Yes | `PENDING`, `APPROVED`, or `REJECTED`. |
| `comment` | Text | No | Reviewer or approver justification. |
| `record_version` | String | Yes | Version of the reviewed record. |
| `approved_by_id` | Foreign key | No | References `User.id`. |
| `approved_at` | Datetime | No | Decision timestamp. |

## Audit Event

| Field | Type | Required | Description |
|---|---|---:|---|
| `id` | Integer or UUID | Yes | Unique audit-event identifier. |
| `event_key` | String | Yes | Human-readable audit identifier. |
| `event_timestamp` | Datetime | Yes | UTC timestamp at which the event occurred. |
| `actor_id` | Foreign key | No | References `User.id`; null for system actions. |
| `event_type` | Enum | Yes | `CREATE`, `UPDATE`, `DELETE`, `STATUS_CHANGE`, `EXECUTE`, `APPROVE`, `REJECT`, or `LOGIN`. |
| `entity_type` | String | Yes | Controlled entity type affected by the action. |
| `entity_id` | Integer or UUID | Yes | Identifier of the affected record. |
| `action_summary` | Text | Yes | Human-readable summary of the action. |
| `before_state` | JSON or Text | No | Serialized state before the action. |
| `after_state` | JSON or Text | No | Serialized state after the action. |
| `reason` | Text | No | Change rationale; required for controlled changes. |
| `request_id` | String | No | Synthetic correlation identifier for the request. |
| `source_ip` | String | No | Synthetic source address if captured. |
| `is_system_event` | Boolean | Yes | Identifies application-generated events. |

## Integrity Rules

- Unique identifiers: `requirement_key`, `risk_key`, `test_case_key`, `execution_key`, `evidence_key`, and `approval_key` must be unique.
- `TestCase` records at OQ or PQ level require at least one linked `Requirement`.
- A `PASSED` `TestExecution` should have accepted evidence or a documented justification.
- Every `Evidence` record must be linked to at least one `TestExecution`, `Requirement`, or `RiskAssessment`.
- Audit events are append-only and must not be edited or deleted.
- Approved controlled records should be retired or superseded rather than deleted.
- Any implementation must enforce the project’s synthetic-data-only limitation.

## Scope Statement

This data dictionary supports a portfolio demonstration and describes current and proposed structures. It is not evidence of production validation, regulatory compliance, electronic-signature controls, or 21 CFR Part 11 compliance.
