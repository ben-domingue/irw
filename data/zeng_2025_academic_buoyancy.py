from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0318347
# DOI: 10.1371/journal.pone.0318347
# Zeng & Zhong (2025), "Overlap or breakthrough? exploration of the
# academic buoyancy structure in Chinese EFL learners". S1/S2 Files. CC BY
# 4.0. Two separate samples: S1 = EFA sample (N=209, all 32 candidate
# items B1-B32); S2 = CFA sample (N=423, the 21-item subset retained after
# EFA item reduction). Shipped as two tables since the item sets and
# samples differ -- not the same instrument administered twice.
FILES = {
    "zeng_2025_academic_buoyancy_efa": ("https://journals.plos.org/plosone/article/file"
                                         "?type=supplementary&id=10.1371/journal.pone.0318347.s001"),
    "zeng_2025_academic_buoyancy_cfa": ("https://journals.plos.org/plosone/article/file"
                                         "?type=supplementary&id=10.1371/journal.pone.0318347.s002"),
}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, url in FILES.items():
        r = requests.get(url, headers=UA, timeout=120)
        r.raise_for_status()
        df = pd.read_excel(io.BytesIO(r.content))
        gender_col = "gender" if "gender" in df.columns else "Gender"
        df = df.rename(columns={gender_col: "cov_gender", "No.": "id"})
        item_cols = [c for c in df.columns if c.startswith("B")]
        long = df.melt(id_vars=["id", "cov_gender"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_gender"]]
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
