#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/33014132
# DOI: 10.6084/m9.figshare.33014132
#   Cao, H., & Chen, P.-F. (2026). Anonymized survey dataset of Digital Health
#   Literacy Scale for Chinese Undergraduate Students [Dataset]. figshare.
# Data: the deposit's single .xls -- 1,292 Chinese undergraduates, 13 items in
#   four prefixed blocks, complete (no missing cell).
# License: CC BY 4.0 (verified on the figshare record, 2026-10-19).
# Item text: NOT shipped. The deposit is one .xls with bare codes
#   (DCE1-3, IU1-3, IE1-4, AA1-3); there is no label level in an .xls and no
#   codebook in the record, so the wording is in the paper only.
#
# ONE table, not four, because this is one instrument. The deposit is the
#   validation sample for a Digital Health Literacy Scale, and the four
#   prefixes are its subscales -- shipping them as four tables would also mean
#   naming four constructs from codes the deposit never expands (DCE, IU, IE,
#   AA), which is a guess. The prefix is preserved in the item code, so a
#   later pass can split without reprocessing.
#
# The observed range is 2-5 on all thirteen items: no respondent used the
#   bottom category. 1-5 is the permitted scale and 1 is simply unused, which
#   is why `permitted_values` is passed explicitly rather than inferred.
#
# id: the row index. The deposit carries no respondent id.
# Covariates: cov_gender (M/F), cov_education_level (F/H/S/J, unexpanded in
#   the deposit), cov_region (1-3), cov_use_frequency (1-5).
import os
import re
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
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "33014132" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 33014132
FNAME = "Anonymized_dataset_Digital_Health_Literacy.xls"
ITEM_RE = re.compile(r"^(DCE|IU|IE|AA)\d+$")
SCALE = set(range(1, 6))
COVS = {"Gender": "cov_gender", "Educational level": "cov_education_level",
        "Region": "cov_region", "Frequency": "cov_use_frequency"}
TABLE = "cao_2026_digital_health_literacy"


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch())
    items = [c for c in df.columns if ITEM_RE.match(str(c))]
    assert len(items) == 13, items
    assert len(df) == 1292, len(df)
    assert not df.isna().any().any(), "the file is complete; a blank is new"
    assert sorted(set(df.columns) - set(items)) == sorted(COVS), \
        sorted(set(df.columns) - set(items))

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in ("cov_region", "cov_use_frequency"):
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")
    for cov in ("cov_gender", "cov_education_level"):
        df[cov] = df[cov].astype(str)

    t = (df[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the 1-5 scale: {bad}"
    print(f"observed range {t['resp'].min()}-{t['resp'].max()} of a permitted "
          f"1-5: the bottom category is unused")
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 1292 and t["item"].nunique() == 13

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:150]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
