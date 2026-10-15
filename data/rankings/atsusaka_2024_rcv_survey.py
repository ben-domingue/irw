#!/usr/bin/env python3
##Ballot-order survey experiments on ranked-choice voting (Alaska and Oakland, autumn 2022) -> IRW rankings tables.
##Source: Atsusaka, Y. "Analyzing Ballot Order Effects When Voters Rank Candidates" (Political
##Analysis, forthcoming at deposit). Replication data, Harvard Dataverse doi:10.7910/DVN/AJXRCV,
##CC0 1.0 (deposited 2024-03-18). Files read (Qualtrics exports; the first three lines are the
##variable names, the question texts and Qualtrics ImportIds):
##  qualtrics_Alaska_nonnumeric.tab (file id 9657835): 354 Alaska respondents, four ranking tasks
##    over the real 8 November 2022 contests: U.S. House (4 candidates) ranked "up to four" (task 1)
##    then "all, order shuffled" (task 2); U.S. Senate (4 candidates) likewise (tasks 3, 4).
##    Covariates as labels.
##  qualtrics_Oakland.tab (file id 9657821): 259 Oakland respondents, two tasks over the ten 2022
##    mayoral candidates: a first ranking question (positions 1-3 observed; its question label in
##    the export is a Qualtrics template placeholder, "rank the following question types") and
##    "rank all candidates, order shuffled" (task 2). Covariates are Qualtrics numeric codes (this
##    deposit has no labelled Oakland export and no codebook).
##The deposit also holds the official Alaska cast vote records for the same contests; those are
##FairVote files already in candidates.csv (alaska_2022 slice) and are not built here.
##Candidates are coded c01.. alphabetically over all names in the file (the party in parentheses
##after the name is dropped; names are not stored). Each task's `trial_display_order` is the
##order the candidates were shown to that respondent, as codes joined by "|": Qualtrics
##randomised it per respondent (the `_DO` columns), which is the design's point.
##Not ranked: -99 or blank. ResponseId, IP address, location and panel columns are dropped.
##
##Usage: python3 atsusaka_2024_rcv_survey.py build <raw dir> <out dir> --all
##Tables: atsusaka_2024_alaska_rcv_survey, atsusaka_2024_oakland_rcv_survey.
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

COLLECTION = "10.7910/DVN/AJXRCV"
DV = "https://dataverse.harvard.edu/api/access/datafile/{fid}?format=original"
FILES = {"atsusaka_2024_alaska_rcv_survey": ("qualtrics_Alaska_nonnumeric.tab", "9657835"),
         "atsusaka_2024_oakland_rcv_survey": ("qualtrics_Oakland.tab", "9657821")}
# task -> (question prefix, contest, required full ranking?)
TASKS = {"atsusaka_2024_alaska_rcv_survey": [("C3", "us_house", "no"), ("C4", "us_house", "yes"),
                                            ("C5", "us_senate", "no"), ("C6", "us_senate", "yes")],
         "atsusaka_2024_oakland_rcv_survey": [("C1", "oakland_mayor", "no"), ("C2", "oakland_mayor", "yes")]}
COVS = {"B1": "cov_age", "B2": "cov_gender", "B3": "cov_race", "B4": "cov_party_id",
        "B5": "cov_education", "B6": "cov_likely_to_vote"}
RESIDENT = {"atsusaka_2024_alaska_rcv_survey": "A5a", "atsusaka_2024_oakland_rcv_survey": "A5o"}
PARTY = re.compile(r"\s*\((Registered [^)]*|[^)]*)\)\s*$")


def strip_party(label: str) -> str:
    return PARTY.sub("", label).strip()


def iso_date(s: str) -> str:
    """Qualtrics exports dates as YYYY-MM-DD or M/D/YYYY depending on the account locale."""
    s = s.strip().split(" ")[0]
    if "/" in s:
        m, d, y = s.split("/")
        return f"{y}-{int(m):02d}-{int(d):02d}"
    return s[:10]


def read_qualtrics(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    names, texts, data = rows[0], rows[1], rows[3:]
    return names, texts, [dict(zip(names, r)) for r in data]


def build(raw_dir: Path, out_dir: Path, tables: list[str]) -> int:
    for t in tables:
        fname, fid = FILES[t]
        src = fetch(DV.format(fid=fid), raw_dir / fname)
        names, texts, data = read_qualtrics(src)
        label = dict(zip(names, texts))
        # candidate labels per task come from the item columns' question text after " - "
        task_items: dict[str, list[tuple[str, str]]] = {}
        all_names = set()
        for q, _, _ in TASKS[t]:
            cols = [n for n in names if re.fullmatch(rf"{q}_\d+", n)]
            items = [(c, strip_party(label[c].rsplit(" - ", 1)[1])) for c in cols]
            task_items[q] = items
            all_names.update(n for _, n in items)
        codes = code_candidates(all_names)
        out = []
        for i, r in enumerate(data, start=1):
            cov = {v: r.get(k, "") for k, v in COVS.items()}
            cov["cov_resident"] = r.get(RESIDENT[t], "")
            for task_no, (q, contest, full) in enumerate(TASKS[t], start=1):
                do = r.get(f"{q}_DO", "")
                shown = []
                for part in do.split("|") if do else []:
                    part = part.strip()
                    if part.isdigit():  # numeric export: position refers to the item column index
                        col = f"{q}_{part}"
                        shown.append(codes[dict(task_items[q])[col]])
                    else:
                        shown.append(codes[strip_party(part)])
                trial = {"trial_contest": contest, "trial_required_full": full,
                         "trial_display_order": "|".join(shown)}
                for col, name in task_items[q]:
                    v = r.get(col, "").strip()
                    if v in ("", "-99") or not v.lstrip("-").isdigit() or int(v) < 1:
                        continue
                    out.append({"id": i, "task": task_no, "item": codes[name], "resp": int(v), **cov, **trial})
        counts = design_counts(out)
        dates = sorted(iso_date(r["StartDate"]) for r in data if r.get("StartDate"))
        place = "Alaska" if "alaska" in t else "Oakland, California"
        design = {"table": t, "source_file": fname, "collection": COLLECTION,
                  "jurisdiction": f"{place} (online survey experiment)", "date": dates[0],
                  "office": ("U.S. House and U.S. Senate, Alaska, 8 November 2022 (hypothetical ballots; tasks 1-2 "
                             "House, 3-4 Senate; tasks 2 and 4 required a full ranking)" if "alaska" in t else
                             "Oakland mayor, 8 November 2022 (hypothetical ballots; task 2 required a full ranking)"),
                  "method": "survey", "seats": "na", **counts,
                  "n_ballots_cast": len(data), "n_ballots_eligible_est": len(data),
                  "write_in_allowed": "no", "candidate_order": "rotated",
                  "evidence": f"Dataverse {COLLECTION} file {fname} (id {fid}); fielded {dates[0]} to {dates[-1]} "
                              f"(StartDate); candidate order randomised per respondent by Qualtrics (the _DO columns, "
                              f"kept as trial_display_order); seats na (a survey); n_positions is the largest rank "
                              f"given in any task; counts computed by atsusaka_2024_rcv_survey.py"}
        write_table(out_dir / f"{t}.csv", out)
        upsert_design(design)
        print(f"{t}: {len(data)} respondents, {counts['n_ballots_with_marks']} with marks, "
              f"{counts['n_candidates']} candidates, {len(out)} rows, fielded {dates[0]}..{dates[-1]}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        rest = argv[3:]
        return build(Path(argv[1]), Path(argv[2]), list(FILES) if rest == ["--all"] else rest)
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
