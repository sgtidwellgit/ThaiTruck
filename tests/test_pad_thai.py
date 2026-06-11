import pandas as pd
import pytest
from thaitruck import pad_thai


class TestSingleString:
    def test_left_align(self):
        assert pad_thai("hi", 5) == "hi   "

    def test_right_align(self):
        assert pad_thai("hi", 5, align="right") == "   hi"

    def test_center_align(self):
        assert pad_thai("hi", 6, align="center") == "  hi  "

    def test_custom_fill(self):
        assert pad_thai("hi", 5, fill="-") == "hi---"

    def test_exact_width_unchanged(self):
        assert pad_thai("hello", 5) == "hello"

    def test_truncate_long_string(self):
        result = pad_thai("hello world", 7, truncate=True)
        assert len(result) == 7
        assert result.endswith("…")

    def test_no_truncate_by_default(self):
        result = pad_thai("hello world", 5)
        assert result == "hello world"

    def test_zero_width_truncate(self):
        assert pad_thai("hi", 0, truncate=True) == ""

    def test_none_treated_as_empty_string(self):
        assert pad_thai(None, 4) == "    "


class TestList:
    def test_pads_all_items(self):
        result = pad_thai(["a", "bb", "ccc"], 4)
        assert result == ["a   ", "bb  ", "ccc "]

    def test_returns_list(self):
        result = pad_thai(["x", "y"], 3)
        assert isinstance(result, list)

    def test_empty_list(self):
        assert pad_thai([], 5) == []


class TestSeries:
    def test_pads_series(self):
        s = pd.Series(["cat", "elephant", "ox"])
        result = pad_thai(s, 10)
        assert all(len(v) == 10 for v in result)

    def test_returns_series(self):
        s = pd.Series(["a", "b"])
        result = pad_thai(s, 5)
        assert isinstance(result, pd.Series)

    def test_right_align_series(self):
        s = pd.Series(["hi", "hello"])
        result = pad_thai(s, 6, align="right")
        assert result.iloc[0] == "    hi"
        assert result.iloc[1] == " hello"


class TestEdgeCases:
    def test_invalid_align_raises(self):
        with pytest.raises(ValueError, match="align must be"):
            pad_thai("x", 5, align="diagonal")

    def test_multi_char_fill_raises(self):
        with pytest.raises(ValueError, match="single character"):
            pad_thai("x", 5, fill="--")

    def test_negative_width_raises(self):
        with pytest.raises(ValueError, match="width must be"):
            pad_thai("x", -1)
