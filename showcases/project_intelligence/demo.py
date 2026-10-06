from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "project_snapshot.json"


def load_snapshot() -> dict:
    with DATA.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_summary(snapshot: dict) -> dict:
    records = snapshot["records"]
    evidence_refs = {ref for record in records for ref in record["evidence_refs"]}
    truth_states = Counter(record["truth_state"] for record in records)

    impact_targets = [
        edge["to"]
        for edge in snapshot["relationships"]
        if edge["relation"] == "may_impact"
    ]

    validated_memory = [
        item for item in snapshot["memory"]
        if item["lifecycle_state"] == "validated"
    ]

    scenario = snapshot["scenario"]
    if scenario["authoritative"] is not False:
        raise ValueError("Public scenario must remain non-authoritative")
    if scenario["mode"] != "non_persistent_scenario":
        raise ValueError("Public scenario must remain non-persistent")

    return {
        "project": snapshot["project_name"],
        "record_count": len(records),
        "truth_states": dict(sorted(truth_states.items())),
        "evidence_reference_count": len(evidence_refs),
        "digital_thread_relationships": len(snapshot["relationships"]),
        "change_impact_targets": impact_targets,
        "validated_memory_count": len(validated_memory),
        "validated_memory": validated_memory,
        "scenario": scenario,
        "governance_note": (
            "Validated memory is reusable knowledge, not certification. "
            "Scenario output is hypothetical, non-persistent and non-authoritative."
        ),
    }


def main() -> None:
    snapshot = load_snapshot()
    print(json.dumps(build_summary(snapshot), indent=2))


if __name__ == "__main__":
    main()
