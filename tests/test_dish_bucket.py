import importlib

import numpy as np
import pandas as pd
import pytest
from thaitruck import dish_bucket

dish_bucket_module = importlib.import_module("thaitruck.dish_bucket")


class TestDowncasting:
    def test_downcasts_small_int64_to_smaller_int(self):
        df = pd.DataFrame({"a": np.array([1, 2, 3], dtype="int64")})
        result = dish_bucket(df)
        assert result["a"].dtype.itemsize < df["a"].dtype.itemsize

    def test_downcasts_small_float64_to_float32(self):
        df = pd.DataFrame({"a": np.array([1.5, 2.5, 3.5], dtype="float64")})
        result = dish_bucket(df)
        assert result["a"].dtype == np.float32

    def test_preserves_values(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [1.5, 2.5, 3.5]})
        result = dish_bucket(df)
        assert list(result["a"]) == [1, 2, 3]
        assert list(result["b"]) == [1.5, 2.5, 3.5]

    def test_large_int_stays_safe(self):
        big = 2**40
        df = pd.DataFrame({"a": np.array([big], dtype="int64")})
        result = dish_bucket(df)
        assert result["a"].iloc[0] == big

    def test_non_numeric_columns_untouched(self):
        df = pd.DataFrame({"a": [1], "label": ["x"]})
        result = dish_bucket(df)
        assert result["label"].dtype == object

    def test_does_not_mutate_input(self):
        df = pd.DataFrame({"a": np.array([1, 2], dtype="int64")})
        original_dtype = df["a"].dtype
        dish_bucket(df)
        assert df["a"].dtype == original_dtype


class TestReport:
    def test_report_prints_output(self, capsys):
        df = pd.DataFrame({"a": np.array([1, 2, 3], dtype="int64")})
        dish_bucket(df, report=True)
        captured = capsys.readouterr()
        assert "dish_bucket" in captured.out

    def test_no_report_prints_nothing(self, capsys):
        df = pd.DataFrame({"a": [1, 2, 3]})
        dish_bucket(df, report=False)
        captured = capsys.readouterr()
        assert captured.out == ""


class TestFlush:
    def test_flush_calls_gc_collect(self, monkeypatch):
        called = []
        monkeypatch.setattr(dish_bucket_module.gc, "collect", lambda: called.append(True))
        dish_bucket.flush()
        assert called == [True]
