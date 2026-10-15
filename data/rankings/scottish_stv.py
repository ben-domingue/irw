#!/usr/bin/env python3
##Scottish council elections (STV, 2007-2022), full preference profiles -> IRW rankings tables.
##Source: the `scot-elex` repository (MGGG Redistricting Lab, https://github.com/mggg/scot-elex),
##CSV conversions of the 1,100 BLT ballot files David McCune assembled from the councils'
##published preference profiles (Scottish local government elections 2007, 2012, 2017, 2022; the
##same data Denis Mollison hosts at macs.hw.ac.uk/~denis/stv_elections/). Files read: one
##`<n>_cands/<council>_<year>_ward<k>.csv` per table, pinned to commit
##de9f8e30c257fa85bfc3c9252e974a12e8faae7b. The repository states no data licence; the council
##releases are public election records (licence to confirm: see candidates.csv).
##File layout (repo README): row 1 = `n_candidates,n_seats`; then one row per DISTINCT ranking,
##`count,c_i,c_j,...` (candidate numbers in preference order); then one row per candidate
##(`"Candidate k","Name","Party"`); last row the ward name. A weighted profile, so this script
##follows rule R5 (Ben, 2026-10-15) by EXPANDING: each distinct ranking becomes `count` ballots with their own `id`
##(the family's `id` is one ballot everywhere else, n_ballots_with_marks must equal the id
##count, and a ward is at most a few tens of thousands of ballots). No cov_weight column.
##Candidates are coded c01.. alphabetically on the printed name (names and parties not stored).
##Scottish STV ballots have no write-ins and no overvotes in the published profiles.
##
##Usage:
##  python3 scottish_stv.py build <raw dir> <out dir> <repo path> [...]
##    e.g. 4_cands/aberdeen_2017_ward11.csv  -> table rcv_aberdeen_20170504_ward11
##Table names: rcv_<council>_<yyyymmdd>_ward<k> (polling day from ELECTION_DATE).
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

COMMIT = "de9f8e30c257fa85bfc3c9252e974a12e8faae7b"
RAW = f"https://raw.githubusercontent.com/mggg/scot-elex/{COMMIT}/{{path}}"
COLLECTION = f"https://github.com/mggg/scot-elex/tree/{COMMIT[:7]}"
ELECTION_DATE = {"2007": "2007-05-03", "2012": "2012-05-03", "2017": "2017-05-04", "2022": "2022-05-05"}
NAME = re.compile(r"^(?P<council>[a-z_]+)_(?P<year>\d{4})_ward(?P<ward>\d+)\.csv$")


def table_name(path: str) -> str:
    m = NAME.match(Path(path).name)
    if not m:
        raise ValueError(f"not a <council>_<year>_ward<k>.csv path: {path}")
    council = m["council"].replace("_", "")
    return f"rcv_{council}_{ELECTION_DATE[m['year']].replace('-', '')}_ward{m['ward']}"


def parse(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    n_cands, n_seats = int(rows[0][0]), int(rows[0][1])
    ballots, names, ward = [], {}, ""
    for r in rows[1:]:
        cells = [c for c in r if c != ""]
        if cells[0].startswith("Candidate "):
            names[int(cells[0].split()[1])] = cells[1].strip()
        elif cells[0].isdigit():
            ballots.append((int(cells[0]), [int(c) for c in cells[1:]]))
        else:
            ward = cells[0].strip()
    if len(names) != n_cands:
        raise ValueError(f"{path}: header says {n_cands} candidates, {len(names)} listed")
    return n_cands, n_seats, ballots, names, ward


def build(raw_dir: Path, out_dir: Path, paths: list[str]) -> int:
    for p in paths:
        t = table_name(p)
        src = fetch(RAW.format(path=p), raw_dir / p)
        n_cands, n_seats, ballots, names, ward = parse(src)
        codes = code_candidates(names.values())
        out, bid = [], 0
        for count, order in ballots:
            for _ in range(count):
                bid += 1
                for pos, cand in enumerate(order, start=1):
                    out.append({"id": bid, "task": 1, "item": codes[names[cand]], "resp": pos})
        counts = design_counts(out)
        m = NAME.match(Path(p).name)
        council = m["council"].replace("_", " ").title()
        design = {"table": t, "source_file": p, "collection": COLLECTION,
                  "jurisdiction": f"{council} Council, Scotland", "date": ELECTION_DATE[m["year"]],
                  "office": f"Ward {m['ward']} ({ward}), councillors", "method": "stv", "seats": n_seats,
                  **counts, "n_ballots_cast": bid, "n_ballots_eligible_est": bid,
                  "write_in_allowed": "no", "candidate_order": "fixed",
                  "evidence": f"scot-elex {p} at commit {COMMIT[:7]} (McCune BLT files from the council's published "
                              f"preference profile); seats from the file header; weighted profile expanded to one id "
                              f"per ballot (rule R5, Ben 2026-10-15); the profile holds only ballots with at least one preference, so "
                              f"n_ballots_cast = n_ballots_with_marks; candidates listed in surname order as on the "
                              f"statutory ballot paper (fixed); no write-ins on Scottish council ballots; counts "
                              f"computed by scottish_stv.py"}
        write_table(out_dir / f"{t}.csv", out)
        upsert_design(design)
        print(f"{t}: {len(ballots)} distinct rankings -> {bid} ballots, {n_cands} candidates, {n_seats} seats, "
              f"{len(out)} rows")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        return build(Path(argv[1]), Path(argv[2]), argv[3:])
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
