#!/usr/bin/env python3
# Source: https://github.com/ndawlab/mars-irt  (03_Calibration/data/data.csv,
#   metadata.tsv, reject.csv; pinned to commit 04eecdaf77d0ee657c65351eab5ed9e744b1ce14)
# Paper DOI: 10.3758/s13428-023-02067-8
#   Zorowitz, S., Chierchia, G., Blakemore, S.-J., & Daw, N. D. (2024). An item
#   response theory analysis of the matrix reasoning item bank (MaRs-IB).
#   Behavior Research Methods, 56(3), 1104-1122 (online 2023).
# Data DOI: none (GitHub repository)
# License: MIT (repository LICENSE, checked on the GitHub API 2026-09-27).
#
# Table: zorowitz_2023_marsib -- the MaRs-IB calibration study: 1,584 online
#   adults each solved 16 matrix-reasoning puzzles, drawn from 384 item clones
#   (64 item templates x shape sets / distractor types), in one of three test
#   forms.
#   item      = item_id (the clone actually shown); item_family = the template
#               (`item`), since clones of one template are not independent.
#   resp      = accuracy (1 correct, 0 incorrect).
#   resp_raw  = choice, which option was picked, coded RELATIVE TO THE KEY by the
#               deposit: 0 is always the correct option and 1-3 the distractors
#               (resp == 1 exactly when resp_raw == 0). Kept so the table is
#               nominal-ready.
#   rt        = response time in seconds (the task timed out at 30 s).
#   Timed-out trials (accuracy and choice missing, 477) are dropped.
#   The authors' screening (01_Screening.ipynb -> reject.csv: insufficient
#   screen resolution, >= 4 missing responses, or >= 4 rapid guesses) is
#   reproduced: participants with reject > 0 are excluded, as in the paper.
#   id is the random subject code, as integers (the code is not carried).
# Covariates: age, gender (the categorical answer), test form (1-3).
# Item covariates: itemcov_dimension (number of rules, Chierchia et al. 2019),
#   itemcov_distractor (md / pd distractor type), itemcov_shape_set.
# NOT carried: race, ethnicity, education, free-text fields, screen
#   resolution, browser interactions, trial position.

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
COMMIT = "04eecdaf77d0ee657c65351eab5ed9e744b1ce14"
BASE = f"https://raw.githubusercontent.com/ndawlab/mars-irt/{COMMIT}/03_Calibration/data/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "zorowitz_2023_marsib"


def fetch(url: str) -> bytes:
    for attempt in range(5):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            return r.content
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} failed after 5 attempts")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(BytesIO(fetch(BASE + "data.csv")))
    m = pd.read_csv(BytesIO(fetch(BASE + "metadata.tsv")), sep="\t")
    rj = pd.read_csv(BytesIO(fetch(BASE + "reject.csv")))
    assert d.shape == (25344, 14), d.shape
    assert d["subject"].nunique() == 1584 and m["subject"].is_unique
    assert set(rj["subject"]) == set(d["subject"])
    assert not d.duplicated(["subject", "item_id"]).any()
    assert (d.groupby("item_id")["item"].nunique() == 1).all()
    ok = d["accuracy"].notna()
    assert (d.loc[~ok, "choice"].isna()).all()
    assert ((d.loc[ok, "choice"] == 0) == (d.loc[ok, "accuracy"] == 1)).all()

    keep = set(rj.loc[rj["reject"] == 0, "subject"])
    d = d[ok & d["subject"].isin(keep)].merge(
        m[["subject", "age", "gender-categorical"]], on="subject", how="left",
        validate="many_to_one")
    codes = {s: i + 1 for i, s in enumerate(sorted(d["subject"].unique()))}
    t = pd.DataFrame({
        "id": d["subject"].map(codes),
        "item": d["item_id"].astype(str),
        "resp": d["accuracy"].astype(int),
        "resp_raw": d["choice"].astype(int),
        "rt": d["rt"],
        "cov_age": d["age"],
        "cov_gender": d["gender-categorical"],
        "cov_test_form": d["test_form"],
        "itemcov_dimension": d["dimension"],
        "itemcov_distractor": d["distractor"],
        "itemcov_shape_set": d["shape_set"],
        "item_family": d["item"].astype(str),
    })
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    assert t["rt"].max() <= 30

    items = sorted(t["item"].unique())
    pv = {i: {0, 1} for i in items}
    cl = {i: "matrix_reasoning" for i in items}
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
          f"items={t['item'].nunique()} families={t['item_family'].nunique()} "
          f"excluded={1584 - len(codes)}")


if __name__ == "__main__":
    convert()
