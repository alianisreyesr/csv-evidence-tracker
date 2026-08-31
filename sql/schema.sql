-- CSV Evidence Tracker — Schema
-- All data in this system is synthetic and non-confidential.
-- For portfolio use only. Not for regulated production use.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ─────────────────────────────────────────────
-- Validation Phases: IQ / OQ / PQ
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS phases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,          -- 'IQ' | 'OQ' | 'PQ'
    description TEXT,
    status      TEXT NOT NULL DEFAULT 'Planned'
                    CHECK(status IN ('Planned','In Progress','Completed','Locked')),
    started_at  TEXT,
    completed_at TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now','utc'))
);

-- ─────────────────────────────────────────────
-- User Requirements (URS)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS requirements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    code        TEXT NOT NULL UNIQUE,          -- e.g. URS-001
    title       TEXT NOT NULL,
    description TEXT,
    category    TEXT,                          -- Functional | Security | Performance | Regulatory
    priority    TEXT NOT NULL DEFAULT 'Medium'
                    CHECK(priority IN ('Critical','High','Medium','Low')),
    phase       TEXT NOT NULL DEFAULT 'OQ'
                    CHECK(phase IN ('IQ','OQ','PQ')),
    status      TEXT NOT NULL DEFAULT 'Draft'
                    CHECK(status IN ('Draft','Approved','Superseded')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now','utc')),

    -- Formal S×P×D risk assessment (see app/scoring.py:score_requirement_risk).
    -- Null until POST /requirements/{id}/risk is called at least once.
    risk_severity      INTEGER CHECK(risk_severity IS NULL OR risk_severity BETWEEN 1 AND 5),
    risk_probability   INTEGER CHECK(risk_probability IS NULL OR risk_probability BETWEEN 1 AND 5),
    risk_detectability INTEGER CHECK(risk_detectability IS NULL OR risk_detectability BETWEEN 1 AND 5),
    risk_score         INTEGER,             -- severity * probability * detectability
    risk_level         TEXT CHECK(risk_level IS NULL OR risk_level IN ('Low','Medium','High','Critical')),
    risk_assessed_by   TEXT,
    risk_assessed_at   TEXT
);

-- ─────────────────────────────────────────────
-- Test Cases (linked to requirements — RTM)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS test_cases (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL REFERENCES requirements(id),
    code           TEXT NOT NULL UNIQUE,       -- e.g. TC-OQ-001
    title          TEXT NOT NULL,
    description    TEXT,
    test_type      TEXT,                       -- Functional | Boundary | Negative | Regression
    expected_result TEXT NOT NULL,
    created_at     TEXT NOT NULL DEFAULT (datetime('now','utc'))
);

-- ─────────────────────────────────────────────
-- Test Executions (ALCOA+: Who, What, When, Where, Why)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS test_executions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id   INTEGER NOT NULL REFERENCES test_cases(id),
    phase_id       INTEGER NOT NULL REFERENCES phases(id),
    executed_by    TEXT NOT NULL,              -- ALCOA+: Who
    executed_at    TEXT NOT NULL,              -- ALCOA+: When (UTC, server-generated)
    result         TEXT NOT NULL
                       CHECK(result IN ('PASS','FAIL','BLOCKED','NOT_RUN')),
    actual_result  TEXT,                       -- What was observed
    evidence_ref   TEXT,                       -- Where is the evidence (doc ref / screenshot)
    notes          TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now','utc'))
);

-- ─────────────────────────────────────────────
-- Deviations (test failures → investigation → resolution)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS deviations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id        INTEGER REFERENCES test_executions(id),
    title               TEXT NOT NULL,
    description         TEXT,
    severity            TEXT NOT NULL DEFAULT 'Minor'
                            CHECK(severity IN ('Critical','Major','Minor')),
    risk_classification TEXT,
    risk_score          INTEGER,               -- Explainable rule-based score (see app/scoring.py)
    contributing_reasons TEXT,                 -- JSON array of contributing reasons for risk_score
    status              TEXT NOT NULL DEFAULT 'Open'
                            CHECK(status IN ('Open','Under Investigation','Resolved','Accepted with Risk')),
    capa_ref            TEXT,                  -- Reference to corrective action
    assigned_to         TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now','utc')),
    resolved_at         TEXT,
    resolution_notes    TEXT,                  -- Required on resolve; see DeviationResolve
    root_cause          TEXT                   -- Required to resolve a Critical deviation (OQ-015 / URS-008)
);

-- ─────────────────────────────────────────────
-- Audit Log — Append-Only, Tamper-Evident
-- 21 CFR Part 11 / ALCOA+ compliant design
-- NEVER UPDATE OR DELETE ROWS FROM THIS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    actor           TEXT NOT NULL,
    action          TEXT NOT NULL,
    table_affected  TEXT,
    record_id       INTEGER,
    previous_value  TEXT,                      -- JSON snapshot
    new_value       TEXT,                      -- JSON snapshot
    ip_address      TEXT,
    user_agent      TEXT,
    status_code     INTEGER,
    latency_ms      REAL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now','utc'))  -- UTC, server-generated
);

-- ─────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_test_cases_req    ON test_cases(requirement_id);
CREATE INDEX IF NOT EXISTS idx_executions_case   ON test_executions(test_case_id);
CREATE INDEX IF NOT EXISTS idx_executions_phase  ON test_executions(phase_id);
CREATE INDEX IF NOT EXISTS idx_executions_result ON test_executions(result);
CREATE INDEX IF NOT EXISTS idx_deviations_status ON deviations(status);
CREATE INDEX IF NOT EXISTS idx_deviations_exec   ON deviations(execution_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor       ON audit_log(actor);
CREATE INDEX IF NOT EXISTS idx_audit_created     ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_record      ON audit_log(table_affected, record_id);
