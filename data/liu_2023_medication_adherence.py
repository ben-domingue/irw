#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10693237
# DOI: 10.7717/peerj.16384
#
# Liu et al. (2023), "Hypertension doctors' awareness and practice of
# medication adherence in hypertensive patients: a questionnaire-based
# survey." PeerJ. CC BY 4.0. N=236 hypertension doctors (Methods: "In
# total, 236 valid questionnaires were collected").
# Supplementary file peerj-11-16384-s001.sav is a Chinese-language
# self-report questionnaire with several distinct raw-item batteries
# (value labels read from the .sav confirm each is a genuine ordinal/
# binary scale, not free text), split per datastandard.md's "one file per
# scale" rule. Single-item questions (Q15, Q17-Q19, Q22-Q23, Q25, Q27-Q28)
# are excluded per the "no single-item scales" rule. The pre-computed
# "认知分"/"实践分" (awareness/practice) composite scores are excluded as
# aggregates. No PII in the file (professional respondents, no names/IDs
# beyond a sequential serial number).
#
# Batteries shipped (item text translated from the source column names):
#   Q14 training_freq   (6 items) -- frequency of related training received,
#                          1 (never) - 5 (always)
#   Q16 poor_adherence   (6 items) -- situations of poor medication
#                          adherence, multi-select: 0 (not selected) / 1
#                          (selected)
#   Q20 adherence_tools  (3 items) -- clarity about adherence-assessment
#                          scales/tools, 1 (not clear) - 5 (very clear)
#   Q21 adherence_factors(4 items) -- importance of factors affecting
#                          patient adherence, 1 (very important) - 5 (not
#                          important)
#   Q24 improve_adherence(7 items) -- frequency of actions taken to improve
#                          patient adherence, 1 (never) - 5 (always)
#   Q26 adherence_barrier(7 items) -- factors that hinder doctors from
#                          improving patient adherence, multi-select: 0/1

import io
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10693237/supplementaryFiles"
MEMBER = "peerj-11-16384-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

BATTERIES = [
    ("Q14相关培训", 6, "liu_2023_training_freq.csv"),
    ("Q16药物依从性不佳的情况", 6, "liu_2023_poor_adherence.csv"),
    ("Q21影响患者药物依从性的因素", 4, "liu_2023_adherence_factors.csv"),
    ("Q24提高患者药物依从性", 7, "liu_2023_improve_adherence.csv"),
    ("Q26哪些因素是医生提高患者药物依从性的阻力", 7, "liu_2023_adherence_barrier.csv"),
]
Q20_COLS = ["Q20量表或工具1", "Q20_量表或工具2", "Q20_量表或工具3"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    data = zf.read(MEMBER)
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(data)
        tmp.flush()
        df, meta = pyreadstat.read_sav(tmp.name)
    df = df.rename(columns={"序号": "id"})
    assert df["id"].nunique() == len(df)
    return df


def write_battery(df: pd.DataFrame, cols: list[str], item_prefix: str, out_name: str):
    sub = df[["id"] + cols].copy()
    sub.columns = ["id"] + [f"{item_prefix}_{i + 1}" for i in range(len(cols))]
    long = sub.melt(id_vars="id", var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_raw()
    for prefix, n_items, out_name in BATTERIES:
        cols = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        item_prefix = out_name.replace(".csv", "")
        write_battery(df, cols, item_prefix, out_name)
    write_battery(df, Q20_COLS, "liu_2023_adherence_tools", "liu_2023_adherence_tools.csv")


if __name__ == "__main__":
    convert()
