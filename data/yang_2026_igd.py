from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0351550
# DOI: 10.1371/journal.pone.0351550
# Yang & Wang (2026), "Longitudinal associations between perceived
# benefits and costs of internet gaming and internet gaming disorder in
# adolescent gamers: A cross-lagged structural equation model". S1 Data.
# CC BY 4.0. N=1032 adolescent gamers, 2 waves.
# d23n1-9 (baseline) / Sd23n1-9 (follow-up): 9 raw DSM-5 IGD criteria
# items, binary endorsed/not (0/1).
# d28a-d (baseline) / Sd28a-d (follow-up): 4 raw perceived-benefit rating
# items, 1-10 scale.
# dIGD_S/sIGD_S/dG_IGD/sG_IGD (derived severity sum / diagnosis flag) are
# NOT shipped -- composite scores, not raw items, per datastandard.md.
# Cryptic demographic/education columns (v1, g46, G_g47, G_g49, edu_F,
# edu_M, D_g49_*, edu_F__*, edu_m__*) are undocumented in the file itself
# and not used as covariates; only age is unambiguous.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0351550.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

CRITERIA_ITEMS = {
    "d23n1": "crit1", "d23n2": "crit2", "d23n3_1": "crit3", "d23n4_1": "crit4",
    "d23n5": "crit5", "d23n6": "crit6", "d23n7": "crit7", "d23n8": "crit8", "d23n9": "crit9",
}
CRITERIA_ITEMS_W2 = {
    "Sd23n1": "crit1", "Sd23n2": "crit2", "Sd23n3": "crit3", "Sd23n4": "crit4",
    "Sd23n5": "crit5", "Sd23n6": "crit6", "Sd23n7": "crit7", "Sd23n8": "crit8", "Sd23n9": "crit9",
}
BENEFIT_ITEMS = {"d28a": "benefit_a", "d28b": "benefit_b", "d28c": "benefit_c", "d28d": "benefit_d"}
BENEFIT_ITEMS_W2 = {"Sd28a": "benefit_a", "Sd28b": "benefit_b", "Sd28c": "benefit_c", "Sd28d": "benefit_d"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def _wave_long(df, id_map, wave, cov):
    sub = df[["id", "cov_age"] + list(id_map.keys())].rename(columns=id_map)
    long = sub.melt(id_vars=["id", "cov_age"], var_name="item", value_name="resp")
    long["wave"] = wave
    return long


def convert():
    df = fetch()
    df = df.rename(columns={"age": "cov_age"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    crit = pd.concat([
        _wave_long(df, CRITERIA_ITEMS, 1, "cov_age"),
        _wave_long(df, CRITERIA_ITEMS_W2, 2, "cov_age"),
    ], ignore_index=True)
    crit["resp"] = pd.to_numeric(crit["resp"], errors="coerce")
    crit = crit.dropna(subset=["resp"]).reset_index(drop=True)
    crit = crit[["id", "item", "resp", "wave", "cov_age"]]
    crit.to_csv(OUT_DIR / "yang_2026_igd_criteria.csv", index=False)
    print(f"yang_2026_igd_criteria: rows={len(crit)} ids={crit['id'].nunique()} "
          f"items={crit['item'].nunique()} resp={crit['resp'].min():.0f}-{crit['resp'].max():.0f}")

    ben = pd.concat([
        _wave_long(df, BENEFIT_ITEMS, 1, "cov_age"),
        _wave_long(df, BENEFIT_ITEMS_W2, 2, "cov_age"),
    ], ignore_index=True)
    ben["resp"] = pd.to_numeric(ben["resp"], errors="coerce")
    ben = ben.dropna(subset=["resp"]).reset_index(drop=True)
    # A handful of cells hold the same repeated fractional value per item
    # (e.g. 4.44 x4, 5.04 x3) on an otherwise strictly-integer 1-10 scale --
    # a repeated-constant pattern consistent with mean/imputed substitution
    # for missing responses, not genuine raw ratings. Dropped.
    ben = ben[ben["resp"] % 1 == 0].reset_index(drop=True)
    ben = ben[["id", "item", "resp", "wave", "cov_age"]]
    ben.to_csv(OUT_DIR / "yang_2026_igd_benefits.csv", index=False)
    print(f"yang_2026_igd_benefits: rows={len(ben)} ids={ben['id'].nunique()} "
          f"items={ben['item'].nunique()} resp={ben['resp'].min():.0f}-{ben['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
