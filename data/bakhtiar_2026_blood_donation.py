#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/33943117
# DOI: 10.6084/m9.figshare.33943117.v1 (data)
#   Bakhtiar A, Omer F, Naveed F, Wajid D, Khan M, Hanif R (2026). Does MBBS Progression Improve
#   Blood Donation Behavior? A Mixed-Methods KAP study [Data set]. figshare.
# License: CC BY 4.0 (figshare)
# Data: MBBS_blood_donation_dataset_deidentified.xlsx, 209 MBBS students at Akhtar Saeed Medical
#   College, Rawalpindi, Pakistan; variable names give the questionnaire section (K knowledge,
#   A attitude, P practice, BAR barrier, MOT motivator).
#
# Table: bakhtiar_2026_blood_donation_attitudes -- the twelve A items (A1-A8 then A9-A12, which the
#   questionnaire places after the practice block), 1-5 agreement as stored; A8 (concern about
#   infection), A10 (a negative experience discouraged me) and A12 (donating is time-consuming) are
#   negatively worded and NOT reversed. item = the deposit's column name. A10 is never above 4.
# Not shipped: K1-K10 knowledge (coded 1/2/3, K8 1-4; the deposit gives neither the options nor the
#   key, and IRW will not guess one); P1-P6 (heterogeneous single questions); BAR_/MOT_ (multi-select
#   checkboxes). Covariates: Gender, Age (grouped) and AcademicYear are codes with no key in the
#   deposit, so none are carried.
# id: the deposit's ID (1-209).
# Item text: not shipped -- the column names paraphrase each statement (A2_ImportantSaveLives), but
#   the questionnaire wording is not in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/69095500"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 209 and d["ID"].is_unique
    items = [c for c in d.columns if c.split("_")[0] in {f"A{i}" for i in range(1, 13)}]
    assert len(items) == 12
    skipped = [c for c in d.columns if c not in items and c != "ID"]
    print("not shipped:", skipped)
    t = d[["ID"] + items].melt(id_vars="ID", var_name="item", value_name="resp")
    t = t.rename(columns={"ID": "id"}).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp"]].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "bakhtiar_2026_blood_donation_attitudes.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
