from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0238437
# DOI: 10.1371/journal.pone.0238437
# Lee & Kim (2020), "Usability of mental illness simulation involving
# scenarios with patients with schizophrenia via immersive virtual
# reality: A mixed methods study". S1 Data. CC BY 4.0. N=60.
# 17-item usability scale (0-10 scale). satisfaction_level/
# communication_competency/VR_experience are single categorical ratings,
# not part of the 17-item scale -- kept as text covariates rather than
# shipped as items (no single-item scales, per standing rule).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0238437.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Gender": "cov_gender", "grade_level": "cov_grade_level",
           "satisfaction_level": "cov_satisfaction_level",
           "communication_competency": "cov_communication_competency",
           "VR_experience": "cov_vr_experience"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def convert():
    df = fetch().rename(columns=COV_MAP)
    item_cols = [c for c in df.columns if c.startswith("Usability")]
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["ID"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long = long.rename(columns={"ID": "id"})
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "lee_2020_vr_usability.csv"
    long.to_csv(out_path, index=False)
    print(f"lee_2020_vr_usability: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
