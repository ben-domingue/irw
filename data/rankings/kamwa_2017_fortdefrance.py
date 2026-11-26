#!/usr/bin/env python3
##Fort-de-France 2017 in situ voting experiment (Kamwa, Joseph & Roger) -> two IRW rankings tables:
##kamwa_2017_fortdefrance_irv (instant-runoff ballots) and kamwa_2017_fortdefrance_borda4 (Borda-4 ballots).
##
##Paper (PrefLib's required citation): Kamwa, E., Joseph, G. & Roger, A. (2020). Une experimentation de
##deux modes de scrutin en Martinique lors du premier tour de l'election presidentielle de 2017. Revue
##d'economie politique, 130(5), 759-798. doi 10.3917/redp.305.0081 (open copy: HAL hal-01965660v2).
##
##Rights: no licence is stated by PrefLib. Eric Kamwa replied by email on 2026-11-16 (from
##eric.kamwa@univ-lorraine.fr): "You have the permission to redistribute both files under the ODbL
##licence, with the proposed attribution and links.", in reply to IRW's letter
##(oneoff/email-drafts-2026-11-15/preflib/kamwa_fortdefrance.txt; Laslier had redirected IRW to the
##authors on 2026-11-15). Original License = Permission via Email; Derived License = ODbL 1.0 (named in
##the reply; accepted for IRW by Ben 2026-10-15). The letter's terms are kept: one table per ballot
##type, one row per ballot and candidate, ballots numbered 1..n, candidates as codes so no name appears,
##each table cites the 2020 REP paper and links PrefLib.
##
##Design (paper, sections 3 and 4, and the ballot in its annex): on 22 April 2017 (the first round; a
##Saturday in Martinique) voters of the three polling stations of the Ecole Dillon D in Fort-de-France
##(bureaux 17, 18, 19) were invited, after their official vote, into a separate room; 524 took part, 508
##ballots were usable. Each participant got one sheet with two ballots: n 1, instant-runoff ("Vote
##Alternatif": write 1 to 11 against the 11 official candidates, all requested, at least one required)
##and n 2, Borda-4 (rank exactly 4 of the 11, scored 4-3-2-1). Both ballots list the 11 candidates in
##the same fixed order, which is PrefLib's alternative numbering (candidate 1 .. 11). So the same
##participants cast both ballots, but PrefLib keeps two separate weighted profiles with no voter key:
##**ids do not link the two tables.**
##
##Files read (nothing in them is executed): PrefLib-Data commit PREFLIB_COMMIT, dataset 00072
##(french-experiments-rankings): 00072-00000002.soi (TITLE Fort-de-France-irv, 480 ballots) and
##00072-00000003.soi (TITLE Fort-de-France-borda-4, 479 ballots). 00072-00000001.soi is Faches-Thumesnil
##2007, already in IRW as farvaque_2007_faches_irv (from the Zenodo deposit), and is not read. Both are
##weighted profiles of strict orders, possibly incomplete (`count: a, b, c`), the first candidate ranked
##first. SHA-256 of both files asserted. Theo Delemazure's Voting Experiments Library lists this
##experiment as "COMING SOON" with no files (checked 2026-11-16), so PrefLib is the only copy.
##
##Counts against the paper (asserted below): PrefLib holds fewer ballots than the paper counts as valid,
##505 IRV and 491 Borda-4 of the 508 usable sheets. Every PrefLib count is at or below the paper's:
##  IRV: first places per candidate <= Table 4, round T1 (sum 505 vs 480); the 19 incomplete rankings
##    are the paper's 505 - 486 (96.24% ranked all 11), so the 25 ballots absent from PrefLib would all
##    be complete rankings.
##  Borda-4: candidate x position counts <= Table 6 in all 44 cells (each position sums to 491 vs 479).
##  Which ballots are absent, and why, is not in the source; nothing is dropped by this script.
##
##Layout (R5, weighted profiles expanded, as mao_2013_mturk_rankings.py): id = one ballot 1..n in
##PrefLib's line order (sorted by count; the order of casting is not in the source); task = 1;
##item = candidate code c01..c11 in the SOURCE numbering (candidate k of PrefLib = c<k>, which is also the
##order printed on the ballot; Ben 2026-11-15: anonymous-code labels keep source numbering, as for
##vanderstraeten_2012_votepluriel_irv); resp = position, 1 = first. Names are never stored. No
##covariates: the sheet's questionnaire (gender, age band, occupation, reported official vote) is not in
##PrefLib.
##
##Usage: python3 -I data/rankings/kamwa_2017_fortdefrance.py build <raw dir> <out dir>
##  reads (and downloads if absent) <raw dir>/preflib/00072/00072-0000000{2,3}.soi
from __future__ import annotations

import hashlib
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `python3 -I` still finds rank_common
from rank_common import design_counts, fetch, upsert_design, write_table  # noqa: E402

