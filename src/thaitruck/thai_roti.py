"""thai_roti — finalized output formatter, the last step before the truck hands off the meal."""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

_SUPPORTED_FORMATS = {"excel", "html"}


def thai_roti(
    df: pd.DataFrame,
    *,
    format: str = "excel",
    path: Union[str, Path, None] = None,
) -> Path:
    """Write a finished DataFrame to a polished, deliverable format.

    Parameters
    ----------
    df:
        DataFrame to write out.
    format:
        ``"excel"`` (requires the optional ``openpyxl`` dependency — install
        with ``pip install thaitruck[excel]``) or ``"html"``.
    path:
        Destination file path. Required for both supported formats. Parent
        directories are created automatically.

    Returns
    -------
    The ``Path`` written to.

    Not implemented
    ----------------
    ``format="od_summary"`` (an origin-destination summary dict) is not
    implemented — what fields it should compute was never pinned down, and
    guessing at a schema for a domain-specific summary isn't a call this
    function should make on its own.

    Example
    -------
    >>> thai_roti(df, format="excel", path="output/report.xlsx")
    >>> thai_roti(df, format="html", path="output/dashboard.html")
    """
    if format == "od_summary":
        raise NotImplementedError(
            "thai_roti(format='od_summary') is not implemented — its output "
            "schema needs a design decision that hasn't been made yet."
        )

    if format not in _SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format {format!r}. Expected one of {sorted(_SUPPORTED_FORMATS)}.")

    if path is None:
        raise ValueError(f"path is required for format={format!r}")

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "excel":
        try:
            df.to_excel(out_path, index=False)
        except ImportError as e:
            raise ImportError(
                "thai_roti(format='excel') requires openpyxl. Install it with: pip install thaitruck[excel]"
            ) from e
    else:  # html
        df.to_html(out_path)

    return out_path
