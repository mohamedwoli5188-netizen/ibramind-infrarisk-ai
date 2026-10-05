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
NVIDIA_MODEL=nvidia/Nemotron-3_5-Lightning
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


## NVIDIA model selected

The hackathon build targets `nvidia/Nemotron-3_5-Lightning` through Nebius Token Factory's OpenAI-compatible endpoint. This model was selected for the first live evaluation because Nebius currently exposes it as a public Nemotron endpoint suited to efficient reasoning/coding-style tasks. The final Devpost quality ratings will be based only on measured hackathon runs, not assumptions.

## API endpoint

`https://api.tokenfactory.nebius.com/v1/`

The API key is intentionally excluded from source control.
