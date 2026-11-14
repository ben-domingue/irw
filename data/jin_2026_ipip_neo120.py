#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/A_standardized_personality_lexicon_for_enhancing_natural_language_processing_and_personalized_human-machine_interaction/29596547
# DOI: 10.6084/m9.figshare.29596547.v3 (data)
#   Jin T, Jiang J, Zhang W, Li Y, Yang Y, Zhong H, Hu X (2026). A standardized personality lexicon
#   for enhancing natural language processing and personalized human-machine interaction [Data set].
#   figshare.
# License: CC BY 4.0 (figshare record)
# Data: formal_data_revised_Chinese_version.xlsx, sheet "3600": 300 Chinese adults. Per the record,
#   the formal-study file holds demographics, the IPIP-NEO-120 and ratings of personality adjectives.
#   The English-version file holds identical values (checked) with English headers.
# Table: jin_2026_ipip_neo120 -- the 120 IPIP-NEO-120 items, 1-5, complete for all 300.
#   item = neo_<k>, k = the item number printed at the start of each Chinese column header
#   ("1\t担忧很多事情" -> neo_1), which is the IPIP-NEO-120 item order (1 = "Worry about things").
# Not shipped: the adjective ratings (each adjective rated by a median of 5 participants, ~65 per
#   person -- too sparse for an item table) and the deposited domain scores.
# Covariates: cov_gender, cov_age_group, cov_employment, cov_education (English labels from the English file).
# Item text: SHIPPED -- data_labels + study_materials: the Chinese column headers are the administered
#   stems; the English file's headers are the IPIP originals (public domain, register row IPIP: ship).
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL_ZH = "https://ndownloader.figshare.com/files/61345300"
URL_EN = "https://ndownloader.figshare.com/files/61345303"


def get(url):
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="3600")


def main():
    zh, en = get(URL_ZH), get(URL_EN)
    assert zh.shape == en.shape == (300, 3730)
    neo_zh = list(zh.columns[5:125])
    nums = [int(re.match(r"^(\d+)", str(c)).group(1)) for c in neo_zh]
    assert nums == list(range(1, 121))
    assert (zh.iloc[:, 5:125].values == en.iloc[:, 5:125].values).all()
    assert en.columns[5] == "Worry about things" and en.columns[124] == "Act without thinking"
    d = en.iloc[:, :5].copy()
    d.columns = ["id", "cov_gender", "cov_age_group", "cov_employment", "cov_education"]
    assert d["id"].is_unique
    items = [f"neo_{k}" for k in nums]
    d = pd.concat([d, pd.DataFrame(zh.iloc[:, 5:125].values, columns=items)], axis=1)
    covs = ["cov_gender", "cov_age_group", "cov_employment", "cov_education"]
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    assert t["resp"].notna().all() and t["resp"].isin([1, 2, 3, 4, 5]).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "jin_2026_ipip_neo120.csv", index=False)
    print("jin_2026_ipip_neo120", len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
