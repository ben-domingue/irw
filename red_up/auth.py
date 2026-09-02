"""Redivis authentication for red_up.

There is exactly one place the write-scoped token is resolved in this project
(src/irw_secrets.py, `load_write_token`): an exported REDIVIS_API_TOKEN wins,
else IRW_REDIVIS_WRITE_ENV, else ~/.config/irw/redivis-write.env. red_up
reuses it rather than adding a fourteenth way to find a credential -- the
copies are what the consolidation on 2026-08-29 existed to remove.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

from .targets import find_config


def src_root() -> Path:
    """The `src` checkout red_up was installed from."""
    return find_config().parent.parent


def authenticate() -> None:
    root = src_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from irw_secrets import load_write_token
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            f"Could not import irw_secrets from {root}: {exc}"
        ) from exc
    load_write_token()

    import redivis

    # redivis warns once per call that a bare dataset name may break if the
    # name changes. That is the right advice in general and the wrong advice
    # here: redivis_config.R is authoritative for *names* and deliberately
    # carries no version hashes (ARCHITECTURE.md section 5), so red_up looks
    # datasets up by name on purpose. Six identical warnings per run would
    # bury the plan.
    warnings.filterwarnings(
        "ignore", message="No reference id was provided.*", category=UserWarning)
    redivis.authenticate()
