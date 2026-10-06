from demo import build_summary, load_snapshot


def test_fixture_is_synthetic():
    snapshot = load_snapshot()
    assert snapshot["project_id"].startswith("SYN-")


def test_scenario_is_non_authoritative():
    snapshot = load_snapshot()
    scenario = snapshot["scenario"]
    assert scenario["mode"] == "non_persistent_scenario"
    assert scenario["authoritative"] is False


def test_validated_memory_is_not_authoritative():
    snapshot = load_snapshot()
    validated = [
        item for item in snapshot["memory"]
        if item["lifecycle_state"] == "validated"
    ]
    assert validated
    assert all(item["authoritative"] is False for item in validated)


def test_truth_evidence_and_thread_are_visible():
    summary = build_summary(load_snapshot())
    assert summary["record_count"] >= 5
    assert summary["evidence_reference_count"] >= 5
    assert summary["digital_thread_relationships"] >= 5
    assert "certified" in summary["truth_states"]
    assert "paid" in summary["truth_states"]
