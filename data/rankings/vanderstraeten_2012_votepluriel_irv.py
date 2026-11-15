#!/usr/bin/env python3
##Vote au pluriel 2012 (online voting experiment, French presidential election) -> one IRW rankings
##table of its instant-runoff ballots. The same voters' approval ballots are the core table
##vanderstraeten_2012_votepluriel_approval (data/laslier_french_experiments.py); id is shared.
##
##Rights: Jean-Francois Laslier, email of 2026-11-15, "You can redistribute these data sets.", in reply
##to IRW's letter (oneoff/email-drafts-2026-11-15/preflib/laslier_french_experiments.txt) about PrefLib
##00074 (and 00026, 00027/00029). The letter offered ODbL, as for the Voter Autrement Zenodo sets; he
##named no licence. Original License = Permission via Email; Derived License = ODbL 1.0. The letter's
##terms are kept: one table per experiment and ballot type, ballots numbered 1..n, candidates as codes
##(no name stored), the paper PrefLib names cited and PrefLib linked.
##
##Paper (PrefLib's required citation): Van der Straeten, K., Laslier, J.-F. & Blais, A. (2013). Vote au
##pluriel: How people vote when offered to vote under different rules. PS: Political Science & Politics
##46(2), 324-328. doi 10.1017/S1049096513000036.
##
##Source: Theo Delemazure's per-voter release of the experiment,
##https://theo.delemazure.fr/datasets/files/2012_vote_pluriel.zip (codebook main.pdf inside, 2025-07-09),
##file votes/irv.csv: one row per voter (8,078), one column per candidate holding the position, 0 = not
##ranked. The online experiment ran 2-21 April 2012, before the first round (22 April); voters had to rank
##at least three of the ten official candidates and could rank all. PrefLib 00074-00000002.soi (PrefLib-
##Data commit 03f5a88) is a weighted profile of the same ballots and is read as a cross-check only: it
##drops the 5 ballots with no ranking and cuts each ranking at its first gap or tie (keeping the
##lowest-numbered of the tied candidates), which changes 3 ballots; this file keeps the marks as recorded. Both files' SHA-256 are asserted.
##
##Layout: id = the voter re-keyed 1..8078 in the release's order (ascending voter id), the same id as in
##the approval table, so the 5 empty ballots leave 5 ids absent here; task = 1; item = candidate code
##c01..c10 in the SOURCE numbering (candidate k of PrefLib 00074 = the k-th column of irv.csv; Ben,
##2026-11-15: anonymous-code labels keep source numbering), names never stored; resp = the position as
##recorded. Three ballots are irregular: one puts three candidates at 3 and two at 10, one puts two at
##9 after a gap at 7, one has positions 1, 2, 8, 9, 10. Ties and gaps are kept as recorded (README,
##Layout).
##No covariates: voters.csv and weights.csv are not carried (Ben, 2026-11-15: ballots only, as the letter said).
##
##Usage: python3 -I data/rankings/vanderstraeten_2012_votepluriel_irv.py build <raw dir> <out dir>
##  <raw dir>/votepluriel/votes/irv.csv (the zip unzipped into <raw dir>/votepluriel/) and
##  <raw dir>/preflib/00074/00074-00000002.soi.
from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rank_common import design_counts, upsert_design, write_table  # noqa: E402

TABLE = "vanderstraeten_2012_votepluriel_irv"
IRV = "votepluriel/votes/irv.csv"
SOI = "preflib/00074/00074-00000002.soi"
PINNED = {IRV: "424f6daf916c14378f67c2e11a09add2a6f38f28aa30635f28d6ad91131e7b5e",
          SOI: "7c80da9779f2ff12af0ea51155c0753ccbb2cf501dd02ad23fc1b3b764915bcb"}


def read(raw: Path, rel: str) -> Path:
    p = raw / rel
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != PINNED[rel]:
        raise SystemExit(f"{rel}: sha256 {h} is not the pinned file")
    return p


def read_soi(path: Path) -> tuple[list[str], Counter]:
    names, prof = [], Counter()
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("# ALTERNATIVE NAME"):
            names.append(line.split(":", 1)[1].strip())
        elif line and not line.startswith("#"):
            n, rest = line.split(":", 1)
            prof[tuple(int(x) for x in re.split(r"\s*,\s*", rest.strip()))] += int(n)
    return names, prof


