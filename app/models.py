from pydantic import BaseModel, Field
from typing import Optional

from app.auth import UserRole


# ---------------------------------------------------------------------------
# Auth models
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: UserRole
    full_name: Optional[str] = None


class UserOut(BaseModel):
    username: str
    role: UserRole
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    full_name: str


class TokenData(BaseModel):
    username: str
    role: UserRole


# ---------------------------------------------------------------------------
# Domain models (unchanged)
# ---------------------------------------------------------------------------
class Phase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str


class RequirementCreate(BaseModel):
    code: str = Field(..., min_length=3)
    title: str = Field(..., min_length=5)
    description: Optional[str] = None
    category: Optional[str] = Field(
        None, pattern="^(Functional|Security|Performance|Regulatory)$"
    )
    priority: str = Field(default="Medium", pattern="^(Critical|High|Medium|Low)$")
    phase: str = Field(default="OQ", pattern="^(IQ|OQ|PQ)$")
    status: str = Field(default="Draft", pattern="^(Draft|Approved|Superseded)$")


class Requirement(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: str
    phase: str
    status: str
    created_at: str
    risk_severity: Optional[int] = None
    risk_probability: Optional[int] = None
    risk_detectability: Optional[int] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    risk_assessed_by: Optional[str] = None
    risk_assessed_at: Optional[str] = None


class RequirementRisk(BaseModel):
    """S x P x D formal risk assessment input for a requirement.

    Each factor is rated 1-5 (ICH Q9-style FMEA scale); risk_score and
    risk_level are always computed server-side via
    app.scoring.score_requirement_risk() — never trusted from the client —
    for the same reason deviation risk_classification is server-computed.
    """
    severity: int = Field(..., ge=1, le=5)
    probability: int = Field(..., ge=1, le=5)
    detectability: int = Field(..., ge=1, le=5)
    assessed_by: str = Field(..., min_length=2)


class TestCase(BaseModel):
    id: int
    requirement_id: int
    code: str
    title: str
    description: Optional[str] = None
    test_type: Optional[str] = None
    expected_result: str
    created_at: str


class TestCaseCreate(BaseModel):
    requirement_id: int
    code: str = Field(..., min_length=3)
    title: str = Field(..., min_length=5)
    description: Optional[str] = None
    test_type: Optional[str] = Field(
        None, pattern="^(Functional|Boundary|Negative|Regression)$"
    )
    expected_result: str = Field(..., min_length=3)


class TestCaseWithRequirement(TestCase):
    requirement_code: Optional[str] = None
    requirement_title: Optional[str] = None


class ExecutionCreate(BaseModel):
    test_case_id: int
    phase_id: int
    executed_by: str = Field(..., min_length=2)
    result: str = Field(..., pattern="^(PASS|FAIL|BLOCKED|NOT_RUN)$")
    actual_result: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None


class Execution(BaseModel):
    id: int
    test_case_id: int
    phase_id: int
    executed_by: str
    executed_at: str
    result: str
    actual_result: Optional[str] = None
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None
    created_at: str


class DeviationCreate(BaseModel):
    execution_id: Optional[int] = None
    title: str = Field(..., min_length=5)
    description: Optional[str] = None
    severity: str = Field(..., pattern="^(Critical|Major|Minor)$")
    risk_classification: Optional[str] = None
    assigned_to: Optional[str] = None


class DeviationResolve(BaseModel):
    actor: str = Field(..., min_length=2)
    resolution_notes: str = Field(..., min_length=10)
    root_cause: Optional[str] = None
    capa_ref: Optional[str] = None
    status: str = Field(default="Resolved", pattern="^(Resolved|Accepted with Risk)$")


class DeviationStatusUpdate(BaseModel):
    """Move a deviation from Open into investigation before resolving it.

    Only target is 'Under Investigation' for now — this is intentionally a
    single-transition endpoint, not a general status setter (resolving is
    handled separately by PATCH /deviations/{id}/resolve, which enforces its
    own Open/Under Investigation -> Resolved|Accepted with Risk rule).
    """
    status: str = Field(pattern="^Under Investigation$")


class Deviation(BaseModel):
    id: int
    execution_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: str
    risk_classification: Optional[str] = None
    risk_score: Optional[int] = None
    contributing_reasons: Optional[list[str]] = None
    status: str
    root_cause: Optional[str] = None
    capa_ref: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None


class AuditEntry(BaseModel):
    id: int
    actor: str
    action: str
    table_affected: Optional[str] = None
    record_id: Optional[int] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    created_at: str
