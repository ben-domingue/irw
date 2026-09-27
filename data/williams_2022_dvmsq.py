#!/usr/bin/env python3
# Source: https://osf.io/y6edb/
#   DVMSQ_ProlificDataOSF_07.17.2022.csv            https://osf.io/download/3xamc/
#   DVMSQ_ProlificStudy_DataDictionary_07.17.2022.csv https://osf.io/download/efr89/
# Paper DOI: 10.3389/fpsyg.2022.897901
#   Williams, Z. J., Cascio, C. J., & Woynaroski, T. G. (2022). Psychometric
#   validation of a brief self-report measure of misophonia symptoms and
#   functional impairment: The Duke-Vanderbilt Misophonia Screening
#   Questionnaire. Frontiers in Psychology, 13, 897901.
# Data DOI: 10.17605/OSF.IO/Y6EDB
# License: CC BY 4.0 (OSF node y6edb, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27). The form itself says "No permission
#   required to reproduce, adapt, modify, translate, display, or distribute."
#
# Table: williams_2022_dvmsq -- the DVMSQ item pool as administered to 1,403
#   Prolific adults (U.S./U.K.): the screening question (S1, 0 = no, 1 = yes) and
#   20 rated items, 0-4. Item names are the source column names; wording is in
#   the deposit's data dictionary (REDCap export):
#     symptoms, "how often do you experience..." (0 never ... 4 very often):
#       miso_irritate, miso_anger, miso_fear, miso_disgust, miso_flee,
#       miso_protect, miso_aggression, miso_loc, miso_attention,
#       miso_phys_sensation, misophonia_overreact, misophonia_avoid
#     interference, past 7 days (0 not at all ... 4 an extreme amount):
#       miso_imp_interact, miso_imp_work, miso_imp_house, miso_imp_comm,
#       miso_imp_conc
#     global impact (same anchors): miso_global_mh, miso_global_prob,
#       miso_global_lifeworse
#   The published 18-item DVMSQ is a subset of this pool: the deposit's
#   DVMSQ_SX equals the sum of the nine symptom items other than miso_fear plus
#   misophonia_avoid, and DVMSQ_IMPAIR the four interference items other than
#   miso_imp_conc plus the three global items (both asserted below).
#
# Branching: the form stops after S1 for anyone answering "No" ("If you respond
#   'No' to this question, you have finished the questionnaire"), and REDCap
#   branches every rated item on misophonia_screen = 1. The deposit fills those
#   570 respondents' 20 unasked items with 0. Those zeros are not responses and
#   are dropped: non-screeners contribute only their S1 row.
#
# No item is reverse-keyed. Covariates: age, gender identity (dictionary
#   labels), sex assigned at birth, education (dictionary labels). prolific_id is
#   dropped and id is the row index.
#
# Not taken: the same file holds the Duke Misophonia Questionnaire symptom
#   scale, the Inventory of Hyperacusis Symptoms, a DSM-5 phonophobia severity
#   scale, OASIS, ODSIS, CUANGOS, RLSS and SSS-8. Several are branched (DMQ on
#   the screen, OASIS/ODSIS items 2-5 on item 1) and zero-filled the same way,
#   and they are outside ben-domingue/irw#261.

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
URL_DATA = "https://osf.io/download/3xamc/"
URL_DICT = "https://osf.io/download/efr89/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "williams_2022_dvmsq"

SX = ["miso_irritate", "miso_anger", "miso_fear", "miso_disgust", "miso_flee",
      "miso_protect", "miso_aggression", "miso_loc", "miso_attention",
      "miso_phys_sensation", "misophonia_overreact", "misophonia_avoid"]
IMP = ["miso_imp_interact", "miso_imp_work", "miso_imp_house", "miso_imp_comm",
       "miso_imp_conc", "miso_global_mh", "miso_global_prob", "miso_global_lifeworse"]
SCREEN = "misophonia_screen"


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def labels(choices: str) -> dict:
    return {int(k): v.strip() for k, v in
            (p.split(",", 1) for p in choices.split("|"))}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(URL_DATA)), low_memory=False)
    k = pd.read_csv(BytesIO(fetch(URL_DICT)), encoding="utf-8-sig").set_index(
        "Variable / Field Name")
    assert d.shape == (1403, 248), d.shape
    items = SX + IMP
    for c in items:
        assert k.loc[c, "Branching Logic (Show field only if...)"] == "[misophonia_screen] = '1'", c
    assert d[[SCREEN] + items].notna().all().all()
    no = d[SCREEN] == 0
    assert (d.loc[no, items] == 0).all().all()     # unasked items zero-filled
    yes = d[~no]
    assert (yes[[c for c in SX if c not in ("miso_fear", "misophonia_overreact")]]
            .sum(axis=1) == yes["DVMSQ_SX"]).all()
    assert (yes[[c for c in IMP if c != "miso_imp_conc"]].sum(axis=1)
            == yes["DVMSQ_IMPAIR"]).all()

    d = d.reset_index(drop=True).copy()
    d["id"] = d.index + 1
    d["cov_age"] = d["age_yrs"]
    g = labels(k.loc["gender", "Choices, Calculations, OR Slider Labels"])
    d["cov_gender"] = d["gender"].map(g)
    d["cov_sex"] = d["sex"].str.lower()
    ed = labels(k.loc["education", "Choices, Calculations, OR Slider Labels"])
    lvl = d["education"].str.extract(r"^LVL(\d+)_")[0].astype(int)
    d["cov_education"] = lvl.map(ed)
    covs = ["cov_age", "cov_gender", "cov_sex", "cov_education"]
    assert d[covs].notna().all().all()

    t = d[["id", SCREEN] + items + covs].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp")
    unasked = t["id"].isin(d.loc[no, "id"]) & (t["item"] != SCREEN)
    print(f"  dropping {int(unasked.sum())} zero-filled cells for "
          f"{int(no.sum())} respondents who answered No to S1")
    t = t[~unasked].dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {c: set(range(0, 5)) for c in items}
    pv[SCREEN] = {0, 1}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {c: "misophonia_symptoms" for c in SX + [SCREEN]}
    cl.update({c: "misophonia_impairment" for c in IMP})
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
          f"screened_in={int((~no).sum())}")


if __name__ == "__main__":
    convert()
