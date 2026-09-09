"""som_tam — DataFrame diffing, sour-and-tangy Thai salad style: what changed, laid bare."""

from typing import Optional, Union

import pandas as pd


def som_tam(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    *,
    key: Optional[Union[str, list[str]]] = None,
) -> pd.DataFrame:
    """Compare two DataFrames and surface what changed.

    Row identity — deciding which row in ``df_after`` corresponds to which row
    in ``df_before`` — is controlled by ``key``:

    - ``key`` given: one or more column names used as the row identity (set as
      the index on copies of both frames before comparing).
    - ``key=None`` (default): the existing index of each DataFrame is used
      directly as the row identity.

    Parameters
    ----------
    df_before, df_after:
        The two DataFrames to compare.
    key:
        Column name or list of column names identifying a row across both
        DataFrames. Must be unique within each DataFrame. If omitted, the
        DataFrame index is used instead.

    Returns
    -------
    A DataFrame indexed by row identity, with columns ``change_type``
    (``"added"``, ``"removed"``, or ``"modified"``) and ``columns_changed``
    (comma-joined column names, set only for ``"modified"`` rows). Rows with
    no changes are omitted entirely.

    Column-level schema drift — columns present in one frame but not the
    other — isn't a row in this table (it isn't tied to any particular row).
    It's attached as ``result.attrs["columns_added"]`` and
    ``result.attrs["columns_removed"]`` instead.

    Example
    -------
    >>> diff = som_tam(df_before, df_after, key="id")
    >>> diff["change_type"].value_counts()
    >>> diff.attrs["columns_added"]
    """
    before = df_before.copy()
    after = df_after.copy()

    if key is not None:
        keys = [key] if isinstance(key, str) else list(key)
        missing_before = [k for k in keys if k not in before.columns]
        missing_after = [k for k in keys if k not in after.columns]
        if missing_before or missing_after:
            raise KeyError(
                f"key column(s) not found — missing in df_before: {missing_before}, "
                f"missing in df_after: {missing_after}"
            )
        before = before.set_index(keys)
        after = after.set_index(keys)

    if before.index.has_duplicates:
        raise ValueError("df_before's row identity (key or index) has duplicate values")
    if after.index.has_duplicates:
        raise ValueError("df_after's row identity (key or index) has duplicate values")

    columns_added = [c for c in after.columns if c not in before.columns]
    columns_removed = [c for c in before.columns if c not in after.columns]
    shared_cols = [c for c in before.columns if c in after.columns]

    added_idx = after.index.difference(before.index)
    removed_idx = before.index.difference(after.index)
    common_idx = before.index.intersection(after.index)

    added_df = pd.DataFrame({"change_type": "added", "columns_changed": None}, index=added_idx)
    removed_df = pd.DataFrame({"change_type": "removed", "columns_changed": None}, index=removed_idx)

    if len(common_idx) and shared_cols:
        b = before.loc[common_idx, shared_cols]
        a = after.loc[common_idx, shared_cols]
        mismatch = ~((b == a) | (b.isna() & a.isna()))
        any_changed = mismatch.any(axis=1)
        modified_idx = common_idx[any_changed.values]
        if len(modified_idx):
            columns_changed = mismatch.loc[modified_idx].apply(
                lambda row: ", ".join(mismatch.columns[row.values]), axis=1
            )
        else:
            columns_changed = pd.Series([], dtype=object, index=modified_idx)
        modified_df = pd.DataFrame(
            {"change_type": "modified", "columns_changed": columns_changed}, index=modified_idx
        )
    else:
        modified_df = pd.DataFrame({"change_type": [], "columns_changed": []}, index=pd.Index([]))

    result = pd.concat([added_df, removed_df, modified_df])
    result.attrs["columns_added"] = columns_added
    result.attrs["columns_removed"] = columns_removed
    return result
