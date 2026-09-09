import pandas as pd
import pytest
from thaitruck import massaman


def price_df():
    return pd.DataFrame({"price": [float(i) for i in range(1, 31)]})


class TestRollingOps:
    def test_rolling_mean_default(self):
        df = price_df()
        result = massaman(df, "price", window=5)
        assert "price_roll_mean_5" in result.columns
        assert result["price_roll_mean_5"].iloc[4] == pytest.approx(3.0)

    def test_rolling_std(self):
        df = price_df()
        result = massaman(df, "price", window=5, ops=["std"])
        assert "price_roll_std_5" in result.columns

    def test_multiple_ops_add_multiple_columns(self):
        df = price_df()
        result = massaman(df, "price", window=20, ops=["mean", "std", "pct_change"])
        assert "price_roll_mean_20" in result.columns
        assert "price_roll_std_20" in result.columns
        assert "price_pct_change" in result.columns

    def test_min_max_sum_median(self):
        df = price_df()
        result = massaman(df, "price", window=3, ops=["min", "max", "sum", "median"])
        assert result["price_roll_min_3"].iloc[2] == 1.0
        assert result["price_roll_max_3"].iloc[2] == 3.0
        assert result["price_roll_sum_3"].iloc[2] == 6.0
        assert result["price_roll_median_3"].iloc[2] == 2.0


class TestPctChange:
    def test_pct_change_not_windowed(self):
        df = pd.DataFrame({"price": [10.0, 20.0, 40.0]})
        result = massaman(df, "price", ops=["pct_change"])
        assert result["price_pct_change"].iloc[1] == pytest.approx(1.0)
        assert result["price_pct_change"].iloc[2] == pytest.approx(1.0)


class TestEdgeCases:
    def test_missing_column_raises(self):
        df = price_df()
        with pytest.raises(KeyError):
            massaman(df, "nonexistent")

    def test_unsupported_op_raises(self):
        df = price_df()
        with pytest.raises(ValueError, match="Unsupported op"):
            massaman(df, "price", ops=["bogus"])

    def test_does_not_mutate_input(self):
        df = price_df()
        original_cols = list(df.columns)
        massaman(df, "price", window=5)
        assert list(df.columns) == original_cols

    def test_preserves_original_columns(self):
        df = pd.DataFrame({"price": [1.0, 2.0, 3.0], "sector": ["a", "b", "c"]})
        result = massaman(df, "price", window=2)
        assert "sector" in result.columns
        assert "price" in result.columns
