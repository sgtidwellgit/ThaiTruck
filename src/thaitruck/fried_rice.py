"""fried_rice — merge N DataFrames with mismatched timestamps into one coherent result."""

import re
from typing import Optional, Union

import numpy as np
import pandas as pd

_DATE_HINTS = {
    "date", "ts", "timestamp", "time", "report_date", "datetime",
    "dt", "period", "day", "trade_date", "as_of_date", "effective_date",
}


def _detect_date_col(df: pd.DataFrame) -> Optional[str]:
    if pd.api.types.is_datetime64_any_dtype(df.index):
        return None
    for col in df.columns:
        if col.lower() in _DATE_HINTS or any(h in col.lower() for h in _DATE_HINTS):
            return col
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for col in df.columns:
        if df[col].dtype == object:
            try:
                pd.to_datetime(df[col].dropna().head(5))
                return col
            except (ValueError, TypeError):
                pass
    return None


def _normalize(name: str) -> str:
    return re.sub(r"[\s_\-]+", "_", name.lower().strip())


def _merge(frames: list[pd.DataFrame], heat: int) -> pd.DataFrame:
    if heat == 1:
        result = frames[0]
        for df in frames[1:]:
            new_cols = [c for c in df.columns if c not in result.columns]
            if new_cols:
                result = result.join(df[new_cols], how="outer")
        return result

    if heat == 2:
        result = frames[0]
        for df in frames[1:]:
            overlap = [c for c in df.columns if c in result.columns]
            result = result.join(df.drop(columns=overlap), how="outer")
        return result

    if heat == 3:
        result = frames[0]
        for i, df in enumerate(frames[1:], start=1):
            result = result.join(df, how="outer", rsuffix=f"_{i}")
        return result

    if heat == 4:
        result = frames[0]
        for df in frames[1:]:
            overlap = [c for c in df.columns if c in result.columns]
            result = result.drop(columns=overlap).join(df, how="outer")
        return result

    # heat == 5: napalm — last non-null wins per cell
    combined = pd.concat(frames, axis=1)
    result_cols = {}
    for col in dict.fromkeys(combined.columns):
        block = combined.loc[:, combined.columns == col]
        result_cols[col] = block.ffill(axis=1).iloc[:, -1]
    return pd.DataFrame(result_cols, index=combined.index)


def fried_rice(
    *dfs: pd.DataFrame,
    freq: str = "D",
    heat: int = 3,
    fuzzy_columns: bool = False,
    fill_method: str = "ffill",
    date_col: Optional[Union[str, list[str]]] = None,
) -> pd.DataFrame:
    """Merge N DataFrames with mismatched timestamps into one coherent result.

    Parameters
    ----------
    *dfs:
        Two or more DataFrames to blend.
    freq:
        Target resampling frequency. Pandas offset alias — 'D' (daily),
        'W' (weekly), 'ME' (month-end), 'QE' (quarter-end), etc.
    heat:
        Conflict resolution when columns collide.
        1 = conservative (keep first), 2 = prefer left, 3 = suffix-disambiguate,
        4 = prefer right, 5 = napalm (last non-null wins).
    fuzzy_columns:
        Normalize column names (lowercase, collapse separators) before merging
        so "Close", "close", and "closing_price" land in the same bucket.
    fill_method:
        How to fill gaps after resampling: 'ffill', 'bfill', or 'interpolate'.
    date_col:
        Override auto-detection. Pass a single string (applied to all dfs) or
        a list with one entry per DataFrame.
    """
    if not dfs:
        return pd.DataFrame()

    prepared: list[pd.DataFrame] = []

    for i, df in enumerate(dfs):
        df = df.copy()

        col = (date_col[i] if isinstance(date_col, list) else date_col) if date_col is not None else _detect_date_col(df)

        if col is not None:
            df[col] = pd.to_datetime(df[col])
            df = df.set_index(col)
        elif not pd.api.types.is_datetime64_any_dtype(df.index):
            raise ValueError(
                f"DataFrame {i}: no date column detected. Pass date_col= to specify it."
            )

        df.index = pd.to_datetime(df.index)

        if fuzzy_columns:
            df.columns = [_normalize(c) for c in df.columns]

        df = df.resample(freq).last()

        if fill_method == "ffill":
            df = df.ffill()
        elif fill_method == "bfill":
            df = df.bfill()
        elif fill_method == "interpolate":
            df = df.interpolate(method="time")

        prepared.append(df)

    if len(prepared) == 1:
        return prepared[0]

    return _merge(prepared, heat)
