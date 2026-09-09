"""larb — raw, fast aggregation stats on unprocessed data."""

from typing import Optional

import pandas as pd

from thaitruck.exceptions import InvalidHeatLevel

_HEAT_IQR = {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.5, 5: 1.0}


def larb(
    df: pd.DataFrame,
    heat: int = 3,
    *,
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Return a quick statistical profile of a DataFrame.

    Each row in the result represents one column from the input. Numeric
    columns get full descriptive stats plus outlier detection; non-numeric
    columns get count, null rate, cardinality, and top value.

    Parameters
    ----------
    df:
        Input DataFrame to profile.
    heat:
        Outlier sensitivity via IQR multiplier.
        1 = IQR x3.0 (extreme outliers only) … 5 = IQR x1.0 (very sensitive).
    include:
        Only profile these columns. Applied before ``exclude``.
    exclude:
        Never profile these columns.
    """
    if heat not in _HEAT_IQR:
        raise InvalidHeatLevel(f"heat must be 1–5, got {heat}")

    multiplier = _HEAT_IQR[heat]
    rows = []

    columns = [c for c in df.columns if c in include] if include is not None else list(df.columns)
    if exclude is not None:
        columns = [c for c in columns if c not in exclude]

    for col in columns:
        s = df[col]
        nonnull = s.notna().sum()
        total = len(s)

        row: dict = {
            "dtype": str(s.dtype),
            "count": int(nonnull),
            "null_pct": round(s.isna().mean() * 100, 2),
        }

        if pd.api.types.is_numeric_dtype(s):
            q1 = s.quantile(0.25)
            q3 = s.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - multiplier * iqr
            upper = q3 + multiplier * iqr
            outlier_mask = s.notna() & ((s < lower) | (s > upper))
            outlier_count = int(outlier_mask.sum())

            row.update({
                "mean": s.mean(),
                "std": s.std(),
                "min": s.min(),
                "p25": q1,
                "median": s.median(),
                "p75": q3,
                "max": s.max(),
                "skew": s.skew(),
                "lower_fence": lower,
                "upper_fence": upper,
                "outliers": outlier_count,
                "outlier_pct": round(outlier_count / nonnull * 100, 2) if nonnull else 0.0,
                "unique": None,
                "top": None,
                "top_freq": None,
            })
        else:
            mode = s.mode()
            top = mode.iloc[0] if not mode.empty else None
            top_freq = int((s == top).sum()) if top is not None else 0

            row.update({
                "mean": None,
                "std": None,
                "min": None,
                "p25": None,
                "median": None,
                "p75": None,
                "max": None,
                "skew": None,
                "lower_fence": None,
                "upper_fence": None,
                "outliers": None,
                "outlier_pct": None,
                "unique": int(s.nunique()),
                "top": top,
                "top_freq": top_freq,
            })

        rows.append({"column": col, **row})

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.set_index("column")
