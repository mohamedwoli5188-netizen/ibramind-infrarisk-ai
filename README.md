# IBRAMIND InfraRisk AI

Hackathon-specific infrastructure risk intelligence prototype for the Nebius x NVIDIA Global AI Hackathon 2026.

## What this repository contains

This repository isolates the new hackathon work from the pre-existing IBRAMIND Engineering Intelligence platform. The goal is to turn engineering/project evidence into traceable risk findings with citations, confidence, recommended actions, and human-review checkpoints.

## Hackathon architecture

- FastAPI service
- Nebius-hosted NVIDIA open-source model through an OpenAI-compatible inference API
- Structured risk-analysis schema
- Evidence-first prompts
- Synthetic/anonymized sample infrastructure evidence
- No production IBRAMIND secrets or customer data

## Required environment variables

Copy `.env.example` to `.env` and provide your own credentials.

```bash
NEBIUS_API_KEY=
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NVIDIA_MODEL=<verified NVIDIA/Nemotron model ID returned by /v1/models>
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Then POST JSON to `/analyze-risk`:

```bash
curl -X POST http://127.0.0.1:8000/analyze-risk \
  -H 'Content-Type: application/json' \
  -d @data/example_project.json
```

## What is new during the hackathon

The pre-existing IBRAMIND platform is not being submitted as if it were new. Hackathon-period work in this repository includes the InfraRisk workflow, Nebius-hosted NVIDIA-model integration layer, evidence schema, evaluation cases, public documentation, and demo flow.

## Status

Public hackathon build in progress. The repository will be updated with the final tested Nebius model identifier, benchmark notes, hosted demo URL, and public demo video before submission.

## License

MIT


## NVIDIA model selection

The live benchmark script queries the Nebius Token Factory /v1/models endpoint, prints NVIDIA/Nemotron candidates, and verifies the selected model ID before any benchmark is recorded. This avoids claiming a model that is not actually available to the account. Final Devpost quality ratings are based only on measured live runs.

## API endpoint

`https://api.tokenfactory.nebius.com/v1/`

The API key is intentionally excluded from source control.


## Reproducible live benchmark

After configuring NEBIUS_API_KEY, run: python scripts/benchmark.py

The script discovers eligible NVIDIA/Nemotron models from the live Nebius API, runs three synthetic infrastructure cases, validates evidence citations and structured output, records latency/token usage, and writes artifacts/benchmark.json.

The benchmark intentionally does not claim independent engineering correctness; it measures observable runtime and provenance properties that judges can reproduce.
