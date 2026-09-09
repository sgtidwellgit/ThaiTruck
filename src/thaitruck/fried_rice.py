"""fried_rice — merge N DataFrames with mismatched timestamps into one coherent result."""

import re
from typing import Optional, Union

import numpy as np
import pandas as pd

from thaitruck.exceptions import DateColumnNotFound

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


_JOIN_TYPES = {"outer", "inner", "left"}


def _reindex_frames(frames: list[pd.DataFrame], join: str) -> list[pd.DataFrame]:
    if join not in _JOIN_TYPES:
        raise ValueError(f"join must be one of {sorted(_JOIN_TYPES)}, got {join!r}")

    if join == "left":
        target = frames[0].index
    elif join == "outer":
        target = frames[0].index
        for df in frames[1:]:
            target = target.union(df.index)
    else:  # inner
        target = frames[0].index
        for df in frames[1:]:
            target = target.intersection(df.index)

    return [df.reindex(target) for df in frames]


def _merge(frames: list[pd.DataFrame], heat: int, suffix_template: Optional[str] = None) -> pd.DataFrame:
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
            suffix = suffix_template.format(i=i) if suffix_template else f"_{i}"
            result = result.join(df, how="outer", rsuffix=suffix)
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
    join: str = "outer",
    fuzzy_columns: bool = False,
    fill_method: str = "ffill",
    date_col: Optional[Union[str, list[str]]] = None,
    suffix_template: Optional[str] = None,
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
    join:
        Which rows survive the merge: 'outer' (default, union of all frames'
        timestamps), 'inner' (intersection only), or 'left' (first frame's
        timestamps only).
    fuzzy_columns:
        Normalize column names (lowercase, collapse separators) before merging
        so "Close", "close", and "closing_price" land in the same bucket.
    fill_method:
        How to fill gaps after resampling: 'ffill', 'bfill', or 'interpolate'.
    date_col:
        Override auto-detection. Pass a single string (applied to all dfs) or
        a list with one entry per DataFrame.
    suffix_template:
        Format string controlling the suffix applied to colliding columns at
        heat=3. Receives the frame's position as ``{i}`` (1-based, since frame
        0 never gets a suffix). Defaults to ``"_{i}"`` — the same suffix used
        when this isn't set.
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
            raise DateColumnNotFound(
                f"DataFrame {i}: no date column detected. Pass date_col= to specify it."
            )

        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

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

    prepared = _reindex_frames(prepared, join)
    return _merge(prepared, heat, suffix_template)
