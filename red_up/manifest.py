"""The IRW version manifest: which Redivis version of every dataset was live, when.

An IRW-based paper cannot currently be replicated, because the data underneath
it moves. Redivis versions each dataset independently -- `irw_meta` is at v19.x
while `irw_simsyn` has had two releases ever -- so there is no corpus-wide
number to cite. This module writes one down: a git-tracked file recording, for
every point in the corpus' history, the released version of every dataset
registered in `redivis_config.R`. That is a lockfile, the same shape as `renv.lock`, and it is what
`irw_version()` in the R and Python packages resolves against. See #1705.

    python3 -m red_up.manifest                 # refresh: append anything new
    python3 -m red_up.manifest --check         # CI: is the file up to date?
    python3 -m red_up.manifest --show 333      # print one IRW version
    python3 -m red_up.manifest --at 2026-08-01 # print the version live that day
    python3 -m red_up.manifest --rebuild       # renumber from scratch (see below)

Exit codes: 0 ok - 1 the file is stale or a rebuild would renumber - 2 bad input.

**Why a full snapshot rather than a log of releases.** Every IRW version
carries a row per dataset, so the file repeats itself and grows by one line per
dataset a release. The alternative -- one line per release, with clients deriving the
snapshot by carrying values forward -- is a quarter the size and was rejected:
the question a person actually asks is "what was everything pinned to at v333",
and it should be answerable by looking, not by reimplementing a carry-forward in
both R and Python and hoping the two agree.

**Why IRW version numbers are never reused.** A published paper cites an integer
here. If a later run renumbered, that citation would silently point at different
data -- the exact failure the manifest exists to prevent. So a normal run only
ever *appends*: it recomputes the whole history, checks that the part already on
disk is unchanged, and refuses if it is not. `--rebuild` overrides that, and
should only be used before the first numbers have been published anywhere.

**Release dates: 142 of 333 are not real, and the file says so.** Redivis'
`releasedAt` was overwritten for the older core shards by a platform-side
migration -- every version of `item_response_warehouse` up to v54.0, of
`item_response_warehouse_2` up to v9.0, and the first two of
`item_response_warehouse_3` claims to have been released inside one 80-minute
window on 2026-07-21. `createdAt` on those versions is genuine. Scored against
the 190 versions whose real release date we do know, substituting `createdAt`
lands within an hour 58% of the time and is off by more than a week 9% of the
time (worst case 23 days), so it is recorded as a *lower bound* and never as
fact: those rows carry `precision = bracketed` and a `redivis_released_before`
giving the upper bound. Anything derived from them -- an `--at` lookup before
2026-07-21, most of all -- must be reported as approximate.

The detection deliberately hardcodes no date. Redivis allows one unreleased
draft per dataset at a time, so version i+1's draft cannot exist until version i
is released: `releasedAt[i] > createdAt[i+1]` is therefore impossible, and every
version that violates it has been overwritten. That catches 140 of the 142; the
last overwritten version in a run has a genuine successor and slips through, so
a second pass extends each run to versions sharing its `releasedAt` window.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path

from .auth import authenticate
from .targets import ConfigError, Target, find_config, load_registry

#: Where the manifest lives. `src/metadata/` alongside `status_history.tsv`,
#: which sets the precedent: small, git-tracked, meant to be read over time.
MANIFEST_NAME = "version_manifest.tsv"

COLUMNS = (
    "irw_version",              # integer, assigned once, never reused
    "irw_released_at",          # when this IRW version became current (UTC)
    "dataset",                  # Redivis dataset name, per redivis_config.R
    "redivis_tag",              # the pinned version, e.g. "v19.3"
    "redivis_released_at",      # when that version was released; a lower bound
                                #   when precision is `bracketed`
    "precision",                # "exact" | "bracketed"
    "redivis_released_before",  # upper bound, `bracketed` rows only
)

EXACT, BRACKETED = "exact", "bracketed"

#: Two versions whose `releasedAt` fall this close together, when one of them is
#: already known to have been overwritten, were stamped by the same migration.
#: The observed window is 80 minutes; four hours leaves room without reaching
#: any genuine release (the nearest is 19 hours away).
RUN_WINDOW = dt.timedelta(hours=4)


def manifest_path(config_path: Path | None = None) -> Path:
    """`src/metadata/version_manifest.tsv`, found the way red_up finds anything."""
    return (config_path or find_config()).parent / MANIFEST_NAME


@dataclass(frozen=True)
class Release:
    """One released Redivis version of one dataset."""

    dataset: str
    tag: str
    index: int
    created_at: dt.datetime
    released_at: dt.datetime          # genuine, or the lower bound if bracketed
    precision: str
    released_before: dt.datetime | None = None

    @property
    def effective_at(self) -> dt.datetime:
        """The date the corpus history is ordered by.

        For a bracketed release this is the lower bound, which is the earliest
        moment the version could have been live. Ordering by anything else
        would claim precision the data does not have.
        """
        return self.released_at


def _when(epoch_ms: int | None) -> dt.datetime | None:
    if not epoch_ms:
        return None
    return dt.datetime.fromtimestamp(epoch_ms / 1000, tz=dt.timezone.utc)


def _iso(when: dt.datetime | None) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%SZ") if when else ""


def _parse(text: str) -> dt.datetime | None:
    if not text:
        return None
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=dt.timezone.utc)


def parse_date(text: str) -> dt.datetime:
    """A user-supplied date or timestamp, as UTC. Raises ValueError."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text, fmt).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"not a date: {text!r} (try 2026-08-01 or 2026-08-01T12:00:00Z)")


