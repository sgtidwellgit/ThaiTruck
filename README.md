# ThaiTruck

<p align="center">
  <img src="assets/ThaiTruckLogo.png" alt="ThaiTruck Logo" width="400"/>
</p>

<p align="center">
  <a href="https://github.com/sgtidwellgit/ThaiTruck/actions/workflows/tests.yml">
    <img src="https://github.com/sgtidwellgit/ThaiTruck/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
</p>

**Spicy data blending and time-series DataFrame merging — Thai food truck style.**

You've got six DataFrames. Three different date column names. Two frequencies.  
One deadline.

*ThaiTruck.*

```python
pip install thaitruck
```

---

## The Problem

Every data engineer has stared at something like this:

```python
prices_df      # daily, column called "Date"
earnings_df    # quarterly, column called "report_date"
macro_df       # monthly, column called "ts"
sentiment_df   # irregular, index is already a DatetimeIndex
```

And thought: *I just want one DataFrame.*

That's what ThaiTruck is for.

---

## The Menu

### `fried_rice` — The Flagship

*Merge N DataFrames with mismatched timestamps into one coherent result.*

The workhorse. Handles date auto-detection, frequency normalization, forward-filling,
and conflict resolution. Accepts as many DataFrames as you can throw at it.

```python
from thaitruck import fried_rice

result = fried_rice(prices_df, earnings_df, macro_df, freq="D")
```

**Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `*dfs` | — | Two or more DataFrames |
| `freq` | `"D"` | Target frequency (`"D"`, `"W"`, `"ME"`, `"QE"`, …) |
| `heat` | `3` | Conflict resolution — see Heat Guide below |
| `join` | `"outer"` | Which rows survive: `"outer"` (union), `"inner"` (overlap only), `"left"` (first frame's timestamps) |
| `fuzzy_columns` | `False` | Normalize column names before merging |
| `fill_method` | `"ffill"` | `"ffill"`, `"bfill"`, or `"interpolate"` |
| `date_col` | `None` | Override auto-detection |
| `suffix_template` | `None` | Format string for heat=3 collision suffixes, e.g. `"_src{i}"` — defaults to `"_{i}"` |

```python
# Quarterly earnings merged into a daily price series
result = fried_rice(
    prices_df,        # daily, "Date" column
    earnings_df,      # quarterly, "report_date" column
    macro_df,         # monthly, "ts" column
    freq="D",
    heat=3,
    fuzzy_columns=True,
)
```

ThaiTruck auto-detects columns named `date`, `ts`, `timestamp`, `report_date`,
`trade_date`, `as_of_date`, and more. If your column has a truly cursed name,
pass `date_col="your_cursed_name"`.

Timezone-aware DatetimeIndex values are automatically stripped to naive
timestamps so they merge cleanly with everything else.

---

### `orange_chicken` — The Glaze

*Normalize and transform raw data into clean, uniform output.*

Raw data is ugly. `orange_chicken` fixes that. Column names lowercased,
separators unified, numeric strings coerced, boolean strings resolved,
sparse columns evicted.

```python
from thaitruck import orange_chicken

clean = orange_chicken(raw_df, heat=3)
```

**What each heat level glazes:**

| Heat | What gets cleaned |
|---|---|
| 1 | Column names only (`"Open Price"` → `"open_price"`) |
| 2 | + strip cell whitespace, drop all-null rows and columns |
| 3 | + coerce numeric strings to numbers *(default)* |
| 4 | + coerce boolean strings (`"yes"`/`"true"`/`"on"` → `True`), drop ≥90% null columns |
| 5 | + drop ≥50% null columns *(napalm)* |

```python
# Raw CSV fresh off the truck
raw = pd.DataFrame({
    "  Open Price  ": ["1,250.00", "1,300.00"],
    "Active?":        ["yes", "no"],
    "Notes":          [None, None],   # 100% null — getting dropped at heat=2
})

clean = orange_chicken(raw, heat=4)
# columns: open_price (float), active (bool)
```

Rename columns or lock in dtypes after cleaning, without a second pass:

```python
clean = orange_chicken(
    raw_df,
    heat=3,
    rename={"open_price": "price"},   # applied after cleaning
    dtypes={"price": "float32"},      # applied last, using the renamed columns
)
```

---

### `larb` — The Raw Bar

*Fast statistical profile of a DataFrame. No cooking required.*

`larb` gives you a one-row-per-column profile covering counts, nulls, descriptive
stats, and outlier detection via IQR fences. Heat controls how aggressively it
flags outliers.

```python
from thaitruck import larb

profile = larb(df, heat=3)
print(profile)
```

```
         dtype  count  null_pct     mean      std    min    p25  median    p75     max    skew  lower_fence  upper_fence  outliers  outlier_pct  ...
price    float64    365      0.0  142.30    38.21  88.00  112.0  140.00  168.0  310.00    0.72        56.0        224.0         3         0.82
volume   int64      365      0.0  1.02M   480K      10K  700K   980K    1.3M    8.5M      2.10      -350K        2.35M         2         0.55
```

**Outlier sensitivity by heat:**

| Heat | IQR Multiplier | What gets flagged |
|---|---|---|
| 1 | × 3.0 | Extreme outliers only |
| 2 | × 2.5 | |
| 3 | × 2.0 | Moderate outliers *(default)* |
| 4 | × 1.5 | Standard Tukey fences |
| 5 | × 1.0 | Very sensitive — expects tightly clustered data |

Non-numeric columns get `unique`, `top`, and `top_freq` instead of numeric stats.

Profile a subset of columns with `include`/`exclude`:

```python
larb(df, include=["price", "volume"])  # only these two
larb(df, exclude=["id"])               # everything except id
```

---

### `pad_thai` — The Noodles

*String padding, alignment, and formatting utilities.*

Works on a single string, a list, or a pandas Series. Handles left/right/center
alignment and optional truncation with a trailing ellipsis.

```python
from thaitruck import pad_thai

pad_thai("close", 10)                          # "close     "
pad_thai("close", 10, align="right")           # "     close"
pad_thai("close", 10, align="center")          # "  close   "
pad_thai("a very long label", 12, truncate=True)  # "a very long…"

# Works on a Series too
df["ticker"] = pad_thai(df["ticker"], width=6, align="right")
```

---

### `sticky_rice` — The Cache

*Persistent disk cache for expensive computations.*

Wrap any function. Results are pickled to `.thaitruck_cache/` and reused within
the TTL. When the cache is warm, the function never runs.

```python
from thaitruck import sticky_rice

@sticky_rice(ttl=3600)
def fetch_and_merge(ticker: str) -> pd.DataFrame:
    # ... expensive API calls, processing, merging ...
    return result

df = fetch_and_merge("NVDA")  # computed and cached
df = fetch_and_merge("NVDA")  # served from disk in milliseconds
```

Clear the cache manually when you need a fresh run:

```python
fetch_and_merge.clear()
```

**Options:**

```python
@sticky_rice(
    ttl=1800,                    # seconds before expiry (0 = never)
    key="my_fixed_key",          # fixed key instead of hash
    cache_dir=Path("/tmp/cache"),# custom cache directory
    compress=True,                # gzip cache files on disk
)
def my_fn(): ...
```

Check hit/miss counts and on-disk size:

```python
fetch_and_merge.stats()
# {"hits": 4, "misses": 1, "size_bytes": 20480}
```

---

### `satay` — The Skewer

*Expressive multi-dimensional DataFrame slicing.*

Pass any combination of column names, row slices, range filters, equality filters,
and callables. Skewers are applied in order — row filters first, column selectors last.

```python
from thaitruck import satay

# Column selection
satay(df, "price")
satay(df, ["price", "volume"])

# Row slice (positional)
satay(df, slice(0, 100))

# Range filter
satay(df, ("price", 10.0, 50.0))

# Comparison filter — (col, value, op), op in > < >= <= == !=
satay(df, ("price", 100, ">"))

# Equality / isin filter
satay(df, {"sector": "Tech"})
satay(df, {"sector": ["Tech", "Energy"]})

# Lambda
satay(df, lambda d: d["volume"] > 1_000_000)

# Mix and match — filters applied left to right
satay(df, {"sector": "Tech"}, ("price", 10, 200), "price", "volume")

# head/tail shorthand
satay.head(df, 10)
satay.tail(df, 10)
```

---

### `tom_kha` — The Broth

*Deep config merging with sensible coconut-milk defaults.*

Later dicts win. Nested dicts are merged recursively — not overwritten wholesale.
Lists are replaced. Pass `defaults=` for a base that everything else overrides.

```python
from thaitruck import tom_kha

config = tom_kha(
    base_config,
    env_config,
    cli_overrides,
    defaults={"retries": 3, "timeout": 30, "db": {"port": 5432}},
)
```

```python
tom_kha(
    {"db": {"host": "localhost", "port": 5432}},
    {"db": {"port": 5433}, "debug": True},
)
# → {"db": {"host": "localhost", "port": 5433}, "debug": True}
```

---

### `massaman` — The Slow-Cooked Curry

*Rolling-window aggregations and percentage change, slow-cooked into new columns.*

Adds rolling mean/std/sum/min/max/median columns for a window, plus row-over-row
percentage change. Named for the curry that takes time and rewards patience.

```python
from thaitruck import massaman

result = massaman(df, "price", window=20, ops=["mean", "std", "pct_change"])
# Adds columns: price_roll_mean_20, price_roll_std_20, price_pct_change
```

Rolling ops (`"mean"`, `"std"`, `"sum"`, `"min"`, `"max"`, `"median"`) are windowed
and suffixed with the window size. `"pct_change"` is not windowed — it's a straight
row-over-row percent change.

---

### `nam_pla` — The Dipping Sauce

*Schema validation — catch bad data before it hits the pan.*

Define what each column should look like; `nam_pla` returns a report of what
violates the spec. Nothing raises by default, so it's safe to run in a
pipeline as a checkpoint — pass `strict=True` when you want it to blow up.

```python
from thaitruck import nam_pla

spec = {
    "price":  {"dtype": float, "min": 0, "nullable": False},
    "sector": {"dtype": str, "nullable": False, "isin": ["Tech", "Energy", "Health"]},
}

report = nam_pla(df, spec)          # returns a violations DataFrame (empty if clean)
nam_pla(df, spec, strict=True)      # raises ValidationError if not clean
```

**Constraint keys:** `dtype`, `nullable`, `min`, `max`, `isin`, `required`
(set `required=False` on a column that's only checked when present).

---

### `som_tam` — The Diff

*DataFrame diffing, sour-and-tangy Thai salad style — what changed, laid bare.*

Compare a before/after pair of DataFrames and get back which rows were added,
removed, or modified. Row identity is your call: pass `key` for one or more
identifying columns, or leave it out to diff by index.

```python
from thaitruck import som_tam

diff = som_tam(before_df, after_df, key="id")
print(diff)
#      change_type columns_changed
# id
# 3        added             None
# 7      removed             None
# 2      modified           price
```

Only rows that actually changed appear — unchanged rows are omitted. Column
additions/removals (schema drift) aren't tied to any one row, so they land in
`diff.attrs["columns_added"]` / `diff.attrs["columns_removed"]` instead of the
table itself.

```python
diff.attrs["columns_added"]     # ["new_column"]
diff.attrs["columns_removed"]   # []
```

`NaN == NaN` counts as unchanged (not flagged as a diff), and both inputs are
validated to have a unique row identity — duplicate keys raise.

---

### `boat_noodles` — Sequential Chunked Processing

*Read a large CSV in bowls, not the whole pot at once.*

A thin wrapper over `pd.read_csv(..., chunksize=N)` that optionally applies a
transform — often another ThaiTruck function — to each chunk as it's yielded.

```python
from thaitruck import boat_noodles, orange_chicken

for chunk in boat_noodles("big_file.csv", chunksize=10_000, apply=orange_chicken):
    process(chunk)
```

Any extra keyword arguments pass straight through to `pd.read_csv` (`sep=`,
`encoding=`, etc.).

---

### `dish_bucket` — The Memory Optimizer

*Keeps the truck nimble when the DataFrame gets massive.*

Downcasts numeric columns to the smallest dtype that holds them safely —
never a blind `float64 → float32`, always checked per column.

```python
from thaitruck import dish_bucket

df = dish_bucket(df)                # returns a downcast copy
dish_bucket(df, report=True)        # also prints before/after memory usage
dish_bucket.flush()                 # gc.collect()
```

Available via `df.truck.dish_bucket()` and in a `TruckPipeline` chain.

---

### `thai_roti` — Finalized Output Formatter

*The last step before the truck hands the meal to the customer.*

Writes a finished DataFrame to Excel or HTML and returns the `Path` it wrote to.

```python
from thaitruck import thai_roti

thai_roti(df, format="excel", path="output/report.xlsx")   # requires: pip install thaitruck[excel]
thai_roti(df, format="html",  path="output/dashboard.html")
```

`format="od_summary"` from the original concept isn't implemented — its
output schema was never pinned down, so it raises `NotImplementedError`
rather than guessing.

---

### `coconut_ice_cream` — Post-Pipeline Cleanup

*The palate cleanser.*

```python
from thaitruck import coconut_ice_cream

coconut_ice_cream(clear_cache=True, flush_temp=True)
```

`clear_cache` deletes everything under the `sticky_rice` cache directory
(default `.thaitruck_cache/`, or pass `cache_dir=` to match a custom one).
`flush_temp` runs `gc.collect()`. The original concept's `reset_env=` isn't
implemented — ThaiTruck holds no global environment state for it to reset.

---

## The Heat Guide

Most ThaiTruck functions accept a `heat` parameter (1–5). The metaphor is
consistent: higher heat is more aggressive.

| Heat | Vibe |
|---|---|
| 1 | Mild. Barely noticeable. Tourist-safe. |
| 2 | A little warmth. |
| 3 | Medium. The default. Regular customer. |
| 4 | Getting spicy. Know what you're doing. |
| 5 | Napalm. No survivors. |

---

## Installation

```bash
pip install thaitruck
```

Requires Python ≥ 3.9 and pandas ≥ 1.5. `thai_roti`'s Excel format needs the
optional `openpyxl` dependency: `pip install thaitruck[excel]`.

---

## Ergonomics

Every DataFrame function is also available as a pandas accessor, and can be
chained through `TruckPipeline` without intermediate variables.

```python
import thaitruck  # registers the `.truck` accessor as a side effect

df.truck.orange_chicken(heat=3)
df.truck.larb()
df.truck.satay({"sector": "Tech"})
```

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

`orange_chicken`, `larb`, `satay`, `fried_rice`, `massaman`, `nam_pla`,
`som_tam`, `dish_bucket`, and `thai_roti` are all callable either way — the
accessor and pipeline are thin wrappers, not a new implementation. `larb`,
`nam_pla`, `som_tam`, and `thai_roti` are accessor-only, not chainable through
`TruckPipeline` — they return a report (or write a file) rather than a
transformed version of the input.

---

## Custom Exceptions

Every raise that used to be a bare `ValueError`/`TypeError` for a package-specific
condition is now also a `ThaiTruckError`, so you can catch broadly or narrowly:

```python
from thaitruck import (
    ThaiTruckError,
    DateColumnNotFound,
    InvalidHeatLevel,
    SkewTypeError,
    ValidationError,
)

try:
    fried_rice(df_without_a_date_column)
except DateColumnNotFound:
    ...

# Or catch anything ThaiTruck-specific:
try:
    orange_chicken(df, heat=9)
except ThaiTruckError:
    ...
```

Each is still a subclass of the exception type it replaces (`DateColumnNotFound`,
`InvalidHeatLevel`, and `ValidationError` are `ValueError`s, `SkewTypeError` is
a `TypeError`), so existing `except ValueError` / `except TypeError` code keeps
working unchanged.

---

## The Full Menu

```python
from thaitruck import fried_rice     # time-series DataFrame merger
from thaitruck import orange_chicken # data normalization and cleaning
from thaitruck import larb           # fast statistical profiling
from thaitruck import pad_thai       # string padding and alignment
from thaitruck import sticky_rice    # persistent disk caching
from thaitruck import satay          # expressive DataFrame slicing
from thaitruck import tom_kha        # deep config dict merging
from thaitruck import massaman       # rolling aggregations and percentage change
from thaitruck import nam_pla        # schema validation
from thaitruck import som_tam        # DataFrame diffing
from thaitruck import boat_noodles   # sequential chunked CSV processing
from thaitruck import dish_bucket    # numeric downcasting for memory
from thaitruck import thai_roti      # Excel / HTML output
from thaitruck import coconut_ice_cream  # cache clearing and gc.collect()
from thaitruck import TruckPipeline  # fluent chained pipeline
```

---

## Why the name?

Mrs. Babble Baz looked over at the screen one day and said *"why do you people
make up such ridiculous names for things?"*

She had a point. `pandas` is a ridiculous name for a data library. `pickle` is
a serialization format. `fuzzywuzzy` is a string matcher. These are load-bearing
tools in production systems at serious companies, and they sound like rejected
Muppet characters.

So we leaned in. If the name is going to be unhinged, it should at least be
**sizzling hot.**

ThaiTruck is genuinely useful. The food truck is just the vibe — and Mrs. Babble
Baz is why it exists.

---

## License

MIT
