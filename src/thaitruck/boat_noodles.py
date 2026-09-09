"""boat_noodles — sequential chunked file processing, one bowl at a time."""

from pathlib import Path
from typing import Callable, Iterator, Optional, Union

import pandas as pd


def boat_noodles(
    path: Union[str, Path],
    *,
    chunksize: int = 10_000,
    apply: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
    **read_csv_kwargs,
) -> Iterator[pd.DataFrame]:
    """Read a large CSV file in chunks without loading it all into memory.

    A thin wrapper around ``pd.read_csv(path, chunksize=chunksize)`` that
    optionally applies a transform to each chunk as it's yielded — the common
    case being another ThaiTruck function like ``orange_chicken``.

    Parameters
    ----------
    path:
        Path to the CSV file.
    chunksize:
        Rows per chunk.
    apply:
        Optional callable applied to each chunk before it's yielded.
    **read_csv_kwargs:
        Passed through to ``pd.read_csv`` (e.g. ``sep=``, ``encoding=``).

    Yields
    ------
    One ``pd.DataFrame`` per chunk, in file order.

    Example
    -------
    >>> from thaitruck import boat_noodles, orange_chicken
    >>> for chunk in boat_noodles("big_file.csv", chunksize=10_000, apply=orange_chicken):
    ...     process(chunk)
    """
    for chunk in pd.read_csv(path, chunksize=chunksize, **read_csv_kwargs):
        yield apply(chunk) if apply is not None else chunk
