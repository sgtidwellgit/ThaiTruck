"""nam_pla — schema validation, the dipping sauce that catches bad data before it hits the pan."""

from typing import Any

import numpy as np
import pandas as pd

from thaitruck.exceptions import ValidationError

_KNOWN_KEYS = {"dtype", "nullable", "min", "max", "isin", "required"}

_DTYPE_CHECKS = {
    float: pd.api.types.is_numeric_dtype,
    int: pd.api.types.is_integer_dtype,
    str: lambda s: s.dtype == object,
    bool: pd.api.types.is_bool_dtype,
}

_REPORT_COLUMNS = ["column", "check", "message"]


def _check_dtype(series: pd.Series, expected: Any) -> bool:
    if expected in _DTYPE_CHECKS:
        return _DTYPE_CHECKS[expected](series)
    try:
        return series.dtype == np.dtype(expected)
    except TypeError:
        return False


def nam_pla(
    df: pd.DataFrame,
    spec: dict[str, dict[str, Any]],
    *,
    strict: bool = False,
) -> pd.DataFrame:
    """Validate a DataFrame against a column schema spec.

    Parameters
    ----------
    df:
        DataFrame to validate.
    spec:
        Mapping of column name -> constraint dict. Supported constraint keys:

        - ``dtype``: expected type — ``float``/``int``/``str``/``bool``, or any
          value accepted by ``numpy.dtype()`` (e.g. ``"datetime64[ns]"``).
          ``float`` accepts any numeric dtype (int or float); the others are
          exact.
        - ``nullable``: bool, default ``True``. If ``False``, no nulls allowed.
        - ``min`` / ``max``: numeric bounds, inclusive.
        - ``isin``: iterable of allowed values.
        - ``required``: bool, default ``True``. If ``False``, the column is
          only checked when present instead of being reported as missing.
    strict:
        If ``True``, raise ``ValidationError`` when any violation is found.

    Returns
    -------
    A DataFrame with one row per violation: columns ``column``, ``check``,
    ``message``. Empty (but with the same columns) when everything passes.

    Example
    -------
    >>> spec = {
    ...     "price":  {"dtype": float, "min": 0, "nullable": False},
    ...     "sector": {"dtype": str, "nullable": False},
    ... }
    >>> report = nam_pla(df, spec)
    """
    violations: list[dict[str, str]] = []

    for column, rules in spec.items():
        unknown = set(rules) - _KNOWN_KEYS
        if unknown:
            raise ValueError(f"Unknown constraint(s) {sorted(unknown)} for column '{column}'")

        if column not in df.columns:
            if rules.get("required", True):
                violations.append({
                    "column": column,
                    "check": "missing_column",
                    "message": "column not found",
                })
            continue

        series = df[column]
        nonnull = series.dropna()

        if "dtype" in rules and not _check_dtype(series, rules["dtype"]):
            violations.append({
                "column": column,
                "check": "dtype",
                "message": f"expected dtype compatible with {rules['dtype']}, got {series.dtype}",
            })

        if rules.get("nullable", True) is False:
            null_count = int(series.isna().sum())
            if null_count:
                violations.append({
                    "column": column,
                    "check": "nullable",
                    "message": f"{null_count} null value(s) found, nullable=False",
                })

        if "min" in rules and not nonnull.empty:
            below = int((nonnull < rules["min"]).sum())
            if below:
                violations.append({
                    "column": column,
                    "check": "min",
                    "message": f"{below} value(s) below min={rules['min']}",
                })

        if "max" in rules and not nonnull.empty:
            above = int((nonnull > rules["max"]).sum())
            if above:
                violations.append({
                    "column": column,
                    "check": "max",
                    "message": f"{above} value(s) above max={rules['max']}",
                })

        if "isin" in rules and not nonnull.empty:
            allowed = set(rules["isin"])
            bad = int((~nonnull.isin(allowed)).sum())
            if bad:
                violations.append({
                    "column": column,
                    "check": "isin",
                    "message": f"{bad} value(s) not in allowed set {sorted(allowed)}",
                })

    report = pd.DataFrame(violations, columns=_REPORT_COLUMNS)

    if strict and not report.empty:
        raise ValidationError(
            f"{len(report)} validation violation(s) found:\n{report.to_string(index=False)}"
        )

    return report