PREFLIB_COMMIT = "03f5a88df70668ea0ab30062562fd57bf721d360"
BASE = ("https://raw.githubusercontent.com/PrefLib/PrefLib-Data/" + PREFLIB_COMMIT
        + "/datasets/00072%20-%20french-experiments-ranking/")
PAPER = "Kamwa, Joseph & Roger 2020, Revue d'economie politique 130(5) 759-798 (10.3917/redp.305.0081)"
PINNED = {"00072-00000002.soi": "dfb4bb7c9a96cad32d638e7e440ef481254e0e6c94b686be68d80ee81a65e64c",
          "00072-00000003.soi": "7e10b47c0f4895b81d8c13fdc9a78abf8e189691011c0f9205c51ce24e24681a"}

# Paper counts, candidates in PrefLib/ballot order (Dupont-Aignan, Le Pen, Macron, Hamon, Arthaud, Poutou,
# Cheminade, Lassalle, Melenchon, Asselineau, Fillon), transcribed from the HAL version.
PAPER_IRV_T1 = [20, 38, 124, 78, 13, 25, 0, 4, 151, 7, 45]  # Table 4, first iteration (505)
PAPER_BORDA = [  # Table 6, rows = positions 1-4 (491 each)
    [16, 40, 125, 76, 13, 21, 0, 3, 144, 6, 47],
    [15, 41, 94, 98, 21, 58, 11, 9, 95, 9, 40],
    [32, 28, 72, 93, 43, 36, 12, 20, 101, 22, 32],
    [35, 44, 53, 68, 54, 44, 27, 40, 48, 19, 59],
]
PAPER_SCORES = [208, 383, 979, 852, 255, 374, 84, 119, 1111, 114, 431]  # Table 6, "Scores bruts"

COMMON = {
    "collection": "https://www.preflib.org/dataset/00072",
    "jurisdiction": "Fort-de-France, Martinique, France (in situ experiment, Ecole Dillon D, polling stations 17-19)",
    "date": "2017-04-22", "seats": "na", "write_in_allowed": "no", "candidate_order": "fixed",
}


def read_soi(path: Path):
    head, prof = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            head[k.strip()] = v.strip()
        elif line.strip():
            count, order = line.split(":", 1)
            prof.append((int(count), tuple(int(x) for x in order.split(","))))
    n_alt = int(head["NUMBER ALTERNATIVES"])
    names = [head[f"ALTERNATIVE NAME {k}"] for k in range(1, n_alt + 1)]
    if sum(c for c, _ in prof) != int(head["NUMBER VOTERS"]) or len(prof) != int(head["NUMBER UNIQUE ORDERS"]):
        raise SystemExit(f"{path.name}: counts do not add up to the header -- stop and look")
    for _, o in prof:
        if len(set(o)) != len(o) or not set(o) <= set(range(1, n_alt + 1)):
            raise SystemExit(f"{path.name}: a ranking repeats or names an unknown candidate -- stop and look")
    return head, names, prof


def load(raw: Path, stem: str):
    p = fetch(BASE + stem, raw / "preflib" / "00072" / stem)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != PINNED[stem]:
        raise SystemExit(f"{stem}: sha256 {h} is not the pinned file")
    return read_soi(p) + (h,)


def expand(prof):
    rows, i = [], 0
    for count, order in prof:
        for _ in range(count):
            i += 1
            rows.extend({"id": i, "task": 1, "item": f"c{k:02d}", "resp": pos}
                        for pos, k in enumerate(order, start=1))
    return rows, i