def preflib_cut(pos: dict[int, int]) -> tuple[int, ...]:
    """PrefLib's reading of a ballot: positions 1, 2, ... while each is held by exactly one candidate;
    at a tie the lowest-numbered tied candidate is kept and the ranking stops; at a gap it stops."""
    out, k = [], 1
    while True:
        at = sorted(c for c, p in pos.items() if p == k)
        if len(at) != 1:
            return tuple(out + at[:1])
        out.append(at[0])
        k += 1


def build(raw: Path, out_dir: Path) -> None:
    with open(read(raw, IRV), newline="", encoding="utf-8") as f:
        ballots = list(csv.DictReader(f))
    names = [c for c in ballots[0] if c != "id"]
    soi_names, soi = read_soi(read(raw, SOI))
    assert names == soi_names and len(names) == 10, "column order is not PrefLib's numbering"
    assert len(ballots) == 8078 and len({b["id"] for b in ballots}) == 8078
    assert [int(b["id"]) for b in ballots] == sorted(int(b["id"]) for b in ballots)
    rows, empty, irregular, cut = [], 0, 0, Counter()
    for i, b in enumerate(ballots, start=1):
        pos = {k: int(b[n]) for k, n in enumerate(names, start=1) if int(b[n]) > 0}
        assert all(0 <= int(b[n]) <= 10 for n in names)
        if not pos:
            empty += 1
            continue
        irregular += sorted(pos.values()) != list(range(1, len(pos) + 1))
        cut[preflib_cut(pos)] += 1
        for k in sorted(pos, key=lambda c: (pos[c], c)):
            rows.append({"id": i, "task": 1, "item": f"c{k:02d}", "resp": pos[k]})
    assert empty == 5 and irregular == 3
    assert cut == soi, "the ballots, read PrefLib's way, are not PrefLib 00074's profile"
    write_table(out_dir / f"{TABLE}.csv", rows)
    counts = design_counts(rows)
    assert counts["n_ballots_with_marks"] == 8073
    upsert_design({
        "table": TABLE, "source_file": "votes/irv.csv", "collection": "https://www.preflib.org/dataset/00074",
        "jurisdiction": "France, presidential election 2012 (online experiment Vote au pluriel)",
        "date": "2012-04-22",
        "office": "rank at least 3 of the 10 candidates (IRV 3-10)",
        "method": "irv", "seats": "na", **counts,
        "n_ballots_cast": len(ballots), "n_ballots_eligible_est": len(ballots),
        "write_in_allowed": "no", "candidate_order": "unknown",
        "evidence": ("Theo Delemazure's release https://theo.delemazure.fr/datasets/files/2012_vote_pluriel.zip "
                     "file votes/irv.csv (sha256 pinned in the script), the per-voter form of PrefLib 00074; "
                     "constraint (at least three ranked) and the dates from the release's codebook main.pdf; "
                     "paper Van der Straeten, Laslier & Blais 2013, PS 46(2) 324-328 (10.1017/S1049096513000036); "
                     "date is the official first round the experiment ran before (2-21 April 2012); seats na "
                     "(an experiment, not a count); 10 candidates offered, all 10 received a mark; "
                     f"{empty} ballots with no ranking (no rows); 3 ballots with repeated positions or gaps, "
                     "kept as recorded (n_tied_ballots 2 in the validator); PrefLib 00074-00000002.soi equals "
                     "these ballots with the empty ones dropped and each cut at its first gap or tie "
                     "(the lowest-numbered tied candidate kept); "
                     "write_in_allowed no (the ten official candidates only); candidate_order not documented; "
                     "counts computed by vanderstraeten_2012_votepluriel_irv.py"),
    })
    print(f"{TABLE}: {len(rows)} rows, {counts['n_ballots_with_marks']} ballots, "
          f"{counts['n_candidates']} candidates, {empty} empty, {irregular} with ties or gaps")


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] != "build":
        print("usage: vanderstraeten_2012_votepluriel_irv.py build <raw dir> <out dir>")
        return 2
    build(Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
