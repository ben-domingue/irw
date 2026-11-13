#!/usr/bin/env python3
# Source: https://osf.io/uhrv4/ ("Data and codebook")
# DOI: 10.17605/OSF.IO/UHRV4 (data); paper Okan Y, Stone ER, Petrova D, Bruine de Bruin W (2024).
#   Communicating Probabilities of Cervical Cancer Screening Results with Icon Arrays or Tree
#   Diagrams: A Longitudinal Experiment. Health Communication, doi 10.1080/10410236.2024.2421612.
# License: CC BY 4.0 (OSF node licence)
# Data: "Cervical screening results_data.sav" + _Codebook.xlsx, 3,100 UK women aged 25-64 (online
#   panel); T1 for all, T2 follow-up for 1,575 (bothwaves). Randomised 3 x 2: presentation format
#   (numerical-only / tree diagram / icon array) x explanatory text (absent / present).
#
# Tables (wave 1 = T1, 2 = T2; item = the codebook variable stem, e.g. gist1, verbatim4):
#   okan_2024_cervical_results_comprehension -- gist1-6 (relative ordering, multiple choice) and
#     verbatim1-9 (exact numbers), scored 0/1 by the authors (*_c_t1/_t2, value labels
#     Incorrect/Correct; each wave's gist_relative and verbatim totals reproduce). resp_raw = the
#     answer given (choice code for gist, number for verbatim).
#   okan_2024_cervical_results_affect -- affect1-6 (assured, hopeful, relieved, anxious, afraid,
#     worried), 1 not at all .. 7 extremely, as stored (positive and negative feelings, not reversed).
#   okan_2024_cervical_results_evaluation -- eval1-6 (understanding, helpfulness, liking, trust,
#     engagement, would read again), 1-7.
#   okan_2024_numeracy -- num1-3_corr (Schwartz et al. 1997), 0/1, T1 only.
#   okan_2024_graph_literacy -- graphlit1-4_corr (short graph literacy items), 0/1, T1 only.
# Not shipped: gistabs*_25 (re-scorings of the verbatim answers), risk perception percentages,
#   intentions (2 items), behaviours, composites, z-scores.
# id: pid. Covariates: cov_age, cov_education, cov_ethnicity, cov_format, cov_text (value labels).
#   Region of residence (location) is dropped (geographic code).
# Item text: not shipped -- the codebook labels and the two survey PDFs carry the wording.
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/68egv/"


def save(t, name, lo, hi, cols):
    t = t.dropna(subset=["resp"]).copy()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(lo, hi).all(), name
    t = t[cols].sort_values(["id", "wave", "item"] if "wave" in cols else ["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 3100 and d["pid"].is_unique
    vl = meta.variable_value_labels
    d["id"] = d["pid"].astype(int)
    covmap = {"cov_education": "education", "cov_ethnicity": "ethnic", "cov_format": "format",
              "cov_text": "text"}
    d["cov_age"] = d["age"]
    for c, v in covmap.items():
        d[c] = d[v].map(vl[v])
    covs = ["cov_age"] + list(covmap)
    base = ["id", "item", "resp"]

    long = []
    for w in (1, 2):
        g = [f"gist{i}" for i in range(1, 7)]
        v = [f"verbatim{i}" for i in range(1, 10)]
        if w == 1:
            assert (d[[f"{x}_c_t1" for x in g]].sum(axis=1) == d["gist_relative_t1"]).all()
            assert (d[[f"{x}_c_t1" for x in v]].sum(axis=1) == d["verbatim_t1"]).all()
        for it in g + v:
            for c in (f"{it}_c_t{w}", f"{it}_t{w}"):
                for k, lab in vl.get(c, {}).items():
                    if c.endswith(f"_c_t{w}"):
                        assert {0: "Incorrect", 1: "Correct"}.get(int(k)) == lab, (c, k, lab)
            long.append(pd.DataFrame({"id": d["id"], "item": it, "resp": d[f"{it}_c_t{w}"],
                                      "resp_raw": d[f"{it}_t{w}"], "wave": w, **{c: d[c] for c in covs}}))
    save(pd.concat(long), "okan_2024_cervical_results_comprehension", 0, 1,
         base + ["resp_raw", "wave"] + covs)

    for name, stem, k in (("affect", "affect_t{w}_{i}", 6), ("evaluation", "eval{i}_t{w}", 6)):
        long = [pd.DataFrame({"id": d["id"], "item": f"{name[:6] if name == 'affect' else 'eval'}{i}",
                              "resp": d[stem.format(w=w, i=i)], "wave": w, **{c: d[c] for c in covs}})
                for w in (1, 2) for i in range(1, k + 1)]
        save(pd.concat(long), f"okan_2024_cervical_results_{name}", 1, 7, base + ["wave"] + covs)

    for name, items in (("numeracy", [f"num{i}_corr" for i in range(1, 4)]),
                        ("graph_literacy", [f"graphlit{i}_corr" for i in range(1, 5)])):
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        save(t, f"okan_2024_{name}", 0, 1, base + covs)


if __name__ == "__main__":
    main()
