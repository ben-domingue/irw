from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0184488
# DOI: 10.1371/journal.pone.0184488
# Kuehner, Welz, Reinhard et al. (2017), "Lab meets real life: A
# laboratory assessment of spontaneous thought and its ecological
# validity". S3 File (person-period, 50 probes/person). CC BY 4.0.
#
# Resolves the "ambiguous t0_*/DoM/ToM labels" note from the original
# retriage: the t0_DoM/t0_ToM/t0_Self/t0_Plan/t0_Sleep/t0_Comfort/
# t0_SomAw/t0_Health/t0_Visual/t0_Verbal columns have unlabeled,
# fractional values (e.g. 0.333, 3.667) consistent with already-averaged
# per-probe composite indices, not raw single items -- not shipped.
# positive_affect/negative_affect (range 6-42) are PANAS-6 sum scores,
# also composite -- not shipped. CESD_sum/STAIT_sum/RSQ_*_sum/MAAS_sum are
# baseline trait-total scores, not raw items -- not shipped. Only two
# columns are genuine single-value raw momentary ratings per probe: MW
# (mind-wandering intensity, 1-7) and RUM (rumination intensity, 1-7).
# Shipped together as a 2-item experience-sampling battery (both
# administered at every probe) rather than as two single-item tables,
# per the no-single-item-scale rule. wave = probe sequence number within
# person (1-50).
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0184488.s004")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"age": "cov_age", "sex": "cov_sex"}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch().rename(columns={"PbnID": "id", **COV_MAP})
    cov_cols = list(COV_MAP.values())
    df["wave"] = df.groupby("id").cumcount() + 1

    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=["MW", "RUM"],
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "kuehner_2017_mw_rumination.csv"
    long.to_csv(out_path, index=False)
    print(f"kuehner_2017_mw_rumination: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
