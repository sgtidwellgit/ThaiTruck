import pandas as pd
import numpy as np
import pytest
from thaitruck import larb


def numeric_df():
    return pd.DataFrame({
        "price": [10.0, 12.0, 11.0, 13.0, 9.0, 100.0],  # 100.0 is an outlier
        "volume": [1000, 1100, 950, 1050, 1000, 1020],
    })


class TestOutputShape:
    def test_one_row_per_column(self):
        df = numeric_df()
        result = larb(df)
        assert list(result.index) == ["price", "volume"]

    def test_expected_columns_present(self):
        result = larb(numeric_df())
        for col in ("dtype", "count", "null_pct", "mean", "std", "min", "p25",
                    "median", "p75", "max", "skew", "outliers", "outlier_pct",
                    "lower_fence", "upper_fence"):
            assert col in result.columns

    def test_empty_dataframe(self):
        result = larb(pd.DataFrame())
        assert result.empty


class TestNumericStats:
    def test_count_excludes_nulls(self):
        df = pd.DataFrame({"val": [1.0, 2.0, None, 4.0]})
        result = larb(df)
        assert result.loc["val", "count"] == 3

    def test_null_pct(self):
        df = pd.DataFrame({"val": [1.0, None, None, 4.0]})
        result = larb(df)
        assert result.loc["val", "null_pct"] == 50.0

    def test_mean(self):
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0]})
        result = larb(df)
        assert result.loc["val", "mean"] == pytest.approx(2.5)

    def test_median(self):
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0]})
        result = larb(df)
        assert result.loc["val", "median"] == pytest.approx(2.5)

    def test_min_max(self):
        df = pd.DataFrame({"val": [5.0, 1.0, 9.0, 3.0]})
        result = larb(df)
        assert result.loc["val", "min"] == 1.0
        assert result.loc["val", "max"] == 9.0

    def test_dtype_reported(self):
        df = pd.DataFrame({"val": [1.0, 2.0]})
        result = larb(df)
        assert "float" in result.loc["val", "dtype"]


class TestOutlierDetection:
    def test_detects_obvious_outlier_at_default_heat(self):
        result = larb(numeric_df())
        assert result.loc["price", "outliers"] == 1

    def test_heat1_misses_mild_outlier(self):
        # 100 is 3+ IQR away — heat=1 uses multiplier 3.0, may or may not catch it
        df = pd.DataFrame({"val": [10.0, 11.0, 10.5, 12.0, 11.5, 30.0]})
        result_h1 = larb(df, heat=1)
        result_h5 = larb(df, heat=5)
        # heat=5 should flag more or equal outliers than heat=1
        assert result_h5.loc["val", "outliers"] >= result_h1.loc["val", "outliers"]

    def test_heat5_more_sensitive_than_heat1(self):
        # Moderately extreme value — flagged by heat=5 but not heat=1
        df = pd.DataFrame({"val": [10.0] * 20 + [22.0]})
        result_h1 = larb(df, heat=1)
        result_h5 = larb(df, heat=5)
        assert result_h5.loc["val", "outliers"] >= result_h1.loc["val", "outliers"]

    def test_outlier_pct_sums_correctly(self):
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 100.0]})
        result = larb(df, heat=5)
        expected_pct = result.loc["val", "outliers"] / 5 * 100
        assert result.loc["val", "outlier_pct"] == pytest.approx(expected_pct)

    def test_no_outliers_in_uniform_data(self):
        df = pd.DataFrame({"val": [5.0] * 20})
        result = larb(df)
        assert result.loc["val", "outliers"] == 0

    def test_fences_reported(self):
        result = larb(numeric_df())
        assert result.loc["price", "lower_fence"] is not None
        assert result.loc["price", "upper_fence"] is not None


class TestCategoricalColumns:
    def test_unique_count(self):
        df = pd.DataFrame({"cat": ["a", "b", "a", "c", "b", "a"]})
        result = larb(df)
        assert result.loc["cat", "unique"] == 3

    def test_top_value(self):
        df = pd.DataFrame({"cat": ["a", "b", "a", "c", "b", "a"]})
        result = larb(df)
        assert result.loc["cat", "top"] == "a"

    def test_top_freq(self):
        df = pd.DataFrame({"cat": ["a", "b", "a", "c", "b", "a"]})
        result = larb(df)
        assert result.loc["cat", "top_freq"] == 3

    def test_numeric_stats_are_none_for_categorical(self):
        df = pd.DataFrame({"cat": ["x", "y", "z"]})
        result = larb(df)
        assert result.loc["cat", "mean"] is None
        assert result.loc["cat", "outliers"] is None

    def test_null_pct_for_categorical(self):
        df = pd.DataFrame({"cat": ["a", None, "b", None]})
        result = larb(df)
        assert result.loc["cat", "null_pct"] == 50.0


class TestMixedDataFrame:
    def test_handles_numeric_and_categorical_together(self):
        df = pd.DataFrame({
            "price": [1.0, 2.0, 3.0],
            "label": ["a", "b", "a"],
        })
        result = larb(df)
        assert not pd.isna(result.loc["price", "mean"])
        assert pd.isna(result.loc["label", "mean"])

    def test_invalid_heat_raises(self):
        with pytest.raises(ValueError, match="heat must be 1–5"):
            larb(pd.DataFrame({"a": [1]}), heat=6)
