"""Four-instrument battery from a Chinese college-student survey.

Source: Ye, L. (2025), Zenodo 10.5281/zenodo.18092016, CC BY 4.0 -- raw data
for "Imposter Phenomenon and Social Anxiety among College Students: The Chain
Mediating Roles of Self-Compassion and Shame". 1,408 respondents.

Four item blocks ship as four tables, delimited by the file's own summary
columns (`MM`, `TQ`, `XC`, `JL`, each the plain sum of the block before it,
plus `m*` means and `Z*` z-scores -- all dropped):

  ye_2025_mm   Q6-Q25    20 items, 1-5
  ye_2025_tq   Q26-Q37   12 items, 1-5
  ye_2025_xc   Q38-Q62   25 items, 1-4
  ye_2025_jl   Q63-Q75   13 items, 1-5

They cannot share a table: `XC` is on a 1-4 scale where the others are 1-5.

BLOCK NAMES ARE THE DEPOSIT'S OWN CODES, DELIBERATELY NOT CONSTRUCT NAMES.
Only Q1-Q5 carry variable labels; every item column is unlabelled, and the
record ships no codebook. The pinyin initials and item counts line up neatly
with the four constructs in the title -- MM/20@1-5 with the 20-item Clance IP
Scale, TQ/12@1-5 with the 12-item Self-Compassion Scale Short Form, XC
(xiuchi, shame) and JL (jiaolu, anxiety) with the other two -- and each
summary column's range is consistent with a simple sum of its block. But that
is inference from abbreviations, not evidence, so the codes are kept verbatim
rather than shipped as guessed construct names. Renaming is safe once someone
confirms the instruments against the paper.

Q1 is the single-valued consent checkbox and is dropped; Q2-Q5 are covariates.
"""
import os

import pandas as pd
import pyreadstat
import requests

RECORD = 18092016
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

# (table, first Q, last Q, allowed response levels)
BLOCKS = [
    ("ye_2025_mm", 6, 25, {1, 2, 3, 4, 5}),
    ("ye_2025_tq", 26, 37, {1, 2, 3, 4, 5}),
    ("ye_2025_xc", 38, 62, {1, 2, 3, 4}),
    ("ye_2025_jl", 63, 75, {1, 2, 3, 4, 5}),
]
COVARIATES = {"Q2": "cov_sex", "Q3": "cov_age_band",
              "Q4": "cov_year", "Q5": "cov_residence"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)
    vl = meta.variable_value_labels

    d = df.rename(columns=COVARIATES).copy()
    for src, dst in COVARIATES.items():
        if vl.get(src):
            # Strip the "A、"/"B、" option prefixes the survey tool emits.
            d[dst] = d[dst].map({k: str(v).split("、")[-1]
                                 for k, v in vl[src].items()})
    d["id"] = d["index"].astype(int)
    assert d["id"].is_unique, "index is not a unique person key"

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, lo, hi, scale in BLOCKS:
        cols = [f"Q{i}" for i in range(lo, hi + 1)]
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{table}: missing {missing}"

        observed = {v for v in pd.unique(d[cols].values.ravel()) if pd.notna(v)}
        assert observed <= scale, \
            f"{table}: off-scale response(s) {sorted(observed - scale)}"

        long = d.melt(id_vars=["id"] + list(COVARIATES.values()),
                      value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        out = long[["id", "item", "resp"] + list(COVARIATES.values())]
        out.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(out):,} responses | {out['id'].nunique():,} ids | "
              f"{out['item'].nunique()} items")


if __name__ == "__main__":
    main()
