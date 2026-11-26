#!/usr/bin/env python3
# Source: https://zenodo.org/records/15692867
# DOI: 10.5281/zenodo.15692867 (data)
#   Doz D, Štemberger T (2025). Statistical anxiety in Slovenia [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: anketa104123-2024-07-07.xlsx, a 1KA survey export of 194 Slovenian (pedagogical-programme)
#   students. Row 1 under the header holds each question's Slovenian wording. 1KA codes: -3 = the
#   respondent left the survey before the question, -1 = no answer; both are missing here, not rows.
#   All items are 1-5 agreement ratings (observed 1-5).
# Tables (item = the 1KA question code):
#   doz_2025_statistics_attitudes -- Q9a-g, Q10a-e, Q11a-g: statements about statistics, statistics
#     courses and statistics lecturers (19 items, all worded so that agreement = more negative view).
#   doz_2025_research_competence  -- Q13a-i, Q14a-i: "Znam ..." self-rated research skills (18 items).
#   doz_2025_research_attitudes   -- Q15a-i, Q16a-m: attitudes towards research in teaching (22 items,
#     mixed wording, e.g. Q15a "Raziskovanja ne maram", Q16h "Raziskovanje je dolgočasno"; not reversed).
# Not shipped: Q12a-d (activities rated with a stem and anchors the export does not carry), Q17 free text.
# Covariates: cov_age (Q4, written in), cov_study_year (Q1). Q2/Q3/Q5-Q8 are coded with no key.
# id: row order. Respondents with no answer in a table are not in it.
# Item text: not shipped -- the Slovenian statements are in the export's first row, but the anchors are
#   not, and the Q9-Q11 statements look adapted from a published statistics-anxiety instrument that
#   has not been identified; recorded in itemtext_provenance.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/15692867/files/anketa104123-2024-07-07.xlsx/content"


def qs(q, letters):
    return [f"{q}{c}" for c in letters]


BLOCKS = {
    "doz_2025_statistics_attitudes": qs("Q9", "abcdefg") + qs("Q10", "abcde") + qs("Q11", "abcdefg"),
    "doz_2025_research_competence": qs("Q13", "abcdefghi") + qs("Q14", "abcdefghi"),
    "doz_2025_research_attitudes": qs("Q15", "abcdefghi") + qs("Q16", "abcdefghijklm"),
}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content))
    assert str(raw.iloc[0]["Q9a"]).startswith("Statistika zame")  # the wording row
    d = raw.iloc[1:].apply(pd.to_numeric, errors="coerce").reset_index(drop=True)
    assert len(d) == 194
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Q4"].where(d["Q4"] > 0)
    d["cov_study_year"] = d["Q1"].where(d["Q1"] > 0)
    covs = ["cov_age", "cov_study_year"]
    for name, items in BLOCKS.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert t["resp"].isin([-3, -1, 1, 2, 3, 4, 5]).all(), name
        t = t[t["resp"] > 0]
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
