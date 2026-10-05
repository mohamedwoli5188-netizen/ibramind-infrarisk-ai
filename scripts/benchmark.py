import json
import os
import statistics
import time
from pathlib import Path
from openai import OpenAI

BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
API_KEY = os.environ["NEBIUS_API_KEY"]
MODEL_OVERRIDE = os.getenv("NVIDIA_MODEL")

SYSTEM_PROMPT = """You are IBRAMIND InfraRisk AI, an infrastructure project risk analyst.
Use only the supplied project context and evidence. Do not invent facts.
Every finding must cite one or more evidence IDs that exist in the input.
Return valid JSON only with a top-level key 'findings'. Each finding must contain:
risk, severity (low|medium|high|critical), confidence (0..1), evidence_ids,
rationale, recommended_action.
If evidence is insufficient, state that explicitly and lower confidence.
"""

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def discover_nvidia_model():
    models = list(client.models.list().data)
    all_ids = [getattr(m, "id", "") for m in models]
    candidates = [mid for mid in all_ids if "nvidia" in mid.lower() or "nemotron" in mid.lower()]
    print("Eligible NVIDIA/Nemotron candidates:")
    for mid in candidates:
        print(" -", mid)
    if MODEL_OVERRIDE:
        if MODEL_OVERRIDE not in all_ids:
            raise SystemExit("Configured NVIDIA_MODEL was not returned by /v1/models")
        return MODEL_OVERRIDE
    if not candidates:
        raise SystemExit("No NVIDIA/Nemotron model found. Set NVIDIA_MODEL after reviewing /v1/models.")
    candidates.sort(key=lambda x: ("nemotron" not in x.lower(), x.lower()))
    return candidates[0]

def evaluate_case(model, path):
    payload = json.loads(path.read_text())
    allowed = {e["id"] for e in payload["evidence"]}
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
    )
    latency_ms = round((time.perf_counter() - start) * 1000)
    parsed = json.loads(response.choices[0].message.content or "{}")
    findings = parsed.get("findings", [])
    cited = [eid for f in findings for eid in (f.get("evidence_ids") or [])]
    invalid = sorted(set(cited) - allowed)
    coverage = len(set(cited) & allowed) / len(allowed) if allowed else 0
    valid_shape = all(
        isinstance(f, dict)
        and f.get("severity") in {"low", "medium", "high", "critical"}
        and isinstance(f.get("confidence"), (int, float))
        and 0 <= f["confidence"] <= 1
        and isinstance(f.get("evidence_ids"), list)
        and bool(f.get("risk"))
        and bool(f.get("rationale"))
        and bool(f.get("recommended_action"))
        for f in findings
    )
    return {
        "case": path.stem,
        "latency_ms": latency_ms,
        "finding_count": len(findings),
        "valid_schema": valid_shape,
        "invalid_evidence_ids": invalid,
        "evidence_coverage": round(coverage, 3),
        "usage": response.usage.model_dump() if response.usage else None,
        "findings": findings,
    }

def main():
    model = discover_nvidia_model()
    case_paths = sorted(Path("data/cases").glob("*.json"))
    if not case_paths:
        raise SystemExit("No benchmark cases found")
    print("Selected model:", model)
    results = [evaluate_case(model, p) for p in case_paths]
    latencies = [r["latency_ms"] for r in results]
    report = {
        "provider": "Nebius Token Factory",
        "model": model,
        "run_epoch": int(time.time()),
        "case_count": len(results),
        "summary": {
            "schema_pass_rate": round(sum(r["valid_schema"] for r in results) / len(results), 3),
            "citation_validity_pass_rate": round(sum(not r["invalid_evidence_ids"] for r in results) / len(results), 3),
            "mean_evidence_coverage": round(statistics.mean(r["evidence_coverage"] for r in results), 3),
            "median_latency_ms": round(statistics.median(latencies)),
            "mean_latency_ms": round(statistics.mean(latencies)),
        },
        "results": results,
        "notes": "Synthetic/anonymized evaluation only. Metrics measure structured-output and citation integrity, not independent engineering correctness."
    }
    Path("artifacts/benchmark.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report["summary"], indent=2))
    print("Wrote artifacts/benchmark.json")

if __name__ == "__main__":
    main()
