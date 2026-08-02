from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0346229
# DOI: 10.1371/journal.pone.0346229
# Wang et al. (2026), "Exploring EFL primary school teachers' behavioral
# intention towards digital game-based learning". S2 Appendix. CC BY 4.0.
# N=500. Standard Technology-Acceptance-Model (TAM) battery, 5 constructs,
# 1-5 Likert: Perceived Usefulness (PU, 3i), Teaching Presence (TP, 8i),
# Technology Anxiety (TA, 3i), Attitude (ATT, 3i), Behavioral Intention
# (BI, 5i) -- construct names inferred from the column-prefix codes and
# the paper's own TAM framing, not confirmed against item text.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0346229.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Pedagogical tenure": "cov_pedagogical_tenure"}

SCALES = {
    "wang_2026_perceived_usefulness": ["PU1", "PU2", "PU3"],
    "wang_2026_teaching_presence": [f"TP{i}" for i in range(1, 9)],
    "wang_2026_technology_anxiety": ["TA1", "TA2", "TA3"],
    "wang_2026_attitude": ["ATT1", "ATT2", "ATT3"],
    "wang_2026_behavioral_intention": [f"BI{i}" for i in range(1, 6)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
