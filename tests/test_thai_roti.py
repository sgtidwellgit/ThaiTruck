from pathlib import Path

import pandas as pd
import pytest
from thaitruck import thai_roti


@pytest.fixture
def df():
    return pd.DataFrame({"price": [1.0, 2.0], "sector": ["Tech", "Energy"]})


class TestExcel:
    def test_writes_excel_file(self, df, tmp_path):
        out = thai_roti(df, format="excel", path=tmp_path / "report.xlsx")
        assert out.exists()

    def test_excel_roundtrips(self, df, tmp_path):
        path = tmp_path / "report.xlsx"
        thai_roti(df, format="excel", path=path)
        result = pd.read_excel(path)
        assert list(result["sector"]) == ["Tech", "Energy"]

    def test_creates_parent_dirs(self, df, tmp_path):
        path = tmp_path / "nested" / "dir" / "report.xlsx"
        thai_roti(df, format="excel", path=path)
        assert path.exists()

    def test_returns_path(self, df, tmp_path):
        path = tmp_path / "report.xlsx"
        result = thai_roti(df, format="excel", path=path)
        assert isinstance(result, Path)
        assert result == path


class TestHtml:
    def test_writes_html_file(self, df, tmp_path):
        path = tmp_path / "dashboard.html"
        thai_roti(df, format="html", path=path)
        content = path.read_text()
        assert "Tech" in content


class TestErrors:
    def test_missing_path_raises(self, df):
        with pytest.raises(ValueError, match="path is required"):
            thai_roti(df, format="excel")

    def test_unsupported_format_raises(self, df, tmp_path):
        with pytest.raises(ValueError, match="Unsupported format"):
            thai_roti(df, format="bogus", path=tmp_path / "x.txt")

    def test_od_summary_raises_not_implemented(self, df):
        with pytest.raises(NotImplementedError):
            thai_roti(df, format="od_summary")
