import pandas as pd
import numpy as np
import pytest
from thaitruck import orange_chicken


class TestColumnNames:
    def test_lowercases(self):
        df = pd.DataFrame({"Price": [1], "Volume": [2]})
        result = orange_chicken(df, heat=1)
        assert list(result.columns) == ["price", "volume"]

    def test_strips_whitespace(self):
        df = pd.DataFrame({" date ": [1], "  close  ": [2]})
        result = orange_chicken(df, heat=1)
        assert "date" in result.columns
        assert "close" in result.columns

    def test_spaces_to_underscores(self):
        df = pd.DataFrame({"Open Price": [1]})
        result = orange_chicken(df, heat=1)
        assert "open_price" in result.columns

    def test_hyphens_and_dots_to_underscores(self):
        df = pd.DataFrame({"adj-close": [1], "report.date": [2]})
        result = orange_chicken(df, heat=1)
        assert "adj_close" in result.columns
        assert "report_date" in result.columns

    def test_collapses_multiple_underscores(self):
        df = pd.DataFrame({"a__b___c": [1]})
        result = orange_chicken(df, heat=1)
        assert "a_b_c" in result.columns

    def test_removes_special_chars(self):
        df = pd.DataFrame({"price($)": [1]})
        result = orange_chicken(df, heat=1)
        assert "price" in result.columns


class TestStringStripping:
    def test_strips_cell_whitespace(self):
        df = pd.DataFrame({"name": ["  Alice  ", " Bob", "Carol "]})
        result = orange_chicken(df, heat=2)
        assert list(result["name"]) == ["Alice", "Bob", "Carol"]

    def test_preserves_non_string_values(self):
        df = pd.DataFrame({"val": [1.0, 2.0, None]})
        result = orange_chicken(df, heat=2)
        assert result["val"].iloc[0] == 1.0

    def test_drops_all_null_rows(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": [4, None, 6]})
        result = orange_chicken(df, heat=2)
        assert len(result) == 2

    def test_drops_all_null_columns(self):
        df = pd.DataFrame({"a": [1, 2], "b": [None, None]})
        result = orange_chicken(df, heat=2)
        assert "b" not in result.columns


class TestNumericCoercion:
    def test_coerces_numeric_strings(self):
        df = pd.DataFrame({"price": ["1.5", "2.3", "0.9"]})
        result = orange_chicken(df, heat=3)
        assert pd.api.types.is_numeric_dtype(result["price"])
        assert result["price"].iloc[0] == 1.5

    def test_leaves_mostly_non_numeric_alone(self):
        df = pd.DataFrame({"name": ["Alice", "Bob", "42"]})
        result = orange_chicken(df, heat=3)
        assert result["name"].dtype == object

    def test_coerces_mixed_if_majority_numeric(self):
        df = pd.DataFrame({"val": ["1", "2", "3", "4", "oops"]})
        result = orange_chicken(df, heat=3)
        assert pd.api.types.is_numeric_dtype(result["val"])

    def test_already_numeric_unchanged(self):
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
        result = orange_chicken(df, heat=3)
        assert pd.api.types.is_numeric_dtype(result["val"])


class TestBooleanCoercion:
    def test_coerces_true_false_strings(self):
        df = pd.DataFrame({"flag": ["true", "false", "true"]})
        result = orange_chicken(df, heat=4)
        assert list(result["flag"]) == [True, False, True]

    def test_coerces_yes_no(self):
        df = pd.DataFrame({"active": ["yes", "no", "yes"]})
        result = orange_chicken(df, heat=4)
        assert list(result["active"]) == [True, False, True]

    def test_coerces_case_insensitive(self):
        df = pd.DataFrame({"flag": ["TRUE", "False", "YES"]})
        result = orange_chicken(df, heat=4)
        assert list(result["flag"]) == [True, False, True]

    def test_leaves_mixed_column_alone(self):
        df = pd.DataFrame({"col": ["true", "false", "maybe", "idk"]})
        result = orange_chicken(df, heat=4)
        assert result["col"].dtype == object

    def test_drops_90pct_null_columns(self):
        data = {"good": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        sparse = [None] * 10
        sparse[0] = 1
        data["sparse"] = sparse
        df = pd.DataFrame(data)
        result = orange_chicken(df, heat=4)
        assert "sparse" not in result.columns
        assert "good" in result.columns


class TestHeat5:
    def test_drops_50pct_null_columns(self):
        df = pd.DataFrame({
            "good": [1, 2, 3, 4],
            "half": [1, None, None, 4],
        })
        result = orange_chicken(df, heat=5)
        assert "half" not in result.columns
        assert "good" in result.columns


class TestEdgeCases:
    def test_invalid_heat_raises(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(ValueError, match="heat must be 1–5"):
            orange_chicken(df, heat=6)

    def test_empty_dataframe(self):
        result = orange_chicken(pd.DataFrame(), heat=3)
        assert result.empty

    def test_does_not_mutate_input(self):
        df = pd.DataFrame({"Price": ["  1.5  ", "  2.0  "]})
        original_col = list(df.columns)
        orange_chicken(df, heat=3)
        assert list(df.columns) == original_col


class TestRename:
    def test_renames_after_cleaning(self):
        df = pd.DataFrame({"Open Price": [1.0, 2.0]})
        result = orange_chicken(df, heat=1, rename={"open_price": "price"})
        assert "price" in result.columns
        assert "open_price" not in result.columns

    def test_no_rename_when_not_given(self):
        df = pd.DataFrame({"Price": [1.0]})
        result = orange_chicken(df, heat=1)
        assert "price" in result.columns


class TestDtypes:
    def test_applies_dtype_override(self):
        df = pd.DataFrame({"price": ["1", "2", "3"]})
        result = orange_chicken(df, heat=1, dtypes={"price": "int64"})
        assert result["price"].dtype == "int64"

    def test_dtypes_applied_after_rename(self):
        df = pd.DataFrame({"Open Price": ["1.5", "2.5"]})
        result = orange_chicken(
            df, heat=1, rename={"open_price": "price"}, dtypes={"price": "float64"}
        )
        assert result["price"].dtype == "float64"
