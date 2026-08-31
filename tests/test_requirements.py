import pytest

from tests.auth_helpers import auth_headers, login


@pytest.mark.asyncio
async def test_list_requirements(client):
    r = await client.get("/requirements")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_filter_requirements_by_phase(client):
    r = await client.get("/requirements?phase=OQ")
    assert r.status_code == 200
    for item in r.json():
        assert item["phase"] == "OQ"


@pytest.mark.asyncio
async def test_get_requirement_by_id(client):
    r = await client.get("/requirements/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


@pytest.mark.asyncio
async def test_requirement_not_found(client):
    r = await client.get("/requirements/9999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_requirement_test_cases(client):
    r = await client.get("/requirements/1/test-cases")
    assert r.status_code == 200
    data = r.json()
    assert "requirement" in data
    assert "test_cases" in data


@pytest.mark.asyncio
async def test_create_requirement(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/requirements",
        json={
            "code": "URS-900",
            "title": "Synthetic portfolio requirement",
            "description": "Created via POST /requirements test.",
            "category": "Functional",
            "priority": "High",
            "phase": "OQ",
            "status": "Draft",
        },
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["code"] == "URS-900"
    assert data["status"] == "Draft"
    assert data["risk_score"] is None
    assert data["risk_level"] is None

    # New requirement shows up on GET /requirements.
    listing = await client.get("/requirements")
    assert any(item["code"] == "URS-900" for item in listing.json())


@pytest.mark.asyncio
async def test_create_requirement_requires_auth(client):
    r = await client.post(
        "/requirements",
        json={"code": "URS-901", "title": "No auth requirement"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_requirement_duplicate_code(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    payload = {"code": "URS-902", "title": "Duplicate code requirement"}
    first = await client.post("/requirements", json=payload, headers=headers)
    assert first.status_code == 201
    second = await client.post("/requirements", json=payload, headers=headers)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_create_test_case(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/test-cases",
        json={
            "requirement_id": 1,
            "code": "TC-OQ-900",
            "title": "Synthetic portfolio test case",
            "description": "Created via POST /test-cases test.",
            "test_type": "Functional",
            "expected_result": "System behaves as expected.",
        },
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["code"] == "TC-OQ-900"
    assert data["requirement_id"] == 1
    assert data["requirement_code"] == "URS-001"

    linked = await client.get("/requirements/1/test-cases")
    codes = [tc["code"] for tc in linked.json()["test_cases"]]
    assert "TC-OQ-900" in codes


@pytest.mark.asyncio
async def test_create_test_case_unknown_requirement(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/test-cases",
        json={
            "requirement_id": 9999,
            "code": "TC-OQ-901",
            "title": "Orphan test case",
            "expected_result": "Should not be creatable.",
        },
        headers=headers,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_requirement_write_endpoints_audited(client):
    """POST /requirements and POST /test-cases are covered by the generic
    AuditMiddleware (mutating, non-/audit-log paths), same as /deviations."""
    admin_headers = auth_headers(await login(client, "admin01", "Admin01!"))
    analyst_headers = auth_headers(await login(client, "analyst01", "Analyst01!"))

    await client.post(
        "/requirements",
        json={"code": "URS-903", "title": "Audited requirement creation"},
        headers=analyst_headers,
    )

    audit = await client.get("/audit-log", headers=admin_headers)
    assert audit.status_code == 200
    actions = [entry["action"] for entry in audit.json()]
    assert "POST /requirements" in actions


# ---------------------------------------------------------------------------
# POST /requirements/{id}/risk — formal S x P x D risk assessment
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_assess_requirement_risk(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    r = await client.post(
        "/requirements/1/risk",
        json={"severity": 5, "probability": 4, "detectability": 3, "assessed_by": "quinn.reviewer"},
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["risk_severity"] == 5
    assert data["risk_probability"] == 4
    assert data["risk_detectability"] == 3
    assert data["risk_score"] == 60  # 5*4*3, server-computed
    assert data["risk_level"] == "High"
    assert data["risk_assessed_by"] == "quinn.reviewer"
    assert data["risk_assessed_at"] is not None


@pytest.mark.asyncio
async def test_assess_requirement_risk_ignores_client_score(client):
    """risk_score/risk_level are always server-computed, never trusted from
    the client — mirrors how deviation risk_classification is handled."""
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    r = await client.post(
        "/requirements/1/risk",
        json={
            "severity": 1,
            "probability": 1,
            "detectability": 1,
            "assessed_by": "quinn.reviewer",
            "risk_score": 999,
            "risk_level": "Critical",
        },
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["risk_score"] == 1
    assert data["risk_level"] == "Low"


@pytest.mark.asyncio
async def test_assess_requirement_risk_requires_qa_role(client):
    headers = auth_headers(await login(client, "analyst01", "Analyst01!"))
    r = await client.post(
        "/requirements/1/risk",
        json={"severity": 3, "probability": 3, "detectability": 3, "assessed_by": "ana.analyst"},
        headers=headers,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_assess_requirement_risk_out_of_range(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    r = await client.post(
        "/requirements/1/risk",
        json={"severity": 6, "probability": 3, "detectability": 3, "assessed_by": "quinn.reviewer"},
        headers=headers,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_assess_requirement_risk_not_found(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    r = await client.post(
        "/requirements/9999/risk",
        json={"severity": 3, "probability": 3, "detectability": 3, "assessed_by": "quinn.reviewer"},
        headers=headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_requirement_risk_visible_in_rtm(client):
    headers = auth_headers(await login(client, "qa_reviewer01", "QAReview01!"))
    await client.post(
        "/requirements/1/risk",
        json={"severity": 4, "probability": 4, "detectability": 4, "assessed_by": "quinn.reviewer"},
        headers=headers,
    )
    r = await client.get("/rtm")
    assert r.status_code == 200
    req_1 = next(item for item in r.json() if item["id"] == 1)
    assert req_1["risk_score"] == 64
    assert req_1["risk_level"] == "High"
