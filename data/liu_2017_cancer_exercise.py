from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0169375
# DOI: 10.1371/journal.pone.0169375
# Liu, Zhang, Shi et al. (2017), "Objectively Assessed Exercise Behavior
# in Chinese Patients with Early-Stage Cancer". S1 File. CC BY 4.0. N=350.
#
# No item-level variable labels in the file, but each block's own
# subscale-total columns (e.g. "Copetotal", "Cconfronce/Cavoidance/
# Cresigntion") confirm 7 distinct raw-item instruments -> 7 output files.
# Two are confidently identified by their exact subscale structure: `cope`
# (20 items, Confrontation/Avoidance/Resignation subscales) matches the
# Medical Coping Modes Questionnaire (MCMQ); `S` (10 items, Objective/
# Subjective/Utilization subscales) matches the Social Support Rating
# Scale (SSRS) -- SSRS's own items legitimately have different per-item
# ranges, hence the wide 1-20 pooled range. `Q` (27 items, Physical-daily/
# Social-family/Emotion/Function subscales) plausibly a FACT-G-style QoL
# measure (27 items matches FACT-G's item count) but not shipped under
# that name since it isn't confirmed from the file itself. `communication`
# (3i), `D` (7i), `O` (6i), `B` (22i, Acceptance/Family/World/Personal/
# Social/Health subscales, likely a benefit-finding scale) are shipped
# under generic names -- true instrument names for D/O/B/Q not confirmed,
# worth a second pass with the paper's Methods text.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0169375.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"AGE": "cov_age", "GENDER": "cov_gender", "NATION": "cov_nation"}

SCALES = {
    "liu_2017_communication": ("communication", 3),
    "liu_2017_mcmq_coping": ("cope", 20),
    "liu_2017_scale_d": ("D", 7),
    "liu_2017_scale_o": ("O", 6),
    "liu_2017_ssrs_support": ("S", 10),
    "liu_2017_benefit_finding": ("B", 22),
    "liu_2017_qol": ("Q", 27),
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch().rename(columns={"NO": "id", **COV_MAP})
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, (prefix, n) in SCALES.items():
        item_cols = [f"{prefix}{i}" for i in range(1, n + 1) if f"{prefix}{i}" in df.columns]
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
