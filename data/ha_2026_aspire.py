#!/usr/bin/env python3
# Source: https://osf.io/5b798/  (Data/ASPIRE Sexting Paper_Data_4.24.25 (with labels).csv,
#   https://osf.io/download/8up5s/; the other copy is the same data without
#   a header row, for Mplus)
# Paper DOI: 10.1016/j.chb.2026.108981
#   Ha, T., Quiroz, S. I., & McNeish, D. (2026). Adolescent sexting in romantic
#   relationships and daily positive and negative affect dynamics: A dyadic
#   intensive longitudinal study. Computers in Human Behavior, 181, 108981.
#   (preprint SSRN 10.2139/ssrn.5529556)
# Data DOI: none (OSF node 5b798)
# License: CC BY 4.0 (OSF node 5b798, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Table: ha_2026_aspire_affect -- ASPIRE study, 101 adolescent romantic couples
#   (202 adolescents), 24 intensive-longitudinal assessments each. The deposit
#   is one row per couple x assessment (EMANum 1-24) with each partner's
#   answers in _A/_B columns. Long format: id = the partner's study ID (ID_A or
#   ID_B; the two sets do not overlap), wave = EMANum, so one person's 24
#   assessments share an id. Items are the seven momentary affect ratings, 1-7,
#   named by the source codes: insec, happy, energ, low, irr, attr, distr. The
#   deposit has no codebook or item wording; the Mplus inputs model happy,
#   energ, low and distr as outcomes. 999 is the missing code (a missed
#   assessment); those cells are dropped.
# No item is recoded; all seven are shipped raw.
# Covariates: couple (CoupleID) and partner (A/B, the deposit's dyad role).
#   NOT carried: the sexting indicators (Sext_*, parsext_*: the paper's
#   predictors, not affect items; Sext_* is 0 even on missed assessments),
#   day_*, relationship status and length, and the coded demographics (gender,
#   age, ethnicity, parents' education, income, free lunch), which have no
#   value labels in the deposit.

import sys
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/8up5s/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "ha_2026_aspire_affect"
ITEMS = ["insec", "happy", "energ", "low", "irr", "attr", "distr"]


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(URL)), encoding="utf-8-sig")
    assert d.shape == (2424, 50), d.shape
    assert d["CoupleID"].nunique() == 101
    assert (d.groupby("CoupleID")["EMANum"].apply(sorted)
            .apply(lambda x: x == list(range(1, 25)))).all()
    assert not set(d["ID_A"]) & set(d["ID_B"])
    assert (d.groupby("CoupleID")[["ID_A", "ID_B"]].nunique() == 1).all().all()

    parts = []
    for side in ("A", "B"):
        x = d[["CoupleID", "EMANum", f"ID_{side}"] + [f"{i}_{side}" for i in ITEMS]]
        x = x.rename(columns={f"ID_{side}": "id", "EMANum": "wave",
                              "CoupleID": "cov_couple",
                              **{f"{i}_{side}": i for i in ITEMS}})
        x["cov_partner"] = side
        parts.append(x.melt(id_vars=["id", "wave", "cov_couple", "cov_partner"],
                            var_name="item", value_name="resp"))
    t = pd.concat(parts, ignore_index=True)
    t = t[t["resp"] != 999].dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t["id"] = t["id"].astype(int)
    t = t[["id", "item", "resp", "wave", "cov_couple", "cov_partner"]].sort_values(
        ["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() >= 100

    pv = {i: set(range(1, 8)) for i in ITEMS}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {i: "momentary_affect" for i in ITEMS}
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()} "
          f"waves={t['wave'].nunique()}")


if __name__ == "__main__":
    convert()