def classify(versions: list[dict]) -> list[Release]:
    """Turn one dataset's raw version properties into Releases, dating each.

    `versions` is the `.properties` of everything `list_versions()` returned,
    in any order. Unreleased drafts are dropped: a draft cannot be fetched by
    anyone else, so pinning one would produce a citation nobody can follow.
    """
    ordered = sorted(versions, key=lambda p: p.get("index", 0))
    released = [p for p in ordered if p.get("isReleased")]
    if not released:
        return []

    # Pass 1 -- the impossible ordering. Redivis permits one draft at a time,
    # so a version released after its successor's draft was opened has had its
    # timestamp rewritten. Compared against the *next released* version, since
    # a draft sitting between the two is not yet a version anyone can cite.
    suspect = [False] * len(released)
    for i, (this, nxt) in enumerate(zip(released, released[1:])):
        rel, nxt_created = _when(this.get("releasedAt")), _when(nxt.get("createdAt"))
        if rel and nxt_created and rel > nxt_created:
            suspect[i] = True

    # Pass 2 -- extend each run. The final version of an overwritten run has a
    # genuine successor, so pass 1 cannot see it; what gives it away is that it
    # shares the migration's timestamp window with a version pass 1 did flag.
    stamps = [_when(p.get("releasedAt")) for p in released]
    flagged = [s for s, bad in zip(stamps, suspect) if bad and s]
    if flagged:
        low, high = min(flagged) - RUN_WINDOW, max(flagged) + RUN_WINDOW
        for i, stamp in enumerate(stamps):
            if stamp and low <= stamp <= high:
                suspect[i] = True

    out: list[Release] = []
    for i, props in enumerate(released):
        created, rel = _when(props.get("createdAt")), stamps[i]
        if created is None:
            # Nothing to fall back on; skip rather than invent a date.
            continue
        if suspect[i] or rel is None:
            # The genuine release is somewhere between this version's own
            # creation and the next version's -- the next draft cannot open
            # until this one is out. With no successor the bound is open.
            nxt = _when(released[i + 1].get("createdAt")) if i + 1 < len(released) else None
            out.append(Release(
                dataset=props["_dataset"], tag=props["tag"], index=props["index"],
                created_at=created, released_at=created,
                precision=BRACKETED, released_before=nxt))
        else:
            out.append(Release(
                dataset=props["_dataset"], tag=props["tag"], index=props["index"],
                created_at=created, released_at=rel, precision=EXACT))
    return out


def collect(owner: str, targets: list[Target]) -> list[Release]:
    """Every released version of every registered dataset, dated. Hits Redivis."""
    import redivis

    releases: list[Release] = []
    for target in targets:
        versions = redivis.user(owner).dataset(target.name).list_versions()
        props = []
        for version in versions:
            entry = dict(version.properties)
            entry["_dataset"] = target.name
            props.append(entry)
        releases.extend(classify(props))
    return releases


@dataclass(frozen=True)
class Row:
    irw_version: int
    irw_released_at: dt.datetime
    release: Release


