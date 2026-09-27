#!/usr/bin/env python3
# Source: https://osf.io/ck5xm/  (merge.sav, https://osf.io/download/dfvme/)
# Paper DOI: 10.1177/00131644211069406
#   Robie, C., Meade, A. W., Risavy, S. D., & Rasheed, S. (2022). Effects of
#   response option order on Likert-type psychometric properties and reactions.
#   Educational and Psychological Measurement, 82(6), 1107-1129.
# Data DOI: 10.17605/OSF.IO/CK5XM
# License: CC BY 4.0 (OSF node ck5xm, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27; also confirmed in the issue thread).
#
# Design: 1,198 business students at a Canadian university, randomly assigned
#   to one of four response-option orders, each item on its own page:
#   cov_condition = ascending (strongly disagree -> strongly agree),
#   descending, random_direction (each item randomly ascending or descending),
#   fully_random (options in a random permutation). Responses are stored on one
#   coding in every condition (1 = strongly disagree ... 5 = strongly agree);
#   item means agree across conditions (e.g. Q1 2.75-2.81), as the paper reports.
#   The paper's instrument order: HEXACO, reactions, CAB, demographics.
#
# Tables:
#   robie_2022_hexaco60: HEXACO-60 (Ashton & Lee 2009), source Q1-Q60 renamed
#     hexaco_1-hexaco_60 (the HEXACO-60 item numbers), 1-5, RAW. The
#     deposit's reversed copies (Q1r ... Q60r) and domain scores are not used.
#     Domains follow the HEXACO-60 key (item i: i mod 6 = 0 H, 5 E, 4 X, 3 A,
#     2 C, 1 O); asserted by rebuilding the deposit's domain means from its
#     own reversed copies.
#   robie_2022_cab: counterproductive academic behaviour (Holtrop et al. 2014,
#     25 items from Hakstian et al. 2002), source Q126-Q150 renamed cab_1-cab_25
#     in order, 1 = never even considered it ... 6 = did it three or more times.
#   The paper's wording of both instruments is in the deposit's .sav labels and
#   Qualtrics .qsf files; no item text is extracted here (HEXACO wording is not
#   shipped by IRW, ruling 2026-09-05).
#
# Not taken: the three directed-response checks (Q61-Q63), the five reaction
#   items (Q121-Q125; Q121 codes "strongly agree" as 10), the Qualtrics per-page
#   timings (T*_...: the paper recovered page order per respondent, and the
#   page-to-item mapping is not documented in the deposit), GPA (self-reported
#   and official, the latter released to the researchers only), and the
#   careless-responding indices and filters.
# Covariates: condition, gender, age, native English speaker, and the
#   participant's own answer to "In your honest opinion, should we use your
#   data?" (cov_use_my_data yes/no; 53 said no, and the authors' minimal filter
#   drops them). Nothing is filtered here.
# Privacy: IP address, latitude/longitude, the SONA identity code, ResponseId,
#   the deposit's `id` and all free text are dropped; id is the row index.

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/dfvme/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DOMAIN = {0: "H", 5: "E", 4: "X", 3: "A", 2: "C", 1: "O"}
COND = {1: "ascending", 2: "descending", 3: "random_direction", 4: "fully_random"}


def fetch():
    tmp = OUT_DIR / ".tmp_robie_merge.sav"
    for attempt in range(5):
        r = requests.get(URL, headers=UA, timeout=300)
        if r.status_code == 200 and len(r.content) > 100000:
            tmp.write_bytes(r.content)
            try:
                return pyreadstat.read_sav(str(tmp))
            finally:
                tmp.unlink()
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{URL} failed after 5 attempts")


def finish(t, name, pv, cl):
    assert (t["resp"] == t["resp"].round()).all()
    t = t.copy()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    checks = run_qc(t, permitted_values=pv, item_constructs=cl)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, m = fetch()
    assert d.shape == (1198, 429), d.shape
    hex_items = [f"Q{i}" for i in range(1, 61)]
    cab_items = [f"Q{i}" for i in range(126, 151)]
    agree = {1.0: "strongly disagree", 2.0: "disagree",
             3.0: "neutral (neither agree nor disagree)", 4.0: "agree",
             5.0: "strongly agree"}
    assert all(m.variable_value_labels[c] == agree for c in hex_items)
    cab_lab = m.variable_value_labels["Q126"]
    assert cab_lab[1.0] == "never even considered it" and len(cab_lab) == 6
    assert all(m.variable_value_labels[c] == cab_lab for c in cab_items)
    assert m.variable_value_labels["cell"] == {
        1.0: "ascending (SD to SA)", 2.0: "descending (SA to SD)",
        3.0: "randomly ascending or descending", 4.0: "totally randomized"}

    # HEXACO domain key check against the deposit's own scores
    rev = {int(c[1:-1]) for c in d.columns if c.startswith("Q") and c.endswith("r")}
    for code in "HEXACO":
        idx = [i for i in range(1, 61) if DOMAIN[i % 6] == code]
        cols = [f"Q{i}r" if i in rev else f"Q{i}" for i in idx]
        assert np.allclose(d[cols].mean(axis=1), d[code], equal_nan=True), code
    for i in rev:   # reversed copies are 6 - raw
        assert ((6 - d[f"Q{i}"]) == d[f"Q{i}r"]).where(d[f"Q{i}"].notna(), True).all()

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_condition"] = d["cell"].map(COND)
    d["cov_gender"] = d["Q151"].map(m.variable_value_labels["Q151"])
    d["cov_age"] = d["Q152"]
    d["cov_native_english"] = d["Q154"].map(m.variable_value_labels["Q154"])
    d["cov_use_my_data"] = d["Q160"].map({1.0: "yes", 2.0: "no"})
    covs = ["cov_condition", "cov_gender", "cov_age", "cov_native_english",
            "cov_use_my_data"]
    assert d["cov_condition"].notna().all()

    def long(cmap):
        x = d[["id"] + list(cmap) + covs].rename(columns=cmap)
        x = x.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        return x.dropna(subset=["resp"])[["id", "item", "resp"] + covs]

    hmap = {f"Q{i}": f"hexaco_{i}" for i in range(1, 61)}
    finish(long(hmap), "robie_2022_hexaco60",
           {v: set(range(1, 6)) for v in hmap.values()},
           {f"hexaco_{i}": DOMAIN[i % 6] for i in range(1, 61)})
    cmap = {c: f"cab_{k}" for k, c in enumerate(cab_items, 1)}
    finish(long(cmap), "robie_2022_cab",
           {v: set(range(1, 7)) for v in cmap.values()},
           {v: "counterproductive_academic_behavior" for v in cmap.values()})


if __name__ == "__main__":
    convert()
