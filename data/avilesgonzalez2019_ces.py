from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Cultural adaptation and psychometric validation of the Caring "
         "Efficacy scale in a sample of Italian nurses (Aviles Gonzalez "
         "et al., 2019, PLOS ONE)")
URL  = "https://plos.figshare.com/articles/dataset/Cultural_adaptation_and_psychometric_validation_of_the_Caring_Efficacy_scale_in_a_sample_of_Italian_nurses/8177303"
DOI  = "10.1371/journal.pone.0217106"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/15243404"

# Caring Efficacy Scale (Coates, 1997), 30 items, 1-6 Likert. A second block
# of 13 all-caps-named items (FEELING, MIXEDFEELING, UNDERCONTROL, ...) also
# exists in the same file but its instrument identity isn't confirmed --
# left unprocessed, flagged for human review separately.
VALID_MAX = 6
CES_ITEM_COLS = [
    "confident", "relation", "touch", "transmit", "shocked", "normalcy",
    "listening", "prejudice", "serenity", "concern", "relationwithothers",
    "lackconfidence", "talk", "learn", "strong", "selfconfidence", "problem",
    "closerealtion", "like", "pointofview", "resolve", "uneasy", "relate",
    "culture", "meaningfulrelation", "empathy", "overwhelmed", "comunication",
    "reallytry", "creativity",
]

COV_COLS = {
    "gender": "cov_gender",
    "department": "cov_department",
    "age": "cov_age",
    "experience": "cov_experience",
    "education": "cov_education",
    "contractual": "cov_contract_type",
    "shifts": "cov_shifts",
}


def convert():
    print("Downloading pone.0217106.s002.sav ...")
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_spss(pd.io.common.BytesIO(r.content), convert_categoricals=False)
    raw = raw.rename(columns={"ID": "id"})
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    items = raw[["id"] + CES_ITEM_COLS].merge(cov, on="id")
    long = items.melt(
        id_vars=["id"] + cov_cols,
        value_vars=CES_ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # A single out-of-range value (resp=7, 1 of 6449 rows) sits just past the
    # documented 1-6 CES scale -- a data-entry artifact, not a real scale
    # point (confirmed: every other value cleanly falls in 1-6).
    long = long[(long["resp"] >= 1) & (long["resp"] <= VALID_MAX)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "avilesgonzalez2019_ces.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
