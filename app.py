import json
import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

app = FastAPI(title="IBRAMIND InfraRisk AI", version="0.1.0")


class EvidenceItem(BaseModel):
    id: str
    type: str
    text: str


class RiskRequest(BaseModel):
    project_name: str
    project_context: str
    evidence: List[EvidenceItem]


class RiskFinding(BaseModel):
    risk: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    evidence_ids: List[str]
    rationale: str
    recommended_action: str


class RiskResponse(BaseModel):
    project_name: str
    findings: List[RiskFinding]
    model: str


SYSTEM_PROMPT = """You are an infrastructure project risk analyst.
Use only the supplied project context and evidence.
Do not invent facts. Every finding must cite one or more evidence IDs.
Return valid JSON with a top-level key 'findings'. Each finding must contain:
risk, severity (low|medium|high|critical), confidence (0..1), evidence_ids,
rationale, recommended_action.
If evidence is insufficient, say so explicitly and lower confidence.
"""


def get_client() -> OpenAI:
    api_key = os.getenv("NEBIUS_API_KEY")
    base_url = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
    if not api_key or not base_url:
        raise HTTPException(
            status_code=503,
            detail="Nebius credentials are not configured. Set NEBIUS_API_KEY and NEBIUS_BASE_URL.",
        )
    return OpenAI(api_key=api_key, base_url=base_url)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "nebius_configured": bool(os.getenv("NEBIUS_API_KEY") and os.getenv("NEBIUS_BASE_URL")),
        "model": os.getenv("NVIDIA_MODEL", "not-configured"),
    }


@app.post("/analyze-risk", response_model=RiskResponse)
def analyze_risk(req: RiskRequest) -> RiskResponse:
    model = os.getenv("NVIDIA_MODEL")
    if not model:
        raise HTTPException(status_code=503, detail="NVIDIA_MODEL is not configured.")

    payload = {
        "project_name": req.project_name,
        "project_context": req.project_context,
        "evidence": [item.model_dump() for item in req.evidence],
    }

    client = get_client()
    completion = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
        findings = [RiskFinding(**x) for x in parsed.get("findings", [])]
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Model returned invalid structured output: {exc}")

    return RiskResponse(project_name=req.project_name, findings=findings, model=model)
