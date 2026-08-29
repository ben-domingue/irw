"""Single resolution point for the write-scoped Redivis API token.

Every script that *uploads* to Redivis needs a token with `data.edit` scope on
`datapages`. That is deliberately a different token from `~/.redivis_api_token`,
which is read-only and is what the site/analysis code uses.

Historically each uploader called a bare `load_dotenv()`, which only finds a
`.env` in the caller's own directory -- so the same write token got copied into
four `.env` files inside the Dropbox-synced project tree. Those copies were
deleted on 2026-08-29 and the token they held was revoked; this module replaces
them with one resolved path outside Dropbox.

Resolution order:

  1. `REDIVIS_API_TOKEN` already exported in the environment (CI, one-off runs).
  2. The path in `IRW_REDIVIS_WRITE_ENV`, if set.
  3. `~/.config/irw/redivis-write.env`  <-- the normal case.

There is deliberately no fallback to a `.env` beside the calling script: that
is the pattern that produced the duplicates, and a stray `.env` silently
working again is exactly the failure this module exists to prevent.

Note that `~/.config/irw/` is intentionally *not* in Dropbox, so it does not
sync: each machine needs its own copy of the token file.
"""

from __future__ import annotations

import os
from pathlib import Path

VAR = "REDIVIS_API_TOKEN"
DEFAULT_PATH = Path.home() / ".config" / "irw" / "redivis-write.env"


def _read_env_file(path: Path) -> str | None:
    """Pull VAR out of a .env file. Accepts an optional `export ` prefix."""
    try:
        text = path.read_text()
    except OSError:
        return None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        if sep and key.strip() == VAR:
            return value.strip().strip("'\"") or None
    return None


def load_write_token(caller: str | None = None) -> str:
    """Return the write-scoped token, and export it so `redivis` can see it.

    `caller` is accepted and ignored; it remains in the signature so the call
    sites reading `__file__` do not all need editing.
    """
    token = os.environ.get(VAR)
    if token:
        return token

    override = os.environ.get("IRW_REDIVIS_WRITE_ENV")
    path = Path(override).expanduser() if override else DEFAULT_PATH

    token = _read_env_file(path)
    if token:
        os.environ[VAR] = token
        return token

    raise SystemExit(
        f"No {VAR} found.\n"
        f"  Looked in: the environment, then {path}.\n"
        f"This must be a *write-scoped* (data.edit on datapages) token -- not the\n"
        f"read-only one in ~/.redivis_api_token. Create the file with:\n"
        f"  install -d -m 700 ~/.config/irw\n"
        f"  printf 'export {VAR}=<token>\\n' > {DEFAULT_PATH}\n"
        f"  chmod 600 {DEFAULT_PATH}\n"
        f"(~/.config is not synced, so each machine needs its own copy.)"
    )
