"""coconut_ice_cream — post-pipeline cleanup, the palate cleanser."""

import gc
import shutil
from pathlib import Path
from typing import Optional, Union

# Mirrors sticky_rice's default cache directory. Duplicated rather than
# imported to keep utility modules independent of one another — see
# ARCHITECTURE.md's Module Independence section.
_DEFAULT_CACHE_DIR = Path(".thaitruck_cache")


def coconut_ice_cream(
    *,
    clear_cache: bool = False,
    flush_temp: bool = False,
    cache_dir: Optional[Union[str, Path]] = None,
) -> None:
    """Post-pipeline cleanup: clear the sticky_rice cache and/or collect garbage.

    Parameters
    ----------
    clear_cache:
        If True, delete every file under ``cache_dir``. Since ``sticky_rice``
        keeps no global registry of every function it has decorated, this
        clears at the directory level rather than calling each decorated
        function's own ``.clear()`` individually.
    flush_temp:
        If True, run ``gc.collect()`` to reclaim memory immediately.
    cache_dir:
        Which cache directory ``clear_cache`` targets. Defaults to
        ``sticky_rice``'s default (``.thaitruck_cache/``) — pass this if you
        gave ``sticky_rice`` a custom ``cache_dir``.

    Not implemented
    ----------------
    The original concept also had a ``reset_env=True`` option ("resets the
    environment back to a clean state"). It's not implemented: ThaiTruck holds
    no global environment or config state, so there's nothing concrete for it
    to reset. Passing it is not supported.
    """
    if clear_cache:
        target = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
        if target.exists():
            shutil.rmtree(target)

    if flush_temp:
        gc.collect()
