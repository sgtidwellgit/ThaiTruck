"""pad_thai — string padding, alignment, and formatting utilities."""

from typing import Union

import pandas as pd


def _pad_one(value: str, width: int, align: str, fill: str, truncate: bool) -> str:
    s = "" if value is None else str(value)
    if truncate and len(s) > width:
        return s[: max(0, width - 1)] + "…" if width > 0 else ""
    if align == "left":
        return s.ljust(width, fill)
    if align == "right":
        return s.rjust(width, fill)
    if align == "center":
        return s.center(width, fill)
    raise ValueError(f"align must be 'left', 'right', or 'center', got {align!r}")


def pad_thai(
    value: Union[str, list, pd.Series],
    width: int,
    align: str = "left",
    fill: str = " ",
    truncate: bool = False,
) -> Union[str, list, pd.Series]:
    """Pad strings to a fixed width with alignment control.

    Parameters
    ----------
    value:
        A single string, a list of strings, or a pandas Series.
    width:
        Target total character width.
    align:
        'left', 'right', or 'center'.
    fill:
        Fill character (single character, default space).
    truncate:
        If True, values longer than width are cut and suffixed with '…'.
    """
    if len(fill) != 1:
        raise ValueError(f"fill must be a single character, got {fill!r}")
    if width < 0:
        raise ValueError(f"width must be >= 0, got {width}")

    if isinstance(value, pd.Series):
        return value.map(lambda v: _pad_one(v, width, align, fill, truncate))

    if isinstance(value, list):
        return [_pad_one(v, width, align, fill, truncate) for v in value]

    return _pad_one(value, width, align, fill, truncate)
