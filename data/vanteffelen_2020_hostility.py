from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239631
# DOI: 10.1371/journal.pone.0239631
# van Teffelen, Lobbestael, Voncken & Peeters (2020), "Uncovering the
# hierarchical structure of self-reported hostility". S1 Data (.sav). CC BY
# 4.0. N=376 (347 community + 29 clinical, Dutch sample). Five distinct
# instruments in one file, shipped as five separate tables per
# datastandard.md's "multiple scales in one file" rule:
#   - PID_1-10  (10 items, 0-3): PID-5 hostility facet (PID-5H)
#   - TA_1-10   (10 items, 1-4): STAXI-2 Trait Anger
#   - HOS_1-8   (8 items,  1-5): Aggression Questionnaire hostility subscale
#   - AGG_1-40  (40 items, 1-5): Forms of Aggression Questionnaire (FOA)
#   - RPQ_1-23  (23 items, 1-3): Reactive-Proactive Aggression Questionnaire
# Item text in the source file is Dutch; original column codes are kept as
# item names since they are already short, meaningful identifiers.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0239631.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "gender": "cov_gender",
    "age": "cov_age",
    "nationality": "cov_nationality",
    "education": "cov_education",
    "work": "cov_work",
    "Sample": "cov_sample",  # 1=community, 2=clinical
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
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)
    df = df.rename(columns={"ID": "id", **COV_COLS})

    pid_cols = [c for c in df.columns if c.startswith("PID_")]
    ta_cols = [c for c in df.columns if c.startswith("TA_")]
    hos_cols = [c for c in df.columns if c.startswith("HOS_")]
    agg_cols = [c for c in df.columns if c.startswith("AGG_")]
    rpq_cols = [c for c in df.columns if c.startswith("RPQ_")]

    for name, cols in [
        ("vanteffelen_2020_pid5_hostility", pid_cols),
        ("vanteffelen_2020_trait_anger", ta_cols),
        ("vanteffelen_2020_aq_hostility", hos_cols),
        ("vanteffelen_2020_foa", agg_cols),
        ("vanteffelen_2020_rpq", rpq_cols),
    ]:
        long = build_long(df, cols)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
