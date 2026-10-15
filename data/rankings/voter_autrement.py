#!/usr/bin/env python3
##Voter Autrement online voting experiments (France, 2017, 2022, 2024) -> IRW rankings tables.
##Source: the "Voter Autrement" research programme (Baujard, Blanch, Bouveret, Delemazure,
##Igersheim, Lang, Laruelle, Laslier, Lebon, Merlin and colleagues). Three Zenodo deposits,
##each under the Open Database License (ODbL 1.0; contents under DbCL 1.0):
##  2017  doi:10.5281/zenodo.1199545   "Voter Autrement 2017 - Online Experiment" (v1.0, 2018-07-25)
##        files read: stv111.csv (rank 1..11 of the 11 presidential candidates, IRV), stv411.csv
##        (rank at least 4 and up to 11, IRV), borda4.csv (rank exactly 4, Borda). One row per
##        participant; one column per candidate holding a SCORE 11 = first .. 1 = last, blank = not
##        ranked; a last column `official vote` (the participant's reported first-round vote).
##        Position = 12 - score. The three files' comment headers all say "Online experiment Borda
##        4" and "rank exactly 1 and 11"; the deposit's PDF (voter-autrement-online.pdf, section
##        "STV 1-11 / STV 4-11 / Borda 4") gives the constraints used here.
##  2022  doi:10.5281/zenodo.10998451  "Voter Autrement 2022 - The Online Experiment" (2024-04-19)
##        files read: irv_1.csv (rank between 4 and 11 of the 12 candidates, IRV-4-11), irv_2.csv
##        (rank between 1 and 11, IRV-1-11), borda.csv (rank exactly 4, Borda), voters.csv
##        (covariates). One row per participant; one column per candidate holding the RANK,
##        0 = not ranked. Each participant tried four rules, so a participant appears in at most
##        one of the three ranking files.
##  2024  doi:10.5281/zenodo.15075251  "Voter Autrement 2024 - The Online Experiment" (v2.0,
##        2025-03-24): European Parliament election, 38 party lists. files read:
##        {selfselected,representative}_votes_rankings.csv (`ranking` = "1. LIST ; 2. LIST ; ..."),
##        {selfselected,representative}_votes_two_choices.csv (first_choice, second_choice),
##        {selfselected,representative}_participants.csv (covariates), lists.csv (the 38 list
##        labels). The lists are the candidates of a list election and five of the 38 labels carry
##        a politician's name, so they are coded c01..c38 like candidates (alphabetical on the label
##        as printed in lists.csv); the participant's stated voting intention gets the same code.
##Dropped: approval, score, majority-judgement, Condorcet (pairwise) and continuous-evaluation
##files (not rankings; the Condorcet files belong with competitions), questionnaire files, and
##weights except the per-participant `weight` already in the 2024 files (kept as cov_weight).
##Participant numbers (`Voter 29483`, `id`) are dropped at re-keying; where the deposit uses one
##id space across files (2017 merged.csv, 2022 voters.csv) the link is not kept across tables.
##`official vote` / `official_vote` (2017, 2022) is a candidate name and is stored as the same
##candidate code as `item` (cov_official_vote), blank when not given.
##
##Usage:
##  python3 voter_autrement.py build <raw dir> <out dir> --all
##  python3 voter_autrement.py build <raw dir> <out dir> voterautrement_2022_irv4 [...]
##
##Layout (data/rankings/README.md): one row per participant x ranked option, task = 1.
##Table names: voterautrement_<year>_<irv1|irv4|borda4> and
##voterautrement_2024_<self|rep>_<ranking|top2>.
from __future__ import annotations

import csv
import sys
from pathlib import Path

from rank_common import code_candidates, design_counts, fetch, upsert_design, write_table

