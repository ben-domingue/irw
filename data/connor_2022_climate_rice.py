#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/1CT07N
# DOI: 10.7910/DVN/1CT07N (data, with questionnaire); paper 10.1016/j.spc.2022.01.034
#   Connor M, Cuong OQ, Demont M, Sander BO, Nelson K (2022). The influence of climate change
#   knowledge on consumer valuation of sustainably produced rice in Vietnam. Sustainable
#   Production and Consumption 31.
#   The same file is also deposited as DVN/JBLPYY ("Replication Data for: ..."); only 1CT07N is used.
# License: CC0 1.0 (Harvard Dataverse)
# Data: "SPC-DIB data.csv" (410 rice consumers in Vietnam) and "SPC-DIB questionnaire.docx".
#
# Tables:
#   connor_2022_cc_knowledge -- Section 2, climate change knowledge, 8 statements answered
#     True / False / Don't know, stored 1 / 2 / 3 (KCC1..KCC8; the file spells item 4 "KCCK4",
#     kept). Scored resp = 1 if the answer matches the key T F F T T F F T (items 1-8), else 0
#     ("don't know" scores 0). The key reproduces the file's own SKCC (total), SKCG (items 1-3, 8)
#     and SKCQ (items 4-7) in all 410 rows. resp_raw keeps 1/2/3.
#   connor_2022_rice_attributes -- "When I buy rice I consider ...", 20 statements, 1 completely
#     disagree - 6 fully agree: ethical production ETP1-8, ecological production ECP1-6,
#     low-emission production LEP1-6 (questionnaire items 9-28). The file's METP etc. are means
#     of these items (checked for METP) and are not shipped.
# Not shipped: the three emission-scale markings (EMR/EMW/EMM, continuous), SRP awareness and
#   certification (single items), WTP.
# id: the file's ID. Covariates: cov_age. Gender (0/1) and Education (1-3; the questionnaire
#   lists six levels) are recoded without a key in the deposit, so they are not shipped.
# Item text: not shipped -- the English stems are in the questionnaire .docx (questionnaire
#   numbering, tied to the codes by order); the survey was administered in Vietnamese.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/6152546?format=original"
KNOW = ["KCC1", "KCC2", "KCC3", "KCCK4", "KCC5", "KCC6", "KCC7", "KCC8"]
KEY = dict(zip(KNOW, [1, 2, 2, 1, 1, 2, 2, 1]))
ATT = [f"ETP{i}" for i in range(1, 9)] + [f"ECP{i}" for i in range(1, 7)] + [f"LEP{i}" for i in range(1, 7)]


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 410 and d["ID"].is_unique
    score = sum((d[c] == k).astype(int) for c, k in KEY.items())
    assert (score == d["SKCC"]).all()
    d["id"] = d["ID"].astype(int)
    d["cov_age"] = d["Age"].astype(int)
    covs = ["cov_age"]

    t = d[["id"] + covs + KNOW].melt(id_vars=["id"] + covs, var_name="item", value_name="resp_raw")
    assert t["resp_raw"].isin([1, 2, 3]).all()
    t["resp"] = (t["resp_raw"] == t["item"].map(KEY)).astype(int)
    t = t[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"])
    assert len(t) == 410 * 8 and not t.duplicated(["id", "item"]).any()
    gate(t)
    t.to_csv(OUT / "connor_2022_cc_knowledge.csv", index=False)
    print("connor_2022_cc_knowledge", len(t), t.id.nunique(), t.item.nunique())

    t = d[["id"] + covs + ATT].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 6).all() and len(t) == 410 * 20
    assert not t.duplicated(["id", "item"]).any()
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "connor_2022_rice_attributes.csv", index=False)
    print("connor_2022_rice_attributes", len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
