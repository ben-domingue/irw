#!/usr/bin/env python3
# Source: https://zenodo.org/records/5025376 (Dryad 10.5061/dryad.5f017)
# DOI: 10.5281/zenodo.5025376 (data); paper 10.1371/journal.pone.0124622
#   Lonnqvist J-E, Hennig-Schmidt H, Walkowitz G (2015). Ethnicity- and sex-based discrimination
#   and the maintenance of self-esteem. PLoS ONE 10(5): e0124622.
# License: CC0 1.0 (Zenodo/Dryad)
# Data: "Lonnqvist et al._2015_data.sav", 205 student "employers" from Israel, the West Bank and
#   Germany in an incentivised employment task (paper N = 205).
#
# Table: lonnqvist_2015_state_selfesteem -- state self-esteem before (wave 1, seT1_item1-3) and
#   after (wave 2, seT2_item1-3) the employment task. Paper, Measures: three items selected from
#   the State Self-Esteem Scale (Heatherton & Polivy 1991), "I feel good about myself", "I feel
#   confident that I understand things", "I feel as smart as others", 1 not at all - 5 extremely,
#   translated into Hebrew, Arabic and German. item = item1..item3 (the suffix of the .sav name),
#   wave = 1/2 (the T1/T2 in it).
# Not shipped: the employment-task decisions (wages wp01-12, minimum-effort yes/no yn01-12, belief
#   elicitations bm/bnm) -- the .sav does not say which applicant (ethnicity x sex) each column is.
# id: row index. Covariates: cov_sex, cov_age. `country` (1/2/3) has no value labels in the file
#   and the paper does not give the coding, so it is not shipped.
# Item text: not shipped -- the paper lists the three English stems, but the .sav names carry only
#   positions; the SSES is a published third-party instrument with no rights-register ruling.
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/records/5025376/files/L%C3%B6nnqvist%20et%20al._2015_data.sav?download=1"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    assert len(d) == 205
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = d["sex"].map({0: "male", 1: "female"})
    d["cov_age"] = d["age"]
    covs = ["cov_sex", "cov_age"]
    cols = [f"seT{w}_item{i}" for w in (1, 2) for i in (1, 2, 3)]
    t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="col", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["wave"] = t["col"].str.extract(r"seT(\d)")[0].astype(int)
    t["item"] = t["col"].str.extract(r"_(item\d)")[0]
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    assert not t.duplicated(["id", "item", "wave"]).any()
    print("dropped blank cells:", 205 * 6 - len(t))
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
    gate(t)
    t.to_csv(OUT / "lonnqvist_2015_state_selfesteem.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
