# ThaiTruck — Project Document

> **Current version:** 0.2.2 | **PyPI:** `pip install thaitruck` | **Python:** ≥ 3.9 | **Pandas:** ≥ 1.5

---

## Table of Contents

1. [What ThaiTruck Is](#what-thaitruck-is)
2. [Repository Layout](#repository-layout)
3. [Current Menu — All 9 Modules](#current-menu--all-9-modules)
4. [The Heat Guide](#the-heat-guide)
5. [Architecture](#architecture)
6. [Tests](#tests)
7. [Build & Publish](#build--publish)
8. [The Food Truck Fleet](#the-food-truck-fleet)
9. [Roadmap — Planned Work](#roadmap--planned-work)
   - [Priority 1: Infrastructure & Quality Gates](#priority-1-infrastructure--quality-gates)
   - [Priority 2: Validation & Alerting (Condiment Caddy)](#priority-2-validation--alerting-condiment-caddy)
   - [Priority 3: Ergonomics](#priority-3-ergonomics)
   - [Priority 4: Enhancements to Existing Modules](#priority-4-enhancements-to-existing-modules)
   - [Priority 5: New Utility Modules](#priority-5-new-utility-modules)
   - [Priority 6: Memory Management](#priority-6-memory-management)
   - [Priority 7: Output & Reporting](#priority-7-output--reporting)
   - [Priority 8: Input / Connectors *(moved to SushiTruck)*](#priority-8-input--connectors)
   - [Priority 9: Orchestration](#priority-9-orchestration)
10. [RamenTruck — Planned ML/AI Sibling](#ramentruck--planned-mlai-sibling)

---

## What ThaiTruck Is

ThaiTruck is a pure Python library for **batch DataFrame cleaning, merging, and processing**. It ships as a PyPI wheel with no framework, no server, and no CLI. Consumers import individual modules directly.

The flagship use-case is data engineering work that involves multiple DataFrames with mismatched date columns, different frequencies, and messy raw values. ThaiTruck handles normalization, merging, profiling, slicing, caching, and config management — all with a consistent "heat" metaphor where higher values are more aggressive.

```python
pip install thaitruck
```

The library currently exports **9 functions plus the `TruckPipeline` fluent
wrapper**, all accessible from the top-level namespace:

```python
from thaitruck import fried_rice      # time-series DataFrame merger
from thaitruck import orange_chicken  # DataFrame normalization / cleaning
from thaitruck import larb            # statistical profiling
from thaitruck import pad_thai        # string padding and alignment
from thaitruck import sticky_rice     # persistent disk caching
from thaitruck import satay           # expressive DataFrame slicing
from thaitruck import tom_kha         # deep config dict merging
from thaitruck import massaman        # rolling aggregations and percentage change
from thaitruck import nam_pla         # schema validation
from thaitruck import TruckPipeline   # fluent chained pipeline
```

Every DataFrame-native function is also reachable as `df.truck.<name>()` via a
registered pandas accessor (`import thaitruck` registers it as a side effect).

---

## Repository Layout

```
ThaiTruck/
├── pyproject.toml              # build config, metadata, dependencies
├── README.md                   # user-facing install and usage guide
├── ARCHITECTURE.md             # technical architecture reference
├── PROJECT.md                  # this file — comprehensive project state + roadmap
├── src/
│   └── thaitruck/
│       ├── __init__.py         # public re-exports + __version__
│       ├── fried_rice.py       # time-series DataFrame merger
│       ├── orange_chicken.py   # DataFrame normalization / cleaning
│       ├── larb.py             # statistical profiling
│       ├── pad_thai.py         # string padding / alignment
│       ├── sticky_rice.py      # persistent disk cache
│       ├── satay.py            # expressive DataFrame slicing
│       ├── tom_kha.py          # deep config dict merging
│       ├── massaman.py         # rolling aggregations and percentage change
│       ├── nam_pla.py          # schema validation
│       ├── exceptions.py       # ThaiTruckError hierarchy (shared, leaf module)
│       ├── pipeline.py         # TruckPipeline fluent wrapper (composition layer)
│       └── accessor.py         # registers the `.truck` pandas accessor (composition layer)
└── tests/
    ├── test_fried_rice.py
    ├── test_orange_chicken.py
    ├── test_larb.py
    ├── test_pad_thai.py
    ├── test_sticky_rice.py
    ├── test_satay.py
    ├── test_tom_kha.py
    ├── test_massaman.py
    ├── test_nam_pla.py
    ├── test_exceptions.py
    ├── test_pipeline.py
    └── test_accessor.py
```

---

## Current Menu — All 9 Modules

---

### `fried_rice` — The Flagship

**File:** `src/thaitruck/fried_rice.py`

Merges N DataFrames with mismatched timestamps into one coherent result. This is the core problem ThaiTruck was built to solve: you have several DataFrames at different frequencies, with different date column names, and you just want one clean DataFrame.

**Signature:**

```python
def fried_rice(
    *dfs: pd.DataFrame,
    freq: str = "D",
    heat: int = 3,
    join: str = "outer",
    fuzzy_columns: bool = False,
    fill_method: str = "ffill",
    date_col: str | list[str] | None = None,
    suffix_template: str | None = None,
) -> pd.DataFrame
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `*dfs` | — | Two or more DataFrames to blend |
| `freq` | `"D"` | Target resampling frequency — any pandas offset alias (`"D"`, `"W"`, `"ME"`, `"QE"`, etc.) |
| `heat` | `3` | Conflict resolution strategy when column names collide (see below) |
| `join` | `"outer"` | Which rows survive: `"outer"` (union of all frames' timestamps), `"inner"` (intersection only), `"left"` (first frame's timestamps only) |
| `fuzzy_columns` | `False` | Normalize column names before merging so `"Close"`, `"close"`, and `"closing_price"` are treated as the same column |
| `fill_method` | `"ffill"` | How to fill gaps after resampling: `"ffill"`, `"bfill"`, or `"interpolate"` |
| `date_col` | `None` | Override auto-detection — single string applied to all DataFrames, or a list with one entry per DataFrame |
| `suffix_template` | `None` | Format string for heat=3 collision suffixes, receiving `{i}` (the 1-based frame position). Defaults to `"_{i}"` |

Timezone-aware DatetimeIndex values are stripped to naive (`tz_localize(None)`)
immediately after date detection, so mixing tz-aware and tz-naive inputs no
longer crashes.

**Heat levels (conflict resolution):**

| Heat | Strategy |
|---|---|
| 1 | Conservative — keep first DataFrame's version of any column; skip entirely if it already exists |
| 2 | Prefer left — later DataFrames skip any column already present |
| 3 | Suffix-disambiguate — duplicate columns from frame N get `_N` suffix (default) |
| 4 | Prefer right — earlier DataFrames' columns are overwritten by later ones |
| 5 | Napalm — last non-null value wins per cell across all frames |

**Date auto-detection logic (applied per DataFrame):**

1. If the DataFrame's index is already a `DatetimeIndex`, use it directly
2. Check column names against a known hints list: `date`, `ts`, `timestamp`, `time`, `report_date`, `datetime`, `dt`, `period`, `day`, `trade_date`, `as_of_date`, `effective_date`
3. Check column dtypes for `datetime64`
4. Try `pd.to_datetime()` on the first 5 values of each `object` column

**Internal helpers (not public):**

- `_detect_date_col(df)` — runs the auto-detection logic above
- `_normalize(name)` — lowercases and collapses whitespace/hyphens/underscores for fuzzy matching
- `_reindex_frames(frames, join)` — computes the target index for `join` and reindexes all prepared frames to it before merging
- `_merge(frames, heat, suffix_template=None)` — dispatches to the correct merge strategy based on heat level

**Processing pipeline per DataFrame:**

1. Copy the input (never mutates)
2. Detect or use the specified date column and set it as the index
3. Optionally fuzzy-normalize column names
4. Resample to `freq` using `.last()` (keeps the last observation per period)
5. Fill gaps with the specified `fill_method`
6. Merge all prepared frames using the heat strategy

**Example:**

```python
from thaitruck import fried_rice

# Three DataFrames: daily prices, quarterly earnings, monthly macro
result = fried_rice(
    prices_df,     # "Date" column, daily
    earnings_df,   # "report_date" column, quarterly
    macro_df,      # "ts" column, monthly
    freq="D",
    heat=3,
    fuzzy_columns=True,
)
```

---

### `orange_chicken` — The Glaze

**File:** `src/thaitruck/orange_chicken.py`

Normalizes and cleans raw DataFrames. Column names are standardized, string whitespace stripped, numeric strings coerced, boolean strings resolved, and sparse columns dropped — all in a single pass controlled by the `heat` level.

**Signature:**

```python
def orange_chicken(
    df: pd.DataFrame,
    heat: int = 3,
    *,
    rename: dict | None = None,
    dtypes: dict | None = None,
) -> pd.DataFrame
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `df` | — | Raw input DataFrame |
| `heat` | `3` | Cleaning aggressiveness — each level is cumulative (includes all lower levels) |
| `rename` | `None` | `{old: new}` column renames, applied after the heat-level cleaning steps |
| `dtypes` | `None` | `{column: dtype}` passed to `.astype()`, applied last — keys refer to post-`rename` column names |

**Heat levels (cumulative):**

| Heat | What gets cleaned |
|---|---|
| 1 | Column names only — lowercase, underscores, strip special characters (`"Open Price"` → `"open_price"`) |
| 2 | + Strip string cell whitespace; drop all-null rows and columns |
| 3 | + Coerce numeric strings to numbers (≥50% of non-null values must convert cleanly) — *default* |
| 4 | + Coerce boolean strings (`"yes"/"true"/"on"/"y"/"1"` → `True`, etc.) for columns with ≥90% boolean-like coverage; drop columns with ≥90% nulls |
| 5 | + Drop columns with ≥50% nulls — napalm |

**Column name normalization (`_clean_col_name`):**

1. Strip leading/trailing whitespace and lowercase
2. Replace spaces, hyphens, and dots with underscores
3. Remove all non-word characters (anything other than letters, digits, underscores)
4. Collapse multiple underscores; strip leading/trailing underscores
5. Fall back to `"col"` if the result is empty

**Boolean string vocabulary recognized:**

- True: `"true"`, `"yes"`, `"y"`, `"t"`, `"1"`, `"on"`
- False: `"false"`, `"no"`, `"n"`, `"f"`, `"0"`, `"off"`

**Internal helpers (not public):**

- `_clean_col_name(name)` — column name normalization
- `_strip_strings(df)` — strip whitespace from all `object` columns
- `_coerce_numeric(df)` — numeric coercion with ≥50% success threshold
- `_coerce_booleans(df)` — boolean coercion with ≥90% coverage threshold
- `_drop_sparse(df, threshold)` — drop columns at or above null fraction

**Not implemented:** an optional change-log return value (what was renamed,
coerced, dropped) is still on the roadmap — it needs a return-shape decision
(new field vs. a second return value vs. `return_log=True` changing the
return type) that wasn't pinned down in this pass.

**Example:**

```python
from thaitruck import orange_chicken

raw = pd.DataFrame({
    "  Open Price  ": ["1,250.00", "1,300.00"],
    "Active?":        ["yes", "no"],
    "Notes":          [None, None],  # 100% null
})

clean = orange_chicken(raw, heat=4)
# Columns: open_price (float64), active (bool)
# "Notes" dropped (100% null at heat=2)
```

---

### `larb` — The Raw Bar

**File:** `src/thaitruck/larb.py`

Returns a one-row-per-column statistical profile of any DataFrame. Numeric columns get full descriptive stats plus IQR-based outlier detection. Non-numeric columns get cardinality and top-value stats. Heat controls how aggressively outliers are flagged.

**Signature:**

```python
def larb(
    df: pd.DataFrame,
    heat: int = 3,
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> pd.DataFrame
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `df` | — | DataFrame to profile |
| `heat` | `3` | Outlier sensitivity — higher heat = tighter IQR fences = more outliers flagged |
| `include` | `None` | Only profile these columns; applied before `exclude` |
| `exclude` | `None` | Never profile these columns |

**Not implemented:** the `plot=True` histogram option is still on the roadmap
— it needs a design decision on the optional `matplotlib` dependency wiring
and what the function returns when plotting (the profile DataFrame plus
figures, or a side-effecting `plt.show()`), which wasn't pinned down here.

**Heat → IQR multiplier mapping:**

| Heat | IQR Multiplier | Character |
|---|---|---|
| 1 | × 3.0 | Extreme outliers only |
| 2 | × 2.5 | |
| 3 | × 2.0 | Moderate outliers — default |
| 4 | × 1.5 | Standard Tukey fences |
| 5 | × 1.0 | Very sensitive — tight clusters |

**Output columns:**

For **numeric** columns:

| Column | Description |
|---|---|
| `dtype` | pandas dtype string |
| `count` | Non-null row count |
| `null_pct` | Percentage of null values |
| `mean` | Arithmetic mean |
| `std` | Standard deviation |
| `min` | Minimum value |
| `p25` | 25th percentile |
| `median` | Median (50th percentile) |
| `p75` | 75th percentile |
| `max` | Maximum value |
| `skew` | Distribution skewness |
| `lower_fence` | IQR lower outlier fence |
| `upper_fence` | IQR upper outlier fence |
| `outliers` | Count of outlier values |
| `outlier_pct` | Outlier percentage |
| `unique` | `None` (N/A for numeric) |
| `top` | `None` (N/A for numeric) |
| `top_freq` | `None` (N/A for numeric) |

For **non-numeric** columns: `dtype`, `count`, `null_pct` plus `unique` (cardinality), `top` (mode value), `top_freq` (mode frequency). All numeric stat columns are `None`.

**Example:**

```python
from thaitruck import larb

profile = larb(df, heat=3)
# Returns DataFrame indexed by column name
print(profile[["count", "null_pct", "mean", "outliers"]])
```

---

### `pad_thai` — The Noodles

**File:** `src/thaitruck/pad_thai.py`

String padding and alignment utility. Works on a single string, a Python list, or a pandas Series. Mirrors the input type in the output.

**Signature:**

```python
def pad_thai(
    value: str | list | pd.Series,
    width: int,
    align: str = "left",
    fill: str = " ",
    truncate: bool = False,
) -> str | list | pd.Series
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `value` | — | A string, list of strings, or pandas Series |
| `width` | — | Target total character width |
| `align` | `"left"` | `"left"`, `"right"`, or `"center"` |
| `fill` | `" "` | Single fill character |
| `truncate` | `False` | If `True`, values longer than `width` are cut and suffixed with `"…"` |

**Behavior:**

- `str` input → `str` output
- `list` input → `list` output (each element padded individually)
- `pd.Series` input → `pd.Series` output (applied with `.map()`)
- `None` values in a list or Series are treated as empty strings

**Examples:**

```python
from thaitruck import pad_thai

pad_thai("close", 10)                            # "close     "
pad_thai("close", 10, align="right")             # "     close"
pad_thai("close", 10, align="center")            # "  close   "
pad_thai("a very long label", 12, truncate=True) # "a very long…"

# Works on a Series
df["ticker"] = pad_thai(df["ticker"], width=6, align="right")
```

---

### `sticky_rice` — The Cache

**File:** `src/thaitruck/sticky_rice.py`

A persistent disk-caching decorator. Wraps any callable and pickles its return value to `.thaitruck_cache/`. On subsequent calls with the same arguments within the TTL window, the cached value is returned without re-running the function.

**Signature (decorator factory):**

```python
@sticky_rice(ttl=3600, key=None, cache_dir=None, compress=False)
def my_fn(...): ...

# Bare decorator (no options, uses all defaults)
@sticky_rice
def my_fn(...): ...
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `ttl` | `3600` | Seconds before a cached entry expires. `0` = never expires |
| `key` | `None` | Fixed cache key string. If omitted, key is `MD5(module.qualname:args:kwargs)` |
| `cache_dir` | `None` | Cache directory. Defaults to `.thaitruck_cache/` in the working directory |
| `compress` | `False` | Gzip cache files on write, and read them back through gzip |

**Decorated function gains:**

- `.clear()` — deletes all cache entries for this function (or the single fixed-key entry if `key=` was set); also resets `.stats()` counters
- `.cache_dir` — `pathlib.Path` pointing to the cache directory
- `.stats()` — returns `{"hits": int, "misses": int, "size_bytes": int}`. Hit/miss
  counts are per-process (reset on restart, not persisted). When `key` is a
  fixed string, `size_bytes` is that one file's size; otherwise it's the whole
  `cache_dir` — content-hash keys have no recoverable link back to a single
  function, the same limitation `.clear()` already has in that case

**Not implemented:** a Redis backend (`backend="redis"`) is still on the
roadmap — it needs an external dependency and connection-config design
(host/port/auth) that wasn't pinned down here.

**Cache storage format:**

Files are stored as `<md5_hash>.pkl`. Each pickle file contains:
```python
{"ts": float,   # unix timestamp when the value was written
 "value": Any}  # the pickled return value
```

**Cache hit / miss logic:**

1. Compute the cache key (hash of function + args, or fixed key)
2. Check if the `.pkl` file exists
3. Load the file and check if `time.time() - stored["ts"] > ttl` (skip if `ttl == 0`)
4. Return cached value on hit; run function and write cache on miss

**Example:**

```python
from thaitruck import sticky_rice

@sticky_rice(ttl=3600)
def fetch_and_merge(ticker: str) -> pd.DataFrame:
    # expensive API calls...
    return result

df = fetch_and_merge("NVDA")  # computed and cached
df = fetch_and_merge("NVDA")  # returned from disk instantly
fetch_and_merge.clear()       # invalidate manually
```

---

### `satay` — The Skewer

**File:** `src/thaitruck/satay.py`

Expressive multi-dimensional DataFrame slicing. Pass any combination of column selectors, row filters, and callables as positional "skewers." Row filters narrow the result set; column selectors determine which columns appear in the output. Column selectors are always applied last regardless of order.

**Signature:**

```python
def satay(df: pd.DataFrame, *skewers: Any) -> pd.DataFrame
```

**Skewer dispatch table:**

| Type | Behavior |
|---|---|
| `str` | Column selector — add this column to the output |
| `list[str]` | Multi-column selector — add all listed columns |
| `slice` | Positional row slice via `iloc` |
| `tuple(col, lo, hi)` | Range row filter — keep rows where `lo <= df[col] <= hi` |
| `tuple(col, value, op)` | Comparison row filter — keep rows where `df[col] op value`. `op` is one of `">"`, `"<"`, `">="`, `"<="`, `"=="`, `"!="`. Dispatch is by the third element's type: a recognized operator string selects this form, anything else falls back to the range form above |
| `dict` | Equality or `isin` filter — `{col: value}` or `{col: [v1, v2]}` |
| `callable` | Boolean mask filter — receives the current DataFrame, returns a bool mask |

**Ordering rules:**

- All non-column skewers (row filters) are applied **in order** as they appear
- String and list skewers (column selectors) are collected and applied **after all row filters**
- Calling `satay(df)` with no skewers returns a copy of the DataFrame unchanged

**Shorthand:** `satay.head(df, n=5)` and `satay.tail(df, n=5)` are attached
directly to the `satay` function object — thin wrappers around
`satay(df, slice(0, n))` / `satay(df, slice(-n, None))`.

**Examples:**

```python
from thaitruck import satay

satay(df, "price")                              # single column
satay(df, ["price", "volume"])                  # multiple columns
satay(df, slice(0, 100))                        # first 100 rows
satay(df, ("price", 10.0, 50.0))               # price between 10 and 50
satay(df, ("price", 100, ">"))                  # price > 100
satay(df, {"sector": "Tech"})                   # equality filter
satay(df, {"sector": ["Tech", "Energy"]})       # isin filter
satay(df, lambda d: d["volume"] > 1_000_000)   # callable
satay.head(df, 10)                              # first 10 rows
satay.tail(df, 10)                              # last 10 rows

# Compose freely — filters applied left to right, columns last
satay(df, {"sector": "Tech"}, ("price", 10, 200), "price", "volume")
```

---

### `tom_kha` — The Broth

**File:** `src/thaitruck/tom_kha.py`

Deep config dict merging. Later dicts win. Nested dicts are merged recursively — they are never wholesale-replaced. Lists and scalar values are always overwritten by the later config.

**Signature:**

```python
def tom_kha(
    *configs: dict[str, Any],
    defaults: dict[str, Any] | None = None,
) -> dict[str, Any]
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `*configs` | — | Config dicts in ascending precedence order (last wins) |
| `defaults` | `None` | Base defaults applied before all configs (lowest precedence) |

**Merge rules:**

- Precedence order: `defaults` → `configs[0]` → `configs[1]` → … (last wins)
- Nested `dict` values are merged recursively via `_deep_merge`
- Lists are replaced entirely (not extended)
- Scalar values are replaced by the later config
- Input dicts are never mutated — all merges happen on copies

**Examples:**

```python
from thaitruck import tom_kha

tom_kha(
    {"db": {"host": "localhost", "port": 5432}},
    {"db": {"port": 5433}, "debug": True},
)
# → {"db": {"host": "localhost", "port": 5433}, "debug": True}

config = tom_kha(
    base_config,
    env_config,
    cli_overrides,
    defaults={"retries": 3, "timeout": 30, "db": {"port": 5432}},
)
```

---

### `massaman` — Window & Rolling Aggregations

**File:** `src/thaitruck/massaman.py`

Named for the slow-cooked curry — this one is about aggregations over a window,
not an instant transform. Adds rolling-window columns and row-over-row percentage
change to a DataFrame without discarding the original columns.

**Signature:**

```python
def massaman(
    df: pd.DataFrame,
    column: str,
    *,
    window: int = 20,
    ops: list[str] | None = None,
) -> pd.DataFrame
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `df` | — | Input DataFrame |
| `column` | — | Column to aggregate |
| `window` | `20` | Rolling window size, in rows |
| `ops` | `None` (→ `["mean"]`) | Any of `"mean"`, `"std"`, `"sum"`, `"min"`, `"max"`, `"median"` (windowed) or `"pct_change"` (not windowed) |

**Output column naming:**

- Windowed ops → `{column}_roll_{op}_{window}` (e.g. `price_roll_mean_20`)
- `"pct_change"` → `{column}_pct_change` — no window suffix, since it is a plain
  row-over-row percent change, not a rolling aggregation

**Current behavior:**

- Raises `KeyError` if `column` is not in `df`
- Raises `ValueError` for an unrecognized op
- Never mutates the input — operates on a `.copy()`
- Note: expanding windows and lag/lead columns (mentioned in earlier roadmap
  drafts) are **not** implemented — they need a parameter design that wasn't
  pinned down, and were deliberately left out of this pass

**Example:**

```python
from thaitruck import massaman

result = massaman(df, "price", window=20, ops=["mean", "std", "pct_change"])
# Adds columns: price_roll_mean_20, price_roll_std_20, price_pct_change
```

**Tests:** `tests/test_massaman.py`

---

### `nam_pla` — Schema Validation

**File:** `src/thaitruck/nam_pla.py`

**Scope decision (locked in 2026-09-09):** `nam_pla` and `nam_prik` were
originally drafted as a heavy/light validator pair. They were merged into one
`nam_pla` — the schema spec shape is identical either way, and two modules with
near-identical signatures was a discoverability tax without a real functional
split. `strict=True` covers the "fast fail-fast in a script" use case that
`nam_prik` was meant for.

**Signature:**

```python
def nam_pla(
    df: pd.DataFrame,
    spec: dict[str, dict[str, Any]],
    *,
    strict: bool = False,
) -> pd.DataFrame
```

**Constraint keys** (per column, all optional):

| Key | Description |
|---|---|
| `dtype` | `float`/`int`/`str`/`bool`, or anything `numpy.dtype()` accepts. `float` accepts any numeric dtype (int or float); the others are exact. |
| `nullable` | Default `True`. If `False`, any null fails. |
| `min` / `max` | Numeric bounds, inclusive. |
| `isin` | Iterable of allowed values. |
| `required` | Default `True`. If `False`, the column is only checked when present instead of being reported as missing. |

**Current behavior:**

- Returns a violations DataFrame (`column`, `check`, `message`) — empty (but
  same columns) when the DataFrame is clean. Nothing raises by default, so it's
  safe as a pipeline checkpoint.
- `strict=True` raises `ValidationError` (see Exceptions below) when the report
  is non-empty, with the report rendered in the message.
- An unrecognized constraint key raises `ValueError` immediately — catches typos
  in the spec itself rather than silently ignoring them.
- Never mutates the input.
- Excluded from `TruckPipeline` for the same reason as `larb`: it returns a
  report, not a transformed version of the input. Available via the accessor
  (`df.truck.nam_pla(spec)`) since the accessor isn't chain-shaped.

**Example:**

```python
from thaitruck import nam_pla

spec = {
    "price":  {"dtype": float, "min": 0, "nullable": False},
    "sector": {"dtype": str, "nullable": False, "isin": ["Tech", "Energy", "Health"]},
}

report = nam_pla(df, spec)          # empty DataFrame if clean
nam_pla(df, spec, strict=True)      # raises ValidationError if not
```

**Tests:** `tests/test_nam_pla.py`

---

## Ergonomics & Infrastructure (Implemented)

Four items from the former Priority 2/3 roadmap are now implemented.

### Pandas Accessor — `df.truck.*`

**File:** `src/thaitruck/accessor.py`

Registers `"truck"` as a pandas DataFrame accessor via
`pd.api.extensions.register_dataframe_accessor`. Registration happens as an
import side effect — `import thaitruck` (or importing anything from it) is
enough; no separate call is required. Wraps `orange_chicken`, `larb`, `satay`,
`fried_rice`, `massaman`, and `nam_pla` — thin delegation, no separate
implementation. Each wrapper method's signature mirrors its underlying
function exactly (e.g. `df.truck.orange_chicken(heat=3, rename=..., dtypes=...)`,
`df.truck.fried_rice(other_df, join="inner", ...)`), so a new parameter on the
function requires a matching update here — there's no `**kwargs` passthrough.

```python
import thaitruck

df.truck.orange_chicken(heat=3)
df.truck.larb()
df.truck.satay({"sector": "Tech"}, "price")
df.truck.nam_pla({"price": {"min": 0}})
```

### `TruckPipeline` — Fluent API

**File:** `src/thaitruck/pipeline.py`

A chainable wrapper around a DataFrame. Each method returns a new
`TruckPipeline` instance wrapping the transformed DataFrame; `.result()` unwraps
back to a plain `pd.DataFrame`. Covers `orange_chicken`, `fried_rice`, `satay`,
and `massaman` (the DataFrame-in/DataFrame-out functions). `larb` is
intentionally excluded — it returns a per-column profile, not a transformed
version of the input, so it doesn't fit the chain's "keep transforming the same
data" semantics; call it standalone or via the accessor for a spot-check.

```python
from thaitruck import TruckPipeline

result = (
    TruckPipeline(raw_df)
    .orange_chicken(heat=3)
    .fried_rice(earnings_df, freq="D")
    .satay({"sector": "Tech"})
    .result()
)
```

### Custom Exceptions

**File:** `src/thaitruck/exceptions.py`

A shared, dependency-free leaf module defining `ThaiTruckError` (base) and four
specific subclasses, each also inheriting the built-in exception type it
replaces so existing `except ValueError` / `except TypeError` code keeps working:

| Exception | Also a... | Raised by |
|---|---|---|
| `ThaiTruckError` | `Exception` | base class |
| `DateColumnNotFound` | `ValueError` | `fried_rice` — no date column detected |
| `InvalidHeatLevel` | `ValueError` | `orange_chicken`, `larb` — heat out of range |
| `SkewTypeError` | `TypeError` | `satay` — unrecognised skewer type |
| `ValidationError` | `ValueError` | `nam_pla` — schema violation, `strict=True` only |

**Tests:** `tests/test_pipeline.py`, `tests/test_accessor.py`, `tests/test_exceptions.py`, `tests/test_nam_pla.py`

---

## The Heat Guide

`fried_rice`, `orange_chicken`, and `larb` all share a `heat` parameter (1–5). The scale is consistent across the package: higher heat is more aggressive. The specific behavior differs per module but the metaphor is always the same.

| Heat | Vibe |
|---|---|
| 1 | Mild. Barely noticeable. Tourist-safe. |
| 2 | A little warmth. |
| 3 | Medium. The default. Regular customer. |
| 4 | Getting spicy. Know what you're doing. |
| 5 | Napalm. No survivors. |

---

## Architecture

### Module Independence

The original 7 utility modules remain fully independent — none imports from
another. External dependencies are `pandas` and `numpy` only. `sticky_rice` and
`tom_kha` use stdlib only. `massaman` and `nam_pla` join them as the eighth and
ninth independent utility modules (`pandas`/`numpy` only).

`exceptions` is a shared, dependency-free leaf module that `fried_rice`,
`orange_chicken`, `larb`, `satay`, and `nam_pla` import for their error types —
a common "errors live in one place" pattern, not a violation of utility-module
independence (none of the utility modules import each other; they only import
the shared leaf).

`pipeline` and `accessor` are a separate **composition layer**, analogous to
`__init__.py`'s re-exports: their entire purpose is to call the utility modules,
so they intentionally depend on several of them.

```
fried_rice     → pandas, numpy, exceptions
orange_chicken → pandas, exceptions
larb           → pandas, exceptions
pad_thai       → pandas
sticky_rice    → stdlib (pickle, hashlib, pathlib, time, functools)
satay          → pandas, exceptions
tom_kha        → stdlib only
massaman       → pandas
nam_pla        → pandas, numpy, exceptions
exceptions     → stdlib only (leaf)
pipeline       → fried_rice, orange_chicken, satay, massaman  (composition layer)
accessor       → fried_rice, orange_chicken, larb, satay, massaman, nam_pla  (composition layer)
```

### Shared Patterns

- **DataFrame modules** (`fried_rice`, `orange_chicken`, `larb`, `satay`) — always accept `pd.DataFrame`, always return `pd.DataFrame`, never mutate the input (all operate on `.copy()`)
- **`pad_thai`** — mirrors input type: `str → str`, `list → list`, `pd.Series → pd.Series`
- **`tom_kha`** — `dict in / dict out`, never mutates input dicts
- **`sticky_rice`** — decorator, wraps any callable, preserves signature via `functools.wraps`

### Build System

| Tool | Role |
|---|---|
| `hatchling` | Build backend (PEP 517) |
| `python -m build` | Produces `.tar.gz` + `.whl` in `dist/` |
| `twine upload dist/*` | Publishes to PyPI |

Version is declared once in `pyproject.toml` and mirrored in `src/thaitruck/__init__.py` as `__version__`.

---

## Tests

One test file per module, mirroring the source layout. Tests use `pytest` with class-based grouping.

```
tests/test_fried_rice.py      ←→  src/thaitruck/fried_rice.py
tests/test_orange_chicken.py  ←→  src/thaitruck/orange_chicken.py
tests/test_larb.py            ←→  src/thaitruck/larb.py
tests/test_pad_thai.py        ←→  src/thaitruck/pad_thai.py
tests/test_sticky_rice.py     ←→  src/thaitruck/sticky_rice.py
tests/test_satay.py           ←→  src/thaitruck/satay.py
tests/test_tom_kha.py         ←→  src/thaitruck/tom_kha.py
tests/test_massaman.py        ←→  src/thaitruck/massaman.py
tests/test_nam_pla.py         ←→  src/thaitruck/nam_pla.py
tests/test_exceptions.py      ←→  src/thaitruck/exceptions.py
tests/test_pipeline.py        ←→  src/thaitruck/pipeline.py
tests/test_accessor.py        ←→  src/thaitruck/accessor.py
```

`sticky_rice` tests use pytest's `tmp_path` fixture to isolate cache files per test run (no `.thaitruck_cache/` pollution). `unittest.mock.patch` is used for time-based TTL testing.

Run tests:

```bash
pip install thaitruck[dev]
pytest
```

---

## Build & Publish

```bash
python -m build            # produces dist/*.whl and dist/*.tar.gz
twine check dist/*         # verify package metadata
twine upload dist/*        # publish to PyPI
```

Bump the version in exactly two places before each release:
- `pyproject.toml` → `version = "x.y.z"`
- `src/thaitruck/__init__.py` → `__version__ = "x.y.z"`

---

## The Food Truck Fleet

ThaiTruck is part of a broader "food truck fleet" of PyPI packages, each with its own lane:

| Package | Status | Focus |
|---|---|---|
| **thaitruck** | Live on PyPI (v0.2.2) | Batch DataFrame cleaning, merging, profiling, caching |
| **sushitruck** | PyPI name secured (v0.1.0 stub) | Streaming ingestion, REST API connectors, file reading, normalization |
| **ramentruck** | PyPI name secured (v0.1.0 stub) | ML/AI toolkit — training, tuning, explainability, deep learning |

Each package is **fully independent** — none imports from another. They compose at the application layer through `pd.DataFrame`. SushiTruck produces them. ThaiTruck transforms them. RamenTruck models them. ThaiTruck's only dependencies are `pandas` and `numpy`; it knows nothing about SushiTruck or RamenTruck.

---

## Roadmap — Planned Work

Priorities are ordered by impact and maturity. Each item is tagged with its conceptual category.

---

### Priority 1: Infrastructure & Quality Gates

#### CI/CD — GitHub Actions

Add `.github/workflows/tests.yml` to run `pytest` on every push and pull request. Test matrix:

- Python versions: 3.9, 3.10, 3.11, 3.12
- Pandas versions: 1.5.x, 2.x

#### Type Stubs

Add a `py.typed` marker file (PEP 561) and fill in any inline type annotations that are missing. This enables IDE type checking for consumers of the library.

#### Benchmarks

Add a `benchmarks/` directory using `pytest-benchmark` to catch performance regressions between releases. Focus on `fried_rice` (resample + merge paths) and `sticky_rice` (cache read/write).

#### CHANGELOG.md

Add a `CHANGELOG.md` file tracking what changed per version — features, fixes, breaking changes.

---

### Priority 2: Validation & Alerting (Condiment Caddy)

> **`nam_pla` is implemented** — see [Current Menu](#nam_pla--schema-validation)
> above. `nam_prik` was merged into it rather than built separately (see the
> scope decision in that section); `strict=True` covers the fast-fail-fast
> spot-check use case `nam_prik` was meant for.

#### `prik_nam_som` — Automated Alerting & Test-Suite Trigger

Adds "bite" to the pipeline by catching data drift, schema mismatches, or sudden drops in row counts. Can trigger a log alert, email, or webhook — or fire a test suite — when anomalies are detected.

```python
from thaitruck import prik_nam_som

prik_nam_som(df, baseline=reference_df, thresholds={"row_drop_pct": 0.10})
# Raises alert or returns anomaly report DataFrame
```

---

### Priority 3: Ergonomics

> **Implemented** — pandas accessor (`df.truck.*`), `TruckPipeline`, and the
> full `ThaiTruckError` hierarchy (including `ValidationError`) are done. See
> [Ergonomics & Infrastructure (Implemented)](#ergonomics--infrastructure-implemented)
> above.

---

### Priority 4: Enhancements to Existing Modules

> **Mostly implemented (2026-09-09)** — see the Current Menu entries above for
> each module's updated signature. What's done and what's still open, per
> module:

#### `fried_rice`

- ✅ **`join` parameter** — `"outer"` (default), `"inner"`, `"left"`
- ✅ **`suffix_template` parameter** — receives `{i}` (frame position), not
  `{source}` as originally sketched — frames aren't named entities in this API
- ✅ **Timezone-aware DatetimeIndex support** — tz is stripped automatically

#### `orange_chicken`

- ✅ **`rename` parameter** — applied after the heat-level cleaning steps
- ✅ **`dtypes` parameter** — applied last, after `rename`
- ⬜ **Change log** — still needs a return-shape decision, see the Current Menu note above

#### `larb`

- ✅ **`include` / `exclude` parameters**
- ⬜ **`plot` parameter** — still needs an optional-dependency + return-shape decision, see the Current Menu note above

#### `sticky_rice`

- ⬜ **Redis backend** — still needs external dependency + connection-config design, see the Current Menu note above
- ✅ **`.stats()` method**
- ✅ **`compress=True` option**

#### `satay`

- ✅ **`.head(n)` and `.tail(n)` shorthand**
- ✅ **`(col, value, op)` tuple form** — disambiguated from `(col, lo, hi)` by
  the third element's type: a recognized operator string picks the comparison
  form, anything else falls back to the range form

---

### Priority 5: New Utility Modules

> **`massaman` is implemented** — see the [Current Menu](#massaman--window--rolling-aggregations)
> above. Expanding windows and lag/lead columns from the original concept are
> not included; they need a parameter design that wasn't pinned down.

#### `som_tam` — DataFrame Diffing

Compare two DataFrames and surface what changed: added rows, removed rows, changed values, and schema drift. Returns a structured diff report DataFrame.

```python
from thaitruck import som_tam

diff = som_tam(df_before, df_after)
# Returns DataFrame with change_type column: "added", "removed", "modified"
```

#### `boat_noodles` — Sequential Chunked Processing

Process large files in chunks without loading everything into memory. Wraps `pd.read_csv(..., chunksize=N)` and auto-applies other ThaiTruck functions per chunk. Sequential (single-threaded). See `chicken_satay` for the async/parallel version.

```python
from thaitruck import boat_noodles

for chunk in boat_noodles("big_file.csv", chunksize=10_000, apply=orange_chicken):
    process(chunk)
```

#### `green_curry` — Recipe-Based Transforms

Apply a named, reproducible sequence of ThaiTruck operations from a config dict or YAML file. Lets teams share cleaning pipelines without writing code.

```python
from thaitruck import green_curry

result = green_curry(df, recipe={
    "orange_chicken": {"heat": 3},
    "fried_rice":     {"freq": "D"},
    "satay":          [{"sector": "Tech"}],
})
```

---

### Priority 6: Memory Management

#### `dish_bucket` (a.k.a. `dish_soap`) — DataFrame Memory Optimizer

Keeps the truck nimble when dealing with massive DataFrames. Downcasts numeric types (`float64 → float32`, `int64 → int32`) and optionally runs `gc.collect()` to reclaim memory.

```python
from thaitruck import dish_bucket

df = dish_bucket(df)             # returns optimized DataFrame
dish_bucket(df, report=True)     # prints before/after memory usage
dish_bucket.flush()              # gc.collect() + clear temp refs
```

Name TBD between `dish_bucket` and `dish_soap` — both work thematically.

---

### Priority 7: Output & Reporting

#### `thai_roti` — Finalized Output Formatter

The last step before the truck hands the meal to the customer. Wraps a finished DataFrame into a polished, deliverable format.

```python
from thaitruck import thai_roti

thai_roti(df, format="excel", path="output/report.xlsx")   # requires openpyxl
thai_roti(df, format="html",  path="output/dashboard.html")
thai_roti(df, format="od_summary")   # returns structured origin-destination dict
```

#### `coconut_ice_cream` — Post-Pipeline Cleanup

The palate cleanser. Post-pipeline cleanup function that flushes temporary storage, clears the `sticky_rice` cache on command, and resets the environment back to a clean state.

```python
from thaitruck import coconut_ice_cream

coconut_ice_cream(clear_cache=True, flush_temp=True, reset_env=True)
```

---

### Priority 8: Input / Connectors

> **Note:** Streaming ingestion, API connectors, and JSON normalization belong to **SushiTruck**, not ThaiTruck. ThaiTruck accepts DataFrames — it does not connect to external sources. `thai_tea` and `spring_rolls` were early roadmap ideas from before SushiTruck was defined as a separate package. They should be built there (`nigiri`, `maki`, `wasabi`) and are removed from the ThaiTruck roadmap.

---

### Priority 9: Orchestration

#### `chicken_satay` — Async / Parallel DataFrame Processing

Handles async chunk-based slicing or parallel processing for large or pre-split DataFrames. When a feast has a very large source, `chicken_satay` skewers it into concurrent workloads (multiprocessing or asyncio) and reassembles the result. Distinct from `boat_noodles` (sequential) — this one goes wide.

```python
from thaitruck import chicken_satay

result = chicken_satay(big_df, apply=orange_chicken, workers=4, chunksize=50_000)
```

#### `thai_feast` — Pipeline Orchestration

The grand finale. Coordinate multiple ThaiTruck operations across multiple data sources as a single declarative pipeline — a mini-DAG runner with a menu instead of a DAG. Supports async execution of independent steps, retry logic, and a manifest/audit log of what ran and when.

```python
from thaitruck import thai_feast

feast = thai_feast({
    "sources": [prices_df, earnings_df, macro_df],
    "clean":   {"module": "orange_chicken", "heat": 3},
    "merge":   {"module": "fried_rice", "freq": "D"},
    "filter":  {"module": "satay", "skewers": [{"sector": "Tech"}]},
    "cache":   {"module": "sticky_rice", "ttl": 3600},
})
result = feast.serve()
```

---

## RamenTruck — Planned ML/AI Sibling

RamenTruck is a planned standalone PyPI package for ML/AI work. The ThaiTruck → RamenTruck pipeline: ThaiTruck cleans and prepares the DataFrame; RamenTruck trains, evaluates, and explains models on it.

**Why the name:** Ramen is deep, layered, complex, and takes real expertise to build well — a direct map to ML/AI work.

### Planned Architecture

Optional extras to avoid dependency bloat:

```bash
pip install ramentruck           # core: broth, tare, soft_boiled_egg, chashu
pip install ramentruck[deep]     # + tonkotsu (PyTorch / TensorFlow)
pip install ramentruck[explain]  # + nori (SHAP)
pip install ramentruck[tracking] # + miso (MLflow / W&B)
```

### Module List

#### Core (scikit-learn + numpy only)

| Module | Metaphor | Purpose |
|---|---|---|
| `broth` | The base — foundation everything builds on | Model training / fitting wrapper |
| `tare` | Concentrated seasoning — small adjustments, big impact | Hyperparameter tuning — wraps GridSearchCV, RandomizedSearchCV, or Optuna |
| `soft_boiled_egg` | All about timing and calibration | Cross-validation — k-fold, stratified, time-series splits; surfaces learning curves |
| `chashu` | Slow-cooked, preserved perfectly | Model serialization and persistence — wraps joblib/pickle with versioning metadata |

#### Explainability (requires `ramentruck[explain]`)

| Module | Metaphor | Purpose |
|---|---|---|
| `nori` | Thin layer on top that adds insight | SHAP wrappers — SHAP values, feature importance, partial dependence plots |

#### Experiment Tracking (requires `ramentruck[tracking]`)

| Module | Metaphor | Purpose |
|---|---|---|
| `miso` | Fermented = accumulated wisdom over runs | MLflow or W&B wrapper — log params, metrics, artifacts |

#### Deep Learning (requires `ramentruck[deep]`)

| Module | Metaphor | Purpose |
|---|---|---|
| `tonkotsu` | Heavy, rich, long-cooked | Deep learning interface — wraps PyTorch or TensorFlow for common architectures; defaults to Keras functional API (not Sequential) |

#### To Be Named

- Feature engineering pipeline module
- Ensemble methods module
- Probability calibration module
- Prediction / inference API wrapper

### Implementation Notes

- `tonkotsu` should default to the Keras **functional API**, not Sequential
- `tare` and `broth` should expose regularization (L2, Dropout) and early stopping as first-class options
- A built-in `EveryNEpochs`-style Keras callback convenience class fits naturally in RamenTruck
- `soft_boiled_egg` should surface train/val/test learning curves natively
- Handle edge cases gracefully: small-N datasets, class imbalance, noisy labels

---

*Last updated: 2026-09-09*
