"""Reserved sources: datasets the IRW must not find, triage, stage or name.

Some sources are held back for a while (for example, as unseen test data) and
must not be written anywhere public in the meantime: no human_review row, seen
ledger, backlog row, dictionary row, data script, log line or PR body. The list
can't be public either, so `reserved.txt` holds a keyed hash of each source's
identifiers, never the identifiers themselves.

    is_reserved(doi=..., url=...)   one candidate
    text_is_reserved(text)          any identifier anywhere in a blob of text
    drop_reserved(rows)             filter dict rows (CSV rows, Hits as dicts)

How it fails
------------
* If reserved.txt lists anything and no key is available, every check raises
  ReservedKeyMissing. The run stops; it does not go ahead unguarded.
* If the key doesn't match the key-check line in reserved.txt, it raises too, so
  a wrong key can't quietly match nothing.
* A reserved candidate is dropped SILENTLY: no print, no log line, no seen-ledger
  entry. It is re-found and re-dropped on every run, which is intended. The only
  record is a count in a local, uncommitted file (DROP_LOG) so someone can see
  the guard is doing something.

The key comes from $IRW_RESERVED_KEY, else the file named by
$IRW_RESERVED_KEY_FILE, else ~/.config/irw/reserved_key. In CI it's the
IRW_RESERVED_KEY repository secret.

Identifiers
-----------
Each source is listed under every form it might show up in: the DOI (raw and
version-collapsed), Zenodo record number, OSF node id, figshare article id, and
a normalized landing-page URL. Matching extracts the same forms from whatever it
is given and checks each one.

CLI
---
    python reserved.py check-diff [BASE]     scan `git diff BASE...HEAD` (added lines)
    python reserved.py check-files PATH...   scan whole files
    python reserved.py check-stdin           scan stdin (e.g. a PR body)
    python reserved.py hash-ids              stdin: one identifier per line ->
                                             stdout: hashed reserved.txt lines
    python reserved.py selftest              key present and matches the list

Checks exit 1 with a generic message on a match. They never print what matched,
because CI logs on a public repo are public.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# IRW_RESERVED_LIST points at a different list. The tests workflow sets it to an
# empty file: those tests exercise other code and get no key. Anything that
# finds, triages or stages candidates must run against the real list.
RESERVED_PATH = Path(os.environ.get("IRW_RESERVED_LIST") or HERE / "reserved.txt")
KEY_CHECK_LABEL = "irw-reserved-key-check"
DEFAULT_KEY_FILE = Path.home() / ".config" / "irw" / "reserved_key"
DROP_LOG = Path(os.environ.get("IRW_RESERVED_DROP_LOG",
                               Path.home() / ".cache" / "irw" / "reserved_drops.log"))


class ReservedKeyMissing(RuntimeError):
    pass


# --------------------------------------------------------------------------
# normalization (shared with irw_discover_updated, which imports these)
# --------------------------------------------------------------------------

# Repository version suffixes: every version of one deposit maps to a single
# key. Scoped to these prefixes on purpose: most DOIs legitimately end in
# `.digits` (`10.1371/journal.pone.0235154`), so a blanket rule would corrupt them.
_VERSIONED_DOI_RULES = (
    (re.compile(r"^10\.17632/[^/]+?(\.\d+)$"),               1),  # Mendeley Data
    (re.compile(r"^10\.6084/m9\.figshare\.[^/]+?(\.v\d+)$"), 1),  # figshare
    (re.compile(r"^10\.5061/dryad\.[^/]+?(\.\d+)$"),         1),  # Dryad
)


def norm_doi(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s


def canonical_doi(doi: str) -> str:
    """Strip a repository version suffix so every version of one deposit maps
    to a single dedup key. Returns the DOI unchanged when no rule applies."""
    d = (doi or "").strip().lower()
    for rx, grp in _VERSIONED_DOI_RULES:
        m = rx.match(d)
        if m:
            return d[: m.start(grp)]
    return d


_DOI_RX = re.compile(r"10\.\d{4,9}/[^\s\"'<>,;|\]\[(){}&#]+", re.I)
_OSF_RX = re.compile(r"osf\.io/([a-z0-9]{5})(?![a-z0-9])", re.I)
_ZENODO_RX = re.compile(r"zenodo\.org/(?:records?|deposit|doi/10\.5281/zenodo\.)/?(\d+)", re.I)
_ZENODO_DOI_RX = re.compile(r"^10\.5281/zenodo\.(\d+)$")
_FIGSHARE_RX = re.compile(r"figshare\.com/articles/(?:[^/\s]+/)*?(\d{6,})", re.I)
_FIGSHARE_DOI_RX = re.compile(r"^10\.6084/m9\.figshare\.(\d+)")
_URL_RX = re.compile(r"https?://[^\s\"'<>,;|\]\[(){}]+", re.I)


def _norm_url(u: str) -> str:
    u = u.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"#.*$", "", u)   # keep the query: Dataverse ids live there
    return u.rstrip("/.")


def identifiers(text: str) -> set[str]:
    """Every identifier form found in `text`, as typed keys ("doi:...",
    "osf:...", "zenodo:...", "figshare:...", "url:...")."""
    if not text:
        return set()
    out: set[str] = set()
    for m in _DOI_RX.finditer(text):
        d = norm_doi(m.group(0)).rstrip(".")
        for form in {d, canonical_doi(d)}:
            out.add("doi:" + form)
            z = _ZENODO_DOI_RX.match(form)
            if z:
                out.add("zenodo:" + z.group(1))
            f = _FIGSHARE_DOI_RX.match(form)
            if f:
                out.add("figshare:" + f.group(1))
            if form.startswith("10.17605/osf.io/"):
                out.add("osf:" + form.rsplit("/", 1)[1][:5])
    for m in _OSF_RX.finditer(text):
        out.add("osf:" + m.group(1).lower())
    for m in _ZENODO_RX.finditer(text):
        out.add("zenodo:" + m.group(1))
    for m in _FIGSHARE_RX.finditer(text):
        out.add("figshare:" + m.group(1))
    for m in _URL_RX.finditer(text):
        out.add("url:" + _norm_url(m.group(0)))
    return out


# --------------------------------------------------------------------------
# key + list
# --------------------------------------------------------------------------

def _load_key() -> bytes | None:
    k = os.environ.get("IRW_RESERVED_KEY", "").strip()
    if k:
        return k.encode()
    p = os.environ.get("IRW_RESERVED_KEY_FILE")
    for path in ([Path(p)] if p else []) + [DEFAULT_KEY_FILE]:
        try:
            k = path.read_text().strip()
        except OSError:
            continue
        if k:
            return k.encode()
    return None


def _hash(key: bytes, ident: str) -> str:
    return hmac.new(key, ident.encode(), hashlib.sha256).hexdigest()


_state: dict = {}


def _load() -> tuple[bytes | None, frozenset]:
    """(key, hashes). Raises ReservedKeyMissing if the list is non-empty and the
    key is absent or wrong."""
    if "hashes" in _state:
        return _state["key"], _state["hashes"]
    hashes, check = set(), None
    if RESERVED_PATH.exists():
        for line in RESERVED_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("# key-check:"):
                check = line.split(":", 1)[1].strip()
            elif line and not line.startswith("#"):
                hashes.add(line.lower())
    key = _load_key()
    if hashes:
        if key is None:
            raise ReservedKeyMissing(
                "automated_finding/reserved.txt is non-empty but no key was found "
                "(IRW_RESERVED_KEY, IRW_RESERVED_KEY_FILE, or "
                "~/.config/irw/reserved_key). Refusing to run unguarded; ask Ben "
                "for the key.")
        if check and not hmac.compare_digest(_hash(key, KEY_CHECK_LABEL), check):
            raise ReservedKeyMissing(
                "The reserved-list key doesn't match reserved.txt's key-check "
                "line. Refusing to run with a wrong key.")
    _state.update(key=key, hashes=frozenset(hashes))
    return key, _state["hashes"]


def _reset_cache() -> None:   # tests
    _state.clear()


def _note_drop(n: int = 1) -> None:
    try:
        DROP_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(DROP_LOG, "a") as f:
            import datetime
            f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t"
                    f"{Path(sys.argv[0]).name}\t{n}\n")
    except OSError:
        pass


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def _any_reserved(ids: set[str]) -> bool:
    key, hashes = _load()
    if not hashes:
        return False
    return any(_hash(key, i) in hashes for i in ids)


def text_is_reserved(text: str) -> bool:
    return _any_reserved(identifiers(text))


def is_reserved(doi: str = "", url: str = "", *more: str) -> bool:
    """True if any given identifier belongs to a reserved source. A bare DOI
    is accepted without its doi.org prefix."""
    parts = [f"https://doi.org/{norm_doi(doi)}" if doi else "", url or "", *more]
    hit = text_is_reserved(" ".join(p for p in parts if p))
    if hit:
        _note_drop()
    return hit


def hit_is_reserved(hit) -> bool:
    """A discovery Hit (anything with .doi / .url)."""
    return is_reserved(getattr(hit, "doi", "") or "", getattr(hit, "url", "") or "")


def row_is_reserved(row: dict) -> bool:
    return text_is_reserved(" ".join(str(v) for v in row.values() if v))


def drop_reserved(rows):
    """Rows (dicts) minus any that mention a reserved source in any field.
    Silent apart from the local drop count."""
    rows = list(rows)
    _, hashes = _load()
    if not hashes:
        return rows
    kept = [r for r in rows if not row_is_reserved(r)]
    if len(kept) != len(rows):
        _note_drop(len(rows) - len(kept))
    return kept


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

_FOUND = ("A reserved source is named in this change. Not printing which (this log "
          "may be public). Ask Ben; run `python automated_finding/reserved.py "
          "check-diff` locally with the key to find it.")


def _check_text_or_exit(text: str, where: str = "") -> int:
    try:
        bad = text_is_reserved(text)
    except ReservedKeyMissing as e:
        print(f"reserved-guard: {e}", file=sys.stderr)
        return 2
    if bad:
        print(f"reserved-guard: {_FOUND}{' ' + where if where else ''}", file=sys.stderr)
        return 1
    return 0


def _local_report(lines: list[tuple[str, str]]) -> None:
    """With --show, name the file and line that matched (local use only)."""
    for where, line in lines:
        if text_is_reserved(line):
            print(f"  {where}", file=sys.stderr)


def main(argv=None) -> int:
    import argparse
    import subprocess
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("check-diff")
    d.add_argument("base", nargs="?", default="origin/main")
    d.add_argument("--show", action="store_true",
                   help="name the matching file:line (LOCAL use only, never in CI)")
    f = sub.add_parser("check-files")
    f.add_argument("paths", nargs="+")
    f.add_argument("--show", action="store_true")
    sub.add_parser("check-stdin")
    sub.add_parser("hash-ids")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)

    if a.cmd == "check-diff":
        diff = subprocess.run(["git", "diff", "--unified=0", "--no-color",
                               f"{a.base}...HEAD"], capture_output=True, text=True,
                              check=True).stdout
        added, cur = [], ""
        for line in diff.splitlines():
            if line.startswith("+++ "):
                cur = line[6:] if line.startswith("+++ b/") else line[4:]
            elif line.startswith("+") and not line.startswith("+++"):
                added.append((cur, line[1:]))
        # file names count too: a data script named after a source
        text = "\n".join(l for _, l in added) + "\n" + "\n".join({w for w, _ in added})
        rc = _check_text_or_exit(text)
        if rc == 1 and a.show:
            _local_report(added)
        return rc
    if a.cmd == "check-files":
        lines = []
        for p in a.paths:
            try:
                for i, l in enumerate(Path(p).read_text(errors="replace").splitlines(), 1):
                    lines.append((f"{p}:{i}", l))
            except OSError:
                continue
        rc = _check_text_or_exit("\n".join(l for _, l in lines))
        if rc == 1 and a.show:
            _local_report(lines)
        return rc
    if a.cmd == "check-stdin":
        return _check_text_or_exit(sys.stdin.read())
    if a.cmd == "hash-ids":
        key = _load_key()
        if key is None:
            print("reserved-guard: no key", file=sys.stderr)
            return 2
        out = set()
        for line in sys.stdin:
            out |= {_hash(key, i) for i in identifiers(line)}
        print(f"# key-check: {_hash(key, KEY_CHECK_LABEL)}")
        for h in sorted(out):
            print(h)
        return 0
    if a.cmd == "selftest":
        try:
            _, hashes = _load()
        except ReservedKeyMissing as e:
            print(f"reserved-guard: {e}", file=sys.stderr)
            return 2
        print(f"reserved-guard: ok ({'key matches' if hashes else 'list empty'})")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
