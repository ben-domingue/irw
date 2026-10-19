#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/21176009
# DOI: 10.6084/m9.figshare.21176009
#   Eriksson, M., Boman, E., & Svedberg, P. (2022). Additional file 1 of
#   "Autonomy and health-related quality of life in adolescents" [Dataset].
#   figshare.
# Paper: 10.1186/s12887-022-03607-5 (BMC Pediatrics) -- open access.
# Data: "12887_2022_3607_MOESM1_ESM.xlsx", sheet "DataAutonomy" -- 154
#   adolescents, a 6-item autonomy scale scored 1-5 plus ten KIDSCREEN-style
#   HRQoL domain scores.
# License: CC BY + CC0 on the figshare record (the article is CC BY 4.0).
# Item text: NOT shipped. The .xlsx header is bare positional codes
#   (AfAitem1-AfAitem6) and the deposit ships no codebook, so the wording is
#   in the paper's own description of its autonomy measure. Recorded here so
#   the next pass starts from the paper rather than re-deriving this.
#
# ONE table, 154 respondents:
#   eriksson_2022_autonomy   AfAitem1-AfAitem6, 1-5 (6 items)
# id: the deposit's own IDNR serial (1-154).
# Covariates: cov_sex, cov_ses (both option-coded 1/2; the paper is the
#   codebook).
# Dropped: the ten HRQoL domain scores (PhysicalHRQoL ... SocialacceptHRQoL)
#   -- continuous Rasch domain scores, not item responses -- and
#   Afascale6items, the sum of the six items.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "21176009" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 21176009, "12887_2022_3607_MOESM1_ESM.xlsx"
NAME, SHEET = "eriksson_2022_autonomy", "DataAutonomy"
SCALE = set(range(1, 6))

ITEMS = [f"AfAitem{i}" for i in range(1, 7)]
COVS = {"sex": "cov_sex", "SES": "cov_ses"}
DROPPED = ["PhysicalHRQoL", "PsychologicalHRQoL", "MoodsHRQoL",
           "SelfperceptHRQoL", "AutonomyHRQoL", "FamilyHRQoL",
           "FinancialHRQoL", "PeersHRQoL", "SchoolHRQoL",
           "SocialacceptHRQoL", "Afascale6items"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch(), sheet_name=SHEET)
    known = set(ITEMS + list(COVS) + DROPPED + ["IDNR"])
    for c in known:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in known]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, HRQoL domain scores and the autonomy sum: {DROPPED}")

    df = df.rename(columns={"IDNR": "id", **COVS})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        df[cov] = pd.to_numeric(df[cov]).astype("Int64")

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 1-5 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
