# Changelog

All notable changes to ThaiTruck are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- `massaman` — rolling mean/std/sum/min/max/median and `pct_change` columns
- `nam_pla` — schema validation (`dtype`/`nullable`/`min`/`max`/`isin`/`required`),
  returns a violations report; `strict=True` raises. Absorbs what would have
  been a separate `nam_prik` — one spec shape covers both use cases
- `som_tam` — DataFrame diffing (added/removed/modified rows); row identity
  via `key=` or the DataFrame index; schema drift surfaces via `.attrs`
- `boat_noodles` — sequential chunked CSV reading with an optional per-chunk
  transform
- `dish_bucket` — downcasts numeric columns to the smallest safe dtype;
  `.flush()` runs `gc.collect()`
- `thai_roti` — writes a DataFrame to Excel or HTML (`format="od_summary"`
  is not implemented — its output schema was never pinned down)
- `coconut_ice_cream` — clears the `sticky_rice` cache directory and/or runs
  `gc.collect()` (`reset_env=` from the original concept is not implemented —
  ThaiTruck holds no global state for it to reset)
- `TruckPipeline` — fluent chaining over `orange_chicken`, `fried_rice`,
  `satay`, `massaman`, `dish_bucket`
- `df.truck.*` pandas accessor covering every DataFrame-native function
- `ThaiTruckError` exception hierarchy (`DateColumnNotFound`,
  `InvalidHeatLevel`, `SkewTypeError`, `ValidationError`), each also a
  subclass of the built-in exception type it replaces
- `fried_rice`: `join=` (outer/inner/left), `suffix_template=`, automatic
  timezone-aware `DatetimeIndex` stripping
- `orange_chicken`: `rename=`, `dtypes=`
- `larb`: `include=`/`exclude=`
- `satay`: `(col, value, op)` comparison tuples, `satay.head()`/`satay.tail()`
- `sticky_rice`: `compress=`, `.stats()`
- `py.typed` marker (PEP 561)
- CI: GitHub Actions running pytest across Python 3.9–3.12 and pandas 1.5.x/2.x
- `benchmarks/` — pytest-benchmark coverage for `fried_rice` and `sticky_rice`
  (not part of the default `pytest` run; `pytest benchmarks/` to run them)

### Known gaps (deliberately deferred — need a design decision)

- `orange_chicken` change-log return value
- `larb` `plot=` option
- `sticky_rice` Redis backend
- `green_curry` (recipe-based transforms)
- `thai_feast` / `chicken_satay` (orchestration)
- `prik_nam_som` (drift alerting)

## [0.2.2] - 2026-06-10

### Fixed

- PyPI homepage URL pointed at the wrong GitHub repo

## [0.2.1] - 2026-06-10

### Added

- Initial release: `fried_rice`, `orange_chicken`, `larb`, `pad_thai`,
  `sticky_rice`, `satay`, `tom_kha`
