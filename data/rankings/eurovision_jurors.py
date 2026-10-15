#!/usr/bin/env python3
##Eurovision Song Contest individual juror rankings -> IRW rankings tables.
##Source: MIRoVision, "Measuring the Eurovision Song Contest: A Living Dataset for
##Real-World MIR" (Burgoyne, Spijkervet & Baker, ISMIR 2023). Zenodo
##doi:10.5281/zenodo.10265412, CC BY 4.0; code and data also at
##https://github.com/Amsterdam-Music-Lab/mirovision (MIT). File read:
##data/CSV/jurors.csv at commit d70e25d4871b84d1502dfe65c9713e217bfdd716 (2023-11-09),
##which MIRoVision compiled from the per-juror breakdowns the EBU publishes on
##eurovision.tv since 2016. One row per (year, round, voting country, performing
##country) with columns A..E holding the rank each of that country's five anonymous
##jurors gave the performance. Jurors rank every song in a show except their own
##country's (so there is no row for it); NA marks a juror who did not vote (2016
##semi-final 1, one juror). The 2022 files omit the six juries whose votes the EBU
##annulled, so n_ballots_cast is the juries MIRoVision carries, not the juries seated.
##No codebook ships beyond the repository README.
##
##Usage:
##  python3 eurovision_jurors.py build <raw dir> <out dir> --all
##  python3 eurovision_jurors.py build <raw dir> <out dir> eurovision_2022_final [...]
##
##`build` downloads jurors.csv into <raw dir> if absent (untrusted data; nothing in
##it is executed), writes one table per show to <out dir>, and upserts each table's
##row in design_tables.csv beside this script.
##
##Layout (data/rankings/README.md): one row per juror x ranked song.
##  id    the juror (voting country x letter), re-keyed 1..n in file order
##  task  1 throughout (one show per table)
##  item  the performing country's ISO code as it appears in the file; songs are not
##        people, so the option label is kept (README, "Candidate codes")
##  resp  the rank given, 1 = best, as recorded
##  cov_jury_country  the voting country (ISO code), cov_juror  the letter A..E
##Table name: eurovision_<year>_<sf1|sf2|final>.
from __future__ import annotations

import csv
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE / "design_tables.csv"
COMMIT = "d70e25d4871b84d1502dfe65c9713e217bfdd716"
URL = f"https://raw.githubusercontent.com/Amsterdam-Music-Lab/mirovision/{COMMIT}/data/CSV/jurors.csv"
COLLECTION = "10.5281/zenodo.10265412"
ROUND = {"semi-final-1": "sf1", "semi-final-2": "sf2", "final": "final"}
JURORS = "ABCDE"


def table_name(year: str, rnd: str) -> str:
    return f"eurovision_{year}_{ROUND[rnd]}"


def fetch(dest: Path) -> None:
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def read_shows(src: Path) -> dict[tuple[str, str], list[dict]]:
    shows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with open(src, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            shows[(row["year"], row["round"])].append(row)
    return shows


def convert(year: str, rnd: str, rows: list[dict]) -> tuple[list[dict], dict]:
    """One show -> (long rows, design record)."""
    juries = list(dict.fromkeys(r["from_country"] for r in rows))  # file order
    songs = {r["to_country"] for r in rows}
    out, with_marks, n_jurors = [], 0, 0
    for jury in juries:
        sub = [r for r in rows if r["from_country"] == jury]
        for letter in JURORS:
            n_jurors += 1
            jid = n_jurors
            marked = 0
            for r in sub:
                v = r[letter]
                if v in ("", "NA"):
                    continue
                out.append({"id": jid, "task": 1, "item": r["to_country"], "resp": int(v),
                            "cov_jury_country": jury, "cov_juror": letter})
                marked += 1
            with_marks += marked > 0
    n_pos = max(r["resp"] for r in out)
    design = {"table": table_name(year, rnd), "source_file": "jurors.csv", "collection": COLLECTION,
              "jurisdiction": "Eurovision Song Contest", "date": "unknown",
              "office": f"{year} {rnd} jury ranking", "method": "jury", "seats": "na",
              "n_positions": n_pos, "n_candidates": len(songs),
              "n_ballots_cast": n_jurors, "n_ballots_eligible_est": n_jurors, "n_ballots_with_marks": with_marks,
              "n_duplicate_marks": 0, "n_overvotes": 0, "n_writeins": 0,
              "write_in_allowed": "no", "candidate_order": "fixed",
              "evidence": f"MIRoVision data/CSV/jurors.csv at commit {COMMIT[:7]} (Zenodo {COLLECTION}); jurors "
                          f"rank every song but their own country's, so a juror's positions run 1..{n_pos} or "
                          f"1..{n_pos - 1}; songs shown in the published running order (candidate_order fixed); "
                          f"no seats (a jury ranking, not an election); counts computed by eurovision_jurors.py"}
    return out, design


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


def build(raw_dir: Path, out_dir: Path, tables: list[str] | None) -> int:
    src = raw_dir / "jurors.csv"
    fetch(src)
    out_dir.mkdir(parents=True, exist_ok=True)
    shows = read_shows(src)
    wanted = {table_name(y, r): (y, r) for y, r in shows}
    for t in tables or sorted(wanted):
        if t not in wanted:
            print(f"{t}: no such show in jurors.csv", file=sys.stderr)
            return 1
        year, rnd = wanted[t]
        rows, design = convert(year, rnd, shows[(year, rnd)])
        with open(out_dir / f"{t}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        upsert_design(design)
        print(f"{t}: {design['n_ballots_cast']} jurors, {design['n_ballots_with_marks']} with marks, "
              f"{design['n_candidates']} songs, {len(rows)} rows")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        raw_dir, out_dir, rest = Path(argv[1]), Path(argv[2]), argv[3:]
        return build(raw_dir, out_dir, None if rest == ["--all"] else rest)
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
