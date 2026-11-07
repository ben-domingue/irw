#!/usr/bin/env python3
# Source: https://zenodo.org/records/8326513 (concept DOI 10.5281/zenodo.8320738)
# DOI: 10.1371/journal.pone.0293608
# Paper: Kabir MR, Mahmud H, Hasan MK (2023). Acceptability of a head-mounted
#   assistive mouse controller for people with upper limb disability: An
#   empirical study using the technology acceptance model. PLoS ONE 18(10):
#   e0293608.
# Data: Zenodo record 8326513, "TAM survey questionnaire responses of a
#   head-mounted assistive mouse controller for people with upper limb
#   disability" (the article's Data Availability statement names the concept
#   DOI 10.5281/zenodo.8320738), one CSV, 150 participants P1..P150, plus
#   TAM_Questionnaires.pdf (the item wording).
# License: CC BY 4.0 on the DEPOSIT (Zenodo record metadata, cc-by-4.0); the
#   article is also CC BY 4.0.
#
# Worked from the cleaned leads list of 2026-11-07 (rank 20; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# SIX output tables, one per TAM construct with at least three items. Every
# item is on the paper's 4-point scale: "1 -- Strongly Disagree, 2 --
# Disagree, 3 -- Agree, and 4 -- Strongly Agree" (no neutral point, by design).
# Item codes are the deposit's own headers, which are the codes in the
# questionnaire PDF's Table 1.
#   kabir_2023_tam_pu   Perceived Usefulness, PU1-PU3 (PU1 holds 2-4 only)
#   kabir_2023_tam_peu  Perceived Ease of Use, PEU1-PEU4
#   kabir_2023_tam_atu  Attitude Towards Usage, ATU1-ATU6
#   kabir_2023_tam_ta   Technology Anxiety, TA1-TA5
#   kabir_2023_tam_pi   Personal Innovativeness, PI1-PI3
#   kabir_2023_tam_bi   Behavioral Intention, BI1-BI3
# Dropped: Subjective Norm (SN1, SN2) and Perceived Behavioral Control (PBC1,
#   PBC2) -- two items each, under the 3-item floor (datastandard.md).
# No covariates in the deposit. `id` is the row index (P1..P150 in order).
#
# Item text: NOT SHIPPED. The full wording is in the deposit's
#   TAM_Questionnaires.pdf (Table 1), but its footnotes mark items as adopted
#   from, adapted from, or new relative to prior TAM studies (Davis 1989;
#   Venkatesh & Davis 2000; others), so the rights basis is mixed and was not
#   resolved in this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
FNAME = "TAM_survey questionnaire responses of a head-mounted assistive mouse controller for people with upper limb disability.csv"
URL = "https://zenodo.org/records/8326513/files/" + requests.utils.quote(FNAME) + "?download=1"
RAW = os.environ.get("KABIR_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SCALES = {
    "pu": ["PU1", "PU2", "PU3"],
    "peu": ["PEU1", "PEU2", "PEU3", "PEU4"],
    "atu": [f"ATU{k}" for k in range(1, 7)],
    "ta": [f"TA{k}" for k in range(1, 6)],
    "pi": ["PI1", "PI2", "PI3"],
    "bi": ["BI1", "BI2", "BI3"],
}
DROPPED = ["SN1", "SN2", "PBC1", "PBC2"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src)


def convert():
    df = load()
    assert len(df) == 150 and (df["Participant"] == [f"P{k}" for k in range(1, 151)]).all()
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["Participant"]
    used = {"Participant"} | set(DROPPED) | {c for v in SCALES.values() for c in v}
    assert used == set(df.columns), set(df.columns) ^ used
    df["id"] = range(1, len(df) + 1)
    names = []
    for key, items in SCALES.items():
        long = df[["id"] + items].melt(id_vars=["id"], var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4}
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        name = f"kabir_2023_tam_{key}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(set(names)) == len(names)
    print(f"dropped (2-item constructs): {DROPPED}")


if __name__ == "__main__":
    convert()
