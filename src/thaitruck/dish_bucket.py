"""dish_bucket — DataFrame memory optimizer, keeping the truck nimble."""

import gc

import pandas as pd


def dish_bucket(df: pd.DataFrame, *, report: bool = False) -> pd.DataFrame:
    """Downcast numeric columns to the smallest dtype that holds them safely.

    Uses ``pd.to_numeric(..., downcast=...)`` per column, so a column only
    shrinks as far as it safely can (e.g. a float column with values outside
    float32 range stays float64) — never a blind ``float64 -> float32`` cast.

    Parameters
    ----------
    df:
        Input DataFrame.
    report:
        If True, print memory usage before and after.

    Returns
    -------
    A copy of ``df`` with numeric columns downcast where safe.
    """
    before_bytes = df.memory_usage(deep=True).sum() if report else None

    df = df.copy()
    for col in df.select_dtypes(include="float").columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include="integer").columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")

    if report:
        after_bytes = df.memory_usage(deep=True).sum()
        pct = (1 - after_bytes / before_bytes) * 100 if before_bytes else 0.0
        print(f"dish_bucket: {before_bytes:,} -> {after_bytes:,} bytes ({pct:.1f}% reduction)")

    return df


def _flush() -> None:
    """Run gc.collect() to reclaim memory immediately."""
    gc.collect()


dish_bucket.flush = _flush
