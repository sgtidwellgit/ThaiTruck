import pandas as pd
import pytest
from thaitruck import fried_rice


def daily(data: dict, start="2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(next(iter(data.values()))), freq="D")
    return pd.DataFrame(data, index=idx)


def with_date_col(data: dict, start="2024-01-01", col="date") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(next(iter(data.values()))), freq="D")
    df = pd.DataFrame(data)
    df[col] = idx
    return df


class TestBasicMerge:
    def test_two_nonoverlapping_columns(self):
        a = daily({"price": [1, 2, 3]})
        b = daily({"volume": [10, 20, 30]})
        result = fried_rice(a, b)
        assert "price" in result.columns
        assert "volume" in result.columns
        assert len(result) == 3

    def test_single_df_passthrough(self):
        a = daily({"price": [1, 2, 3]})
        result = fried_rice(a)
        pd.testing.assert_frame_equal(result, a)

    def test_empty_returns_empty(self):
        result = fried_rice()
        assert result.empty


class TestDateColDetection:
    def test_detects_date_named_column(self):
        df = with_date_col({"price": [1, 2, 3]}, col="date")
        result = fried_rice(df)
        assert pd.api.types.is_datetime64_any_dtype(result.index)

    def test_detects_report_date_column(self):
        df = with_date_col({"eps": [1.5, 1.6, 1.7]}, col="report_date")
        result = fried_rice(df)
        assert pd.api.types.is_datetime64_any_dtype(result.index)

    def test_explicit_date_col_override(self):
        df = with_date_col({"val": [1, 2, 3]}, col="my_ts")
        result = fried_rice(df, date_col="my_ts")
        assert pd.api.types.is_datetime64_any_dtype(result.index)

    def test_raises_when_no_date_found(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="no date column detected"):
            fried_rice(df)


class TestFrequencyResampling:
    def test_quarterly_upsampled_to_daily(self):
        # "Q" (not "QE") on purpose: "QE" doesn't exist before pandas 2.2,
        # "Q" works everywhere ThaiTruck supports (pandas>=1.5) — deprecated
        # but functional on pandas 2.x, native on 1.5.
        dates = pd.date_range("2024-01-01", periods=4, freq="Q")
        quarterly = pd.DataFrame({"eps": [1.0, 1.2, 1.1, 1.3]}, index=dates)
        daily_prices = daily({"price": range(365)}, start="2024-01-01")
        result = fried_rice(quarterly, daily_prices, freq="D")
        assert len(result) >= 365
        assert result["eps"].notna().any()

    def test_forward_fill_propagates(self):
        dates = pd.to_datetime(["2024-01-01", "2024-04-01"])
        df = pd.DataFrame({"val": [10, 20]}, index=dates)
        result = fried_rice(df, freq="D", fill_method="ffill")
        assert result.loc["2024-02-15", "val"] == 10
        assert result.loc["2024-04-01", "val"] == 20


class TestHeatLevels:
    def _overlapping(self):
        a = daily({"price": [1, 2, 3], "shared": [10, 20, 30]})
        b = daily({"volume": [4, 5, 6], "shared": [40, 50, 60]})
        return a, b

    def test_heat1_keeps_first(self):
        a, b = self._overlapping()
        result = fried_rice(a, b, heat=1)
        assert list(result["shared"]) == [10, 20, 30]

    def test_heat4_keeps_last(self):
        a, b = self._overlapping()
        result = fried_rice(a, b, heat=4)
        assert list(result["shared"]) == [40, 50, 60]

    def test_heat3_creates_suffixed_columns(self):
        a, b = self._overlapping()
        result = fried_rice(a, b, heat=3)
        assert "shared" in result.columns
        assert "shared_1" in result.columns

    def test_heat5_napalm_last_nonnull_wins(self):
        a = daily({"val": [1, None, 3]})
        b = daily({"val": [None, 2, None]})
        result = fried_rice(a, b, heat=5)
        assert result["val"].notna().all()


class TestFuzzyColumns:
    def test_normalizes_case_and_separators(self):
        a = daily({"Close Price": [1, 2, 3]})
        b = daily({"close_price": [4, 5, 6]})
        result = fried_rice(a, b, fuzzy_columns=True, heat=4)
        assert "close_price" in result.columns
        assert result["close_price"].iloc[0] == 4


class TestJoin:
    def test_outer_is_default_union_of_index(self):
        a = daily({"price": [1, 2, 3]}, start="2024-01-01")
        b = daily({"volume": [10, 20, 30]}, start="2024-01-02")
        result = fried_rice(a, b, join="outer")
        assert len(result) == 4

    def test_inner_keeps_only_overlap(self):
        a = daily({"price": [1, 2, 3]}, start="2024-01-01")
        b = daily({"volume": [10, 20, 30]}, start="2024-01-02")
        result = fried_rice(a, b, join="inner")
        assert len(result) == 2

    def test_left_keeps_only_first_frame_index(self):
        a = daily({"price": [1, 2, 3]}, start="2024-01-01")
        b = daily({"volume": [10, 20, 30]}, start="2024-01-02")
        result = fried_rice(a, b, join="left")
        assert len(result) == 3

    def test_invalid_join_raises(self):
        a = daily({"price": [1, 2, 3]})
        b = daily({"volume": [10, 20, 30]})
        with pytest.raises(ValueError, match="join must be"):
            fried_rice(a, b, join="bogus")


class TestSuffixTemplate:
    def test_custom_suffix_template(self):
        a = daily({"price": [1, 2, 3], "shared": [10, 20, 30]})
        b = daily({"volume": [4, 5, 6], "shared": [40, 50, 60]})
        result = fried_rice(a, b, heat=3, suffix_template="_src{i}")
        assert "shared_src1" in result.columns

    def test_default_suffix_unchanged_when_not_set(self):
        a = daily({"shared": [10, 20, 30]})
        b = daily({"shared": [40, 50, 60]})
        result = fried_rice(a, b, heat=3)
        assert "shared_1" in result.columns


class TestTimezoneHandling:
    def test_tz_aware_index_is_stripped_and_mergeable(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
        a = pd.DataFrame({"price": [1, 2, 3]}, index=idx)
        b = daily({"volume": [10, 20, 30]})
        result = fried_rice(a, b)
        assert result.index.tz is None
        assert "volume" in result.columns
