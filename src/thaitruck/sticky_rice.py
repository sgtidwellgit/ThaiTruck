"""sticky_rice — persistent caching layer for expensive computations."""

import functools
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


def _read_cache(path: Path, ttl: int) -> tuple[bool, Any]:
    if not path.exists():
        return False, None
    try:
        with path.open("rb") as f:
            stored = pickle.load(f)
        if ttl > 0 and time.time() - stored["ts"] > ttl:
            return False, None
        return True, stored["value"]
    except Exception:
        return False, None


def _write_cache(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump({"ts": time.time(), "value": value}, f)


def sticky_rice(
    fn: Optional[Callable] = None,
    *,
    key: Optional[str] = None,
    ttl: int = 3600,
    cache_dir: Optional[Path] = None,
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
    """
    resolved_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            cache_key = _make_key(f, args, kwargs, key)
            path = _cache_path(resolved_dir, cache_key)
            hit, value = _read_cache(path, ttl)
            if hit:
                return value
            result = f(*args, **kwargs)
            _write_cache(path, result)
            return result

        def clear():
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

        wrapper.clear = clear
        wrapper.cache_dir = resolved_dir
        return wrapper

    if fn is not None:
        return decorator(fn)
    return decorator
