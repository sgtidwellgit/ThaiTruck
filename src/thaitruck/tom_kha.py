"""tom_kha — deep config merging with sensible coconut-milk defaults."""

from typing import Any


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def tom_kha(*configs: dict[str, Any], defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deep-merge N config dicts, applying defaults for any missing keys.

    Later dicts take precedence. Nested dicts are merged recursively rather
    than overwritten wholesale. Lists and scalar values are always overwritten
    by the later config.

    Parameters
    ----------
    *configs:
        Config dicts in ascending precedence order (last one wins).
    defaults:
        Base defaults applied before all configs (lowest precedence).

    Examples
    --------
    >>> tom_kha({"db": {"host": "localhost"}}, {"db": {"port": 5432}})
    {'db': {'host': 'localhost', 'port': 5432}}

    >>> tom_kha({"retries": 3}, {"retries": 5, "timeout": 30})
    {'retries': 5, 'timeout': 30}
    """
    result: dict[str, Any] = {}

    if defaults:
        result = _deep_merge(result, defaults)

    for config in configs:
        if not isinstance(config, dict):
            raise TypeError(f"All configs must be dicts, got {type(config).__name__}")
        result = _deep_merge(result, config)

    return result
