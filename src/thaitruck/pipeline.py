"""pipeline — TruckPipeline, a fluent chainable wrapper around ThaiTruck DataFrame operations."""

from typing import Any, Optional, Union

import pandas as pd

from thaitruck.fried_rice import fried_rice
from thaitruck.massaman import massaman
from thaitruck.orange_chicken import orange_chicken
from thaitruck.satay import satay


class TruckPipeline:
    """Chain ThaiTruck DataFrame operations without intermediate variables.

    Each method returns a new ``TruckPipeline`` wrapping the transformed
    DataFrame, so calls can be chained. Call ``.result()`` at the end to
    get the plain ``pd.DataFrame`` back.

    Examples
    --------
    >>> result = (
    ...     TruckPipeline(raw_df)
    ...     .orange_chicken(heat=3)
    ...     .fried_rice(earnings_df, freq="D")
    ...     .satay({"sector": "Tech"})
    ...     .result()
    ... )
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def orange_chicken(self, heat: int = 3) -> "TruckPipeline":
        return TruckPipeline(orange_chicken(self._df, heat=heat))

    def fried_rice(
        self,
        *dfs: pd.DataFrame,
        freq: str = "D",
        heat: int = 3,
        fuzzy_columns: bool = False,
        fill_method: str = "ffill",
        date_col: Optional[Union[str, list[str]]] = None,
    ) -> "TruckPipeline":
        return TruckPipeline(
            fried_rice(
                self._df,
                *dfs,
                freq=freq,
                heat=heat,
                fuzzy_columns=fuzzy_columns,
                fill_method=fill_method,
                date_col=date_col,
            )
        )

    def satay(self, *skewers: Any) -> "TruckPipeline":
        return TruckPipeline(satay(self._df, *skewers))

    def massaman(
        self,
        column: str,
        *,
        window: int = 20,
        ops: Optional[list[str]] = None,
    ) -> "TruckPipeline":
        return TruckPipeline(massaman(self._df, column, window=window, ops=ops))

    def result(self) -> pd.DataFrame:
        return self._df
