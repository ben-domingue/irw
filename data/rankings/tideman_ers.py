#!/usr/bin/env python3
##Electoral Reform Society (ERS) ballot data tabulated by Nicolaus Tideman -> IRW rankings tables.
##Source: ballots from elections of British organisations (mostly trade unions, voting by PR-STV or
##IRV), recorded under a stipulation that the organisations stay anonymous. Elections 1-32 were
##gathered in 1987 and 48-99 in 1988 by Nicolaus Tideman (NSF grant SES86-18328); 33-35 were gathered
##by David Hill; 36-47 were never assigned (https://rangevoting.org/TidemanData.html). 87 elections.
##The same ballots are PrefLib dataset 00007 "ers" (Mattei & Walsh 2013, https://www.preflib.org/dataset/00007).
##Rights: no licence is stated anywhere. Tideman granted permission to republish by email on
##2026-11-15 ("yes you may republish them") in reply to IRW's letter
##(oneoff/email-drafts-2026-11-15/preflib/tideman_ers.txt), which promised: one table per election,
##only elections with at least 50 ballots, one row per ballot and ranked position, ballots numbered
##1..n, candidates as codes only, organisations and candidates anonymous as they are now, a citation
##of Tideman and a link to PrefLib. The letter offered CC BY 4.0 as the default licence; he named
##none. Dictionary: Original License = Permission via Email, Derived License = CC BY 4.0.
##
##Files read (nothing in them is executed):
##  * TiData/A<k>.HIL from rangevoting.org, David Hill's format: line 1 = `n_candidates n_seats`;
##    then one line per ballot paper, `1 c_i c_j ... 0` (the leading 1 is a multiplicity, always 1;
##    the ranking ends at the 0); a line `0` ends the ballots; then the candidate labels in quotes
##    ("Candidate  1", "1", "A", ...: already anonymous) and the election label ("a1", "f:a11").
##    Invalid votes and a few write-in references were deleted by the tabulators. Some files hold
##    `1 0` lines: ballot papers with no ranking, counted in n_ballots_cast, no rows.
##  * PrefLib 00007-<n>.soi at PrefLib-Data commit PREFLIB_COMMIT, read only as a cross-check. PrefLib
##    set n is A<k> in lexical order of the file names (A1, A10, A11, ..., A2, ...). The .soi is a
##    weighted profile (count: ranking), sorted by count, so it has lost the ballot order. It also
##    differs from the HIL file in two ways, both verified here for all 87: ballots with no ranking
##    are left out, and a ranking one short of complete has the remaining candidate appended. The
##    tables follow the HIL file (marks as recorded, ballot order kept); the build stops if dropping
##    the empty HIL ballots and completing the one-short ones does not give PrefLib's profile exactly.
##
##Layout: id = the ballot paper re-keyed 1..n in HIL file order over ballots with at least one mark,
##task = 1, item = candidate code, resp = the position recorded. Candidate codes: the HIL labels are
##already anonymous numbers or letters in candidate-number order, so candidate k is c<k> (two digits;
##at most 29 candidates). The README's alphabetical rule on printed names would scramble numeric
##labels ("10" before "2") and has no personal name to protect here; flagged for Ben in the PR.
##No ballot in the 87 repeats a candidate, so there are no duplicate marks, overvotes, write-ins or
##ties. No covariates: nothing in the files varies within an election except the ranking.
##
##Built: elections with at least 50 ballots with marks (the family floor and the letter's promise).
##Not built: under the floor (A4, A22, A31, A33, A51, A68 -- A68 has 50 ballot papers, one empty);
##A33-A35 were gathered by David Hill, not Tideman. Ben ruled 2026-11-15 that Tideman's permission
##covers them: Tideman distributes all 87 as one collection and is its named contact, and the letter
##asked about all 87. A34 and A35 are built and credit Hill as gatherer; A33 is under the floor.
##
##Usage: python3 tideman_ers.py build <raw dir> <out dir> [--all | a01 a02 ...]
##Table: tideman_ers_a<kk> (Tideman's own election number, two digits).
from __future__ import annotations

import collections
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `python3 -I` still finds rank_common
from rank_common import design_counts, fetch, upsert_design, write_table  # noqa: E402

HIL_URL = "https://rangevoting.org/TiData/A{k}.HIL"
PREFLIB_COMMIT = "220b7e5c7a7e04dcde56ce04b8923b8c589cbb33"
SOI_URL = ("https://raw.githubusercontent.com/PrefLib/PrefLib-Data/" + PREFLIB_COMMIT
           + "/datasets/00007%20-%20ers/00007-{n:08d}.soi")
COLLECTION = "https://www.preflib.org/dataset/00007"
ELECTIONS = list(range(1, 36)) + list(range(48, 100))  # 87; 36-47 were never assigned
HELD: dict[int, str] = {}  # A34/A35 released by Ben 2026-11-15
FLOOR = 50
PREFLIB_SET = {k: i for i, k in enumerate(sorted(ELECTIONS, key=lambda k: f"A{k}.HIL"), start=1)}


def table_name(k: int) -> str:
    return f"tideman_ers_a{k:02d}"


