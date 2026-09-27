#!/usr/bin/env python3
# Source: https://osf.io/dkrhy/  (BICB_Data.csv, https://osf.io/download/7vqf9/)
# Paper DOI: 10.1016/j.tsc.2021.100797
#   Silvia, P. J., Rodriguez, R. M., Beaty, R. E., Frith, E., Kaufman, J. C.,
#   Loprinzi, P., & Reiter-Palmon, R. (2021). Measuring everyday creativity: A
#   Rasch model analysis of the Biographical Inventory of Creative Behaviors
#   (BICB) scale. Thinking Skills and Creativity, 39, 100797.
#   (preprint 10.31234/osf.io/3wq7c)
# Data DOI: 10.17605/OSF.IO/DKRHY
# License: CC BY 4.0 (OSF node dkrhy, "CC-By Attribution 4.0 International",
#   checked on the OSF API 2026-09-27).
#
# Table: silvia_2021_bicb -- Biographical Inventory of Creative Behaviors (Batey
#   2007), 34 yes/no items (1 = did it in the past 12 months), English, 2,359
#   U.S. adults pooled by the authors from seven studies (UNCG, University of
#   Mississippi and others; "there were no missing observations"). Items
#   bicb01-bicb34 follow the order of the deposited form ("Batey, BICB
#   Scale.doc"): bicb01 "Written a short story" ... bicb34 "Made a collage"; the
#   paper's items 20 ("Made someone a present") and 34 ("Made a collage") match.
#   The deposit has no id column, so id is the row index. Distinct from
#   bicb-j_ishiguro_2025 (the Japanese BICB-J).
# Covariates: age; gender (1 = woman, 0 = man: the paper reports 1,716 women and
#   643 men, which are the counts of 1 and 0); study (the source study label).
# No item is reverse-keyed.

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
URL = "https://osf.io/download/7vqf9/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "silvia_2021_bicb"


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(URL)))
    items = [f"bicb{i:02d}" for i in range(1, 35)]
    assert list(d.columns) == items + ["age", "gender", "study"], list(d.columns)
    assert len(d) == 2359 and d.notna().all().all()
    assert (d["gender"] == 1).sum() == 1716 and (d["gender"] == 0).sum() == 643

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["cov_age"] = d["age"]
    d["cov_gender"] = d["gender"].map({1: "female", 0: "male"})
    d["cov_study"] = d["study"]
    covs = ["cov_age", "cov_gender", "cov_study"]
    t = d[["id"] + items + covs].melt(id_vars=["id"] + covs,
                                      var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {i: {0, 1} for i in items}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    cl = {i: "everyday_creativity" for i in items}
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
