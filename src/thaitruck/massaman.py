"""massaman — slow-cooked rolling and percentage-change aggregations."""

from typing import Optional

import pandas as pd

_ROLLING_OPS = {"mean", "std", "sum", "min", "max", "median"}


def massaman(
    df: pd.DataFrame,
    column: str,
    *,
    window: int = 20,
    ops: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Add rolling-window and percentage-change columns for one column.

    Parameters
    ----------
    df:
        Input DataFrame.
    column:
        Name of the column to aggregate.
    window:
        Rolling window size, in rows.
    ops:
        Aggregations to compute. Any of "mean", "std", "sum", "min", "max",
        "median" (rolling, windowed) or "pct_change" (row-over-row percent
        change, not windowed). Defaults to ``["mean"]``.

    Returns
    -------
    A copy of ``df`` with one new column per requested op:
    ``{column}_roll_{op}_{window}`` for rolling ops, ``{column}_pct_change``
    for percentage change.

    Examples
    --------
    >>> massaman(df, "price", window=20, ops=["mean", "std", "pct_change"])
    # Adds columns: price_roll_mean_20, price_roll_std_20, price_pct_change
    """
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")

    ops = ops if ops is not None else ["mean"]

    df = df.copy()
    series = df[column]

    for op in ops:
        if op in _ROLLING_OPS:
            df[f"{column}_roll_{op}_{window}"] = getattr(series.rolling(window), op)()
        elif op == "pct_change":
            df[f"{column}_pct_change"] = series.pct_change()
        else:
            raise ValueError(
                f"Unsupported op {op!r}. Expected one of "
                f"{sorted(_ROLLING_OPS | {'pct_change'})}."
            )

    return df
