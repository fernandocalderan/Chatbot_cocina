from app.services.flow_diff import diff_json


def test_diff_json_basic():
    base = {"a": 1, "b": {"c": 2}, "list": [1, 2]}
    override = {"a": 1, "b": {"c": 3}, "d": True, "list": [1, 2, 3]}
    diff = diff_json(base, override)
    assert "b.c" in diff["changed"]
    assert "d" in diff["added"]
    assert "list" in diff["changed"]
