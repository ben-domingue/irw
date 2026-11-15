#!/usr/bin/env python3
##Mechanical Turk dots and sliding-puzzle rankings (Mao, Procaccia & Chen, AAAI 2013) -> IRW rankings tables.
##Citation: Mao, A., Procaccia, A. D., & Chen, Y. (2013). Better Human Computation Through Principled
##Voting. Proceedings of the AAAI Conference on Artificial Intelligence, 27(1), 1142-1148.
##https://doi.org/10.1609/aaai.v27i1.8460. Data distributed by PrefLib as datasets 00024 "dots" and
##00025 "puzzle" (https://www.preflib.org/dataset/00024, https://www.preflib.org/dataset/00025).
##Rights: no licence is stated by PrefLib or by Andrew Mao's page. Ariel Procaccia granted permission by
##email on 2026-11-15 ("Sure, go ahead.") in reply to IRW's letter
##(oneoff/email-drafts-2026-11-15/preflib/procaccia_mturk_dots_puzzle.txt), which promised: one table per
##file, one row per worker and ranked position, workers numbered 1..n with no ids kept, the items as
##shown with their true order recorded, a citation of the AAAI paper and a link to PrefLib. The letter
##offered CC BY 4.0 as the default licence; he named none. Dictionary: Original License = Permission via
##Email, Derived License = CC BY 4.0.
##
##Design (from the paper, section 4): each MTurk HIT ($0.10) asked a worker to order four objects shown
##in randomised order in a square grid, by drag and drop into a line, and every object had to be placed.
##Dots: four pictures with 200, 200+x, 200+2x, 200+3x dots (x = 3, 5, 7, 9), sorted "from fewest dots to
##most dots". Puzzle: four 8-puzzles d, d+3, d+6, d+9 moves from the solution (d = 5, 7, 9, 11, by A*),
##ranked "from closest to furthest". For each domain and level, 40 sets of objects, about 20 rankings per
##set; at most 5 HITs per worker per day, and no worker saw the same set twice. PrefLib pooled the 40 sets
##of a level into one file "as per the data owners request".
##
##Files read (nothing in them is executed): PrefLib 00024-0000000{1..4}.soc and 00025-0000000{1..4}.soc at
##PrefLib-Data commit PREFLIB_COMMIT. Each is a weighted profile of complete strict orders: a header with
##`# ALTERNATIVE NAME k: <dots or moves>` and `count: a,b,c,d` lines, the first item ranked first.
##
##Layout: R5 (weighted profiles are expanded): one id per ranking, in PrefLib's line order (sorted by
##count; the original submission order and the HIT/worker link are not in the source), task = 1,
##item = the object's dot or move count as text ("200 dots", "11 moves"), resp = position, 1 = first.
##**id is one ranking (one HIT), not one worker**: a worker could rank up to 5 sets a day, and PrefLib
##keeps no worker key, so rankings by the same worker cannot be linked (the letter said "one row per
##worker"; flagged in the PR). No worker id exists in the source, so none is kept.
##True order: item k (alternative k, ascending count) belongs at position k in both tasks, i.e. the
##correct ranking is the items sorted by their number. The rankings standard has no column for a known
##correct order, so it is recorded in the design record's `evidence`, the dictionary description and
##the processing note owed at upload (flagged in the PR). The display order was randomised per HIT but is
##not in the source, so there is no trial_display_order.
##
##Usage: python3 -I mao_2013_mturk_rankings.py build <raw dir> <out dir>
##Tables: mao_2013_dots_x<3|5|7|9> and mao_2013_puzzle_d<05|07|09|11>.
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `python3 -I` still finds rank_common
from rank_common import design_counts, fetch, upsert_design, write_table  # noqa: E402

PREFLIB_COMMIT = "220b7e5c7a7e04dcde56ce04b8923b8c589cbb33"
BASE = "https://raw.githubusercontent.com/PrefLib/PrefLib-Data/" + PREFLIB_COMMIT + "/datasets/"
DIRS = {"00024": "00024%20-%20dots", "00025": "00025%20-%20puzzle"}
PAPER = "https://doi.org/10.1609/aaai.v27i1.8460"

# PrefLib file -> (table, task, step, unit, PrefLib title)
FILES = {
    "00024-00000001": ("mao_2013_dots_x3", "dots", 3, "dots", "all_200x3"),
    "00024-00000002": ("mao_2013_dots_x5", "dots", 5, "dots", "all_200x5"),
    "00024-00000003": ("mao_2013_dots_x7", "dots", 7, "dots", "all_200x7"),
    "00024-00000004": ("mao_2013_dots_x9", "dots", 9, "dots", "all_200x9"),
    "00025-00000002": ("mao_2013_puzzle_d05", "puzzle", 5, "moves", "all_5_8_11_14"),
    "00025-00000003": ("mao_2013_puzzle_d07", "puzzle", 7, "moves", "all_7_10_13_16"),
    "00025-00000004": ("mao_2013_puzzle_d09", "puzzle", 9, "moves", "all_9_12_15_18"),
    "00025-00000001": ("mao_2013_puzzle_d11", "puzzle", 11, "moves", "all_11_14_17_20"),
}


