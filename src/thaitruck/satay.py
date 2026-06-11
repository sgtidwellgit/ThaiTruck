"""satay — fancy array slicing, skewering data on a stick."""

from typing import Any, Callable, Union

import pandas as pd


def satay(df: pd.DataFrame, *skewers: Any) -> pd.DataFrame:
    """Slice a DataFrame with expressive multi-dimensional selectors.

    Skewers are applied in order. Row filters narrow the result set;
    column selectors determine which columns appear in the output.
    If no column selector is provided, all columns are returned.

    Skewer types
    ------------
    str
        Select a single column.
    list[str]
        Select multiple columns.
    slice
        Positional row slice (passed to ``iloc``).
    tuple(col, lo, hi)
        Row filter: keep rows where ``lo <= df[col] <= hi``.
    dict
        Row filter: ``{col: value}`` or ``{col: [v1, v2, ...]}`` (isin).
    callable
        Row filter: function receives the current DataFrame, returns a bool mask.

    Examples
    --------
    >>> satay(df, "price", "volume")                       # two columns
    >>> satay(df, slice(0, 10))                            # first ten rows
    >>> satay(df, ("price", 10, 50))                       # price between 10-50
    >>> satay(df, {"sector": "Tech"})                      # equality filter
    >>> satay(df, {"sector": ["Tech", "Energy"]})          # isin filter
    >>> satay(df, lambda d: d["volume"] > 1000, "price")   # lambda + column
    """
    if not skewers:
        return df.copy()

    result = df
    cols_selected: list[str] = []

    for skewer in skewers:
        if isinstance(skewer, str):
            cols_selected.append(skewer)

        elif isinstance(skewer, list) and all(isinstance(s, str) for s in skewer):
            cols_selected.extend(skewer)

        elif isinstance(skewer, slice):
            result = result.iloc[skewer]

        elif isinstance(skewer, tuple):
            if len(skewer) != 3:
                raise ValueError(
                    f"Tuple skewer must be (col, lo, hi), got length {len(skewer)}"
                )
            col, lo, hi = skewer
            result = result[(result[col] >= lo) & (result[col] <= hi)]

        elif isinstance(skewer, dict):
            for col, val in skewer.items():
                if isinstance(val, list):
                    result = result[result[col].isin(val)]
                else:
                    result = result[result[col] == val]

        elif callable(skewer):
            result = result[skewer(result)]

        else:
            raise TypeError(
                f"Unrecognised skewer type {type(skewer).__name__}. "
                "Expected str, list, slice, tuple, dict, or callable."
            )

    if cols_selected:
        missing = [c for c in cols_selected if c not in result.columns]
        if missing:
            raise KeyError(f"Columns not found: {missing}")
        result = result[cols_selected]

    return result
