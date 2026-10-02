#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.5477932.v2
# DOI: 10.1038/s41598-020-74310-7
#   "Individual and group level personality change across the lifespan in
#   dogs" (Turcsán, Wallis, Berczik, Range, Kubinyi & Virányi, 2020),
#   Scientific Reports 10:17276. Found through the article's Data
#   Availability link; the deposit is the VIDOPET database (Turcsán, Wallis,
#   Virányi et al., figshare, "Personality traits in companion dogs -- Results
#   from the VIDOPET").
# Data: VIDOPETdatabase.xlsx (figshare file 11779076), sheet
#       raw_data_questionnaire (217 dogs x dog name + 45 items); sex and age
#       come from sheet factor_scores, joined on dog name (unique in both).
# License: CC BY 4.0 (figshare record; the article is also CC BY 4.0).
#
# Item text: not shipped. The workbook carries only codes that encode the
#   factor, facet and reverse-keying (q1_F1Facet_1R ...); the factor_scores
#   sheet names the five factors (fearfulness, aggression towards people,
#   activity/excitability, responsiveness to training, aggression towards
#   animals), which is the structure of the 45-item Dog Personality
#   Questionnaire short form (Jones 2008). The wording is in Jones (2008), not
#   in the deposit.
#
# Table: turcsan_2020_dog_dpq -- owner ratings of their dog on the 45 DPQ
#   items, 1-5, codes kept exactly as the sheet spells them (R marks a
#   reverse-keyed item; responses are as recorded, not reversed). id is the
#   dog (row index; dog names are not carried). 11 dogs have no questionnaire
#   answers and drop out, leaving 206.
# No two dogs share an answer pattern. No human PII (owners are not named).

import io
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/11779076"
TABLE = "turcsan_2020_dog_dpq"


def fetch() -> bytes:
    for attempt in range(6):
        try:
            r = requests.get(URL, headers=UA, timeout=300)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(20 * (attempt + 1))


def convert() -> None:
    blob = fetch()
    q = pd.read_excel(io.BytesIO(blob), sheet_name="raw_data_questionnaire")
    fs = pd.read_excel(io.BytesIO(blob), sheet_name="factor_scores", header=1)
    assert q.shape == (217, 46), q.shape
    items = [c for c in q.columns if c != "dog name"]
    assert len(items) == 45 and all(str(c).startswith("q") for c in items)
    assert q["dog name"].is_unique and fs["dog name"].is_unique
    print("  skip dog name: identifier, replaced by row index")

    fs = fs[["dog name", "sex", "age"]].rename(
        columns={"sex": "cov_sex", "age": "cov_age_years"})
    d = q.merge(fs, on="dog name", how="left", validate="one_to_one")
    assert len(d) == 217
    d = d[d[items].notna().any(axis=1)].reset_index(drop=True)
    assert len(d) == 206, len(d)
    assert not d[items].duplicated().any()
    d.insert(0, "id", d.index + 1)
    d = d.drop(columns=["dog name"])
    cov_cols = ["cov_sex", "cov_age_years"]

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                  var_name="item", value_name="resp")
    n_na = int(long["resp"].isna().sum())
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all()
    assert not set(long["resp"]) - {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    print(f"  dropped {n_na} blank cells")

    pv = {i: {1, 2, 3, 4, 5} for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
