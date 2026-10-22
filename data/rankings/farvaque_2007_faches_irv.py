#!/usr/bin/env python3
##Instant-runoff voting experiment at the 2007 French presidential election -> one IRW rankings table.
##Source: Farvaque, E., Jayet, H. and Ragot, L. "Quel mode de scrutin pour quel << vainqueur >> ?
##Une experience sur le vote preferentiel transferable", Revue d'economie politique 119(2), 2009,
##221-246 (doi 10.3917/redp.192.0221). Data deposited by Theo Delemazure as
##doi:10.5281/zenodo.15290476 (version record 15290477), ODbL 1.0 -- the licence the Voter
##Autrement ballots are already in IRW under (Ben, 2026-10-15).
##
##The experiment ran beside the real first round (22 April 2007) in Faches-Thumesnil, northern
##France: voters leaving two polling stations were invited to rank the twelve official candidates
##under Hare's instant-runoff method. Files read: rankings.csv (one row per ballot, one column per
##candidate holding the position, 0 = not ranked), voters.csv (the ballot's polling station),
##candidates.csv (official first-round scores; not carried into the table).
##
##Layout: id = the ballot re-keyed 1..893 in file order, task = 1, item = the candidate code
##(README, "Candidate codes": the twelve printed names sorted case-insensitively, names never
##stored), resp = the position as marked. A few ballots give two candidates the same position;
##those are ties, kept as recorded (Ben, 2026-10-15), and counted in the design record's evidence
##(n_tied_ballots) rather than as duplicate marks, which are a different thing. No ballot is empty.
##cov_polling_station is bureau_1 or bureau_6 from voters.csv.
##
##Usage: python3 farvaque_2007_faches_irv.py build <raw dir> <out dir>
##Table: farvaque_2007_faches_irv.
from __future__ import annotations

import csv
import sys
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

TABLE = "farvaque_2007_faches_irv"
COLLECTION = "10.5281/zenodo.15290476"
BASE = "https://zenodo.org/api/records/15290477/files/{name}/content"
FILES = ("rankings.csv", "voters.csv")


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def build(raw_dir: Path, out_dir: Path) -> None:
    paths = {n: fetch(BASE.format(name=n), raw_dir / n) for n in FILES}
    ranks = read_csv(paths["rankings.csv"])
    voters = {r["id"]: r for r in read_csv(paths["voters.csv"])}
    names = [c for c in ranks[0] if c != "id"]
    codes = code_candidates(names)
    rows, empty, tied = [], 0, 0
    for i, r in enumerate(ranks, start=1):
        station = (voters.get(r["id"], {}).get("polling_station") or "").strip()
        marks = []
        for name in names:
            v = (r[name] or "").strip()
            if not v or int(v) < 1:
                continue
            marks.append({"id": i, "task": 1, "item": codes[name], "resp": int(v),
                          "cov_polling_station": station})
        if not marks:
            empty += 1
            continue
        positions = [m["resp"] for m in marks]
        tied += len(positions) != len(set(positions))
        rows.extend(marks)
    write_table(out_dir / f"{TABLE}.csv", rows)
    counts = design_counts(rows)
    upsert_design({
        "table": TABLE, "source_file": "rankings.csv", "collection": COLLECTION,
        "jurisdiction": "Faches-Thumesnil, France (voting experiment at two polling stations)",
        "date": "2007-04-22",
        "office": ("President of France, first round, 22 April 2007 (experimental instant-runoff ballot "
                   "offered to voters leaving the polling station; 12 official candidates)"),
        "method": "irv", "seats": "na", **counts,
        "n_ballots_cast": len(ranks), "n_ballots_eligible_est": len(ranks),
        "write_in_allowed": "no", "candidate_order": "unknown",
        "evidence": (f"Zenodo {COLLECTION} (version record 15290477) files rankings.csv and voters.csv, "
                     f"ODbL 1.0; paper Farvaque, Jayet & Ragot 2009, Revue d'economie politique 119(2) "
                     f"221-246 (10.3917/redp.192.0221); date is the official first round the experiment ran "
                     f"alongside; seats na (an experiment, not a count); 12 candidates were offered and all 12 "
                     f"received a mark; {empty} empty ballots; n_tied_ballots {tied} (two candidates at one "
                     f"position, kept as recorded); candidate_order not documented; counts computed by "
                     f"farvaque_2007_faches_irv.py"),
    })
    print(f"{TABLE}: {len(rows)} rows, {counts['n_ballots_with_marks']} ballots, "
          f"{counts['n_candidates']} candidates, {tied} tied ballots")


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] != "build":
        print("usage: farvaque_2007_faches_irv.py build <raw dir> <out dir>")
        return 2
    build(Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
