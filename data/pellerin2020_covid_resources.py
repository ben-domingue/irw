from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Psychological Resources Protect Well-Being During the COVID-19 "
         "Pandemic: A Longitudinal Study During the French Lockdown "
         "(Pellerin & Raufaste, 2020, Frontiers in Psychology)")
URL  = "https://osf.io/45aq3/"
DOI  = "10.3389/fpsyg.2020.590276"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://osf.io/download/dc6me/"

# Nine psychological-resource instruments administered at Wave 0 (baseline,
# "wave 1" in the paper) and Wave 5 (final follow-up, "wave 6" in the paper)
# only -- items are 100% NaN at Waves 1-4 (weekly threat/well-being-only
# follow-ups), confirmed empirically before writing this script. All use a
# 1-7 Likert ("strongly disagree".."strongly agree") except Acceptance,
# which uses 1-5 ("never".."always") per the paper.
SCALES = {
    # CPC-12 (Compound Psychological Capital questionnaire, Lorenz et al. 2016)
    # -- the paper treats its three facets as three separate resource variables.
    "pellerin2020_cpc_hope":          [f"Hope_{i}" for i in range(1, 4)],
    "pellerin2020_cpc_optimism":      [f"Opt_{i}"  for i in range(1, 4)],
    "pellerin2020_cpc_selfefficacy":  [f"SAE_{i}"  for i in range(1, 4)],
    # 3D-WS-12 (12-item Abbreviated Three-Dimensional Wisdom Scale, Thomas
    # et al. 2017) -- the paper combines all three facets into one "personal
    # wisdom" score, so kept as a single file rather than split by facet.
    "pellerin2020_3dws": ([f"Cog_{i}" for i in range(1, 5)]
                           + [f"Refl_{i}" for i in range(1, 5)]
                           + [f"Aff_{i}" for i in range(1, 5)]),
    # ASTI (Adult Self-Transcendence Inventory, Koller et al. 2017)
    # -- self-transcendence dimension only (7 of its items).
    "pellerin2020_asti": [f"ST_{i}" for i in range(1, 8)],
    # GQ-6 (Gratitude Questionnaire-6, McCullough et al. 2002; French version)
    "pellerin2020_gq6": [f"GQ_{i}" for i in range(1, 7)],
    # Minimalist Well-Being Scale (Kan et al. 2009) -- the paper treats its
    # two facets as two separate resource variables.
    "pellerin2020_mwbs_gratbeing": [f"Mini_G{i}"  for i in range(1, 5)],
    "pellerin2020_mwbs_pd":        [f"Mini_PD{i}" for i in range(1, 8)],
    # Brief Serenity Scale, Acceptance dimension (Kreitzer et al. 2009)
    "pellerin2020_serenity_acceptance": [f"Acc_{i}" for i in range(1, 9)],
}

COV_COLS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Income": "cov_income",
    "Country": "cov_country",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content))
    return df.rename(columns={"ID": "id", "Wave": "wave"})


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame) -> pd.DataFrame:
    items = raw[["id", "wave"] + item_cols]
    cov_cols = list(cov.columns.drop("id"))
    long = items.merge(cov, on="id").melt(
        id_vars=["id", "wave"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp", "wave"] + cov_cols
    return long[col_order].sort_values(["id", "wave", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading data.PsyR_lockdown2020.csv ...")
    raw = fetch_data()
    # Country/Gender/Age/Income are only populated on the row(s) where they
    # were actually collected (mostly wave 0) -- forward/back-fill within
    # each id before collapsing to one covariate row per person.
    cov_raw = raw[["id"] + list(COV_COLS.keys())].sort_values("id")
    cov_raw[list(COV_COLS.keys())] = (
        cov_raw.groupby("id")[list(COV_COLS.keys())].transform(lambda s: s.ffill().bfill())
    )
    cov = cov_raw.rename(columns=COV_COLS).drop_duplicates("id")

    for table, item_cols in SCALES.items():
        write_scale(_melt_scale(raw, item_cols, cov), f"{table}.csv")


if __name__ == "__main__":
    convert()
