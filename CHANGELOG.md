# Changelog

All notable changes to ThaiTruck are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [0.3.0] - 2026-09-09

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

### Fixed

- `tom_kha` used `dict[str, Any] | None` (PEP 604 union syntax), which
  requires Python ≥3.10 to evaluate — broke every `import thaitruck` on
  Python 3.9. Pre-existing bug; nothing caught it until CI was added.
- `test_sticky_rice.py`'s `mock.patch` on a dotted path hit a real CPython
  bug (fixed upstream in 3.11) that surfaces whenever a package re-exports a
  submodule's function under the submodule's own name, as `__init__.py`
  does throughout this package
- A test used `freq="QE"`, a pandas ≥2.2-only alias; switched to `"Q"`,
  which works identically on pandas 1.5 and 2.x
- CI installed a version-unconstrained `pandas` and then force-downgraded it
  in a second step, which could leave an ABI-incompatible `numpy` in place
  for the `pandas==1.5.*` matrix leg; now pinned to `numpy<2` for that leg
  and installed together with the package in one resolved step
- The sdist was pulling in an untracked local `.claude/settings.local.json`
  (a known recurrence — the same class of leak already fixed in RamenTruck)
  plus `.github/` and the README's image `assets/`, bloating it to 2.4MB for
  no reason; excluded all three via `[tool.hatch.build] exclude`, down to 61KB

### Changed

- Added a proper `LICENSE` file (previously only declared in
  `pyproject.toml`, not shipped as a file) and PyPI classifiers

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
