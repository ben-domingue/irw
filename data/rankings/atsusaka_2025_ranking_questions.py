#!/usr/bin/env python3
##Survey ranking questions with anchor and repeat items (US, June 2023) -> one IRW rankings table.
##Source: Atsusaka, Y. and Kim, S.-y. S. "Addressing Measurement Errors in Ranking Questions for
##the Social Sciences", Political Analysis 33(4), 2025, 339-360. Replication data, Harvard
##Dataverse doi:10.7910/DVN/UCTXEF, CC0 1.0 (deposited 2024-09-15). File read:
##ranking_error.zip -> ranking_error-main.zip -> ranking_error-main/data/raw/AmericanRanking_June_2023.sav (YouGov, 1,082 US
##adults, June 2023). Nothing else in the archive is read or run (its R code is GPL-3 and not
##used). No codebook ships; variable labels in the .sav are the item texts.
##Each respondent answered a battery of ranking questions, each a complete permutation of 3 to 6
##options (the Qualtrics/YouGov rank widget forces a permutation): the paper's anchor questions
##("no_context", items literally labelled "Blank - 1..4", and a question with an objectively
##correct order, "esystems"), substantive questions (Tate 1993 roles, Hopkins identity, holidays,
##affective polarisation, electoral-system goals), two wording arms (alphabet vs exact), and
##repeats of four questions later in the survey. Half the sample saw each arm of the randomised
##pairs, so tasks have 532-1,082 respondents each. One task per question; `trial_question` is the
##variable stem. Option texts are kept as items (none is a person).
##Exception: `estemporal` has 12 of 550 responses that are not permutations (a repeated position);
##those respondents' estemporal rankings are dropped (R3 forbids a repeated position; the design
##record notes the count). Everything else is as recorded.
##Covariates: age4, gender3, race4, educ4, pid3 (labels). Weights, free text and the YouGov
##screeners are dropped.
##
##Usage: python3 atsusaka_2025_ranking_questions.py build <raw dir> <out dir>
##Table: atsusaka_2025_ranking_questions.
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from rank_common import design_counts, fetch, upsert_design, write_table

COLLECTION = "10.7910/DVN/UCTXEF"
URL = "https://dataverse.harvard.edu/api/access/datafile/10649987"
SAV = "ranking_error-main/data/raw/AmericanRanking_June_2023.sav"
TABLE = "atsusaka_2025_ranking_questions"
#: task number -> variable stem, in questionnaire order
QUESTIONS = ["no_context_3", "no_context_4", "anc_tate_1993", "app_tate_1993", "identityhopkins", "app_identity",
             "alpha", "exact", "holidays", "appaffectivepolar", "esystems", "esystems_app", "esalphabet",
             "estemporal", "app_tate_1993_repeat", "app_identity_repeat", "appaffectivepolar_repeat",
             "esystems_app_repeat"]
COVS = {"age4": "cov_age", "gender3": "cov_gender", "race4": "cov_race", "educ4": "cov_education",
        "pid3": "cov_party_id"}


def build(raw_dir: Path, out_dir: Path) -> int:
    import pyreadstat
    z = fetch(URL, raw_dir / "ranking_error.zip")
    sav = raw_dir / "AmericanRanking_June_2023.sav"
    if not sav.exists():
        with zipfile.ZipFile(z) as outer:  # the Dataverse zip wraps the GitHub archive zip
            inner = io.BytesIO(outer.read("ranking_error-main.zip"))
        with zipfile.ZipFile(inner) as zf:
            sav.write_bytes(zf.read(SAV))
    df, meta = pyreadstat.read_sav(str(sav))
    labels = dict(zip(meta.column_names, meta.column_labels))
    vlabels = meta.variable_value_labels
    out, dropped = [], {}
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        cov = {}
        for var, name in COVS.items():
            v = r[var]
            cov[name] = "" if v != v else vlabels.get(var, {}).get(v, str(v))
        for task_no, stem in enumerate(QUESTIONS, start=1):
            cols = [c for c in df.columns if c.startswith(stem + "_") and c[len(stem) + 1:].isdigit()]
            vals = [(c, r[c]) for c in cols if r[c] == r[c]]
            if not vals:
                continue
            positions = [int(v) for _, v in vals]
            if len(set(positions)) != len(positions):
                dropped[stem] = dropped.get(stem, 0) + 1
                continue
            for c, v in vals:
                out.append({"id": i, "task": task_no, "item": labels[c], "resp": int(v), **cov,
                            "trial_question": stem})
    counts = design_counts(out)
    n = len(df)
    design = {"table": TABLE, "source_file": "AmericanRanking_June_2023.sav", "collection": COLLECTION,
              "jurisdiction": "United States (YouGov online panel)", "date": "2023-06-01",
              "office": "18 survey ranking questions, 3 to 6 options each (anchor, substantive, wording-arm and "
                        "repeat questions)", "method": "survey", "seats": "na", **counts,
              "n_ballots_cast": n, "n_ballots_eligible_est": n, "write_in_allowed": "no",
              "candidate_order": "rotated",
              "evidence": f"Dataverse {COLLECTION}, {SAV}; date is the fielding month in the file name (day unknown); "
                          f"option order randomised per respondent (the *_row_rnd variables); seats na (a survey); "
                          f"n_candidates counts distinct option texts across all tasks; dropped non-permutation "
                          f"responses: {dropped}; counts computed by atsusaka_2025_ranking_questions.py"}
    write_table(out_dir / f"{TABLE}.csv", out)
    upsert_design(design)
    print(f"{TABLE}: {n} respondents, {counts['n_ballots_with_marks']} with marks, {len(out)} rows, "
          f"{counts['n_candidates']} option texts, dropped {dropped}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["build"] and len(argv) == 3:
        return build(Path(argv[1]), Path(argv[2]))
    print(__doc__ or "", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
