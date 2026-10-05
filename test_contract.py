from app import EvidenceItem, RiskRequest, RiskFinding

def test_request_contract():
    req = RiskRequest(
        project_name="Synthetic Bridge Rehabilitation Package",
        project_context="Synthetic evaluation case.",
        evidence=[EvidenceItem(id="E-001", type="site_diary", text="Access delay.")],
    )
    assert req.evidence[0].id == "E-001"

def test_finding_contract():
    f = RiskFinding(
        risk="Schedule delay",
        severity="high",
        confidence=0.8,
        evidence_ids=["E-001"],
        rationale="Access delay affects the planned activity.",
        recommended_action="Recover access and update the short-term programme.",
    )
    assert f.confidence == 0.8
