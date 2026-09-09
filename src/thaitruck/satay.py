"""satay — fancy array slicing, skewering data on a stick."""

import operator
from typing import Any, Callable, Union

import pandas as pd

from thaitruck.exceptions import SkewTypeError

_COMPARISON_OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


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
    tuple(col, value, op)
        Row filter: keep rows where ``df[col] op value``, where ``op`` is one
        of ``">"``, ``"<"``, ``">="``, ``"<="``, ``"=="``, ``"!="``. Only
        applies when the third element is one of these operator strings;
        otherwise the tuple is treated as ``(col, lo, hi)`` above.
    dict
        Row filter: ``{col: value}`` or ``{col: [v1, v2, ...]}`` (isin).
    callable
        Row filter: function receives the current DataFrame, returns a bool mask.

    Examples
    --------
    >>> satay(df, "price", "volume")                       # two columns
    >>> satay(df, slice(0, 10))                            # first ten rows
    >>> satay(df, ("price", 10, 50))                       # price between 10-50
    >>> satay(df, ("price", 100, ">"))                     # price > 100
    >>> satay(df, {"sector": "Tech"})                      # equality filter
    >>> satay(df, {"sector": ["Tech", "Energy"]})          # isin filter
    >>> satay(df, lambda d: d["volume"] > 1000, "price")   # lambda + column
    >>> satay.head(df, 10)                                 # first ten rows
    >>> satay.tail(df, 10)                                 # last ten rows
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
                    f"Tuple skewer must be (col, lo, hi) or (col, value, op), got length {len(skewer)}"
                )
            col, second, third = skewer
            if isinstance(third, str) and third in _COMPARISON_OPS:
                result = result[_COMPARISON_OPS[third](result[col], second)]
            else:
                lo, hi = second, third
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
            raise SkewTypeError(
                f"Unrecognised skewer type {type(skewer).__name__}. "
                "Expected str, list, slice, tuple, dict, or callable."
            )

    if cols_selected:
        missing = [c for c in cols_selected if c not in result.columns]
        if missing:
            raise KeyError(f"Columns not found: {missing}")
        result = result[cols_selected]

    return result


def _head(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Shorthand for ``satay(df, slice(0, n))``."""
    return satay(df, slice(0, n))


def _tail(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Shorthand for ``satay(df, slice(-n, None))``."""
    return satay(df, slice(-n, None))


satay.head = _head
satay.tail = _tail
