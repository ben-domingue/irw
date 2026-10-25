#!/usr/bin/env python3
"""Fill in `irw_version` for correction entries that name no release.

WHY
---
The corrections policy promises that every fix names the version carrying it,
and `red_up/README.md` says to append the `table_changes.csv` row once the
release is live, with the `irw_version` of the release that carries it. 92 of
715 entries were appended at upload time instead and never got a version
(review R-12, issue #3216). An entry with no version cannot answer the one
question a reader of the Corrections page has -- which pinned release contains
this fix -- so the column is the whole value of the row.

The dates alone cannot answer it. `date` is a day, and several shard releases
can land on one day: the `ALSECYPIAMH_WU_2022_SDQ` fix of 2026-08-27 is
recorded as IRW 311, which is `item_response_warehouse` v45.1 at 22:46, not
v45.0 at 16:35 the same morning. Guessing between them would publish a wrong
release pointer, which is worse than a blank one.

HOW IT DECIDES
--------------
Redivis serves a dataset listing at any released version, and the listing gives
each table's content `hash`. So the release that carried a correction is
observable: it is the first version in which the table's hash (or its presence,
for a rename or a retirement) stops being what it was before the fix. This
script walks the shard's releases from the one in force on the correction's date
forward, finds that transition, and maps the tag back to the first
`irw_version` in `version_manifest.tsv` that carries it -- which is the
definition `red_up/README.md` gives.

It reports rather than guesses. A row whose table never changes inside the
window is left blank and listed as unresolved: a documentation-only entry has
no transition to find, and so does a fix whose release is outside the window.

USAGE (from src/metadata, with REDIVIS_API_TOKEN set)

  python3 pin_corrections.py                 # report, change nothing
  python3 pin_corrections.py --write         # fill the resolved rows in place
  python3 pin_corrections.py --issue '#3100' --window 45
  python3 pin_corrections.py --table wu2021_affect

Listings are cached under --cache (a scratch directory by default), because one
listing is ~5 s and a cluster of 30 corrections in one shard re-reads the same
handful of versions.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHANGES = HERE / "table_changes.csv"
MANIFEST = HERE / "version_manifest.tsv"
CONFIG = HERE / "redivis_config.R"

#: Which family CSV describes a table, and the Redivis dataset each one is for.
#: metadata.csv carries its own `dataset` column; the others are one dataset
#: each. A retired table is in none of them, so its shard is discovered by
#: probing (see locate_dataset).
FAMILY_CSVS = {
    "metadata.csv": None,
    "nominal_metadata.csv": "irw_nominal",
    "comps_metadata.csv": "irw_competitions",
    "simsyn_metadata.csv": "irw_simsyn",
    "rank_metadata.csv": "irw_rank",
    #: `conj_metadata.csv`, not `conjoint_`: the conjoint family's CSV is named
    #: for the `conj` source key. Leaving it out is how the one correction this
    #: script could not place went unplaced on the first run.
    "conj_metadata.csv": "irw_conjoint",
}


def owner() -> str:
    m = re.search(r'IRW_OWNER\s*<-\s*"([^"]+)"', CONFIG.read_text())
    if not m:
        sys.exit(f"error: no IRW_OWNER in {CONFIG}")
    return m.group(1)


def config_datasets() -> list[str]:
    """Every dataset a correction could name, out of redivis_config.R: the core
    shards plus the named aux datasets. irw_meta holds no response data and is
    left out; item text is not recorded in table_changes.csv at all (#2168)."""
    text = CONFIG.read_text()
    out: list[str] = []
    for vec in ("IRW_CORE_DATASETS", "IRW_CONJ_DATASETS", "IRW_RANK_DATASETS"):
        m = re.search(vec + r"\s*<-\s*c\((.*?)\)", text, re.S)
        if m:
            out += re.findall(r'"([^"]+)"', m.group(1))
    m = re.search(r"IRW_AUX_DATASETS\s*<-\s*c\((.*?)\)", text, re.S)
    if m:
        out += [v for k, v in re.findall(r'(\w+)\s*=\s*"([^"]+)"', m.group(1))
                if v != "irw_meta"]
    return out


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def table_datasets() -> dict[str, str]:
    """table name -> Redivis dataset, for every table a family CSV describes."""
    out: dict[str, str] = {}
    for name, dataset in FAMILY_CSVS.items():
        for row in read_csv(HERE / name):
            out[row["table"]] = row.get("dataset") or dataset
    return out


def manifest_releases() -> dict[str, list[tuple[str, str, int]]]:
    """dataset -> [(released_at, tag, first irw_version carrying it)], in order.

    One entry per TAG, not per manifest row: a tag stays in place across later
    versions, and `red_up/README.md` defines the correction's version as the
    FIRST one carrying it."""
    seen: dict[tuple[str, str], tuple[str, int]] = {}
    for row in _read_tsv(MANIFEST):
        key = (row["dataset"], row["redivis_tag"])
        version = int(row["irw_version"])
        at = row["redivis_released_at"]
        if key not in seen or version < seen[key][1]:
            seen[key] = (at, version)
    out: dict[str, list[tuple[str, str, int]]] = {}
    for (dataset, tag), (at, version) in seen.items():
        out.setdefault(dataset, []).append((at, tag, version))
    for dataset in out:
        out[dataset].sort()
    return out


def _read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


class Listings:
    """Cached {table: hash} for a dataset at a released version."""

    def __init__(self, cache: Path, account: str):
        self.cache = cache
        self.account = account
        self.cache.mkdir(parents=True, exist_ok=True)
        self._mem: dict[tuple[str, str], dict[str, str]] = {}

    def at(self, dataset: str, tag: str) -> dict[str, str]:
        key = (dataset, tag)
        if key in self._mem:
            return self._mem[key]
        path = self.cache / f"{dataset}@{tag.replace('.', '_')}.json"
        if path.exists():
            data = json.loads(path.read_text())
        else:
            import redivis  # imported here so --help works without credentials
            ver = tag[1:] if tag.startswith("v") else tag
            ds = redivis.organization(self.account).dataset(dataset, version=ver)
            data = {t.name: str(t.properties.get("hash") or "") for t in ds.list_tables()}
            path.write_text(json.dumps(data, sort_keys=True))
        self._mem[key] = data
        return data


#: Per-variable statistics compared by the deep pass. Not every type carries
#: every key, so a missing one is recorded as None rather than skipped -- a key
#: that appears or disappears is itself a change.
_STAT_KEYS = ("count", "numDistinct", "min", "max", "mean")


def table_signature(dataset: str, tag: str, table: str, account: str):
    """Per-variable statistics for one table at one release, or None.

    THE HASH IS NOT ENOUGH, and this is not theoretical: the three
    `kemp_2019_mss_*` tables were re-uploaded with CORRECTED dates under hashes
    byte-identical to the wrong ones (irw#3110, 2026-10-19), so the cheap scan
    above calls that release a no-op. Statistics see it: the `date` minimum goes
    from 1507719 to 1507719457, which is January 1970 becoming October 2017.

    One request per variable, so this is the slow path and runs only for the
    rows the hash scan could not settle.
    """
    import redivis
    ver = tag[1:] if tag.startswith("v") else tag
    try:
        tab = redivis.organization(account).dataset(dataset, version=ver).table(table)
        out = {}
        for var in tab.list_variables():
            stats = var.get_statistics() or {}
            out[var.name] = tuple(stats.get(k) for k in _STAT_KEYS)
        return out
    except Exception:
        return None


def window_tags(releases: list[tuple[str, str, int]], date: str, days: int):
    """The release in force on `date`, then every release up to `days` later.

    The base is the last release whose timestamp is at or before the END of the
    correction's date -- a release earlier the same day may already carry the
    fix, which is exactly the ALSECYPIAMH case -- so the base is the last
    release STRICTLY BEFORE the date, and the same-day releases are candidates.
    """
    import datetime as dt
    day = dt.date.fromisoformat(date)
    lo = day.isoformat()
    hi = (day + dt.timedelta(days=days)).isoformat()
    base = None
    cands = []
    for at, tag, version in releases:
        if at[:10] < lo:
            base = (at, tag, version)
        elif at[:10] <= hi:
            cands.append((at, tag, version))
    return base, cands


def locate_dataset(table: str, datasets: list[str], listings: Listings,
                   releases, date: str) -> str | None:
    """Which shard held a table that no family CSV describes any more?

    Probes each dataset at the release in force before the correction, which is
    the last version in which a retired or renamed-away table still exists."""
    for dataset in datasets:
        base, _ = window_tags(releases.get(dataset, []), date, 0)
        if base is None:
            continue
        if table in listings.at(dataset, base[1]):
            return dataset
    return None


def resolve(row: dict, dataset: str, listings: Listings, releases, days: int,
            deep: bool = False, account: str = ""):
    """(irw_version, note) for one correction row, or (None, why not)."""
    base, cands = window_tags(releases.get(dataset, []), row["date"], days)
    if not cands:
        return None, f"no {dataset} release within {days} days of {row['date']}"
    was_present = base is not None and row["table"] in listings.at(dataset, base[1])
    was_hash = listings.at(dataset, base[1]).get(row["table"], "") if base else ""
    for at, tag, version in cands:
        now = listings.at(dataset, tag)
        present = row["table"] in now
        if present != was_present or (present and now[row["table"]] != was_hash):
            what = ("appeared" if present and not was_present else
                    "removed" if was_present and not present else "content changed")
            return version, f"{dataset} {tag} ({at[:10]}, {what})"
    if not deep:
        return None, (f"{row['table']} is unchanged across {len(cands)} {dataset} "
                      f"release(s) after {row['date']} -- a hash is blind to a "
                      f"same-shape swap (irw#3110), so try --deep before "
                      f"concluding the fix is not released")
    #: The deep pass: per-variable statistics rather than the content hash.
    if base is None:
        return None, f"no {dataset} release before {row['date']} to compare against"
    was = table_signature(dataset, base[1], row["table"], account)
    if was is None:
        return None, (f"{row['table']} is not readable at {dataset} {base[1]}, "
                      f"so there is nothing to compare the later releases with")
    for at, tag, version in cands:
        now = table_signature(dataset, tag, row["table"], account)
        if now is None:
            continue
        if now != was:
            moved = sorted(k for k in set(was) | set(now)
                           if was.get(k) != now.get(k))
            return version, (f"{dataset} {tag} ({at[:10]}, statistics changed: "
                             f"{', '.join(moved[:4])})")
    return None, (f"{row['table']} is unchanged across {len(cands)} {dataset} "
                  f"release(s) after {row['date']}, by hash and by per-variable "
                  f"statistics -- the fix is in no release yet")


def write_changes(rows: list[dict], fields: list[str]) -> None:
    """LF, minimal quoting: the form table_changes.csv is already in, so the
    diff is the filled cells and nothing else."""
    with CHANGES.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true",
                    help="fill the resolved rows in table_changes.csv")
    ap.add_argument("--issue", help="only rows with this issue (e.g. '#3100')")
    ap.add_argument("--table", help="only rows for this table")
    ap.add_argument("--deep", action="store_true",
                    help="for rows the hash scan cannot settle, compare "
                         "per-variable statistics instead (one request per "
                         "variable per release -- slow, and the only signal "
                         "that sees a same-shape content swap)")
    ap.add_argument("--window", type=int, default=30,
                    help="days after the correction's date to look for its release (default 30)")
    ap.add_argument("--cache", default=os.environ.get("PIN_CACHE", "/tmp/irw-pin-cache"),
                    help="directory for cached version listings")
    args = ap.parse_args(argv)

    with CHANGES.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    todo = [r for r in rows if not (r.get("irw_version") or "").strip()]
    if args.issue:
        todo = [r for r in todo if r.get("issue") == args.issue]
    if args.table:
        todo = [r for r in todo if r.get("table") == args.table]
    print(f"{len(rows)} entries, {len(todo)} to pin"
          + (" (filtered)" if args.issue or args.table else ""))
    if not todo:
        return 0

    listings = Listings(Path(args.cache), owner())
    releases = manifest_releases()
    known = table_datasets()
    datasets = config_datasets()

    resolved = 0
    unresolved: list[tuple[dict, str]] = []
    for row in todo:
        dataset = known.get(row["table"])
        if dataset is None:
            dataset = locate_dataset(row["table"], datasets, listings, releases, row["date"])
        if dataset is None:
            unresolved.append((row, "no dataset holds this table, before or after"))
            continue
        version, note = resolve(row, dataset, listings, releases, args.window,
                                deep=args.deep, account=listings.account)
        if version is None:
            unresolved.append((row, note))
            continue
        row["irw_version"] = str(version)
        resolved += 1
        print(f"  {row['table']:<55} {row['issue']:>7}  IRW {version:<4} {note}")

    print(f"\nresolved {resolved} of {len(todo)}")
    if unresolved:
        print(f"unresolved {len(unresolved)} -- left blank:")
        for row, why in unresolved:
            print(f"  {row['table']:<55} {row['issue']:>7}  {why}")
    if args.write and resolved:
        write_changes(rows, fields)
        print(f"wrote {CHANGES.name}")
    elif resolved:
        print("(report only; pass --write to fill them in)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
