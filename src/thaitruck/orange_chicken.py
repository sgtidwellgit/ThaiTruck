"""orange_chicken — normalize and transform raw data into clean, uniform output."""

import re

import pandas as pd

_BOOL_TRUE = {"true", "yes", "y", "t", "1", "on"}
_BOOL_FALSE = {"false", "no", "n", "f", "0", "off"}


def _clean_col_name(name: str) -> str:
    name = str(name).strip().lower()
    name = re.sub(r"[\s\-\.]+", "_", name)
    name = re.sub(r"[^\w]+", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "col"


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(lambda v: v.strip() if isinstance(v, str) else v)
    return df


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        # Only apply if at least half the non-null values converted cleanly
        original_nonnull = df[col].notna().sum()
        converted_nonnull = converted.notna().sum()
        if original_nonnull > 0 and converted_nonnull / original_nonnull >= 0.5:
            df[col] = converted
    return df


def _coerce_booleans(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include="object").columns:
        lowered = df[col].map(lambda v: v.strip().lower() if isinstance(v, str) else v)
        is_true = lowered.isin(_BOOL_TRUE)
        is_false = lowered.isin(_BOOL_FALSE)
        is_null = df[col].isna()
        coverage = (is_true | is_false | is_null).mean()
        if coverage >= 0.9:
            df[col] = is_true.where(is_true | is_false, other=None)
    return df


def _drop_sparse(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    null_frac = df.isnull().mean()
    return df.drop(columns=null_frac[null_frac >= threshold].index.tolist())


def orange_chicken(df: pd.DataFrame, heat: int = 3) -> pd.DataFrame:
    """Glaze a raw DataFrame into clean, uniform output.

    Each heat level is cumulative — higher heat includes all lower-heat steps.

    Parameters
    ----------
    df:
        Raw input DataFrame.
    heat:
        Cleaning aggressiveness.
        1 = normalize column names only.
        2 = + strip string whitespace, drop all-null rows and columns.
        3 = + coerce numeric strings to numbers (default).
        4 = + coerce boolean strings, drop columns with >90% nulls.
        5 = + drop columns with >50% nulls (napalm).
    """
    if heat < 1 or heat > 5:
        raise ValueError(f"heat must be 1–5, got {heat}")

    df = df.copy()

    # heat >= 1: normalize column names
    df.columns = [_clean_col_name(c) for c in df.columns]

    if heat >= 2:
        df = _strip_strings(df)
        df = df.dropna(how="all", axis=0)
        df = df.dropna(how="all", axis=1)

    if heat >= 3:
        df = _coerce_numeric(df)

    if heat >= 4:
        df = _coerce_booleans(df)
        df = _drop_sparse(df, threshold=0.9)

    if heat >= 5:
        df = _drop_sparse(df, threshold=0.5)

    return df
