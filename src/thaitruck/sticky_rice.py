"""sticky_rice — persistent caching layer for expensive computations."""

import functools
import gzip
import hashlib
import os
import pickle
import time
from pathlib import Path
from typing import Any, Callable, Optional

_DEFAULT_CACHE_DIR = Path(".thaitruck_cache")


def _make_key(fn: Callable, args: tuple, kwargs: dict, key: Optional[str]) -> str:
    if key:
        return key
    raw = f"{fn.__module__}.{fn.__qualname__}:{repr(args)}:{repr(sorted(kwargs.items()))}"
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_path(cache_dir: Path, cache_key: str) -> Path:
    return cache_dir / f"{cache_key}.pkl"


def _read_cache(path: Path, ttl: int, compress: bool) -> tuple[bool, Any]:
    if not path.exists():
        return False, None
    try:
        opener = gzip.open if compress else open
        with opener(path, "rb") as f:
            stored = pickle.load(f)
        if ttl > 0 and time.time() - stored["ts"] > ttl:
            return False, None
        return True, stored["value"]
    except Exception:
        return False, None


def _write_cache(path: Path, value: Any, compress: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if compress else open
    with opener(path, "wb") as f:
        pickle.dump({"ts": time.time(), "value": value}, f)


def sticky_rice(
    fn: Optional[Callable] = None,
    *,
    key: Optional[str] = None,
    ttl: int = 3600,
    cache_dir: Optional[Path] = None,
    compress: bool = False,
) -> Callable:
    """Cache the result of a callable to disk, reusing it within the TTL.

    Can be used as a plain decorator or a decorator factory:

        @sticky_rice
        def my_fn(x): ...

        @sticky_rice(ttl=600, cache_dir=Path("/tmp/cache"))
        def my_fn(x): ...

    Parameters
    ----------
    fn:
        The function to wrap (set automatically when used as a bare decorator).
    key:
        Fixed cache key. Defaults to a hash of the function name + arguments.
    ttl:
        Seconds before a cached result is considered stale. 0 = never expires.
    cache_dir:
        Directory for cache files. Defaults to .thaitruck_cache in the cwd.
    compress:
        Gzip cache files on write (and expect gzip on read). Trades CPU for
        disk space on large cached results.
    """
    resolved_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR

    def decorator(f: Callable) -> Callable:
        counts = {"hits": 0, "misses": 0}

        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = _make_key(f, args, kwargs, key)
            path = _cache_path(resolved_dir, cache_key)
            hit, value = _read_cache(path, ttl, compress)
            if hit:
                counts["hits"] += 1
                return value
            counts["misses"] += 1
            result = f(*args, **kwargs)
            _write_cache(path, result, compress)
            return result

        def clear() -> None:
            """Delete all cache entries for this function."""
            prefix = key or f"{f.__module__}.{f.__qualname__}"
            for p in resolved_dir.glob("*.pkl"):
                try:
                    with p.open("rb") as fh:
                        stored = pickle.load(fh)
                    _ = stored  # valid file
                except Exception:
                    pass
            # Simpler: clear by matching key if fixed, else clear all for fn
            if key:
                _cache_path(resolved_dir, key).unlink(missing_ok=True)
            else:
                for p in resolved_dir.glob("*.pkl"):
                    p.unlink(missing_ok=True)
            counts["hits"] = 0
            counts["misses"] = 0

        def stats() -> dict:
            """Return this wrapper's hit/miss counts and on-disk cache size.

            When ``key`` is a fixed string, ``size_bytes`` is that one file's
            size. Otherwise cache keys are content hashes with no recoverable
            link back to this function, so ``size_bytes`` reflects the whole
            cache_dir — the same scope ``.clear()`` uses in that case.
            """
            if key:
                paths = [_cache_path(resolved_dir, key)]
            else:
                paths = list(resolved_dir.glob("*.pkl"))
            size_bytes = sum(p.stat().st_size for p in paths if p.exists())
            return {"hits": counts["hits"], "misses": counts["misses"], "size_bytes": size_bytes}

        wrapper.clear = clear
        wrapper.stats = stats
        wrapper.cache_dir = resolved_dir
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator
