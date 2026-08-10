from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0265880
# DOI: 10.1371/journal.pone.0265880
# Iqbal et al. (2022), "How curriculum delivery translates into
# entrepreneurial skills: The mediating role of knowledge of information
# and communication technology". S1 File. CC BY 4.0. N=482, all items
# 1-7 Likert. Constructs: entrepreneurial skills (ES1-9); curriculum
# delivery -- objectives (CO1-3), content mastery (CM1-7), teaching
# strategies (TS1-6), feedback/assessment (FA1-6); ICT knowledge (ICT1-7).
# Three isolated single-cell outliers (CM3=23, CM5=32, ICT2=32) fall far
# outside the 1-7 range used everywhere else on those items and are
# dropped as data-entry errors (single respondent/item each), consistent
# with datastandard.md's "data entry errors at known values" guidance.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0265880.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Background": "cov_background",
    "Gender": "cov_gender",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Case ID": "id", **COV_COLS})

    item_cols = ([f"ES{i}" for i in range(1, 10)]
                 + [f"CO{i}" for i in range(1, 4)]
                 + [f"CM{i}" for i in range(1, 8)]
                 + [f"TS{i}" for i in range(1, 7)]
                 + [f"FA{i}" for i in range(1, 7)]
                 + [f"ICT{i}" for i in range(1, 8)])
    missing = [c for c in item_cols if c not in df.columns]
    assert not missing, f"missing expected item columns: {missing}"

    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "iqbal_2022_curriculum_skills.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
