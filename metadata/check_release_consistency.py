#!/usr/bin/env python3
"""Does everything the project has promised about a table agree with what is
published? Run this BEFORE clicking Publish.

Closes the release-stage half of the 2026-10-24 adversarial review's prevention
section: R-10, R-11, R-12, R-13, R-14, R-15, R-16, and one of R-01's two
exposure paths.

WHY A GATE AND NOT A REPORT
---------------------------
`drift_report.py` already answers "is anything downstream behind?" and it
deliberately never fails: a stale warehouse is a fact to act on, not a broken
build. This script answers a different question -- "do the records disagree with
the data?" -- and that one has to be able to stop a release, because every
mismatch it finds is a statement the project is making about a table that is not
true of the table.

The four kinds of mismatch, each with the case that motivated it:

  schema      `metadata.csv`'s `variables` string is written once, when a table
              first appears, and `01_metadata.R`'s rolling refresh pass updates
              only the seven numeric statistics. A table rebuilt with fewer
              columns therefore keeps its ORIGINAL column list in the published
              catalog for ever. In October 2026 nineteen tables declared columns
              that had been removed from the data, and because five of the
              removals were removals of personal fields, the catalog was
              publishing the names of exactly the columns a correction had taken
              out (review R-11, and the second exposure path of R-01).

  counts      57 tables published an `n_responses` larger than the number of
              rows the table actually has, which is impossible under the site's
              own definition of the field, and `number_pattern_game` published
              `n_items` wrong by a factor of 100, which made its `density` 1.765
              (review R-13, R-04). Both are the same defect: a published number
              computed against a table that has since been replaced.

  unexplained-repeats
              A published `density` above 1 is proof that an id-item pair
              repeats: there are more responses than person-item cells. 743
              tables are above 1 and 705 of them say why, with an occasion
              column. The rest are silent, and on 2026-10-25 two thirds of them
              were silent because `n_participants` was stale -- `sris_silvia2022`
              published 221 against 1,192 live, a factor of 5.4 -- which the
              `counts` check cannot see, since it bounds every count above by
              numRows and a stale participant count is too SMALL. The remainder
              hold duplicate rows that nothing in the table explains: one id
              covering two respondents (`liu_2017_*`, where the covariates give
              two different ages for the shared id), or a trial-level task whose
              trial column was dropped at ingest (review R-21, #3222).

  corrections The corrections policy promises every fix names the release that
              carries it. 92 of 715 entries name no version (review R-12), and
              59 identifiers in the correction log match nothing in the public
              index and have no successor that does (review R-16).

  withdrawals A withdrawal that does not reach a consumer is not a withdrawal
              (issue #51). The ledger records tables as withdrawn that are in
              the current release, item text is still served under the retired
              name of a withdrawn table, and `reinstated.tsv` is maintained by
              hand and covers none of the affected tables (review R-10, R-14).

WHAT IT COMPARES

  live        the Redivis catalog: one `datasets/<ref>/tables` listing per
              family dataset, public and unauthenticated, giving each table's
              `numRows`, `variableCount` and content `hash`
  declared    the per-family metadata CSVs this repository writes and
              `upload_meta.py` ships -- `metadata.csv` and the `*_metadata.csv`
              siblings
  records     `metadata/table_changes.csv` (corrections), `itemtext/
              withdrawals.csv` (the one withdrawal ledger), and the biblio,
              tags and itemtext_metadata CSVs that a withdrawal must reach

The repository CSVs, not the published `irw_meta` tables, are the `declared`
side, for the reason `01_metadata.R` gives at its top: the repo is what the
pipeline writes and what `upload_meta.py` ships, so a row corrected on `main`
and not yet uploaded is correct, not stale. A gate reading the published tables
would therefore fail on work that is already done.

THE RATCHET
-----------
Every check here finds existing mismatches -- that is why the review found them.
A gate that fails on all of them today is a gate that gets switched off this
afternoon, so each check's current count is recorded in
`metadata/release_gate_baseline.json` and the check fails only when its count
goes UP. Today's corpus passes; the next release that introduces a mismatch does
not. Lower a baseline whenever you fix something (`--update-baseline` writes the
current counts), and never raise one to make a release go through: that is the
one move this file exists to prevent.

PERSONAL COLUMN NAMES ARE NOT PRINTED BY DEFAULT
------------------------------------------------
The schema check's interesting output is the list of columns a table declares
and no longer has, and five of those names in October 2026 were the names of
personal fields a correction had removed. Naming them in a CI log, a PR comment
or a committed artifact re-publishes the thing the correction removed, in a
second place. So the default output gives counts and table names and withholds
the column names; `--show-removed-columns` prints them for someone working the
queue locally. The same reasoning is why this script writes no file of its own.

EXIT CODES
    0  no check is above its baseline
    1  at least one is
    2  a source could not be read or parsed. An unreadable source is a failure,
       not a pass: the cheapest way to make a comparison green is to compare
       nothing (the floor `check_config_parity.py` has, for the same reason).

USAGE
    python3 metadata/check_release_consistency.py
    python3 metadata/check_release_consistency.py --json
    python3 metadata/check_release_consistency.py --only schema,counts
    python3 metadata/check_release_consistency.py --show-removed-columns
    python3 metadata/check_release_consistency.py --update-baseline

Network: one listing per family dataset plus one `/variables` call per table
whose declared column count disagrees with the live one. No credentials, no
data export, nothing against the 200 GB quota.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_config_parity as ccp  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
META = REPO / "metadata"
BASELINE = META / "release_gate_baseline.json"

API = "https://redivis.com/api/v1"
OWNER = "datapages"

#: Floors against a vacuous pass, on `check_config_parity.py`'s reasoning: a
#: catalog listing that came back short would make every table look consistent.
MIN_LIVE_TABLES = 6000
MIN_DECLARED_ROWS = 6000

#: Which declared CSV describes which family's dataset list, for the schema and
#: counts checks. Conjoint is deliberately absent: its tables carry no
#: `item`/`resp` and `conj_metadata.csv` has no `variables` column, so neither
#: check is defined for it.
FAMILIES = {
    "core": ("metadata.csv", "core"),
    "nom": ("nominal_metadata.csv", "nom"),
    "comp": ("comps_metadata.csv", "comp"),
    "sim": ("simsyn_metadata.csv", "sim"),
    "rank": ("rank_metadata.csv", "rank"),
}

#: Every family, for the "does this name still resolve to a table?" question.
#:
#: This is a SUPERSET of FAMILIES and the distinction is load-bearing. The
#: records checks ask whether a correction or a withdrawal names something the
#: catalog still serves, and conjoint tables are served -- so listing only the
#: five families above made every conjoint table look absent. That reported six
#: correction entries as unresolvable (`bankert_2023_consumer_origin`,
#: `shandler_2023_cyberterror`, `arias_2022_climate_migrants_us`,
#: `donnaloja_2022_citizenship` and the two `avina_2026_immigrant_*`) when all
#: six are live, which is the exact failure mode this gate exists to catch,
#: inverted: a record and the data agreeing, reported as a disagreement.
ALL_FAMILY_KEYS = tuple(FAMILIES) + ("conj",)


class SourceError(RuntimeError):
    """A source could not be read. Never reported as "consistent"."""


@dataclass
class LiveTable:
    name: str
    dataset: str
    num_rows: int | None
    variable_count: int | None
    hash: str | None


@dataclass
class Check:
    key: str
    title: str
    closes: str
    detail: str
    hits: List[str] = field(default_factory=list)
    #: Table-keyed extra facts the default output withholds (see the docstring).
    withheld: Dict[str, List[str]] = field(default_factory=dict)
    #: Tables the check could not decide about. Printed, never counted as a
    #: hit and never a reason to fail -- but a check that can see nothing must
    #: say so rather than read as a clean result.
    unknown: int = 0

    @property
    def count(self) -> int:
        return len(self.hits)


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def fetch(url: str) -> str:
    """GET a URL with curl.

    curl rather than urllib for the reason `check_client_reach.py` gives: these
    hosts publish AAAA records that do not answer from every network and
    Python's socket layer does not happy-eyeball, so a one-second request
    becomes a ten-second stall per address.
    """
    p = subprocess.run(["curl", "-sSfL", "--max-time", "120", url],
                       capture_output=True)
    if p.returncode != 0:
        tail = p.stderr.decode("utf-8", "replace").strip().splitlines()
        raise SourceError(f"GET {url.split('?')[0]} failed: "
                          f"{tail[-1] if tail else f'curl exit {p.returncode}'}")
    return p.stdout.decode("utf-8", "replace")


def _as_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def live_tables(dataset: str) -> List[LiveTable]:
    """Every table in one published dataset.

    Paginates with `pageToken`, which this endpoint honours -- unlike the rows
    endpoint, where `pageToken`, `startIndex`, `offset` and a `Range: rows=`
    header are all accepted and silently ignored (verified three ways during the
    2026-10 review). Listings are the reason this gate can be corpus-wide and
    still cost nothing.
    """
    out: List[LiveTable] = []
    token: str | None = None
    while True:
        url = f"{API}/datasets/{OWNER}.{dataset}/tables?maxResults=100"
        if token:
            url += "&pageToken=" + urllib.parse.quote(token)
        try:
            payload = json.loads(fetch(url))
        except json.JSONDecodeError as exc:
            raise SourceError(f"{dataset} table listing was not JSON ({exc})") from exc
        results = payload.get("results")
        if not isinstance(results, list):
            raise SourceError(f"{dataset} table listing carried no results array")
        for row in results:
            name = row.get("name")
            if not isinstance(name, str):
                continue
            hashed = row.get("hash")
            out.append(LiveTable(name, dataset, _as_int(row.get("numRows")),
                                 _as_int(row.get("variableCount")),
                                 hashed if isinstance(hashed, str) else None))
        token = payload.get("nextPageToken")
        if not token:
            return out


def live_variables(dataset: str, table: str) -> List[str]:
    """One table's live column names, from the schema endpoint.

    Schema only. This is the endpoint the review used to establish R-01 without
    retrieving a single personal value, and the same discipline applies here.
    """
    url = f"{API}/tables/{OWNER}.{dataset}.{table}/variables?maxResults=500"
    payload = json.loads(fetch(url))
    return [v["name"] for v in payload.get("results", []) if "name" in v]


def _shown(path: Path) -> str:
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def read_csv_rows(path: Path) -> List[dict]:
    if not path.exists():
        raise SourceError(f"{_shown(path)} is missing")
    try:
        with path.open(newline="", encoding="utf-8-sig") as fh:
            return list(csv.DictReader(fh))
    except (OSError, csv.Error) as exc:
        raise SourceError(f"{_shown(path)} is unreadable ({exc})") from exc


def declared_datasets() -> Dict[str, List[str]]:
    """The family dataset lists, from the one file that owns them."""
    try:
        return ccp.parse_pipeline_config(META / "redivis_config.R")
    except ccp.ParseError as exc:
        raise SourceError(f"redivis_config.R could not be parsed ({exc})") from exc


def split_variables(cell: str | None) -> List[str]:
    """`metadata.csv` stores a column list as `a| b| c`, lowercased."""
    return [part.strip() for part in (cell or "").split("|") if part.strip()]


def _num(cell: str | None) -> float | None:
    try:
        return float(cell)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_schema(declared: Dict[str, dict], live: Dict[str, LiveTable],
                 live_ds: Dict[str, str]) -> Check:
    chk = Check("schema", "declared column lists that the data no longer has",
                "R-11, R-01 (second exposure path)",
                "a table's published `variables` string names columns the live "
                "table does not have, so the catalog describes a schema that was "
                "replaced -- and where the replacement removed personal fields, "
                "republishes their names")
    suspects = []
    for name, row in declared.items():
        lt = live.get(name)
        if lt is None or lt.variable_count is None:
            continue
        if len(split_variables(row.get("variables"))) != lt.variable_count:
            suspects.append(name)
    #: A count mismatch is cheap and corpus-wide; it is also only a hint, since
    #: a rename keeps the count. Only the mismatching tables pay for a schema
    #: call, which is what keeps this check affordable at 6,700 tables.
    for name in sorted(suspects):
        try:
            names_live = {n.lower() for n in live_variables(live_ds[name], name)}
        except (SourceError, json.JSONDecodeError, KeyError):
            continue
        gone = sorted(set(split_variables(declared[name].get("variables"))) - names_live)
        if gone:
            chk.hits.append(name)
            chk.withheld[name] = gone
    return chk


def check_counts(declared: Dict[str, dict], live: Dict[str, LiveTable]) -> Check:
    chk = Check("counts", "published counts the table cannot support",
                "R-13, R-04",
                "`n_responses`, `n_items` or `n_participants` exceeds the number "
                "of rows the live table has -- impossible for a long-format table "
                "under the site\'s own definitions, so the row was computed "
                "against a table that has since been replaced")
    #: Every bound here is against `numRows` and never against `n_responses`,
    #: because `n_responses` counts rows with a non-null `resp` while
    #: `n_participants` and `n_items` are distinct-value counts over ALL rows.
    #: 310 core tables have a string-typed `resp` and null-`resp` rows are legal
    #: data (`01_metadata.R`, the `count_resp_via_query` comment), so
    #: `n_participants > n_responses` is ordinary rather than impossible -- it
    #: fired on 29 Chilean and Mexican survey tables when this check was first
    #: written, every one of them correct.
    for name, row in sorted(declared.items()):
        lt = live.get(name)
        if lt is None or lt.num_rows is None:
            continue
        for col in ("n_responses", "n_items", "n_participants"):
            value = _num(row.get(col))
            if value is not None and value > lt.num_rows:
                chk.hits.append(f"{name}: {col} {value:.0f} > numRows {lt.num_rows}")
                break
    return chk


#: The columns `datastandard.md` defines as indexing a repeated measurement,
#: plus `date`. Deliberately the same list `irw_validate`'s occasion_columns()
#: and the two clients' long2resp() use, so "this repeat is explained" means
#: the same thing in the catalog, the validator and the reshape.
OCCASION_COLUMNS = ("rater", "wave", "timepoint", "trialnum", "trial", "order",
                    "session", "occasion", "period", "block", "subtest", "date")


def _explains_a_repeat(variables: str | None) -> bool:
    cols = split_variables(variables)
    return any(c in OCCASION_COLUMNS or c.startswith("trial_") for c in cols)


def check_unexplained_repeats(declared: Dict[str, dict]) -> Check:
    chk = Check("unexplained-repeats",
                "tables that must hold duplicate id-item rows nothing explains",
                "R-21",
                "`density` above 1 is proof by pigeonhole that an id-item pair "
                "repeats -- there are more responses than person-item cells -- "
                "and the published column list names no occasion column and no "
                "`date` to key those repeats on, so either the row is stale or "
                "the table holds duplicates that are a defect")
    #: Query-free on purpose: this is arithmetic on the published row, so it
    #: costs nothing at 6,720 tables and runs in the same pass as the rest.
    #:
    #: It fills the hole check_counts cannot reach. That check bounds every
    #: count ABOVE, by numRows, which catches a count that grew too large and
    #: is blind to one that stayed too small -- and a stale `n_participants` is
    #: always too small, because tables gain respondents. On 2026-10-25 all 68
    #: hits had a correct `n_responses` and 27 had an `n_participants` wrong by
    #: up to 5.4x (`sris_silvia2022`, 221 published against 1,192 live), so the
    #: counts gate passed every one of them.
    #:
    #: Above 1 is NOT itself a defect: 743 tables are, and 705 of them say why
    #: with an occasion column. Only the silent ones are listed.
    for name, row in sorted(declared.items()):
        density = _num(row.get("density"))
        if density is None or density <= 1:
            continue
        if _explains_a_repeat(row.get("variables")):
            continue
        chk.hits.append(f"{name}: density {density:.4f}")
    return chk


def check_freshness(declared: Dict[str, dict], live: Dict[str, LiveTable],
                    recorded_hash: Dict[str, str]) -> Check:
    chk = Check("freshness", "rows computed against a table that has since changed",
                "R-13, R-04",
                "the live table's content hash is not the hash that was in place "
                "when its metadata row was computed, so every derived number in "
                "that row -- `n_items`, `density`, the item statistics -- is a "
                "statement about a previous version of the table")
    #: Hash, not timestamp. Redivis resets every table's `updatedAt` whenever
    #: the draft it sits in is touched (ARCHITECTURE.md section 4), which on
    #: 2026-10-24 put all 1,031 tables of shards 7 and 8 in the same month and
    #: would make a timestamp comparison call 6,463 of 6,720 rows stale -- a
    #: number nobody can act on, from a signal that is not measuring staleness.
    #: A table whose hash was never recorded is reported as UNKNOWN, not as
    #: stale: `metadata_refresh_log.csv` only gained the column in October 2026
    #: and fills in as the rolling refresh reaches each table.
    for name in sorted(declared):
        lt = live.get(name)
        if lt is None:
            continue
        was = recorded_hash.get(name)
        if not was or not lt.hash:
            chk.unknown += 1
            continue
        if was != lt.hash:
            chk.hits.append(name)
    return chk


def check_corrections_pinned(changes: List[dict]) -> Check:
    chk = Check("corrections-pinned", "corrections that name no release",
                "R-12",
                "the corrections policy promises every fix names the version "
                "carrying it, and `red_up/README.md` says the `irw_version` is "
                "the first manifest version carrying the new shard tag")
    for row in changes:
        if not (row.get("irw_version") or "").strip():
            table = (row.get("table") or "?").strip()
            issue = (row.get("issue") or "").strip()
            chk.hits.append(f"{table}{f' ({issue})' if issue else ''}")
    return chk


def check_corrections_resolve(changes: List[dict], live_names: set[str],
                              withdrawn: set[str]) -> Check:
    chk = Check("corrections-resolve", "corrections naming a table nothing serves",
                "R-16",
                "an identifier in the correction log that is not live, has no "
                "`replaced_by` that is live, and is not in the withdrawal "
                "ledger, is a correction a reader cannot follow to any table")
    #: Successors are collected per TABLE and not per row. A table usually has
    #: several correction entries and only the last one names the successor:
    #: `nba_2012-2018` has an ordinary correction from IRW 470 with an empty
    #: `replaced_by` and a retirement from 2026-10-01 naming
    #: `fivethirtyeight_nba_1946_2023`, which is live. Reading rows
    #: independently reported the first of those as unresolvable while the
    #: answer sat two hundred rows below it.
    successors: Dict[str, set[str]] = {}
    for row in changes:
        table = (row.get("table") or "").strip()
        successor = (row.get("replaced_by") or "").strip()
        if table and successor:
            successors.setdefault(table, set()).add(successor)
    seen: set[str] = set()
    for row in changes:
        table = (row.get("table") or "").strip()
        if not table or table in seen or table in live_names or table in withdrawn:
            continue
        seen.add(table)
        named = sorted(successors.get(table, ()))
        if any(s in live_names for s in named):
            continue
        chk.hits.append(table + (f" -> {', '.join(named)} (also absent)" if named else ""))
    return chk


def check_withdrawals_live(ledger: List[dict], live_names: set[str]) -> Check:
    chk = Check("withdrawals-live", "wholly withdrawn tables still in the release",
                "R-10",
                "the ledger records the table as withdrawn and the current "
                "release still serves it. A withdrawal that does not reach a "
                "consumer is not a withdrawal (#51)")
    for row in ledger:
        if (row.get("kind") or "").strip() != "whole":
            continue
        table = (row.get("table") or "").strip()
        if table and table in live_names:
            chk.hits.append(f"{table} ({(row.get('reason') or '?').strip()})")
    return chk


def check_withdrawals_records(ledger: List[dict], surfaces: Dict[str, set[str]],
                              live_names: set[str]) -> Check:
    chk = Check("withdrawals-records", "withdrawn tables still described by the records",
                "R-14, R-27",
                "withdrawals reach metadata, tags and collections but not "
                "`biblio` or `itemtext_metadata`, so a retired table keeps its "
                "citation and its item text is still described under the "
                "retired name")
    for row in ledger:
        if (row.get("kind") or "").strip() != "whole":
            continue
        table = (row.get("table") or "").strip()
        if not table:
            continue
        #: An item-text withdrawal retires the `*__items` table, not the
        #: response table, so the response table's own records stay. Only
        #: `itemtext_metadata` is checked for those, against the base name it
        #: keys on.
        if table.endswith("__items"):
            base = table[: -len("__items")]
            where = ["itemtext_metadata"] if base in surfaces["itemtext_metadata"] else []
        else:
            #: A table the ledger calls withdrawn and the catalog still serves
            #: is a CLEAN REBUILD in every case checked during the 2026-10
            #: review -- the withdrawal happened, the table came back corrected,
            #: and nothing updated the ledger. Its biblio and tags rows are then
            #: CORRECT, and flagging them would report 184 right answers as
            #: wrong. The stale thing is the ledger row, which is what
            #: `withdrawals-live` reports. So the records are only checked for a
            #: table that is genuinely gone.
            if table in live_names:
                continue
            where = [s for s in ("biblio", "tags", "itemtext_metadata")
                     if table in surfaces[s]]
        if where:
            chk.hits.append(f"{table}: still in {', '.join(where)}")
    return chk


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def gather(only: Sequence[str] | None) -> List[Check]:
    cfg = declared_datasets()
    live: Dict[str, LiveTable] = {}
    live_ds: Dict[str, str] = {}
    live_names: set[str] = set()
    schema_keys = {FAMILIES[k][1] for k in FAMILIES}
    for cfg_key in ALL_FAMILY_KEYS:
        cfg_key = FAMILIES[cfg_key][1] if cfg_key in FAMILIES else cfg_key
        for dataset in cfg.get(cfg_key, []):
            for lt in live_tables(dataset):
                live_names.add(lt.name)
                if cfg_key not in schema_keys:
                    continue
                #: Core shards are searched newest-first and the first match
                #: wins (ARCHITECTURE.md section 2), so a name in two shards
                #: resolves to its newest copy -- which is the one a declared
                #: row is a statement about.
                live[lt.name] = lt
                live_ds[lt.name] = dataset
    if len(live_names) < MIN_LIVE_TABLES:
        raise SourceError(f"the catalog listed {len(live_names)} tables, below the "
                          f"floor of {MIN_LIVE_TABLES}; treating as unread rather "
                          f"than reporting every record consistent")

    declared: Dict[str, dict] = {}
    for filename, _ in FAMILIES.values():
        for row in read_csv_rows(META / filename):
            name = (row.get("table") or "").strip()
            if name:
                declared[name] = row
    if len(declared) < MIN_DECLARED_ROWS:
        raise SourceError(f"the declared CSVs held {len(declared)} rows, below the "
                          f"floor of {MIN_DECLARED_ROWS}")

    recorded_hash: Dict[str, str] = {}
    for row in read_csv_rows(META / "metadata_refresh_log.csv"):
        name = (row.get("table") or "").strip()
        value = (row.get("hash") or "").strip()
        if name and value and value != "NA":
            recorded_hash[name] = value

    changes = read_csv_rows(META / "table_changes.csv")
    ledger = read_csv_rows(REPO / "itemtext" / "withdrawals.csv")
    withdrawn = {(r.get("table") or "").strip() for r in ledger}
    surfaces = {
        "biblio": {(r.get("table") or "").strip() for r in read_csv_rows(META / "biblio.csv")},
        "tags": {(r.get("table") or "").strip() for r in read_csv_rows(META / "tags.csv")},
        "itemtext_metadata": {(r.get("table") or "").strip()
                              for r in read_csv_rows(META / "itemtext_metadata.csv")},
    }

    checks = [
        check_counts(declared, live),
        check_unexplained_repeats(declared),
        check_schema(declared, live, live_ds) if _wanted("schema", only) else None,
        check_freshness(declared, live, recorded_hash),
        check_corrections_pinned(changes),
        check_corrections_resolve(changes, live_names, withdrawn),
        check_withdrawals_live(ledger, live_names),
        check_withdrawals_records(ledger, surfaces, live_names),
    ]
    out = [c for c in checks if c is not None and _wanted(c.key, only)]
    return out


def _wanted(key: str, only: Sequence[str] | None) -> bool:
    return not only or key in only


def read_baseline() -> Dict[str, int]:
    if not BASELINE.exists():
        return {}
    try:
        payload = json.loads(BASELINE.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceError(f"{BASELINE.name} is unreadable ({exc})") from exc
    counts = payload.get("counts", {})
    if not isinstance(counts, dict):
        raise SourceError(f"{BASELINE.name} has no counts object")
    return {k: int(v) for k, v in counts.items() if isinstance(v, int)}


DEFAULT_BASELINE_COMMENT = (
    "Accepted mismatch counts for metadata/check_release_consistency.py. A check fails "
    "when its count goes UP. Lower an entry when you fix something; never raise one to "
    "let a release through.")


def write_baseline(checks: Iterable[Check]) -> None:
    """Rewrite the baseline counts, keeping whatever the file says about them.

    `_comment` is preserved rather than regenerated: the counts are mechanical
    and the note beside them is not -- it is where a reader finds out WHY a
    baseline is 0 or 92, which is the only thing that makes raising one feel
    like the mistake it is. An earlier version overwrote the note on every
    `--update-baseline`, which silently deleted the explanation each time the
    numbers moved.
    """
    existing = {}
    if BASELINE.exists():
        try:
            existing = json.loads(BASELINE.read_text())
        except (OSError, json.JSONDecodeError):
            existing = {}
    comment = existing.get("_comment") or DEFAULT_BASELINE_COMMENT
    BASELINE.write_text(json.dumps({
        "_comment": comment,
        "updated": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        "counts": {c.key: c.count for c in checks},
    }, indent=2) + "\n")


def report(checks: List[Check], baseline: Dict[str, int], show_columns: bool) -> int:
    worst = 0
    for chk in checks:
        allowed = baseline.get(chk.key)
        over = allowed is not None and chk.count > allowed
        if allowed is None and chk.count:
            over = True
        status = "FAIL" if over else ("ok" if not chk.count else "held")
        budget = "no baseline recorded" if allowed is None else f"baseline {allowed}"
        unknown = f", {chk.unknown} undecidable" if chk.unknown else ""
        print(f"[{status:4}] {chk.key}: {chk.count} ({budget}{unknown}) -- {chk.title}")
        if chk.count:
            print(f"         closes {chk.closes}: {chk.detail}")
            shown = chk.hits if over else chk.hits[:10]
            for hit in shown:
                extra = ""
                if chk.withheld.get(hit) is not None:
                    gone = chk.withheld[hit]
                    extra = (f": {', '.join(gone)}" if show_columns
                             else f": {len(gone)} declared column(s) absent from the "
                                  f"data (--show-removed-columns to name them)")
                print(f"         - {hit}{extra}")
            if not over and len(chk.hits) > len(shown):
                print(f"         ... and {len(chk.hits) - len(shown)} more")
        if over:
            worst = 1
    print()
    print("consistent with the recorded baselines" if not worst else
          "a record disagrees with the published data; do not publish until it is "
          "fixed or the baseline is deliberately lowered")
    return worst


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--only", help="comma-separated check keys to run")
    ap.add_argument("--show-removed-columns", action="store_true",
                    help="name the declared columns a table no longer has. Off by "
                         "default because some of those names are the personal "
                         "fields a correction removed")
    ap.add_argument("--update-baseline", action="store_true",
                    help="record the current counts as the accepted baseline")
    args = ap.parse_args(argv)
    only = [k.strip() for k in args.only.split(",")] if args.only else None

    try:
        checks = gather(only)
        baseline = read_baseline()
    except SourceError as exc:
        print(f"could not run: {exc}", file=sys.stderr)
        return 2

    if args.update_baseline:
        if only:
            print("refusing to write a baseline from a partial run (--only)", file=sys.stderr)
            return 2
        write_baseline(checks)
        print(f"wrote {BASELINE.relative_to(REPO)}: "
              + ", ".join(f"{c.key}={c.count}" for c in checks))
        return 0

    if args.json:
        print(json.dumps({
            "baseline": baseline,
            "checks": [{"key": c.key, "title": c.title, "closes": c.closes,
                        "count": c.count, "unknown": c.unknown,
                        "over_baseline": c.count > baseline.get(c.key, -1),
                        "hits": c.hits if args.show_removed_columns else
                                [h.split(":")[0] for h in c.hits]}
                       for c in checks],
        }, indent=2))
        return 1 if any(c.count > baseline.get(c.key, -1) for c in checks) else 0

    return report(checks, baseline, args.show_removed_columns)


if __name__ == "__main__":
    sys.exit(main())