def parse_soc(path: Path):
    head, prof = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            head[k.strip()] = v.strip()
        elif line.strip():
            count, order = line.split(":", 1)
            prof.append((int(count), tuple(int(x) for x in order.split(","))))
    return head, prof


def expected_labels(task: str, step: int) -> list[str]:
    start = 200 if task == "dots" else step
    inc = step if task == "dots" else 3
    return [str(start + j * inc) for j in range(4)]


def build(raw_dir: Path, out_dir: Path) -> int:
    for stem, (t, task, step, unit, title) in FILES.items():
        series = stem[:5]
        src = fetch(BASE + DIRS[series] + f"/{stem}.soc", raw_dir / "preflib" / f"{stem}.soc")
        head, prof = parse_soc(src)
        n_alt = int(head["NUMBER ALTERNATIVES"])
        labels = [head[f"ALTERNATIVE NAME {k}"] for k in range(1, n_alt + 1)]
        n_voters = int(head["NUMBER VOTERS"])
        # Stop on anything the build's reading of the file depends on.
        if head.get("DATA TYPE") != "soc" or head.get("TITLE") != title or n_alt != 4:
            raise SystemExit(f"{stem}: header not as expected -- stop and look")
        if labels != expected_labels(task, step):
            raise SystemExit(f"{stem}: alternatives {labels} are not the paper's sequence -- stop and look")
        if sum(c for c, _ in prof) != n_voters or len(prof) != int(head["NUMBER UNIQUE ORDERS"]):
            raise SystemExit(f"{stem}: counts do not add up to the header -- stop and look")
        if any(sorted(o) != [1, 2, 3, 4] for _, o in prof) or len({o for _, o in prof}) != len(prof):
            raise SystemExit(f"{stem}: a ranking is not a complete strict order, or repeats -- stop and look")
        items = {k: f"{lab} {unit}" for k, lab in enumerate(labels, start=1)}
        out, i = [], 0
        for count, order in prof:
            for _ in range(count):
                i += 1
                out.extend({"id": i, "task": 1, "item": items[a], "resp": pos}
                           for pos, a in enumerate(order, start=1))
        counts = design_counts(out)
        n_correct = sum(c for c, o in prof if o == (1, 2, 3, 4))
        true_order = " < ".join(items[k] for k in range(1, 5))
        sha = hashlib.sha256(src.read_bytes()).hexdigest()
        if task == "dots":
            office = (f"Dots task, x = {step}: order four pictures of {', '.join(labels)} dots from fewest to most "
                      f"(PrefLib {stem}, 40 picture sets pooled)")
            ask = "'sorting four pictures from fewest dots to most dots'"
        else:
            office = (f"8-puzzle task, d = {step}: order four puzzles {', '.join(labels)} moves from the solution, "
                      f"closest first (PrefLib {stem}, 40 puzzle sets pooled)")
            ask = "'rank four 8-puzzles by the least number of moves ... from closest to furthest'"
        design = {
            "table": t, "source_file": f"{stem}.soc (PrefLib-Data {PREFLIB_COMMIT[:7]})",
            "collection": f"https://www.preflib.org/dataset/{series}",
            "jurisdiction": "Amazon Mechanical Turk (online experiment)", "date": "unknown", "office": office,
            "method": "survey", "seats": "na", **counts,
            "n_ballots_cast": n_voters, "n_ballots_eligible_est": n_voters,
            "write_in_allowed": "no", "candidate_order": "rotated",
            "evidence": (
                f"{BASE}{DIRS[series]}/{stem}.soc, sha256 {sha}, read 2026-11-15; a weighted profile of "
                f"{len(prof)} distinct complete orders expanded to one id per ranking (R5) in the file's line "
                f"order; design from Mao, Procaccia & Chen (2013), {PAPER}, section 4: the HIT asked for {ask}; "
                f"TRUE ORDER (the correct ranking, positions 1-4): {true_order} -- item k of the source sits at "
                f"position k; {n_correct} of {n_voters} rankings are exactly the true order; "
                "40 sets of objects at this level, about 20 rankings each, pooled into one file by PrefLib "
                "at the data owners' request (the set of each ranking is not in the source, and the objects "
                "differ across sets: the item is the object's dot or move count, not one picture); "
                "id is one ranking (one HIT), not one worker: up to 5 HITs per worker per day and no worker "
                "key in the source; candidate_order rotated: 'The objects were presented in randomized order "
                "in a square starting grid' (per HIT; the order shown is not in the source); write_in_allowed "
                "no and n_positions 4: every object had to be placed in the target line; seats na (an "
                "experiment); date unknown (the paper gives no fielding date); n_ballots_eligible_est equals "
                "n_ballots_cast (no precinct column); counts computed by mao_2013_mturk_rankings.py")}
        write_table(out_dir / f"{t}.csv", out)
        upsert_design(design)
        print(f"{t}: {n_voters} rankings, {len(prof)} distinct, {n_correct} exactly correct, {len(out)} rows")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) == 3:
        return build(Path(argv[1]), Path(argv[2]))
    print("usage: mao_2013_mturk_rankings.py build <raw dir> <out dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
