import pandas as pd
import pytest
from thaitruck import nam_pla, ValidationError, ThaiTruckError


def clean_df():
    return pd.DataFrame({
        "price": [10.0, 20.0, 30.0],
        "sector": ["Tech", "Energy", "Tech"],
    })


class TestCleanData:
    def test_no_violations_returns_empty_report(self):
        spec = {"price": {"dtype": float, "min": 0}, "sector": {"dtype": str, "nullable": False}}
        report = nam_pla(clean_df(), spec)
        assert report.empty
        assert list(report.columns) == ["column", "check", "message"]


class TestDtype:
    def test_float_accepts_int_dtype(self):
        df = pd.DataFrame({"price": [1, 2, 3]})
        report = nam_pla(df, {"price": {"dtype": float}})
        assert report.empty

    def test_str_mismatch_flagged(self):
        df = pd.DataFrame({"sector": [1, 2, 3]})
        report = nam_pla(df, {"sector": {"dtype": str}})
        assert (report["check"] == "dtype").any()

    def test_int_rejects_float_dtype(self):
        df = pd.DataFrame({"count": [1.0, 2.0]})
        report = nam_pla(df, {"count": {"dtype": int}})
        assert (report["check"] == "dtype").any()


class TestNullable:
    def test_nulls_flagged_when_not_nullable(self):
        df = pd.DataFrame({"price": [1.0, None, 3.0]})
        report = nam_pla(df, {"price": {"nullable": False}})
        assert (report["check"] == "nullable").any()

    def test_nulls_allowed_by_default(self):
        df = pd.DataFrame({"price": [1.0, None, 3.0]})
        report = nam_pla(df, {"price": {}})
        assert report.empty


class TestMinMax:
    def test_below_min_flagged(self):
        df = pd.DataFrame({"price": [-5.0, 10.0]})
        report = nam_pla(df, {"price": {"min": 0}})
        assert (report["check"] == "min").any()

    def test_above_max_flagged(self):
        df = pd.DataFrame({"price": [5.0, 999.0]})
        report = nam_pla(df, {"price": {"max": 100}})
        assert (report["check"] == "max").any()

    def test_in_range_passes(self):
        df = pd.DataFrame({"price": [5.0, 50.0, 99.0]})
        report = nam_pla(df, {"price": {"min": 0, "max": 100}})
        assert report.empty


class TestIsin:
    def test_disallowed_value_flagged(self):
        df = pd.DataFrame({"sector": ["Tech", "Bogus"]})
        report = nam_pla(df, {"sector": {"isin": ["Tech", "Energy"]}})
        assert (report["check"] == "isin").any()

    def test_allowed_values_pass(self):
        df = pd.DataFrame({"sector": ["Tech", "Energy"]})
        report = nam_pla(df, {"sector": {"isin": ["Tech", "Energy"]}})
        assert report.empty


class TestMissingColumn:
    def test_required_missing_column_flagged(self):
        df = pd.DataFrame({"price": [1.0]})
        report = nam_pla(df, {"sector": {"dtype": str}})
        assert (report["check"] == "missing_column").any()

    def test_optional_missing_column_not_flagged(self):
        df = pd.DataFrame({"price": [1.0]})
        report = nam_pla(df, {"sector": {"dtype": str, "required": False}})
        assert report.empty


class TestStrictMode:
    def test_strict_raises_on_violation(self):
        df = pd.DataFrame({"price": [-5.0]})
        with pytest.raises(ValidationError):
            nam_pla(df, {"price": {"min": 0}}, strict=True)

    def test_strict_raises_as_thaitruck_error(self):
        df = pd.DataFrame({"price": [-5.0]})
        with pytest.raises(ThaiTruckError):
            nam_pla(df, {"price": {"min": 0}}, strict=True)

    def test_strict_does_not_raise_when_clean(self):
        report = nam_pla(clean_df(), {"price": {"min": 0}}, strict=True)
        assert report.empty


class TestSpecValidation:
    def test_unknown_constraint_key_raises(self):
        with pytest.raises(ValueError, match="Unknown constraint"):
            nam_pla(clean_df(), {"price": {"bogus_key": 1}})
