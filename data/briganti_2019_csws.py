#!/usr/bin/env python3
# Source: https://osf.io/73c4q/  (SupplementaryMaterials.zip,
#   https://osf.io/download/xbh8q/ -> SupplementaryMaterials/Data/Briganti_NA_CSWS_DATA.csv)
# Paper DOI: 10.1016/j.psychres.2018.12.080
#   Briganti, G., Fried, E. I., & Linkowski, P. (2019). Network analysis of
#   Contingencies of Self-Worth Scale in 680 university students. Psychiatry
#   Research, 272, 252-257.
# Reused by Marinazzo et al. (2024), Behavior Research Methods 56, 8057-8079
#   (10.3758/s13428-024-02471-8), the paper that raised this in ben-domingue/irw#151.
# License: CC BY 4.0 (OSF node 73c4q, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Table: briganti_2019_csws -- Contingencies of Self-Worth Scale (Crocker et al.
#   2003), 35 items c1-c35 in the original order, 1-7. 680 university students
#   (Brussels); README: "full anonymized dataset (N 680)". No id column in the
#   deposit, so id is the row index. No covariates were deposited.
#
# Item-to-domain mapping (Supplementary Table1.docx, and the lavaan model in
#   Briganti2018_NA_CSWStreshsum_script_3parts.R, which agree):
#   family support 7/10/16/24/29, competition 3/12/20/25/32, appearance
#   1/4/17/21/30, God's love 2/8/18/26/31, academic competence 13/19/22/27/33,
#   virtue 5/11/14/28/34, others' approval 6/9/15/23/35.
#
# Reverse-keyed items. Table1 marks items 4, 6, 10, 13, 15, 23 and 30 as
#   "(Reversed)". In this file they are ALREADY REVERSE-SCORED: every one of them
#   correlates positively with its domain (e.g. c4 with c17 r = .36, c10 with c7
#   r = .30), which a raw negatively worded item would not, and the authors' sum
#   scores are plain sums of these columns. Kept as deposited: higher = more
#   contingent self-worth on every item.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/xbh8q/"
MEMBER = "SupplementaryMaterials/Data/Briganti_NA_CSWS_DATA.csv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "briganti_2019_csws"

DOMAINS = {
    "family_support": (7, 10, 16, 24, 29),
    "competition": (3, 12, 20, 25, 32),
    "appearance": (1, 4, 17, 21, 30),
    "gods_love": (2, 8, 18, 26, 31),
    "academic_competence": (13, 19, 22, 27, 33),
    "virtue": (5, 11, 14, 28, 34),
    "others_approval": (6, 9, 15, 23, 35),
}
REVERSED = (4, 6, 10, 13, 15, 23, 30)


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=300)
        if r.status_code == 200 and r.content[:2] == b"PK":
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(BytesIO(fetch(URL))) as z:
        d = pd.read_csv(BytesIO(z.read(MEMBER)), sep=";")
    items = [f"c{i}" for i in range(1, 36)]
    assert list(d.columns) == items and len(d) == 680, (d.shape, list(d.columns))
    assert d.notna().all().all()
    assert sorted(set(d.values.ravel())) == list(range(1, 8))
    # reversed items already reversed: positive correlation with own domain
    c = d.corr()
    for dom, idx in DOMAINS.items():
        for i in idx:
            if i in REVERSED:
                others = [f"c{j}" for j in idx if j != i]
                assert c.loc[f"c{i}", others].mean() > 0.1, (dom, i)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={f"c{i}": f"csws_{i}" for i in range(1, 36)})
    t = d.melt(id_vars=["id"], var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {f"csws_{i}": set(range(1, 8)) for i in range(1, 36)}
    cl = {f"csws_{i}": dom for dom, idx in DOMAINS.items() for i in idx}
    assert len(cl) == 35
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
