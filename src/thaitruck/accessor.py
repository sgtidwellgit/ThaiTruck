"""accessor — registers `.truck` as a pandas DataFrame accessor.

Importing this module (done automatically by ``thaitruck/__init__.py``)
registers the accessor as a side effect. It is not meant to be imported
for its own exports.
"""

from typing import Any, Optional, Union

import pandas as pd

from thaitruck.fried_rice import fried_rice
from thaitruck.larb import larb
from thaitruck.massaman import massaman
from thaitruck.orange_chicken import orange_chicken
from thaitruck.satay import satay


@pd.api.extensions.register_dataframe_accessor("truck")
class TruckAccessor:
    """Call ThaiTruck DataFrame functions as methods: ``df.truck.orange_chicken()``."""

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._df = pandas_obj

    def orange_chicken(self, heat: int = 3) -> pd.DataFrame:
        return orange_chicken(self._df, heat=heat)

    def larb(self, heat: int = 3) -> pd.DataFrame:
        return larb(self._df, heat=heat)

    def satay(self, *skewers: Any) -> pd.DataFrame:
        return satay(self._df, *skewers)

    def fried_rice(
        self,
        *dfs: pd.DataFrame,
        freq: str = "D",
        heat: int = 3,
        fuzzy_columns: bool = False,
        fill_method: str = "ffill",
        date_col: Optional[Union[str, list[str]]] = None,
    ) -> pd.DataFrame:
        return fried_rice(
            self._df,
            *dfs,
            freq=freq,
            heat=heat,
            fuzzy_columns=fuzzy_columns,
            fill_method=fill_method,
            date_col=date_col,
        )

    def massaman(
        self,
        column: str,
        *,
        window: int = 20,
        ops: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        return massaman(self._df, column, window=window, ops=ops)