def build(releases: list[Release], order: list[str]) -> list[Row]:
    """Expand a flat list of releases into the full per-version snapshot.

    Releases sharing a timestamp to the second are one IRW version, not
    several: two datasets published together are one state of the corpus.
    Within a snapshot the datasets keep registry order, so a diff between
    consecutive versions is one changed line rather than a reshuffle.
    """
    rank = {name: i for i, name in enumerate(order)}
    events = sorted(releases, key=lambda r: (r.effective_at, rank.get(r.dataset, 99),
                                             r.index))
    rows: list[Row] = []
    live: dict[str, Release] = {}
    number = 0
    i = 0
    while i < len(events):
        moment = events[i].effective_at
        while i < len(events) and events[i].effective_at == moment:
            live[events[i].dataset] = events[i]
            i += 1
        number += 1
        for name in order:
            if name in live:
                rows.append(Row(number, moment, live[name]))
    return rows


def write(rows: list[Row], path: Path) -> None:
    with path.open("w", newline="") as handle:
        out = csv.writer(handle, delimiter="\t", lineterminator="\n")
        out.writerow(COLUMNS)
        for row in rows:
            r = row.release
            out.writerow([
                row.irw_version, _iso(row.irw_released_at), r.dataset, r.tag,
                _iso(r.released_at), r.precision,
                _iso(r.released_before) if r.precision == BRACKETED else "",
            ])


def read(path: Path) -> list[Row]:
    """Load a manifest written by `write`. Raises ConfigError on a bad header."""
    if not path.is_file():
        return []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ConfigError(
                f"{path} does not have the expected columns.\n"
                f"  expected: {list(COLUMNS)}\n  found:    {reader.fieldnames}")
        rows = []
        for line in reader:
            rows.append(Row(
                irw_version=int(line["irw_version"]),
                irw_released_at=_parse(line["irw_released_at"]),
                release=Release(
                    dataset=line["dataset"], tag=line["redivis_tag"], index=-1,
                    created_at=_parse(line["redivis_released_at"]),
                    released_at=_parse(line["redivis_released_at"]),
                    precision=line["precision"],
                    released_before=_parse(line["redivis_released_before"]))))
    return rows


def _comparable(rows: list[Row]) -> list[tuple]:
    """The parts of a row a rebuild must not change. `index` is not one."""
    return [(r.irw_version, _iso(r.irw_released_at), r.release.dataset,
             r.release.tag, _iso(r.release.released_at), r.release.precision,
             _iso(r.release.released_before) if r.release.precision == BRACKETED
             else "") for r in rows]


def diverges(existing: list[Row], fresh: list[Row]) -> str | None:
    """Where a rebuild would contradict what is already published, if anywhere.

    Only the existing rows are checked -- new ones appended past the end are
    the normal case. Anything else means an IRW version number would come to
    mean something different than it did, which invalidates every citation of
    it, so the caller must refuse rather than write.
    """
    old, new = _comparable(existing), _comparable(fresh)
    if len(new) < len(old):
        return (f"the rebuilt manifest has {len(new)} rows but {len(old)} are "
                f"already recorded -- versions would disappear")
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b:
            return (f"line {i + 2} already records IRW v{a[0]} as "
                    f"{a[2]} {a[3]} ({a[1]}), but a rebuild makes it "
                    f"{b[2]} {b[3]} ({b[1]})")
    return None


def snapshot(rows: list[Row], version: int) -> list[Row]:
    return [r for r in rows if r.irw_version == version]


def version_at(rows: list[Row], when: dt.datetime) -> int | None:
    """The IRW version current at `when`, or None if the corpus predates it."""
    live = [r.irw_version for r in rows if r.irw_released_at <= when]
    return max(live) if live else None


def approximate(rows: list[Row], version: int) -> list[Row]:
    """The rows of a snapshot whose release date is a lower bound, not a fact."""
    return [r for r in snapshot(rows, version) if r.release.precision == BRACKETED]


