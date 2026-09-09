import numpy as np
import pandas as pd
import pytest
from thaitruck import som_tam


class TestIndexBasedIdentity:
    def test_added_row(self):
        before = pd.DataFrame({"price": [1.0, 2.0]}, index=[1, 2])
        after = pd.DataFrame({"price": [1.0, 2.0, 3.0]}, index=[1, 2, 3])
        diff = som_tam(before, after)
        assert diff.loc[3, "change_type"] == "added"

    def test_removed_row(self):
        before = pd.DataFrame({"price": [1.0, 2.0]}, index=[1, 2])
        after = pd.DataFrame({"price": [1.0]}, index=[1])
        diff = som_tam(before, after)
        assert diff.loc[2, "change_type"] == "removed"

    def test_modified_row(self):
        before = pd.DataFrame({"price": [1.0, 2.0]}, index=[1, 2])
        after = pd.DataFrame({"price": [1.0, 99.0]}, index=[1, 2])
        diff = som_tam(before, after)
        assert diff.loc[2, "change_type"] == "modified"
        assert diff.loc[2, "columns_changed"] == "price"

    def test_unchanged_row_omitted(self):
        before = pd.DataFrame({"price": [1.0]}, index=[1])
        after = pd.DataFrame({"price": [1.0]}, index=[1])
        diff = som_tam(before, after)
        assert diff.empty

    def test_identical_frames_empty_diff(self):
        df = pd.DataFrame({"price": [1.0, 2.0], "sector": ["Tech", "Energy"]})
        diff = som_tam(df, df.copy())
        assert diff.empty


class TestKeyBasedIdentity:
    def test_key_column_identity(self):
        before = pd.DataFrame({"id": [1, 2], "price": [10.0, 20.0]})
        after = pd.DataFrame({"id": [1, 2, 3], "price": [10.0, 25.0, 30.0]})
        diff = som_tam(before, after, key="id")
        assert diff.loc[2, "change_type"] == "modified"
        assert diff.loc[3, "change_type"] == "added"

    def test_multi_column_key(self):
        before = pd.DataFrame({"a": [1, 1], "b": [1, 2], "price": [10.0, 20.0]})
        after = pd.DataFrame({"a": [1, 1], "b": [1, 2], "price": [10.0, 99.0]})
        diff = som_tam(before, after, key=["a", "b"])
        assert diff.loc[(1, 2), "change_type"] == "modified"

    def test_missing_key_column_raises(self):
        before = pd.DataFrame({"id": [1], "price": [10.0]})
        after = pd.DataFrame({"price": [10.0]})
        with pytest.raises(KeyError):
            som_tam(before, after, key="id")


class TestDuplicateIdentity:
    def test_duplicate_index_raises(self):
        before = pd.DataFrame({"price": [1.0, 2.0]}, index=[1, 1])
        after = pd.DataFrame({"price": [1.0, 2.0]}, index=[1, 2])
        with pytest.raises(ValueError, match="duplicate"):
            som_tam(before, after)

    def test_duplicate_key_column_raises(self):
        before = pd.DataFrame({"id": [1, 1], "price": [10.0, 20.0]})
        after = pd.DataFrame({"id": [1, 2], "price": [10.0, 20.0]})
        with pytest.raises(ValueError, match="duplicate"):
            som_tam(before, after, key="id")


class TestNullHandling:
    def test_nan_equals_nan_not_flagged(self):
        before = pd.DataFrame({"price": [np.nan]}, index=[1])
        after = pd.DataFrame({"price": [np.nan]}, index=[1])
        diff = som_tam(before, after)
        assert diff.empty

    def test_nan_to_value_is_modified(self):
        before = pd.DataFrame({"price": [np.nan]}, index=[1])
        after = pd.DataFrame({"price": [5.0]}, index=[1])
        diff = som_tam(before, after)
        assert diff.loc[1, "change_type"] == "modified"


class TestSchemaDrift:
    def test_columns_added_in_attrs(self):
        before = pd.DataFrame({"price": [1.0]}, index=[1])
        after = pd.DataFrame({"price": [1.0], "volume": [100]}, index=[1])
        diff = som_tam(before, after)
        assert diff.attrs["columns_added"] == ["volume"]
        assert diff.attrs["columns_removed"] == []

    def test_columns_removed_in_attrs(self):
        before = pd.DataFrame({"price": [1.0], "volume": [100]}, index=[1])
        after = pd.DataFrame({"price": [1.0]}, index=[1])
        diff = som_tam(before, after)
        assert diff.attrs["columns_removed"] == ["volume"]

    def test_dropped_column_not_compared_as_modified(self):
        before = pd.DataFrame({"price": [1.0], "volume": [100]}, index=[1])
        after = pd.DataFrame({"price": [1.0]}, index=[1])
        diff = som_tam(before, after)
        assert diff.empty  # only schema drift, no row-level change


class TestMultipleColumnsChanged:
    def test_multiple_changed_columns_joined(self):
        before = pd.DataFrame({"price": [1.0], "volume": [100]}, index=[1])
        after = pd.DataFrame({"price": [2.0], "volume": [200]}, index=[1])
        diff = som_tam(before, after)
        changed = diff.loc[1, "columns_changed"]
        assert "price" in changed
        assert "volume" in changed


class TestDoesNotMutate:
    def test_inputs_unmodified(self):
        before = pd.DataFrame({"id": [1], "price": [1.0]})
        after = pd.DataFrame({"id": [1], "price": [2.0]})
        before_cols = list(before.columns)
        som_tam(before, after, key="id")
        assert list(before.columns) == before_cols
        assert "id" in before.columns
