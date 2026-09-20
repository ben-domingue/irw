#!/usr/bin/env python3
"""Well-being instruments from a Canadian COVID-19 pet-ownership survey.

Source: https://www.nature.com/articles/s41598-022-10019-z
DOI: 10.1038/s41598-022-10019-z
Data: https://osf.io/56sbh/ (file "Leger sociodresub.sav")
License: CC BY 4.0 (Crossref; the triage row read `unknown`, which was the
         connector defect fixed in this batch)

2,424 respondents from Léger's LEO probability-based Canadian panel, April
2020. Five standard instruments, one table each:

  amiot_2022_ucla_loneliness  UCLA Loneliness Scale, 20 items, 1-4
  amiot_2022_pss14            Perceived Stress Scale, 14 items, 1-5
  amiot_2022_vitality         Subjective Vitality Scale, 7 items, 1-7
  amiot_2022_swls             Satisfaction With Life Scale, 5 items, 1-7
  amiot_2022_mlq_presence     Meaning in Life Questionnaire (presence), 5, 1-7

The deposit's variable name `anxiety1..14` is the survey's own label, but the
items are the Perceived Stress Scale's ("how often have you felt nervous and
stressed", "...felt that difficulties were piling up"), so the table is named
for the instrument rather than for the column prefix.

RAW COLUMNS ONLY. The deposit ships reverse-scored copies (`lone1_r`,
`anxiety4_r`, `vital2_r`, `lifemean9_r`) and a per-scale composite under the
bare prefix (`lone`, `anxiety`, `vital`, `Lifesat`, `lifemean`). Both are
excluded: the composite is not a response, and the standard's rule is to keep
reverse-worded items in their raw direction rather than recoding them.

The MLQ block is items 1, 4, 5, 6 and 9 of the published instrument -- the
presence-of-meaning subscale. The numbering is kept as the source has it
rather than renumbered 1-5, so the codes still point at the published item.

Missing data are genuine and are dropped, not filled: 5-24 NaN per item, and
the paper describes no imputation (searched for "imput", "missing",
"listwise", "complete case" -- no hits).

Item text: NOT SHIPPED, and the reason is rights, not availability. The
deposit is in fact an ideal data_labels source -- every item carries its full
stem in the SPSS variable label, and four of the five blocks carry a value
label for every scale point. But `itemtext/instrument_rights_register.csv`
already rules on three of these instruments corpus-wide:

  Perceived Stress Scale (PSS-4/10/14)   block  2026-09-06 irw#1955
  Meaning in Life Questionnaire (MLQ)    block  2026-09-08 irw#1945
  Satisfaction With Life Scale (SWLS)    block  2026-09-09

Those rulings turn on the rights holder's own terms and are not overridden by
this deposit's CC BY licence -- that is the settled position since the DSES
ruling of 2026-09-04: a quotable restriction from the rights holder outranks
the licence of the deposit the words were copied from.

The Subjective Vitality Scale falls under the Center for Self-Determination
Theory entry, which Ben ruled on 2026-09-09 covers the whole CSDT library
("the theories, metrics, measurements, scales, publications and other
tools"), so it is blocked too -- and it is the one block with no value labels
anyway.

That leaves the UCLA Loneliness Scale, which is NOT in the register and has
no verdict either way. It is not shipped here because it needs the quote test
run against Russell's own distribution first, which is the same open question
already parked on `tatala_2023_ucla_loneliness`. Doing it once settles both.
Flagged in TODO.md.
"""
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
DATA_URL = ("https://osf.io/download/2wpxc/"
            "?view_only=bbca7561fdff46618666454a0d66c892")
UA = {"User-Agent": "irw-batch/1.0 (research)"}
SAV = Path("/tmp/irw_amiot_2022.sav")

SCALES = {
    "amiot_2022_ucla_loneliness": ([f"lone{i}" for i in range(1, 21)], (1, 4)),
    "amiot_2022_pss14":           ([f"anxiety{i}" for i in range(1, 15)], (1, 5)),
    "amiot_2022_vitality":        ([f"vital{i}" for i in range(1, 8)], (1, 7)),
    "amiot_2022_swls":            ([f"Lifesat{i}" for i in range(1, 6)], (1, 7)),
    "amiot_2022_mlq_presence":    ([f"lifemean{i}" for i in (1, 4, 5, 6, 9)], (1, 7)),
}
COV_COLS = {"age": "cov_age_band", "gender": "cov_gender",
            "petOwn": "cov_pet_owner", "EDUC": "cov_education",
            "INCOME": "cov_income_band", "Q0": "cov_survey_language"}


def load() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    SAV.write_bytes(r.content)
    df, _ = pyreadstat.read_sav(str(SAV))
    SAV.unlink()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)   # the deposit carries no id column
    return df


def convert() -> None:
    raw = load()
    cov = raw[["id"] + list(COV_COLS)].rename(columns=COV_COLS)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (item_cols, (lo, hi)) in SCALES.items():
        missing = [c for c in item_cols if c not in raw.columns]
        assert not missing, f"{table}: missing columns {missing}"
        # Guard against picking up a reverse-scored copy or the composite.
        assert not any(c.endswith("_r") for c in item_cols), table

        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        dropped = int(long["resp"].isna().sum())
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), f"{table}: resp outside {lo}-{hi}"
        assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
        assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
        assert long["item"].nunique() == len(item_cols), f"{table}: item count changed"
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, [(c.name, c.detail) for c in bad]

        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()} (dropped {dropped} missing)")


if __name__ == "__main__":
    convert()
