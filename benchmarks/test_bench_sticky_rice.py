"""Benchmarks for sticky_rice's cache read/write paths.

Not part of the default `pytest` run (see `testpaths` in pyproject.toml).
Run explicitly with: pytest benchmarks/
"""

import pandas as pd
from thaitruck import sticky_rice


def _make_df() -> pd.DataFrame:
    return pd.DataFrame({"a": range(10_000), "b": range(10_000)})


def test_bench_cache_write(benchmark, tmp_path):
    @sticky_rice(cache_dir=tmp_path)
    def compute(seed: int) -> pd.DataFrame:
        return _make_df()

    # A unique arg per round is required — otherwise later rounds would hit
    # the cache instead of measuring a fresh write each time.
    counter = {"n": 0}

    def setup():
        counter["n"] += 1
        return (counter["n"],), {}

    benchmark.pedantic(compute, setup=setup, rounds=20)


def test_bench_cache_hit(benchmark, tmp_path):
    @sticky_rice(cache_dir=tmp_path)
    def compute() -> pd.DataFrame:
        return _make_df()

    compute()  # warm the cache once
    benchmark(compute)
