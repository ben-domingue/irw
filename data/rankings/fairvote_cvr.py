#!/usr/bin/env python3
##FairVote ranked-choice cast vote records -> IRW rankings tables.
##Source: three Harvard Dataverse collections deposited by FairVote, all CC0 1.0,
##no restricted files, no terms:
##  doi:10.7910/DVN/AMK8PJ  single-winner RCV (instant runoff)   607 files
##  doi:10.7910/DVN/STVUET  proportional RCV (STV)                 40 files
##  doi:10.7910/DVN/04LOQX  sequential RCV                         10 files
##Every file is one contest: one row per ballot, columns rank1..rankK holding the
##candidate's name as printed or one of the tokens skipped / overvote / writein
##(spelling varies: writein, Write-in, Write-In), plus in some files ballot-level
##columns (ballotID, precinct, ward, Ballot.Style, ballot_type, countingGroup,
##district, votingLocation, tally_type, source_file). The deposits ship no codebook;
##the token vocabulary is what was observed across the files read (KNOWN_TOKENS),
##and any other lowercase single-word value is reported as a suspected token.
##
##Usage:
##  python3 fairvote_cvr.py manifest                   # refresh fairvote_manifest.csv from the Dataverse API
##  python3 fairvote_cvr.py build <raw dir> <out dir> <table> [<table> ...]
##  python3 fairvote_cvr.py build <raw dir> <out dir> --all
##
##`build` downloads each file (Dataverse tab export, by file id from the manifest)
##into <raw dir> if it is not already there, writes <out dir>/<table>.csv, and
##appends/updates the table's row in design_tables.csv beside this script. Downloads
##are untrusted data: nothing in them is executed.
##
##Layout (data/rankings/README.md): one row per ballot x marked position.
##  id    ballot, re-keyed 1..n in file order (the source's ballotID/Index is dropped)
##  task  1 throughout (one contest per table)
##  item  candidate code c01, c02, ... in case-insensitive alphabetical order of the
##        names as printed in this file; or the reserved values (write-in), (overvote)
##  resp  the position marked, 1 = first choice, as recorded; skips leave a gap
##  cov_* every other source column, snake_cased, repeated on each of the ballot's rows
##Skipped cells are not rows. A ballot with no marks has no rows; the design record
##keeps n_ballots_cast and n_ballots_with_marks. Duplicate marks (one candidate at
##two positions) are kept as two rows. Candidate names are not stored anywhere: the
##mapping is reproducible from the public file and the rule above.
from __future__ import annotations

import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "fairvote_manifest.csv"
DESIGN = HERE / "design_tables.csv"
API = "https://dataverse.harvard.edu/api"
COLLECTIONS = [("10.7910/DVN/AMK8PJ", "irv"), ("10.7910/DVN/STVUET", "stv"), ("10.7910/DVN/04LOQX", "sequential")]

##Tokens seen in rank cells, lower-cased with spaces and hyphens removed.
KNOWN_TOKENS = {"skipped": None, "undervote": None, "overvote": "(overvote)", "writein": "(write-in)"}
##Source columns that identify the ballot row or the file, not a covariate.
ID_COLS = {"ballotid", "index", "cast.vote.record", "cast_vote_record", "source_file", "id", "cvr_id"}
RANK = re.compile(r"^rank(\d+)$", re.I)

JUR = {"NewYorkCity": "nyc", "SanFrancisco": "sf", "Minneapolis": "mpls", "SanLeandro": "sanleandro",
       "PierceCounty": "pierce", "PortlandME": "portlandme", "PortlandOR": "portlandor", "TakomaPark": "takoma",
       "USVirginIslands": "usvi", "StLouisPark": "stlouispark", "RedondoBeach": "redondo",
       "WoodlandHills": "woodlandhills", "LasCruces": "lascruces", "SantaFe": "santafe", "ElkRidge": "elkridge"}
ABBREV = [("citycouncil", "council"), ("boardofeducation", "boe"), ("schoolcommittee", "school"),
          ("boroughpresident", "bp"), ("chartercommission", "charter"), ("housedistrict", "hd"),
          ("senatedistrict", "sd"), ("district", "d"), ("democratic", "dem"), ("republican", "rep"),
          ("governorlieutenantgovernor", "gov"), ("lieutenantgovernor", "ltgov"), ("councilmember", "council"),
          ("supervisor", "sup"), ("partialterm", "pt"), ("official", ""), ("citywide", ""), ("county", ""),
          ("atlarge", "al"), ("special", "sp")]


def table_name(filename: str) -> str:
    """rcv_<jurisdiction>_<yyyymmdd>_<office>, <= 40 chars, from the FairVote file name."""
    parts = filename[:-4].split("_")
    jur = JUR.get(parts[0], parts[0].lower())
    office = re.sub(r"[^a-z0-9]", "", "".join(parts[2:]).lower())
    for a, b in ABBREV:
        office = office.replace(a, b)
    name = f"rcv_{jur}_{parts[1]}_{office}"
    assert len(name) <= 40, name
    return name


def snake(col: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", col).replace(".", "_").replace(" ", "_").lower()
    return "cov_" + re.sub(r"_+", "_", s).strip("_")


# ---------------------------------------------------------------- manifest
UA = {"User-Agent": "irw-rankings/0.1 (+https://github.com/ben-domingue/irw)"}


def _open(url: str):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA))


