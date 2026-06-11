import pandas as pd
import pytest
from thaitruck import satay


@pytest.fixture
def df():
    return pd.DataFrame({
        "name":   ["Alice", "Bob", "Carol", "Dave", "Eve"],
        "sector": ["Tech", "Energy", "Tech", "Health", "Energy"],
        "price":  [10.0, 25.0, 15.0, 8.0, 30.0],
        "volume": [100, 200, 150, 50, 300],
    })


class TestColumnSelection:
    def test_single_column_string(self, df):
        result = satay(df, "price")
        assert list(result.columns) == ["price"]

    def test_multiple_columns_list(self, df):
        result = satay(df, ["price", "volume"])
        assert list(result.columns) == ["price", "volume"]

    def test_no_skewers_returns_copy(self, df):
        result = satay(df)
        pd.testing.assert_frame_equal(result, df)

    def test_missing_column_raises(self, df):
        with pytest.raises(KeyError):
            satay(df, "nonexistent")


class TestRowSlice:
    def test_positional_slice(self, df):
        result = satay(df, slice(0, 2))
        assert len(result) == 2
        assert list(result["name"]) == ["Alice", "Bob"]

    def test_slice_with_step(self, df):
        result = satay(df, slice(None, None, 2))
        assert len(result) == 3  # rows 0, 2, 4


class TestTupleRangeFilter:
    def test_numeric_range(self, df):
        result = satay(df, ("price", 10.0, 20.0))
        assert all(10.0 <= p <= 20.0 for p in result["price"])

    def test_range_excludes_outside(self, df):
        result = satay(df, ("price", 10.0, 20.0))
        assert 25.0 not in result["price"].values
        assert 30.0 not in result["price"].values

    def test_bad_tuple_length_raises(self, df):
        with pytest.raises(ValueError, match="[Tt]uple skewer must be"):
            satay(df, ("price", 10))


class TestDictFilter:
    def test_equality_filter(self, df):
        result = satay(df, {"sector": "Tech"})
        assert all(s == "Tech" for s in result["sector"])
        assert len(result) == 2

    def test_isin_filter(self, df):
        result = satay(df, {"sector": ["Tech", "Health"]})
        assert set(result["sector"]) == {"Tech", "Health"}

    def test_multi_key_dict_filters_all(self, df):
        result = satay(df, {"sector": "Tech", "price": 10.0})
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Alice"


class TestCallableFilter:
    def test_lambda_mask(self, df):
        result = satay(df, lambda d: d["volume"] > 150)
        assert all(v > 150 for v in result["volume"])

    def test_named_function(self, df):
        def high_value(d):
            return d["price"] > 20

        result = satay(df, high_value)
        assert all(p > 20 for p in result["price"])


class TestCombined:
    def test_filter_then_columns(self, df):
        result = satay(df, {"sector": "Tech"}, "price")
        assert list(result.columns) == ["price"]
        assert len(result) == 2

    def test_slice_then_columns(self, df):
        result = satay(df, slice(0, 3), ["name", "price"])
        assert list(result.columns) == ["name", "price"]
        assert len(result) == 3

    def test_invalid_skewer_type_raises(self, df):
        with pytest.raises(TypeError, match="Unrecognised skewer"):
            satay(df, 42)