Z = "https://zenodo.org/api/records/{rec}/files/{name}/content"
DEPOSITS = {"2017": "10.5281/zenodo.1199545", "2022": "10.5281/zenodo.10998451", "2024": "10.5281/zenodo.15075251"}
RECORDS = {"2017": "1199545", "2022": "10998451", "2024": "15075251"}

# table -> (year, file, office/constraint text, method)
TABLES = {
    "voterautrement_2017_irv1": ("2017", "stv111.csv", "rank between 1 and 11 of the 11 candidates (IRV 1-11)", "irv"),
    "voterautrement_2017_irv4": ("2017", "stv411.csv", "rank between 4 and 11 of the 11 candidates (IRV 4-11)", "irv"),
    "voterautrement_2017_borda4": ("2017", "borda4.csv", "rank exactly 4 of the 11 candidates (Borda 4)", "survey"),
    "voterautrement_2022_irv4": ("2022", "irv_1.csv", "rank between 4 and 11 of the 12 candidates (IRV 4-11)", "irv"),
    "voterautrement_2022_irv1": ("2022", "irv_2.csv", "rank between 1 and 11 of the 12 candidates (IRV 1-11)", "irv"),
    "voterautrement_2022_borda4": ("2022", "borda.csv", "rank exactly 4 of the 12 candidates (Borda 4)", "survey"),
    "voterautrement_2024_self_ranking": ("2024", "selfselected_votes_rankings.csv",
                                         "rank any number of the 38 lists, self-selected sample", "survey"),
    "voterautrement_2024_rep_ranking": ("2024", "representative_votes_rankings.csv",
                                        "rank any number of the 38 lists, representative sample", "survey"),
    "voterautrement_2024_self_top2": ("2024", "selfselected_votes_two_choices.csv",
                                      "first and second choice among the 38 lists, self-selected sample", "survey"),
    "voterautrement_2024_rep_top2": ("2024", "representative_votes_two_choices.csv",
                                     "first and second choice among the 38 lists, representative sample", "survey"),
}
ELECTION_DATE = {"2017": "2017-04-23", "2022": "2022-04-10", "2024": "2024-06-09"}
EXTRA_FILES = {"2022": ["voters.csv"],
               "2024": ["selfselected_participants.csv", "representative_participants.csv", "lists.csv"]}


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def convert_2017(rows: list[dict]) -> list[dict]:
    cands = [c for c in rows[0] if c not in ("Voter", "official vote")]
    codes = code_candidates(cands)
    out = []
    for i, r in enumerate(rows, start=1):
        marks = [(c, r[c]) for c in cands if r[c].strip()]
        if not marks:
            continue
        ov = r["official vote"].strip()
        cov = codes.get(ov, "") if ov else ""
        for c, s in marks:
            out.append({"id": i, "task": 1, "item": codes[c], "resp": 12 - int(s), "cov_official_vote": cov})
    return out


def convert_2022(rows: list[dict], voters: dict[str, dict]) -> list[dict]:
    cands = [c for c in rows[0] if c != "id"]
    codes = code_candidates(cands)
    out = []
    for i, r in enumerate(rows, start=1):
        marks = [(c, r[c]) for c in cands if r[c].strip() not in ("", "0")]
        if not marks:
            continue
        v = voters.get(r["id"], {})
        ov = v.get("official_vote", "").strip()
        cov = {"cov_country": v.get("country", ""), "cov_studies": v.get("studies", ""),
               "cov_socpro": v.get("socpro", ""), "cov_age": v.get("age", ""), "cov_gender": v.get("gender", ""),
               "cov_official_vote": codes.get(ov, "") if ov else ""}
        for c, s in marks:
            out.append({"id": i, "task": 1, "item": codes[c], "resp": int(s), **cov})
    return out


