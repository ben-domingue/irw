#!/usr/bin/env python3
# Source: https://peerj.com/articles/17134/
# DOI: 10.7717/peerj.17134
# "Validation of the questionnaire 'Pregnancy Vaccine Hesitancy Scale (pVHS)'
# toward COVID-19 vaccine for Malaysian pregnant women" (Che Mood et al., 2024),
# PeerJ 12:e17134.
# Data: peerj-12-17134-s001.xlsx ("Dataset for vaccine hesitancy items"),
#       fetched via the Europe PMC supplementaryFiles endpoint for PMC10977085.
# License: CC BY 4.0 (PeerJ; confirmed in the Europe PMC full-text <license>
#          element). Article-attached Supporting Information, so the article
#          licence is the source licence -- no separate deposit.
#
# Item text: shipped (paper Table 2 lists every item pL1-pL10 against its code,
#   in the administered Malay and the authors' own English; anchors from the
#   paper's Methods and the Malay scale in S2). mapping_basis=paper_explicit,
#   so verify_che_mood_2024_pvhs.R checks the code->data tie against the
#   paper's own statistics.
#
# Layout: one sheet, 200 rows x 10 columns headed "pL 1" .. "pL  10" (the
# number of spaces varies; they are normalised to pL1..pL10, the codes the
# paper uses). No id column and no covariates in the deposit -- the triage
# "low-confidence id mapping" was the first item column being guessed as an
# id. id is the row index.
#
# Scale: 1 strongly disagree, 2 disagree, 3 not sure, 4 agree, 5 strongly
# agree (Methods, Stage 1). The paper says pL5 and pL9 "were given reverse
# scoring". The deposit stores them UNREVERSED -- checked, not assumed: the
# paper's 10-item Cronbach alpha is 0.859; this file gives 0.887 as stored and
# 0.859 with pL5/pL9 reflected (6 - x). So the authors reflected them at
# analysis time and every column here is raw agreement with the item as worded.
# No recoding is applied (direction may differ across items).
#
# All 10 administered items ship, including pL5 and pL9, which the paper's EFA
# dropped from the final 8-item pVHS-M (loadings 0.096 / 0.119). They were
# administered and answered; IRW keeps them.
#
# No imputation language in the paper; all cells are integers 1-5, no NaN.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10977085/supplementaryFiles"
XLSX = "peerj-12-17134-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "che_mood_2024_pvhs"
ITEMS = [f"pL{i}" for i in range(1, 11)]


def load() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.read_excel(BytesIO(fh.read()))
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def convert() -> None:
    wide = load()
    wide.columns = [str(c).replace(" ", "") for c in wide.columns]
    # Books: every source column must be one of the ten items.
    extra = [c for c in wide.columns if c not in ITEMS]
    assert not extra, f"unexpected source columns: {extra}"
    assert list(wide.columns) == ITEMS, wide.columns.tolist()

    wide = wide.reset_index(drop=True)
    wide.insert(0, "id", wide.index + 1)
    long = wide.melt(id_vars=["id"], value_vars=ITEMS,
                     var_name="item", value_name="resp").dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all(), "fractional resp -- chase imputation"
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    assert long["resp"].between(1, 5).all(), "resp outside 1-5"
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 10

    bad = [c for c in run_qc(long, permitted_values=[1, 2, 3, 4, 5])
           if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]
    report = irw_validate.validate_frame(long, label=TABLE, profile="upload")
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():g}-{long['resp'].max():g}")


if __name__ == "__main__":
    convert()
