from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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


class TestCase(BaseModel):
    id: int
    requirement_id: int
    code: str
    title: str
    description: Optional[str] = None
    test_type: Optional[str] = None
    expected_result: str
    created_at: str


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
    capa_ref: Optional[str] = None
    status: str = Field(default="Resolved", pattern="^(Resolved|Accepted with Risk)$")


class Deviation(BaseModel):
    id: int
    execution_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: str
    risk_classification: Optional[str] = None
    status: str
    capa_ref: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None


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
