import pandas as pd
import pytest
from thaitruck import boat_noodles, orange_chicken


@pytest.fixture
def csv_path(tmp_path):
    path = tmp_path / "data.csv"
    pd.DataFrame({"Price": [1, 2, 3, 4, 5], "Volume": [10, 20, 30, 40, 50]}).to_csv(path, index=False)
    return path


class TestChunking:
    def test_yields_chunks_of_requested_size(self, csv_path):
        chunks = list(boat_noodles(csv_path, chunksize=2))
        assert [len(c) for c in chunks] == [2, 2, 1]

    def test_all_rows_covered(self, csv_path):
        chunks = list(boat_noodles(csv_path, chunksize=2))
        total = pd.concat(chunks)
        assert len(total) == 5

    def test_is_a_generator(self, csv_path):
        result = boat_noodles(csv_path, chunksize=2)
        assert hasattr(result, "__next__")


class TestApply:
    def test_apply_transforms_each_chunk(self, csv_path):
        chunks = list(boat_noodles(csv_path, chunksize=2, apply=orange_chicken))
        for chunk in chunks:
            assert "price" in chunk.columns

    def test_no_apply_returns_raw_chunks(self, csv_path):
        chunks = list(boat_noodles(csv_path, chunksize=2))
        assert "Price" in chunks[0].columns


class TestReadCsvKwargsPassthrough:
    def test_passes_sep_kwarg(self, tmp_path):
        path = tmp_path / "semicolon.csv"
        pd.DataFrame({"a": [1, 2]}).to_csv(path, index=False, sep=";")
        chunks = list(boat_noodles(path, chunksize=10, sep=";"))
        assert "a" in chunks[0].columns
