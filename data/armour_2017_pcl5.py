#!/usr/bin/env python3
# Source: https://osf.io/mj5wa/  (file PTSD_data.sav, https://osf.io/download/vuf6m/)
# Paper DOI: 10.1016/j.janxdis.2016.11.008
#   Armour, C., Fried, E. I., Deserno, M. K., Tsai, J., & Pietrzak, R. H. (2017).
#   A network analysis of DSM-5 posttraumatic stress disorder symptoms and
#   correlates in U.S. military veterans. Journal of Anxiety Disorders, 45, 49-59.
# Reused by Marinazzo et al. (2024), Behavior Research Methods 56, 8057-8079
#   (10.3758/s13428-024-02471-8), the paper that raised this in ben-domingue/irw#151.
# License: CC BY 4.0 (OSF node mj5wa, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Table: armour_2017_pcl5 -- PCL-5, the 20 DSM-5 PTSD symptoms (past month),
#   0 = not at all ... 4 = extremely. The deposit holds only the paper's analytic
#   sample: 221 veterans with subthreshold-or-higher PTSD symptoms
#   (`Subthreshold_or_Higher_PM_PCL` is 1 for every row). Items are
#   `Q28_01_MONTH` ... `Q28_20_MONTH`, renamed pcl5_1 ... pcl5_20 in DSM-5 order
#   (B1-B5 intrusion, C1-C2 avoidance, D1-D7 cognition/mood, E1-E6 arousal), as
#   the authors' PTSD_code.R labels them. No PCL-5 item is reverse-keyed.
#
# Skipped columns (all composites or design variables, printed at run time):
#   SUM_PM_PCL5, PM_PCL5_38, PTSD_2cat, SUM_SX_CRITERIA, Subthreshold flag,
#   SUM_LIFETIME_TRAUMAS, Sum_GAD2, Sum_PHQ2, Passive/Active/Any SI,
#   PCS/MCS (SF-8 summary scores), QualityofLife_SUM, and `weight`
#   (poststratification weight). `CaseID` is the survey's case number and is
#   replaced by the row index.

import sys
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/vuf6m/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "armour_2017_pcl5"

ITEMS = [f"Q28_{i:02d}_MONTH" for i in range(1, 21)]
COV = {"PPAGE": "cov_age", "PPGENDER": "cov_gender"}
SKIP = {
    "CaseID": "survey case number -- replaced by the row index",
    "weight": "poststratification weight (design variable)",
    "Subthreshold_or_Higher_PM_PCL": "sample-selection flag, constant 1",
    "PM_PCL5_38": "probable-PTSD flag (composite)",
    "SUM_PM_PCL5": "PCL-5 total (composite)",
    "PTSD_2cat": "PTSD category (composite)",
    "SUM_SX_CRITERIA": "count of DSM-5 criteria met (composite)",
    "SUM_LIFETIME_TRAUMAS": "trauma count (composite)",
    "Sum_GAD2": "GAD-2 sum (composite; items not deposited)",
    "Sum_PHQ2": "PHQ-2 sum (composite; items not deposited)",
    "Passive_SI_FINAL": "derived suicidal-ideation score",
    "Active_SI_FINAL": "derived suicidal-ideation score",
    "Any_SI": "derived suicidal-ideation flag",
    "PCS": "SF-8 physical component summary (composite)",
    "MCS": "SF-8 mental component summary (composite)",
    "QualityofLife_SUM": "Q-LES-Q-SF total (composite)",
}


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_DIR / ".tmp_PTSD_data.sav"
    tmp.write_bytes(fetch(URL))
    try:
        d, _ = pyreadstat.read_sav(str(tmp))
    finally:
        tmp.unlink()
    assert d.shape == (221, 38), d.shape
    acc = set(ITEMS) | set(COV) | set(SKIP)
    assert set(d.columns) == acc, set(d.columns) ^ acc
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert (d["Subthreshold_or_Higher_PM_PCL"] == 1).all()
    # the deposited total is the plain item sum
    assert (d[ITEMS].sum(axis=1) == d["SUM_PM_PCL5"]).all()

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COV)
    assert d["cov_age"].between(18, 100).all()
    d["cov_gender"] = d["cov_gender"].map({1: "male", 2: "female"})
    assert d["cov_gender"].notna().all()
    d = d.rename(columns={c: f"pcl5_{i}" for i, c in enumerate(ITEMS, 1)})
    covs = list(COV.values())
    t = d[["id"] + [f"pcl5_{i}" for i in range(1, 21)] + covs].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    assert (t["resp"] == t["resp"].round()).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {f"pcl5_{i}": set(range(0, 5)) for i in range(1, 21)}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {}
    for rng, k in ((range(1, 6), "intrusion"), (range(6, 8), "avoidance"),
                   (range(8, 15), "cognition_mood"), (range(15, 21), "arousal")):
        cl.update({f"pcl5_{i}": k for i in rng})
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
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    convert()
