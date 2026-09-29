#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.29815862
# DOI: 10.3390/bs15091237
#   "Psychometric Adaptation and Validity of the Resistance to Peer Influence
#   Scale Among Young Chinese Drivers and Its Links with Peer Pressure and
#   Risky Driving Behaviours" (Li, Liu, Wang & Sun, 2025), Behavioral
#   Sciences 15(9):1237.
# Data: figshare 29815862 (depositor Wenchengxu Li), single file
#       "8.2RPI&Risky driviing.xls" (269 x 72). Young drivers, Dalian, China.
# License: CC BY 4.0 (figshare record; article CC BY 4.0).
#
# Item text: not shipped. The .xls carries bare codes (a1.., R1..) and no
#   labels (both label levels absent: xls has neither). The paper prints one
#   sample item per subscale (2.2.1-2.2.4); the RPI wording is in the paper's
#   Supplementary Table S1 (MDPI /s1, "item description"), not fetched, and is
#   the two-sided Steinberg & Monahan format. Administered in Chinese.
#
# Tables (block -> composite column in the file, asserted: block mean ==
#   composite on every row):
#   li_2025_rpi             Resistance to Peer Influence, R1-R10, 1-4 (choose
#                           a side, then "sort of" / "really" true) -> RPI
#   li_2025_pprds           Peer Pressure on Risky Driving Scale, Chinese
#                           version: a1-a6 risk-encouraging direct (RED),
#                           b1-b5 risk-discouraging direct (RDD), c1-c9
#                           indirect (IDD); 20 items, 1-5
#   li_2025_sdcaf           Safe Driving Climate among Friends, Chinese
#                           version: d1-d4 shared commitment (SC), e1-e5
#                           communication (CO), f1-f4 friend pressure (FP),
#                           g1-g5 social costs (SOCO); 18 items, 1-5
#   li_2025_risky_driving   six risky driving behaviours, rb1-rb6, 1-5
#                           (never .. very often) -> RDr
# Item codes: source headers; the PPRDS and SDCaF ones get an instrument
#   prefix (pprds_a1, sdcaf_d1; see PREFIX).
# Skipped: the nine composites. id: ID (unique). Covariates: sex, age,
#   education, driving experience (years), driving frequency, accidents,
#   penalties, driving with friends. No PII, no missing cells, no duplicate
#   rows.

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/56869706"
COVS = {"sex": "cov_sex", "age": "cov_age", "education": "cov_education",
        "Experience": "cov_driving_years", "Frequency": "cov_driving_freq",
        "accident": "cov_accidents", "penalty": "cov_penalties",
        "friends": "cov_drives_with_friends"}
BLOCKS = {"a": (6, "RED"), "b": (5, "RDD"), "c": (9, "IDD"), "d": (4, "SC"),
          "e": (5, "CO"), "f": (4, "FP"), "g": (5, "SOCO"), "rb": (6, "RDr"),
          "R": (10, "RPI")}


def cols(p):
    return [f"{p}{i}" for i in range(1, BLOCKS[p][0] + 1)]


SCALES = {
    "li_2025_rpi": (cols("R"), range(1, 5)),
    "li_2025_pprds": (cols("a") + cols("b") + cols("c"), range(1, 6)),
    "li_2025_sdcaf": (cols("d") + cols("e") + cols("f") + cols("g"),
                      range(1, 6)),
    "li_2025_risky_driving": (cols("rb"), range(1, 6)),
}
# The one-letter PPRDS/SDCaF codes are prefixed with the instrument (a1 ->
# pprds_a1, d1 -> sdcaf_d1), reversibly: bare "c1".."g5" collide with other
# instruments' codes in irw-validate's rights register.
PREFIX = {"li_2025_pprds": "pprds_", "li_2025_sdcaf": "sdcaf_"}


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (269, 72), d.shape
    comps = [c for _, c in BLOCKS.values()]
    acc = {"ID"} | set(COVS) | set(comps)
    for items, _ in SCALES.values():
        acc |= set(items)
    assert set(d.columns) == acc and len(d.columns) == len(acc)
    for p, (_, comp) in BLOCKS.items():
        assert np.allclose(d[cols(p)].mean(axis=1), d[comp]), p
        print(f"  skip {comp}: mean of {p}-block")
    assert d["ID"].is_unique
    d = d.rename(columns={"ID": "id", **COVS})
    cov_cols = list(COVS.values())
    assert len(set(SCALES)) == len(SCALES)
    total = 0
    for table, (items, allowed) in SCALES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        pre = PREFIX.get(table)
        if pre:
            long["item"] = pre + long["item"]
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].isin(list(allowed)).all()
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: set(allowed) for i in long["item"].unique()}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        total += len(long)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert total == 269 * 54


if __name__ == "__main__":
    convert()