def parse_hil(path: Path):
    lines = path.read_text(encoding="ascii").splitlines()
    n_cands, n_seats = (int(x) for x in lines[0].split()[:2])
    ballots, end = [], None
    for j, line in enumerate(lines[1:], start=1):
        p = line.split()
        if not p:
            continue
        if p == ["0"]:
            end = j
            break
        if p[0] != "1" or p[-1] != "0":
            raise ValueError(f"{path.name} line {j + 1}: not `1 ... 0`: {line!r}")
        order = tuple(int(x) for x in p[1:-1])
        if any(c < 1 or c > n_cands for c in order) or len(set(order)) != len(order):
            raise ValueError(f"{path.name} line {j + 1}: candidate out of range or repeated: {line!r}")
        ballots.append(order)
    if end is None:
        raise ValueError(f"{path.name}: no end-of-ballots line")
    return n_cands, n_seats, ballots


def parse_soi(path: Path):
    prof, n_alt = collections.Counter(), None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# NUMBER ALTERNATIVES:"):
            n_alt = int(line.split(":")[1])
        elif line and not line.startswith("#"):
            count, order = line.split(":", 1)
            prof[tuple(int(x) for x in order.strip().split(","))] += int(count)
    return n_alt, prof


def cross_check(k: int, n_cands: int, ballots, soi: Path) -> None:
    n_alt, prof = parse_soi(soi)
    full = set(range(1, n_cands + 1))
    mine = collections.Counter(o + tuple(full - set(o)) if len(o) == n_cands - 1 else o
                               for o in ballots if o)
    if n_alt != n_cands or mine != prof:
        raise SystemExit(f"A{k}: HIL file does not reproduce PrefLib set {PREFLIB_SET[k]} -- stop and look")


def build(raw_dir: Path, out_dir: Path, wanted: list[int]) -> int:
    for k in wanted:
        hil = fetch(HIL_URL.format(k=k), raw_dir / "hil" / f"A{k}.HIL")
        soi = fetch(SOI_URL.format(n=PREFLIB_SET[k]), raw_dir / "preflib" / f"00007-{PREFLIB_SET[k]:08d}.soi")
        n_cands, n_seats, ballots = parse_hil(hil)
        cross_check(k, n_cands, ballots, soi)
        marked = [o for o in ballots if o]
        t = table_name(k)
        if k in HELD:
            print(f"{t}: HELD ({HELD[k]}); {len(marked)} ballots with marks, not written")
            continue
        if len(marked) < FLOOR:
            print(f"{t}: {len(marked)} ballots with marks, under the floor of {FLOOR}; not written")
            continue
        width = 2
        out = [{"id": i, "task": 1, "item": f"c{c:0{width}d}", "resp": pos}
               for i, order in enumerate(marked, start=1) for pos, c in enumerate(order, start=1)]
        counts = design_counts(out)
        n_short = sum(1 for o in marked if len(o) == n_cands - 1)
        unranked = n_cands - counts["n_candidates"]
        sha = hashlib.sha256(hil.read_bytes()).hexdigest()
        gatherer = ("Nicolaus Tideman, 1987" if k <= 32 else
                    "David Hill (year not recorded); distributed by Tideman in the same collection" if k <= 35 else
                    "Nicolaus Tideman, 1988")
        design = {
            "table": t, "source_file": f"TiData/A{k}.HIL (rangevoting.org)", "collection": COLLECTION,
            "jurisdiction": "Anonymous British organisation (ERS collection)", "date": "unknown",
            "office": f"election A{k} of the Tideman ERS collection (PrefLib 00007-{PREFLIB_SET[k]:08d}); "
                      f"{n_seats} to elect",
            "method": "unknown", "seats": n_seats, **counts,
            "n_ballots_cast": len(ballots), "n_ballots_eligible_est": len(ballots),
            "write_in_allowed": "unknown", "candidate_order": "unknown",
            "evidence": (
                f"https://rangevoting.org/TiData/A{k}.HIL, sha256 {sha}, read 2026-11-15; gathered by {gatherer}; "
                f"cross-checked against PrefLib 00007-{PREFLIB_SET[k]:08d}.soi at PrefLib-Data commit "
                f"{PREFLIB_COMMIT[:7]}: the same ballots once the {len(ballots) - len(marked)} empty ballot "
                f"papers are left out and the {n_short} rankings one short of complete have the remaining "
                f"candidate appended, as PrefLib does; the table keeps the HIL marks as recorded and its "
                f"ballot order. seats from the file's header line; {n_cands} candidates in the header"
                + (f", {unranked} of them ranked on no ballot" if unranked else "")
                + "; method unknown (the collection is 'mostly trade unions using PR-STV or IRV' with no rule "
                "per election); date unknown (the organisations are anonymous and only the year the ballots "
                "were gathered is known); n_positions is the longest recorded ranking, not a ballot fact; "
                "write_in_allowed unknown (the tabulators deleted 'a small number of references to write-in "
                "candidates'); candidate_order unknown; PrefLib says some files are complete sets of ballots "
                "and some random samples, without saying which; n_ballots_eligible_est equals n_ballots_cast "
                "(no precinct column); candidate k coded c<k> (labels already anonymous); counts computed by "
                "tideman_ers.py")}
        write_table(out_dir / f"{t}.csv", out)
        upsert_design(design)
        print(f"{t}: {len(ballots)} ballot papers, {len(marked)} with marks, {n_cands} candidates, "
              f"{n_seats} seats, {len(out)} rows")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        if argv[3:] == ["--all"]:
            wanted = ELECTIONS
        else:
            wanted = [int(a.lower().lstrip("a")) for a in argv[3:]]
            bad = [k for k in wanted if k not in ELECTIONS]
            if bad:
                print(f"no such election: {bad}", file=sys.stderr)
                return 2
        return build(Path(argv[1]), Path(argv[2]), wanted)
    print(__doc__ or "usage: tideman_ers.py build <raw dir> <out dir> [--all | a01 ...]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
