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
from thaitruck.nam_pla import nam_pla
from thaitruck.orange_chicken import orange_chicken
from thaitruck.satay import satay
from thaitruck.som_tam import som_tam


@pd.api.extensions.register_dataframe_accessor("truck")
class TruckAccessor:
    """Call ThaiTruck DataFrame functions as methods: ``df.truck.orange_chicken()``."""

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._df = pandas_obj

    def orange_chicken(
        self,
        heat: int = 3,
        *,
        rename: Optional[dict] = None,
        dtypes: Optional[dict] = None,
    ) -> pd.DataFrame:
        return orange_chicken(self._df, heat=heat, rename=rename, dtypes=dtypes)

    def larb(
        self,
        heat: int = 3,
        *,
        include: Optional[list] = None,
        exclude: Optional[list] = None,
    ) -> pd.DataFrame:
        return larb(self._df, heat=heat, include=include, exclude=exclude)

    def satay(self, *skewers: Any) -> pd.DataFrame:
        return satay(self._df, *skewers)

    def fried_rice(
        self,
        *dfs: pd.DataFrame,
        freq: str = "D",
        heat: int = 3,
        join: str = "outer",
        fuzzy_columns: bool = False,
        fill_method: str = "ffill",
        date_col: Optional[Union[str, list[str]]] = None,
        suffix_template: Optional[str] = None,
    ) -> pd.DataFrame:
        return fried_rice(
            self._df,
            *dfs,
            freq=freq,
            heat=heat,
            join=join,
            fuzzy_columns=fuzzy_columns,
            fill_method=fill_method,
            date_col=date_col,
            suffix_template=suffix_template,
        )

    def massaman(
        self,
        column: str,
        *,
        window: int = 20,
        ops: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        return massaman(self._df, column, window=window, ops=ops)

    def nam_pla(
        self,
        spec: dict,
        *,
        strict: bool = False,
    ) -> pd.DataFrame:
        return nam_pla(self._df, spec, strict=strict)

    def som_tam(
        self,
        df_after: pd.DataFrame,
        *,
        key: Optional[Union[str, list]] = None,
    ) -> pd.DataFrame:
        return som_tam(self._df, df_after, key=key)
