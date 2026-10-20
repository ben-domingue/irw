#!/usr/bin/env python3
"""Can the RELEASED clients see the whole corpus? (ben-domingue/irw#3091, item 8)

`check_config_parity.py` compares the three config files with each other. All
three can agree and all three be behind the warehouse -- which is what happened
in October 2026. The seventh core warehouse released on 2026-10-15 with 761
tables; CRAN accepted `irw` 1.3.1 on 10-18 from a tag cut on 10-07 that knew
about six. Every CRAN install was therefore short by about 12% of the released
core corpus, and short *silently*: a shard absent from the spec list produces no
loop iteration in the client, so neither of its two warning paths can fire. The
tables drop out of the listings and the counts come back smaller with nothing to
say so. Nobody noticed for four days, because nothing compared what the
*released* package knows about against what is live.

That is the gap here. The question is not "do the configs agree" but "is there a
live shard that a released client cannot reach, and would its user be told?"

WHAT IT COMPARES

  live        the Redivis organization catalog -- published, publicly readable
              datasets, from the same documented endpoint the clients' own
              shard discovery reads
  cran        `R/redivis-config.R` out of the CRAN source tarball of the current
              released version
  pypi        `src/irw/config.py` out of the PyPI sdist of the current released
              version
  main        the two config files in local or CI checkouts, when given

A family is a dataset's base name; a shard is that base plus `_N`. A live shard
is counted as missing from a client when the client declares its family and not
that shard -- the same rule the clients use to decide what to adopt, so this
reports exactly what they would and would not reach. A genuinely new family
(something matching no configured base name) is NOT reported as missing: no
client is meant to adopt one silently, since a family needs a `source` value,
filters and metadata wiring, and must fail loudly until it has them.

WHY THE VERDICT TURNS ON SHARD DISCOVERY AND NOT ON THE LISTS

Since Rpkg#205 and Python-pkg#119 both clients read the catalog once a session
and append shards that extend a family they already know. A released client
whose literal list is short therefore still reaches the tables, and tells its
user once that their install predates the shard. Short and loud, which is a
release owed -- not a user reading wrong numbers.

So:

  silent gap   a live shard missing from a client that has no discovery.
               Users of that release are getting short counts right now and
               cannot tell. This is the condition that was live from 10-15, and
               it stays live until the next CRAN cut ships discovery.
  loud gap     a live shard missing from a client that has discovery. Reachable;
               a release is owed, and the README's "what CRAN lacks" list is
               probably stale.
  current      nothing missing.

Exits 0 when no client has a gap, 1 when any does, 2 when a source could not be
read or parsed -- an unreadable source is a failure, not a pass, for the same
reason `check_config_parity.py` has a parser floor: the cheapest way to make a
comparison green is to compare nothing.

USAGE
    python3 metadata/check_client_reach.py
    python3 metadata/check_client_reach.py --json
    python3 metadata/check_client_reach.py --rpkg ../Rpkg/R/redivis-config.R \
                                           --pypkg ../Python-pkg/src/irw/config.py

Network: three public GETs (Redivis, CRAN, PyPI), no credentials. Downloads are
read out of the archive in memory and never extracted to disk.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_config_parity as ccp  # noqa: E402

CATALOG_URL = ("https://redivis.com/api/v1/organizations/datapages/"
               "datasets?maxResults=1000")
CRAN_DESCRIPTION = "https://cran.r-project.org/web/packages/irw/DESCRIPTION"
CRAN_TARBALL = "https://cran.r-project.org/src/contrib/irw_{version}.tar.gz"
PYPI_JSON = "https://pypi.org/pypi/irw/json"

#: Member paths whose presence in a release means that release has shard
#: discovery. Matched on the tail of the path, because an sdist roots everything
#: under `irw-<version>/` and a tarball under `irw/`.
DISCOVERY_FILES = ("R/shard-discovery.R", "irw/utils/redivis/shard_discovery.py")

#: A floor on the live catalog, for the same reason check_config_parity.py has
#: one: a catalog that came back empty would make every client look current.
MIN_LIVE_DATASETS = 20

SILENT, LOUD, CURRENT, ERROR = "silent", "loud", "current", "error"


class ReachError(RuntimeError):
    """A source could not be read. Never reported as "no gap"."""


@dataclass
class LiveShard:
    reference: str
    version: str
    tables: int | None


@dataclass
class Client:
    key: str
    title: str
    version: str | None = None
    discovery: bool = False
    datasets: set[str] = field(default_factory=set)
    missing: list[LiveShard] = field(default_factory=list)
    error: str | None = None

    @property
    def status(self) -> str:
        if self.error:
            return ERROR
        if not self.missing:
            return CURRENT
        return LOUD if self.discovery else SILENT

    def as_dict(self) -> dict:
        return {"key": self.key, "title": self.title, "version": self.version,
                "discovery": self.discovery, "status": self.status,
                "error": self.error,
                "missing": [{"reference": s.reference, "version": s.version,
                             "tables": s.tables} for s in self.missing]}


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch(url: str, binary: bool = False) -> bytes | str:
    """GET a URL with curl.

    curl rather than urllib because Python's socket layer does not happy-eyeball
    and several of these hosts publish AAAA records that do not answer from
    every network, which turns a one-second request into a ten-second stall per
    address. curl is on every runner and on every machine that can run `gh`.
    """
    cmd = ["curl", "-sSfL", "--max-time", "120", url]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        detail = p.stderr.decode("utf-8", "replace").strip().splitlines()
        raise ReachError(f"GET {url.split('?')[0]} failed: "
                         f"{detail[-1] if detail else f'curl exit {p.returncode}'}")
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def live_shards() -> dict[str, LiveShard]:
    """Published, publicly readable datasets in the IRW organization.

    The reference *name* comes from `scopedReference`, not `name`: `name` is a
    display name and does not resolve -- `irw_rank` shows as "IRW_rank" and the
    seventh core warehouse as "Item Response Warehouse 7". A `scopedReference`
    carries a version as its third field only once one has been published, so
    requiring three fields is also the released-or-not test, exactly as the
    clients do it.
    """
    try:
        payload = json.loads(fetch(CATALOG_URL))
    except json.JSONDecodeError as exc:
        raise ReachError(f"Redivis catalog was not JSON ({exc})") from exc
    results = payload.get("results")
    if not isinstance(results, list):
        raise ReachError("Redivis catalog carried no results array")

    out: dict[str, LiveShard] = {}
    seen = 0
    for row in results:
        seen += 1
        ref = row.get("scopedReference")
        if not isinstance(ref, str):
            continue
        parts = ref.split(":")
        if len(parts) != 3:          # no published version
            continue
        if row.get("publicAccessLevel") != "data":
            continue
        count = row.get("tableCount")
        out[parts[0]] = LiveShard(parts[0], parts[2],
                                  int(count) if isinstance(count, int) else None)
    if seen < MIN_LIVE_DATASETS:
        raise ReachError(f"Redivis catalog returned {seen} datasets, below the "
                         f"floor of {MIN_LIVE_DATASETS}; treating as unread "
                         f"rather than reporting every client current")
    return out


def _member(archive, candidates: tuple[str, ...]) -> str | None:
    """The first member whose path ends in one of `candidates`."""
    for name in archive:
        for tail in candidates:
            if name.endswith(tail):
                return name
    return None


def _from_tarball(data: bytes, wanted: tuple[str, ...]) -> tuple[str | None, list[str]]:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        names = tar.getnames()
        hit = _member(names, wanted)
        if hit is None:
            return None, names
        fh = tar.extractfile(hit)
        return (fh.read().decode("utf-8", "replace") if fh else None), names


def _from_wheel(data: bytes, wanted: tuple[str, ...]) -> tuple[str | None, list[str]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
        hit = _member(names, wanted)
        if hit is None:
            return None, names
        return zf.read(hit).decode("utf-8", "replace"), names


def _parse_config(text: str, parser, label: str, suffix: str) -> set[str]:
    """Run one of check_config_parity's parsers over text held in memory.

    The parsers take a path, which is the right interface for the per-PR check
    they were written for. Writing the member to a temporary file keeps that
    interface rather than forking the regexes -- the parse rules stay in one
    place, so a config reformatted past the parser fails both checks at once
    instead of one of them going quietly vacuous.
    """
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=True) as fh:
        fh.write(text)
        fh.flush()
        try:
            families = parser(Path(fh.name))
        except ccp.ParseError as exc:
            raise ReachError(f"{label}: config parsed to implausibly little ({exc})") from exc
        except Exception as exc:
            raise ReachError(f"{label}: could not parse config ({exc})") from exc
    return {ccp._strip_hash(d) for refs in families.values() for d in refs}


def cran_client() -> Client:
    c = Client("cran", "CRAN `irw`")
    try:
        description = fetch(CRAN_DESCRIPTION)
        m = re.search(r"^Version:\s*(\S+)\s*$", description, re.MULTILINE)
        if not m:
            raise ReachError("no Version: field in CRAN's DESCRIPTION for irw")
        c.version = m.group(1)
        data = fetch(CRAN_TARBALL.format(version=c.version), binary=True)
        text, names = _from_tarball(data, ("R/redivis-config.R",))
        if text is None:
            raise ReachError(f"irw_{c.version}.tar.gz holds no R/redivis-config.R")
        c.discovery = _member(names, DISCOVERY_FILES) is not None
        c.datasets = _parse_config(text, ccp.parse_rpkg_config, "CRAN", ".R")
    except ReachError as exc:
        c.error = str(exc)
    return c


def pypi_client() -> Client:
    c = Client("pypi", "PyPI `irw`")
    try:
        payload = json.loads(fetch(PYPI_JSON))
        c.version = payload.get("info", {}).get("version")
        if not c.version:
            raise ReachError("PyPI returned no version for irw")
        files = payload.get("urls") or []
        sdist = next((f for f in files if f.get("packagetype") == "sdist"), None)
        wheel = next((f for f in files if f.get("packagetype") == "bdist_wheel"), None)
        chosen = sdist or wheel
        if not chosen:
            raise ReachError(f"irw {c.version} on PyPI has neither sdist nor wheel")
        data = fetch(chosen["url"], binary=True)
        reader = _from_tarball if chosen is sdist else _from_wheel
        text, names = reader(data, ("irw/config.py",))
        if text is None:
            raise ReachError(f"irw {c.version} artifact holds no irw/config.py")
        c.discovery = _member(names, DISCOVERY_FILES) is not None
        c.datasets = _parse_config(text, ccp.parse_python_config, "PyPI", ".py")
    except ReachError as exc:
        c.error = str(exc)
    return c


def checkout_client(key: str, title: str, path: Path, parser, suffix: str,
                    discovery_file: str) -> Client:
    """A config file in a checkout -- `main`, rather than a release.

    Reported separately because the two answer different questions. A release
    with a gap is users reading short counts; `main` with a gap is work owed
    before the next cut, and nobody is affected yet.
    """
    c = Client(key, title, version="main")
    try:
        if not path.exists():
            raise ReachError(f"{path} does not exist")
        c.datasets = _parse_config(path.read_text(), parser, title, suffix)
        # Relative to the config file, not to a guessed repository root: the
        # two configs sit at different depths in their repositories and a
        # checkout can be given by any path.
        c.discovery = (path.parent / discovery_file).exists()
    except ReachError as exc:
        c.error = str(exc)
    return c


# ---------------------------------------------------------------------------
# Comparing
# ---------------------------------------------------------------------------

def family_of(reference: str) -> str:
    """`item_response_warehouse_7` -> `item_response_warehouse`."""
    return re.sub(r"_\d+$", "", reference)


def gaps(client: Client, live: dict[str, LiveShard]) -> list[LiveShard]:
    """Live shards this client declares the family of, but not the shard.

    Family-only, deliberately. A live dataset matching no configured base name
    is a new *family*, and no client adopts one of those silently: it needs a
    source value, filters and metadata wiring, so it must keep failing loudly.
    Reporting it here would make this check red for months at a time over
    something it is not asking about.
    """
    families = {family_of(d) for d in client.datasets}
    return sorted((s for ref, s in live.items()
                   if ref not in client.datasets and family_of(ref) in families),
                  key=lambda s: s.reference)


def render(clients: list[Client], live: dict[str, LiveShard]) -> list[str]:
    total = sum(s.tables for s in live.values() if s.tables)
    out = [f"{len(live)} published, public datasets in the catalog "
           f"({total:,} tables)."]
    for c in clients:
        if c.status == ERROR:
            out.append(f"  ERROR    {c.title}: {c.error}")
            continue
        if c.status == CURRENT:
            out.append(f"  current  {c.title} {c.version} reaches every live shard")
            continue
        label = "SILENT" if c.status == SILENT else "loud"
        lost = sum(s.tables for s in c.missing if s.tables)
        out.append(f"  {label:8} {c.title} {c.version} does not list "
                   f"{len(c.missing)} live shard(s), {lost:,} tables"
                   + ("" if c.discovery else "  <-- and cannot warn about them"))
        for s in c.missing:
            out.append(f"             {s.reference} {s.version} "
                       f"({'?' if s.tables is None else format(s.tables, ',')} tables)")
    if any(c.status == SILENT for c in clients):
        out += ["",
                "A SILENT gap means that release has no shard discovery, so its "
                "users' table counts are short and nothing in the client says so.",
                "Fix: cut a release carrying the shard, or carrying discovery."]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--rpkg", default=None,
                    help="R config in a checkout, to report `main` alongside the releases")
    ap.add_argument("--pypkg", default=None, help="Python config in a checkout")
    ap.add_argument("--no-releases", action="store_true",
                    help="skip CRAN and PyPI (offline; only the checkouts given)")
    args = ap.parse_args(argv)

    try:
        live = live_shards()
    except ReachError as exc:
        print(f"could not read the live catalog: {exc}", file=sys.stderr)
        return 2

    clients: list[Client] = []
    if not args.no_releases:
        clients += [cran_client(), pypi_client()]
    if args.rpkg:
        clients.append(checkout_client("rpkg-main", "Rpkg `main`", Path(args.rpkg),
                                       ccp.parse_rpkg_config, ".R",
                                       "shard-discovery.R"))
    if args.pypkg:
        clients.append(checkout_client("pypkg-main", "Python-pkg `main`", Path(args.pypkg),
                                       ccp.parse_python_config, ".py",
                                       "utils/redivis/shard_discovery.py"))
    for c in clients:
        if c.status != ERROR:
            c.missing = gaps(c, live)

    if args.json:
        print(json.dumps({"live": {r: {"version": s.version, "tables": s.tables}
                                   for r, s in live.items()},
                          "clients": [c.as_dict() for c in clients]}, indent=2))
    else:
        print("\n".join(render(clients, live)))

    if any(c.status == ERROR for c in clients):
        return 2
    return 1 if any(c.missing for c in clients) else 0


if __name__ == "__main__":
    raise SystemExit(main())
