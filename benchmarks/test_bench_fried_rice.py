"""Benchmarks for fried_rice's resample + merge paths.

Not part of the default `pytest` run (see `testpaths` in pyproject.toml).
Run explicitly with: pytest benchmarks/
"""

import pandas as pd
from thaitruck import fried_rice


def _daily_frame(n_rows: int, col: str) -> pd.DataFrame:
    idx = pd.date_range("2000-01-01", periods=n_rows, freq="D")
    return pd.DataFrame({col: range(n_rows)}, index=idx)


def test_bench_two_frame_merge_heat3(benchmark):
    a = _daily_frame(10_000, "price")
    b = _daily_frame(10_000, "volume")
    benchmark(fried_rice, a, b, freq="D", heat=3)


def test_bench_five_frame_merge_napalm(benchmark):
    frames = [_daily_frame(5_000, f"col_{i}") for i in range(5)]
    benchmark(lambda: fried_rice(*frames, freq="D", heat=5))
