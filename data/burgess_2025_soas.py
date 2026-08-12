#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12515426
# DOI: 10.7717/peerj.20153
#
# Burgess et al. (2025), "The 6-item specific object anthropomorphism
# scale (SOAS): a new questionnaire for children and adolescents." PeerJ.
# CC BY 4.0. Study 3 data (peerj-13-20153-s004.sav, N=120 children aged
# 5-12), the study that produced the final 6-item scale via CFA-based item
# reduction. Per the paper's Results ("Confirmatory factor analysis and
# item reduction"), the file's 13 raw SOAS items were reduced to a final
# 6-item scale by removing items 1/2/3/8/13 (overlapping residual
# correlations), item 4 (rephrasing/residual issues), and item 6 (poor
# test-retest reliability) -- retained items are SOAS5, SOAS7, SOAS9,
# SOAS10, SOAS11, SOAS12, matching Table 4's "Final factor loading"
# column exactly. `SOAS*_total`/`SOAS7_total`/`SOAS6_total` are
# pre-computed aggregate scores, excluded. Two waves: baseline (all 120)
# and a ~14-day follow-up retest (SOAS*_fu, 79 respondents, 65.83%
# retention, matches the paper's reported retention rate). 3-point scale:
# 0=no, 1=maybe, 2=yes. No PII (ChildGender/ChildEthnicity/ChildAge/
# ParentGender/ParentEthnicity/ParentAge are ordinary demographic
# covariates; ChildID/ParentID are study-assigned sequential IDs, not
# identifying).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12515426/supplementaryFiles"
MEMBER = "peerj-13-20153-s004.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FINAL_ITEMS = [5, 7, 9, 10, 11, 12]

COV_RENAME = {
    "ChildGender": "cov_child_gender",
    "ChildEthnicity": "cov_child_ethnicity",
    "ChildAge": "cov_child_age",
    "ParentGender": "cov_parent_gender",
    "ParentEthnicity": "cov_parent_ethnicity",
    "ParentAge": "cov_parent_age",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with io.BytesIO(zf.read(MEMBER)) as buf:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
            tmp.write(buf.getvalue())
            tmp.flush()
            df = pd.read_spss(tmp.name)

    df = df.rename(columns={"ChildID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    assert df["id"].nunique() == len(df)
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    base_items = [f"SOAS{i}" for i in FINAL_ITEMS]
    fu_items = [f"SOAS{i}_fu" for i in FINAL_ITEMS]

    base = df.melt(id_vars=["id"] + cov_cols, value_vars=base_items,
                    var_name="item", value_name="resp")
    base["wave"] = 1

    fu = df.melt(id_vars=["id"] + cov_cols, value_vars=fu_items,
                 var_name="item", value_name="resp")
    fu["item"] = fu["item"].str.replace("_fu", "", regex=False)
    fu["wave"] = 2

    long = pd.concat([base, fu], ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 2)]

    out_cols = ["id", "item", "resp", "wave"] + cov_cols
    long = long[out_cols]

    out_path = OUT_DIR / "burgess_2025_soas.csv"
    long.to_csv(out_path, index=False)
    print(f"burgess_2025_soas: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
