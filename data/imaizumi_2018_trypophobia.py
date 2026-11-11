#!/usr/bin/env python3
# Source: https://springernature.figshare.com/articles/dataset/MOESM2_of_Rasch_analysis_of_the_Trypophobia_Questionnaire/5891146
# DOI: 10.6084/m9.figshare.5891146 (data); paper 10.1186/s13104-018-3245-5
#   Imaizumi S, Tanno Y (2018). Rasch analysis of the Trypophobia Questionnaire.
#   BMC Research Notes 11:128.
# License: CC BY 4.0 (figshare "CC BY + CC0"; BMC additional file)
# Data: 13104_2018_3245_MOESM2_ESM.xls, sheet "Dataset": 582 healthy native Japanese
#   speakers recruited online (paper's N = 582), ID, Sex, Age and the Trypophobia
#   Questionnaire (Le et al. 2015), Japanese version.
#
# Table: imaizumi_2018_trypophobia -- 17 TQ items, 1-5 (not at all .. extremely), item
#   names are the source column headers (e.g. Feel_freaked_out). The two filler items
#   Want_to_laugh_DUMMY and Feel_at_peace_DUMMY (marked DUMMY in the source, not scored)
#   are dropped. Covariates: cov_sex, cov_age. The source ID is kept as id (1..582).
# Item text: not shipped -- headers are English paraphrases of the stems; the Japanese
#   administered wording is in the paper's Additional file 1 / Imaizumi et al. 2016, not
#   in this deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/10489654"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Dataset")
    assert len(d) == 582 and d["ID"].is_unique
    items = [c for c in d.columns if c not in ("ID", "Sex", "Age") and not c.endswith("_DUMMY")]
    assert len(items) == 17
    d = d.rename(columns={"ID": "id", "Sex": "cov_sex", "Age": "cov_age"})
    t = d[["id", "cov_sex", "cov_age"] + items].melt(id_vars=["id", "cov_sex", "cov_age"],
                                                       var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp", "cov_sex", "cov_age"]].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "imaizumi_2018_trypophobia.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
