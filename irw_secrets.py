"""Single resolution point for the write-scoped Redivis API token.

Every script that *uploads* to Redivis needs a token with `data.edit` scope on
`datapages`. That is deliberately a different token from `~/.redivis_api_token`,
which is read-only and is what the site/analysis code uses.

Historically each uploader called a bare `load_dotenv()`, which only finds a
`.env` in the caller's own directory -- so the same write token got copied into
four `.env` files inside the Dropbox-synced project tree. This module replaces
that with one resolved path outside Dropbox.

Resolution order:

  1. `REDIVIS_API_TOKEN` already exported in the environment (CI, one-off runs).
  2. The path in `IRW_REDIVIS_WRITE_ENV`, if set.
  3. `~/.config/irw/redivis-write.env`  <-- the normal case.
  4. A `.env` next to the calling script -- DEPRECATED, warns on use.

Step 4 exists only so this change is non-breaking on machines that still have
the old in-tree copies. It goes away once those are deleted.

Note that `~/.config/irw/` is intentionally *not* in Dropbox, so it does not
sync: each machine needs its own copy of the token file.
"""

from __future__ import annotations

import os
import sys
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

    `caller` should be the calling script's `__file__`; it is used only to find
    the deprecated adjacent `.env`.
    """
    token = os.environ.get(VAR)
    if token:
        return token

    override = os.environ.get("IRW_REDIVIS_WRITE_ENV")
    candidates = [Path(override).expanduser()] if override else [DEFAULT_PATH]

    legacy = Path(caller).resolve().parent / ".env" if caller else None
    if legacy is not None:
        candidates.append(legacy)

    for path in candidates:
        token = _read_env_file(path)
        if not token:
            continue
        if path == legacy:
            print(
                f"WARNING: read {VAR} from {path}.\n"
                f"         That in-tree copy is deprecated and syncs to Dropbox. "
                f"Move it to {DEFAULT_PATH} (chmod 600) and delete this one.",
                file=sys.stderr,
            )
        os.environ[VAR] = token
        return token

    raise SystemExit(
        f"No {VAR} found.\n"
        f"  Looked in: the environment, then {DEFAULT_PATH}"
        + (f", then {legacy}" if legacy else "")
        + ".\n"
        f"This must be a *write-scoped* (data.edit on datapages) token -- not the\n"
        f"read-only one in ~/.redivis_api_token. Create the file with:\n"
        f"  install -d -m 700 ~/.config/irw\n"
        f"  printf 'export {VAR}=<token>\\n' > {DEFAULT_PATH}\n"
        f"  chmod 600 {DEFAULT_PATH}\n"
        f"(~/.config is not synced, so each machine needs its own copy.)"
    )
