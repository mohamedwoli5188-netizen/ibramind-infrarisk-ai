from demo import build_thread, load_project, summarize


def test_synthetic_fixture_only():
    project = load_project()
    assert project["project_id"].startswith("SYN-")


def test_expected_thread_shape():
    project = load_project()
    edges = build_thread(project)
    relations = {edge["relation"] for edge in edges}

    assert "supports_quantity_takeoff" in relations
    assert "maps_to_boq" in relations
    assert "measured_by" in relations
    assert "included_in" in relations


def test_truth_states_are_visible():
    project = load_project()
    summary = summarize(project, build_thread(project))
    assert "measured" in summary["truth_states"]
    assert "approved" in summary["truth_states"]
    assert "certified" in summary["truth_states"]
