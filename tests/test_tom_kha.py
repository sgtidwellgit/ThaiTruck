import pytest
from thaitruck import tom_kha


class TestShallowMerge:
    def test_single_config_returned_as_is(self):
        result = tom_kha({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_later_config_wins(self):
        result = tom_kha({"a": 1}, {"a": 99})
        assert result["a"] == 99

    def test_non_overlapping_keys_merged(self):
        result = tom_kha({"a": 1}, {"b": 2})
        assert result == {"a": 1, "b": 2}

    def test_three_configs_last_wins(self):
        result = tom_kha({"x": 1}, {"x": 2}, {"x": 3})
        assert result["x"] == 3

    def test_empty_configs_returns_empty(self):
        assert tom_kha() == {}


class TestDeepMerge:
    def test_nested_dicts_merged_recursively(self):
        a = {"db": {"host": "localhost", "port": 5432}}
        b = {"db": {"port": 5433}}
        result = tom_kha(a, b)
        assert result["db"]["host"] == "localhost"
        assert result["db"]["port"] == 5433

    def test_deeply_nested(self):
        a = {"l1": {"l2": {"l3": "original"}}}
        b = {"l1": {"l2": {"l3": "override", "new": "val"}}}
        result = tom_kha(a, b)
        assert result["l1"]["l2"]["l3"] == "override"
        assert result["l1"]["l2"]["new"] == "val"

    def test_list_values_overwritten_not_merged(self):
        result = tom_kha({"tags": [1, 2, 3]}, {"tags": [4, 5]})
        assert result["tags"] == [4, 5]

    def test_dict_does_not_overwrite_with_scalar(self):
        result = tom_kha({"cfg": {"a": 1}}, {"cfg": "replaced"})
        assert result["cfg"] == "replaced"

    def test_scalar_does_not_overwrite_with_dict(self):
        result = tom_kha({"cfg": "original"}, {"cfg": {"a": 1}})
        assert result["cfg"] == {"a": 1}


class TestDefaults:
    def test_defaults_lowest_precedence(self):
        result = tom_kha({"a": 99}, defaults={"a": 1, "b": 2})
        assert result["a"] == 99
        assert result["b"] == 2

    def test_defaults_fills_missing_keys(self):
        result = tom_kha({"x": 10}, defaults={"x": 0, "y": 20, "z": 30})
        assert result["x"] == 10
        assert result["y"] == 20

    def test_defaults_none_is_noop(self):
        result = tom_kha({"a": 1}, defaults=None)
        assert result == {"a": 1}

    def test_defaults_deep_merge(self):
        result = tom_kha(
            {"server": {"port": 8080}},
            defaults={"server": {"host": "0.0.0.0", "port": 80}},
        )
        assert result["server"]["host"] == "0.0.0.0"
        assert result["server"]["port"] == 8080


class TestEdgeCases:
    def test_non_dict_raises(self):
        with pytest.raises(TypeError, match="must be dicts"):
            tom_kha({"a": 1}, [1, 2, 3])

    def test_does_not_mutate_inputs(self):
        a = {"x": 1}
        b = {"x": 2}
        tom_kha(a, b)
        assert a["x"] == 1
        assert b["x"] == 2

    def test_nested_does_not_mutate(self):
        a = {"db": {"host": "localhost"}}
        b = {"db": {"port": 5432}}
        tom_kha(a, b)
        assert "port" not in a["db"]
