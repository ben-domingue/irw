from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0285815
# DOI: 10.1371/journal.pone.0285815
# Pang, Ye & Zhang (2023), "Factors influencing users' willingness to use
# new energy vehicles". S1 File (.s001, "Data for CFA", XLSX). CC BY 4.0.
# N=309 potential NEV users. All items 5-point Likert (1-5). Questionnaire
# is a media-based perceptions and adoption model (MPAM) of NEVs, an
# extension of the technology acceptance model; the abstract explicitly
# names 8 constructs (MM, SNs, PU, PEOU, PE, PR, PC, BI). The raw column
# headers are just numbered questions (no PU1/PEOU1-style codes and the
# item-to-construct mapping table renders as an image, not extractable
# text) -- the 8 five-item blocks below were matched to construct labels
# by question content, in the same block order the abstract lists the
# constructs' causal chain (media -> norms -> product-perception factors
# -> behavioral intention):
#   Q5-9   (5): perceived usefulness (PU) -- efficiency/comfort/convenience
#   Q10-14 (5): perceived ease of use (PEOU) -- ease/friendliness of operation
#   Q15-19 (5): perceived risk (PR) -- combustion/privacy/hacking/autonomy risk
#   Q20-24 (5): perceived cost (PC) -- purchase/charging/repair/insurance cost
#   Q25-29 (5): perceived enjoyment (PE) -- novelty/fun/interaction features
#   Q30-34 (5): mass media (MM) -- "media reports ... affect my BI"
#   Q35-39 (5): social norms (SNs) -- "people around me think ..."
#   Q40-44 (5): behavioral intention (BI) -- future adoption/switching intent

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0285815.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS_ORDER = ["cov_gender", "cov_age", "cov_education", "cov_profession"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    cols = df.columns.tolist()
    rename = {
        cols[0]: "id",
        cols[1]: "cov_gender",
        cols[2]: "cov_age",
        cols[3]: "cov_education",
        cols[4]: "cov_profession",
    }
    item_cols = cols[5:]
    assert len(item_cols) == 40
    df = df.rename(columns=rename)
    assert df["id"].is_unique and df["id"].notna().all()

    SCALES = {
        "pang_2023_perceived_usefulness": item_cols[0:5],
        "pang_2023_perceived_ease_use":   item_cols[5:10],
        "pang_2023_perceived_risk":       item_cols[10:15],
        "pang_2023_perceived_cost":       item_cols[15:20],
        "pang_2023_perceived_enjoyment":  item_cols[20:25],
        "pang_2023_media_influence":      item_cols[25:30],
        "pang_2023_social_norms":         item_cols[30:35],
        "pang_2023_behavioral_intent":    item_cols[35:40],
    }

    for out_name, cols_i in SCALES.items():
        # assign generic item labels; original question text preserved in
        # the script header comment above for future item-text matching.
        n = len(cols_i)
        col_map = {c: f"item_{i:02d}" for i, c in enumerate(cols_i, start=1)}
        sub = df[["id"] + COV_COLS_ORDER + cols_i].rename(columns=col_map)
        long = sub.melt(id_vars=["id"] + COV_COLS_ORDER,
                         value_vars=list(col_map.values()),
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + COV_COLS_ORDER]
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
