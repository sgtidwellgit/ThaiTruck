# ThaiTruck

<p align="center">
  <img src="assets/ThaiTruckLogo.png" alt="ThaiTruck Logo" width="400"/>
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
| `fuzzy_columns` | `False` | Normalize column names before merging |
| `fill_method` | `"ffill"` | `"ffill"`, `"bfill"`, or `"interpolate"` |
| `date_col` | `None` | Override auto-detection |

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
    cache_dir=Path("/tmp/cache") # custom cache directory
)
def my_fn(): ...
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

# Equality / isin filter
satay(df, {"sector": "Tech"})
satay(df, {"sector": ["Tech", "Energy"]})

# Lambda
satay(df, lambda d: d["volume"] > 1_000_000)

# Mix and match — filters applied left to right
satay(df, {"sector": "Tech"}, ("price", 10, 200), "price", "volume")
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

Requires Python ≥ 3.9 and pandas ≥ 1.5.

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

`orange_chicken`, `larb`, `satay`, `fried_rice`, and `massaman` are all callable
either way — the accessor and pipeline are thin wrappers, not a new implementation.

---

## Custom Exceptions

Every raise that used to be a bare `ValueError`/`TypeError` for a package-specific
condition is now also a `ThaiTruckError`, so you can catch broadly or narrowly:

```python
from thaitruck import ThaiTruckError, DateColumnNotFound, InvalidHeatLevel, SkewTypeError

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

Each is still a subclass of the exception type it replaces (`DateColumnNotFound`
and `InvalidHeatLevel` are `ValueError`s, `SkewTypeError` is a `TypeError`), so
existing `except ValueError` / `except TypeError` code keeps working unchanged.

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