def manifest() -> None:
    rows = []
    for doi, method in COLLECTIONS:
        with _open(f"{API}/datasets/:persistentId/?persistentId=doi:{doi}") as r:
            v = json.load(r)["data"]["latestVersion"]
        assert v["license"]["name"].startswith("CC0"), (doi, v["license"])
        for f in v["files"]:
            df = f["dataFile"]
            rows.append({"table": table_name(df["filename"]), "filename": df["filename"], "file_id": df["id"],
                         "collection": doi, "dataset_version": v["versionNumber"], "method": method,
                         "filesize": df["filesize"], "md5": df.get("md5", "")})
    names = [r["table"] for r in rows]
    assert len(names) == len(set(names)), "table-name collision"
    rows.sort(key=lambda r: r["table"])
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} files -> {MANIFEST}")


def read_manifest() -> dict:
    with open(MANIFEST, newline="") as f:
        return {r["table"]: r for r in csv.DictReader(f)}


# ---------------------------------------------------------------- build
def fetch(file_id: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    with _open(f"{API}/access/datafile/{file_id}") as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def convert(src: Path, meta: dict) -> tuple[list[dict], dict, list[str]]:
    """One FairVote tab file -> (long rows, design record, warnings)."""
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        raw = list(reader)
    rank_cols = sorted(((int(RANK.match(h).group(1)), i) for i, h in enumerate(header) if RANK.match(h)))
    assert rank_cols, f"{src.name}: no rank columns in {header}"
    cov_cols = [(snake(h), i) for i, h in enumerate(header)
                if not RANK.match(h) and h.lower() not in ID_COLS]

    def classify(v: str):
        key = re.sub(r"[\s\-_]", "", v).lower()
        if key in KNOWN_TOKENS:
            return "token", KNOWN_TOKENS[key]
        return "name", v

    names, suspects = set(), set()
    for row in raw:
        for _, i in rank_cols:
            kind, val = classify(row[i])
            if kind == "name":
                names.add(val)
                if re.fullmatch(r"[a-z]+", val):
                    suspects.add(val)
    code = {n: f"c{k:0{max(2, len(str(len(names))))}d}"
            for k, n in enumerate(sorted(names, key=lambda s: (s.casefold(), s)), 1)}

    out, with_marks, dup_marks, overvotes, writeins = [], 0, 0, 0, 0
    marked_flags = []
    for bid, row in enumerate(raw, 1):
        cov = {c: row[i] for c, i in cov_cols}
        marked, seen = 0, set()
        for pos, i in rank_cols:
            kind, val = classify(row[i])
            if kind == "token" and val is None:
                continue
            item = code[val] if kind == "name" else val
            if item == "(overvote)":
                overvotes += 1
            elif item == "(write-in)":
                writeins += 1
            if item in seen:
                dup_marks += 1
            seen.add(item)
            marked += 1
            out.append({"id": bid, "task": 1, "item": item, "resp": pos, **cov})
        with_marks += marked > 0
        marked_flags.append(marked > 0)
    # NYC's exports list every ballot of the primary, including precincts where this
    # contest was not on the ballot (D49: 213 of 312 precincts have no marked ballot).
    # n_ballots_eligible_est counts ballots whose precinct has at least one marked
    # ballot; it equals n_ballots_cast when the file has no precinct column.
    pcol = next((i for c, i in cov_cols if c in ("cov_precinct", "cov_precincts")), None)
    if pcol is None:
        eligible = len(raw)
    else:
        live = {row[pcol] for row, m in zip(raw, marked_flags) if m}
        eligible = sum(row[pcol] in live for row in raw)
    design = {"table": meta["table"], "source_file": src.name, "collection": meta["collection"],
              "jurisdiction": src.name.split("_")[0], "date": re.sub(r"(\d{4})(\d{2})(\d{2})", r"\1-\2-\3", src.name.split("_")[1]),
              "office": src.name[:-4].split("_", 2)[2], "method": meta["method"], "seats": "unknown",
              "n_positions": max(p for p, _ in rank_cols), "n_candidates": len(names),
              "n_ballots_cast": len(raw), "n_ballots_eligible_est": eligible, "n_ballots_with_marks": with_marks,
              "n_duplicate_marks": dup_marks, "n_overvotes": overvotes, "n_writeins": writeins,
              "write_in_allowed": "yes" if writeins else "unknown", "candidate_order": "unknown",
              "evidence": f"file {src.name} (Dataverse file id {meta['file_id']}, collection {meta['collection']} "
                          f"v{meta['dataset_version']}); method from the collection; counts computed by fairvote_cvr.py"}
    warn = [f"{src.name}: suspected unlisted token(s) coded as candidates: {sorted(suspects)}"] if suspects else []
    return out, design, warn


def upsert_design(record: dict) -> None:
    rows = []
    if DESIGN.exists():
        with open(DESIGN, newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["table"] != record["table"]]
    rows.append(record)
    rows.sort(key=lambda r: r["table"])
    with open(DESIGN, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(record), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def build(raw_dir: Path, out_dir: Path, tables: list[str]) -> int:
    man = read_manifest()
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for t in tables:
        meta = man[t]
        src = raw_dir / meta["filename"]
        fetch(meta["file_id"], src)
        rows, design, warnings = convert(src, meta)
        cols = list(rows[0]) if rows else ["id", "task", "item", "resp"]
        with open(out_dir / f"{t}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        upsert_design(design)
        print(f"{t}: {design['n_ballots_cast']} ballots, {design['n_ballots_with_marks']} with marks, "
              f"{design['n_candidates']} candidates, {design['n_positions']} positions, {len(rows)} rows")
        for wmsg in warnings:
            print("  WARN", wmsg)
            bad += 1
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["manifest"]:
        manifest()
        return 0
    if argv[:1] == ["build"] and len(argv) >= 4:
        raw_dir, out_dir, rest = Path(argv[1]), Path(argv[2]), argv[3:]
        tables = sorted(read_manifest()) if rest == ["--all"] else rest
        return build(raw_dir, out_dir, tables)
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
