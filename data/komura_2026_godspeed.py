from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0340449
# DOI: 10.1371/journal.pone.0340449
# Komura & Yamada (2026), "Deepening ideas vs. exploring new ones: AI
# strategy effects in human-AI creative collaboration". S3 File. CC BY
# 4.0. N=148. Two validated instruments administered together: the
# Godspeed Questionnaire Series (GQS; Bartneck et al.) -- 5 subscales,
# 1-5 semantic-differential scale -- and the Multi-Dimensional Measure of
# Trust (MDMT; Ullman & Malle) -- 4 subscales, 0-7 scale. Shipped as 9
# separate scale files per datastandard.md's one-scale-per-file rule.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0340449.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"participantInfo_age": "cov_age", "participantInfo_gender": "cov_gender",
           "aitype": "cov_aitype"}

SCALES = {
    "komura_2026_gqs_anthropomorphism": [f"gqs_anthropomorphism_{i}" for i in range(1, 6)],
    "komura_2026_gqs_animacy": [f"gqs_animacy_{i}" for i in range(1, 6)],
    "komura_2026_gqs_likeability": [f"gqs_likeability_{i}" for i in range(1, 6)],
    "komura_2026_gqs_perceived_intelligence": [f"gqs_perceived_intelligence_{i}" for i in range(1, 6)],
    "komura_2026_gqs_perceived_safety": [f"gqs_perceived_safety_{i}" for i in range(1, 4)],
    "komura_2026_mdmt_reliable": [f"mdmt_reliable_{i}" for i in range(1, 5)],
    "komura_2026_mdmt_capable": [f"mdmt_capable_{i}" for i in range(1, 5)],
    "komura_2026_mdmt_ethical": [f"mdmt_ethical_{i}" for i in range(1, 5)],
    "komura_2026_mdmt_sincere": [f"mdmt_sincere_{i}" for i in range(1, 5)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={**COV_MAP, "sessionId": "id"})
    return df


def convert():
    df = fetch()
    cov_cols = list(COV_MAP.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