def build(raw: Path, out_dir: Path) -> int:
    h_irv, names_irv, irv, sha_irv = load(raw, "00072-00000002.soi")
    h_b4, names_b4, b4, sha_b4 = load(raw, "00072-00000003.soi")
    assert h_irv["TITLE"] == "Fort-de-France-irv" and h_b4["TITLE"] == "Fort-de-France-borda-4"
    assert names_irv == names_b4 and len(names_irv) == 11, "the two files do not share the 11 candidates"

    # ---- IRV --------------------------------------------------------------------------------------
    lengths = Counter()
    for c, o in irv:
        lengths[len(o)] += c
    assert sum(lengths.values()) == 480 and lengths[11] == 461 and lengths[10] == 0
    first = Counter()
    for c, o in irv:
        first[o[0]] += c
    assert all(first[k] <= PAPER_IRV_T1[k - 1] for k in range(1, 12)), "more first places than the paper"
    assert sum(PAPER_IRV_T1) == 505 and 505 - round(505 * 0.9624) == 480 - 461  # 19 incomplete in both
    rows, n = expand(irv)
    counts = design_counts(rows)
    assert n == 480 and counts["n_ballots_with_marks"] == 480 and counts["n_candidates"] == 11
    write_table(out_dir / "kamwa_2017_fortdefrance_irv.csv", rows)
    dist = ", ".join(f"{k} ranked: {lengths[k]}" for k in sorted(lengths))
    upsert_design({**COMMON,
        "table": "kamwa_2017_fortdefrance_irv", "source_file": f"00072-00000002.soi (PrefLib-Data {PREFLIB_COMMIT[:7]})",
        "office": "rank 1 to 11 of the 11 candidates, all 11 requested (IRV 1-11)",
        "method": "irv", **counts, "n_ballots_cast": n, "n_ballots_eligible_est": n,
        "evidence": (
            f"{BASE}00072-00000002.soi, sha256 {sha_irv}, read 2026-11-16; a weighted profile of {len(irv)} "
            f"distinct strict orders expanded to one id per ballot (R5) in the file's line order; paper {PAPER}: "
            "section 4.3 and the annex ballot (n 1, Vote Alternatif: 'Inscrire 1 ... jusqu'a 11', all candidates "
            "requested, at least one required); date is the official first round, held on Saturday 22 April "
            "2017 in Martinique; seats na (an experiment, not a count); 11 candidates offered, all 11 received a "
            f"mark; marks per ballot: {dist}; PrefLib holds 480 of the 505 valid IRV ballots the paper counts "
            "(Table 4, T1): first places per candidate are at or below the paper's for every candidate, and the "
            "19 incomplete rankings equal the paper's 505 - 486 (96.24% ranked all), so the 25 absent ballots "
            "would be complete rankings; which ones and why is not in the source; write_in_allowed no (the "
            "ballot lists the 11 official candidates only); candidate_order fixed (the annex ballot prints the "
            "official order, which is PrefLib's numbering, for every voter); the same participants cast "
            "kamwa_2017_fortdefrance_borda4 on the same sheet but ids do not link (PrefLib keeps no voter key); "
            "candidate k coded c<k>; n_ballots_eligible_est equals n_ballots_cast (no precinct column); "
            "counts computed by kamwa_2017_fortdefrance.py")})
    print(f"kamwa_2017_fortdefrance_irv: {len(rows)} rows, {n} ballots, {len(irv)} distinct, {dist}")

    # ---- Borda-4 ----------------------------------------------------------------------------------
    assert all(len(o) == 4 for _, o in b4), "a Borda-4 ballot does not rank exactly 4"
    cell = Counter()
    for c, o in b4:
        for pos, k in enumerate(o):
            cell[pos, k] += c
    assert all(sum(r) == 491 for r in PAPER_BORDA)
    assert [sum(PAPER_BORDA[p][k] * (4 - p) for p in range(4)) for k in range(11)] == PAPER_SCORES
    over = [(p + 1, k) for p in range(4) for k in range(1, 12) if cell[p, k] > PAPER_BORDA[p][k - 1]]
    assert not over, f"PrefLib has more marks than the paper's Table 6 at {over}"
    rows, n = expand(b4)
    counts = design_counts(rows)
    assert n == 479 and counts["n_ballots_with_marks"] == 479 and counts["n_candidates"] == 11
    assert counts["n_positions"] == 4
    write_table(out_dir / "kamwa_2017_fortdefrance_borda4.csv", rows)
    upsert_design({**COMMON,
        "table": "kamwa_2017_fortdefrance_borda4",
        "source_file": f"00072-00000003.soi (PrefLib-Data {PREFLIB_COMMIT[:7]})",
        "office": "rank exactly 4 of the 11 candidates (Borda 4)",
        "method": "survey", **counts, "n_ballots_cast": n, "n_ballots_eligible_est": n,
        "evidence": (
            f"{BASE}00072-00000003.soi, sha256 {sha_b4}, read 2026-11-16; a weighted profile of {len(b4)} "
            f"distinct strict orders expanded to one id per ballot (R5) in the file's line order; paper {PAPER}: "
            "section 4.4 and the annex ballot (n 2, Regle de Borda a 4: rank only four of the 11 candidates, "
            "1 to 4; scored 4-3-2-1, unranked 0); method survey, as voterautrement_2017_borda4 (Borda is a "
            "scoring count with no rankings method value); date is the official first round, held on Saturday "
            "22 April 2017 in Martinique; seats na (an experiment, not a count); every ballot ranks exactly 4, "
            "strictly, with no tie or gap; 11 candidates offered, all 11 received a mark; PrefLib holds 479 of "
            "the 491 valid Borda-4 ballots the paper counts (Table 6): every candidate x position count is at "
            "or below the paper's (and the paper's raw scores follow from its own Table 6), so 12 ballots are "
            "absent; which ones and why is not in the source; write_in_allowed no; candidate_order fixed (the "
            "annex ballot prints the official order, PrefLib's numbering); the same participants cast "
            "kamwa_2017_fortdefrance_irv on the same sheet but ids do not link (PrefLib keeps no voter key); "
            "candidate k coded c<k>; n_ballots_eligible_est equals n_ballots_cast (no precinct column); "
            "counts computed by kamwa_2017_fortdefrance.py")})
    print(f"kamwa_2017_fortdefrance_borda4: {len(rows)} rows, {n} ballots, {len(b4)} distinct, "
          f"{491 - n} fewer than the paper's 491")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) == 3:
        return build(Path(argv[1]), Path(argv[2]))
    print("usage: kamwa_2017_fortdefrance.py build <raw dir> <out dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
