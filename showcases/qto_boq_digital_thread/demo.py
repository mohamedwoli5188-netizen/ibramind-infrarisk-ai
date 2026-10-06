from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "synthetic_project.json"


def load_project() -> dict:
    with DATA.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def build_thread(project: dict) -> list[dict]:
    edges: list[dict] = []

    drawing = project["drawing"]
    for qto in project["qto"]:
        edges.append({
            "from": drawing["id"],
            "relation": "supports_quantity_takeoff",
            "to": qto["id"],
            "evidence": [drawing["evidence_ref"], qto["evidence_ref"]],
        })

    for boq in project["boq"]:
        edges.append({
            "from": boq["qto_id"],
            "relation": "maps_to_boq",
            "to": boq["id"],
            "evidence": [boq["evidence_ref"]],
        })

    for measurement in project["measurements"]:
        edges.append({
            "from": measurement["boq_id"],
            "relation": "measured_by",
            "to": measurement["id"],
            "evidence": [measurement["evidence_ref"]],
        })

    for commercial in project["commercial"]:
        for measurement_id in commercial["measurement_ids"]:
            edges.append({
                "from": measurement_id,
                "relation": "included_in",
                "to": commercial["id"],
                "evidence": [commercial["evidence_ref"]],
            })

    return edges


def summarize(project: dict, edges: list[dict]) -> dict:
    return {
        "project": project["project_name"],
        "qto_records": len(project["qto"]),
        "boq_records": len(project["boq"]),
        "measurement_records": len(project["measurements"]),
        "commercial_records": len(project["commercial"]),
        "digital_thread_relationships": len(edges),
        "truth_states": sorted({
            project["drawing"]["truth_state"],
            *(x["truth_state"] for x in project["qto"]),
            *(x["truth_state"] for x in project["boq"]),
            *(x["truth_state"] for x in project["measurements"]),
            *(x["truth_state"] for x in project["commercial"]),
        }),
    }


def main() -> None:
    project = load_project()
    edges = build_thread(project)
    result = {
        "summary": summarize(project, edges),
        "digital_thread": edges,
        "note": (
            "Synthetic public demonstrator only. Relationships and truth-state labels "
            "illustrate IBRAMIND principles and are not the private production implementation."
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
