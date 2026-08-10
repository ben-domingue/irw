from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269201
# DOI: 10.1371/journal.pone.0269201
# Busch, Mohammed, Nadile & Cooper (2022), "Aspects of online college
# science courses that alleviate and exacerbate undergraduate depression".
# S1 Dataset (.csv). CC BY 4.0. N=2175 undergraduates; the course-aspect
# checklist items were only shown to the 1179 respondents who reported
# depression symptoms while taking online science courses, so all other
# rows are NaN on these items and drop out during melt.
# Two distinct binary (0/1) checklist item sets, shipped as two tables per
# datastandard.md's "multiple scales in one file" rule:
#   - idep.* (17 items): course aspects that EXACERBATE depression
#   - ddep.* (13 items): course aspects that ALLEVIATE depression
# `severity.depression.online` (single 4-point item) is kept as a
# covariate, not a table, per the "no single-item scales" rule.
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269201.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "GPA": "cov_gpa",
    "STEM.major.clean": "cov_stem_major",
    "race2": "cov_race",
    "division": "cov_division",
    "gender2": "cov_gender",
    "gen.stat2": "cov_generation_status",
    "lgbtq2": "cov_lgbtq",
    "financially.stable2": "cov_financially_stable",
    "severity.depression.online": "cov_depression_severity",
}


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"] + cov_names]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_COLS)

    idep_cols = [c for c in df.columns if c.startswith("idep.")]
    ddep_cols = [c for c in df.columns if c.startswith("ddep.")]

    for name, cols in [
        ("busch_2022_course_exacerbate", idep_cols),
        ("busch_2022_course_alleviate", ddep_cols),
    ]:
        long = build_long(df, cols)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