def show(rows: list[Row], version: int, as_of: bool = False) -> None:
    """Print one snapshot.

    `as_of` changes what the caveat says, and the difference matters. Asked for
    IRW v269 directly, a bracketed row means only that we cannot date it: the
    pin itself is exactly what v269 held. Asked what was live on a *date*, the
    same row means the pin may be wrong -- the next version could already have
    been released inside the bracket. Reporting the weaker caveat in the
    stronger case is the overclaim this whole file exists to avoid.
    """
    rows = snapshot(rows, version)
    if not rows:
        print(f"no IRW version {version} in the manifest", file=sys.stderr)
        return
    print(f"IRW v{version}   released {_iso(rows[0].irw_released_at)}   "
          f"{len(rows)} dataset(s)")
    for row in rows:
        r = row.release
        note = (f"  approx, released before {_iso(r.released_before) or 'unknown'}"
                if r.precision == BRACKETED else "")
        print(f"  {r.dataset:<28} {r.tag:<8} {_iso(r.released_at)}{note}")
    stale = [r for r in rows if r.release.precision == BRACKETED]
    if stale and as_of:
        print(f"\n  APPROXIMATE. {len(stale)} of {len(rows)} pins rest on a "
              f"release date Redivis overwrote, so for those the *tag* may be "
              f"wrong too: a later version could already have been live within "
              f"the bracket shown. Do not cite this as-of result; cite an IRW "
              f"version number instead.")
    elif stale:
        print(f"\n  {len(stale)} of {len(rows)} release dates are approximate: "
              f"Redivis overwrote them. The pins are exactly what IRW "
              f"v{version} held; only their dates are lower bounds.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="red_up.manifest",
        description="Record which Redivis version of every IRW dataset was live, when.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the manifest is missing anything (for CI)")
    ap.add_argument("--rebuild", action="store_true",
                    help="renumber from scratch, discarding existing IRW version "
                         "numbers. Only safe before any number has been cited.")
    ap.add_argument("--show", type=int, metavar="N",
                    help="print IRW version N and exit (reads the file, no network)")
    ap.add_argument("--at", metavar="DATE",
                    help="print the IRW version current on DATE and exit "
                         "(reads the file, no network)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be appended, write nothing")
    args = ap.parse_args(argv)

    try:
        path = manifest_path()
    except ConfigError as exc:
        print(f"red_up.manifest: {exc}", file=sys.stderr)
        return 2

    # The two read-only queries need neither credentials nor the network, so
    # they are answered before anything reaches out.
    if args.show is not None or args.at:
        try:
            rows = read(path)
        except ConfigError as exc:
            print(f"red_up.manifest: {exc}", file=sys.stderr)
            return 2
        if not rows:
            print(f"red_up.manifest: {path} is empty; run it with no arguments "
                  f"first", file=sys.stderr)
            return 2
        if args.at:
            try:
                when = parse_date(args.at)
            except ValueError as exc:
                print(f"red_up.manifest: {exc}", file=sys.stderr)
                return 2
            version = version_at(rows, when)
            if version is None:
                print(f"nothing was released before {_iso(when)}; the corpus "
                      f"begins at {_iso(rows[0].irw_released_at)}", file=sys.stderr)
                return 1
            print(f"as of {_iso(when)}:")
            show(rows, version, as_of=True)
            return 0
        show(rows, args.show)
        return 0

    try:
        owner, targets = load_registry()
    except ConfigError as exc:
        print(f"red_up.manifest: {exc}", file=sys.stderr)
        return 2

    authenticate()
    print(f"reading version history for {len(targets)} dataset(s) ...")
    releases = collect(owner, targets)
    fresh = build(releases, [t.name for t in targets])
    bracketed = sum(1 for r in releases if r.precision == BRACKETED)
    print(f"  {len(releases)} released version(s), {bracketed} with an "
          f"overwritten release date")

    try:
        existing = read(path)
    except ConfigError as exc:
        print(f"red_up.manifest: {exc}", file=sys.stderr)
        return 2

    if existing and not args.rebuild:
        problem = diverges(existing, fresh)
        if problem:
            print(f"\nred_up.manifest: refusing to write -- {problem}.\n"
                  f"An IRW version number is a citation; renumbering silently "
                  f"repoints it at other data. Investigate, then use --rebuild "
                  f"only if no number here has been published.", file=sys.stderr)
            return 1

    added = len(fresh) - len(existing)
    highest_old = existing[-1].irw_version if existing else 0
    highest_new = fresh[-1].irw_version if fresh else 0
    if args.check:
        if added or highest_new != highest_old:
            print(f"\nSTALE: {added} row(s) missing, latest IRW version is "
                  f"v{highest_new} but the file stops at v{highest_old}. "
                  f"Run `python3 -m red_up.manifest`.")
            return 1
        print(f"\nup to date at IRW v{highest_new} ({len(existing)} rows).")
        return 0

    if args.dry_run:
        print(f"\n--dry-run: would write {len(fresh)} rows (v1..v{highest_new}), "
              f"{added:+d} versus the {len(existing)} on disk. Nothing written.")
        return 0

    write(fresh, path)
    if not existing:
        print(f"\nwrote {path} -- {len(fresh)} rows, IRW v1..v{highest_new}.")
    elif added:
        print(f"\nappended {added} row(s) to {path}; IRW v{highest_old} -> "
              f"v{highest_new}.")
    else:
        print(f"\n{path} was already current at IRW v{highest_new}.")
    print("Commit it: the file is the reproducibility record, and its git "
          "history is the corpus' release history.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