def convert_2024(rows: list[dict], participants: dict[str, dict], lists: set[str], top2: bool) -> list[dict]:
    codes = code_candidates(lists)
    out = []
    for i, r in enumerate(rows, start=1):
        if top2:
            marks = [(r["first_choice"].strip(), 1), (r["second_choice"].strip(), 2)]
            marks = [(m, p) for m, p in marks if m]
        else:
            marks = []
            for part in r["ranking"].split(" ; "):
                if not part.strip():  # 171 participants submitted an empty ranking (self-selected file)
                    continue
                pos, label = part.split(". ", 1)
                marks.append((label.strip(), int(pos)))
        if not marks:
            continue
        for label, _ in marks:
            if label not in lists:
                raise ValueError(f"row {r['id']}: list label not in lists.csv: {label!r}")
        p = participants.get(r["id"], {})
        intent = p.get("intention", "").strip()
        cov = {"cov_age": p.get("age", ""), "cov_studies": p.get("studies", ""),
               "cov_knew_lists": p.get("knewIt", ""), "cov_intention": codes.get(intent, "") if intent else "",
               "cov_weight": r.get("weight", "")}
        for label, pos in marks:
            out.append({"id": i, "task": 1, "item": codes[label], "resp": pos, **cov})
    return out


def build(raw_dir: Path, out_dir: Path, tables: list[str]) -> int:
    for t in tables:
        if t not in TABLES:
            print(f"{t}: not a Voter Autrement table", file=sys.stderr)
            return 1
    for t in tables:
        year, fname, constraint, method = TABLES[t]
        rec = RECORDS[year]
        for extra in EXTRA_FILES.get(year, []):
            fetch(Z.format(rec=rec, name=extra), raw_dir / year / extra)
        src = fetch(Z.format(rec=rec, name=fname), raw_dir / year / fname)
        rows = read_csv(src)
        if year == "2017":
            long = convert_2017(rows)
            juris, n_options = "France, presidential election 2017 (online experiment)", 11
        elif year == "2022":
            voters = {v["id"]: v for v in read_csv(raw_dir / year / "voters.csv")}
            long = convert_2022(rows, voters)
            juris, n_options = "France, presidential election 2022 (online experiment)", 12
        else:
            sample = "selfselected" if "_self_" in t else "representative"
            participants = {p["id"]: p for p in read_csv(raw_dir / year / f"{sample}_participants.csv")}
            lists = {r["Name"].strip() for r in read_csv(raw_dir / year / "lists.csv")}
            if len(lists) != 38:
                raise ValueError(f"lists.csv: expected 38 lists, found {len(lists)}")
            long = convert_2024(rows, participants, lists, top2=t.endswith("_top2"))
            juris, n_options = "France, European Parliament election 2024 (online experiment)", len(lists)
        counts = design_counts(long)
        n_cast = len(rows)
        design = {"table": t, "source_file": fname, "collection": DEPOSITS[year], "jurisdiction": juris,
                  "date": ELECTION_DATE[year], "office": constraint, "method": method, "seats": "na",
                  **counts,
                  "n_ballots_cast": n_cast, "n_ballots_eligible_est": n_cast,
                  "write_in_allowed": "no", "candidate_order": "unknown",
                  "evidence": f"Zenodo {DEPOSITS[year]} file {fname}; constraint from the deposit's documentation PDF; "
                              f"date is the official election the experiment ran alongside; seats na (an experiment, "
                              f"not a count); {n_options} options were offered, of which "
                              f"{counts['n_candidates']} received a mark (n_candidates counts those); candidate_order not documented; counts "
                              f"computed by voter_autrement.py"}
        write_table(out_dir / f"{t}.csv", long)
        upsert_design(design)
        print(f"{t}: {n_cast} participants, {counts['n_ballots_with_marks']} with marks, "
              f"{counts['n_candidates']}/{n_options} options marked, {len(long)} rows, "
              f"max position {counts['n_positions']}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) >= 4:
        raw_dir, out_dir, rest = Path(argv[1]), Path(argv[2]), argv[3:]
        return build(raw_dir, out_dir, list(TABLES) if rest == ["--all"] else rest)
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
