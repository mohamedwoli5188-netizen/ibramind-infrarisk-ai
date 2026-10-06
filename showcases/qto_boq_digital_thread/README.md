# IBRAMIND QTO / BOQ + Digital Thread Showcase

This is a **safe public demonstrator** of one IBRAMIND engineering-intelligence workflow.

It uses synthetic data only. It does not contain production Customer OMNI code, tenant data, proprietary commercial rules, private APIs, credentials, or Founder controls.

## What it demonstrates

A simplified public flow:

```
Drawing / BIM reference
        ↓
Quantity Takeoff
        ↓
BOQ item
        ↓
Measurement record
        ↓
Commercial record
        ↓
Digital Thread relationships
        ↓
Evidence references
        ↓
Truth-state summary
```

The goal is not to reproduce the private IBRAMIND platform. The goal is to demonstrate the principles behind connected, traceable engineering records.

## Run

```bash
python showcases/qto_boq_digital_thread/demo.py
```

The script reads the bundled synthetic project and prints:

- QTO quantities
- linked BOQ records
- measurement/commercial relationships
- evidence references
- truth states
- downstream relationship paths

## Safety boundary

This showcase intentionally excludes:

- production tenant isolation implementation
- private database schema
- proprietary pricing or contract logic
- private Project Truth implementation
- production Evidence Passport internals
- private Digital Thread graph implementation
- customer data
- live project documents
- production infrastructure

The private IBRAMIND platform remains the authoritative product.

For commercial pilots: https://ibramind.com
