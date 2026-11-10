#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_The_Mediating_Role_of_Anxiety_in_the_Relationship_Between_Misophonia_and_Quality_of_Life_Findings_from_the_Validated_Turkish_Version_of_MisoQuest_b_/24903288
# DOI: 10.6084/m9.figshare.24903288 (data); paper 10.3389/fpsyg.2024.1361645
#   Ay E, Huviyetli M, Cakmak E (2024). The mediating role of anxiety in the relationship between
#   misophonia and quality of life: findings from the validated Turkish version of
#   MisoQuest. Frontiers in Psychology.
# License: CC BY 4.0 (figshare record)
# Data: MisoQuest_Data1_Validity_Reliability-2.sav (548 adults: validity/reliability
#   sample, MisoQuest only) and MisoQuest_Data2_Eng_Correlation.sav (117 adults: MisoQuest
#   + SF-36 + STAI). Two independently collected samples (only 1 of 117 Data2 rows
#   matches any Data1 row on all 14 items + age, consistent with chance).
#
# Tables:
#   ay_2024_misoquest   MisoQuest (Siepsiak et al.), Turkish version, 14 items M1..M14,
#                       1-5 (definitely disagree .. definitely agree). Same items and
#                       response scale in both files -> one table with cov_study
#                       (validity = Data1, correlation = Data2); Data2 ids offset by 1000.
#   ay_2024_stai_state  State-Trait Anxiety Inventory (Turkish, Oner & Le Compte), state
#                       items DSK1_Dur..DSK20_Dur, 1-4, reverse-keyed items raw. Data2 only.
#   ay_2024_stai_trait  STAI trait items DSK21_Sur..DSK40_Sur, 1-4, raw. Data2 only.
#   (item codes for STAI drop the Turkish suffix: DSK21_Sür -> DSK21; each maps to one column)
# Not shipped: SF-36 (deposited as per-item 0-100 transformed scores, not raw responses),
#   MisoQuest totals.
# id: no id column in either file; row index (Data1 1..548, Data2 1001..1117).
# Covariates: cov_age, cov_gender (Female/Male), cov_education (as in each file; Data1
#   six levels, Data2 two levels), cov_study.
# Item text: not shipped -- Data2 SPSS variable labels carry the Turkish MisoQuest and STAI
#   stems; MisoQuest_TurkishVersion.pdf is in the deposit. No register row yet.
import io
import tempfile
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL1 = "https://ndownloader.figshare.com/files/45381304"
URL2 = "https://ndownloader.figshare.com/files/45381310"


def read_sav(url):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        df, meta = pyreadstat.read_sav(f.name, apply_value_formats=False)
    return df, meta


def long(df, items, covs, rename=None):
    t = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    if rename:
        t["item"] = t["item"].map(rename)
    return t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)


def main():
    a, _ = read_sav(URL1)
    b, _ = read_sav(URL2)
    assert len(a) == 548 and len(b) == 117
    M = [f"M{i}" for i in range(1, 15)]
    gmap = {"1": "Female", "2": "Male", 1.0: "Female", 2.0: "Male"}
    a["id"] = range(1, len(a) + 1)
    b["id"] = range(1001, 1001 + len(b))
    a["cov_study"], b["cov_study"] = "validity", "correlation"
    for d in (a, b):
        d["cov_age"] = d["Age"]
        d["cov_gender"] = d["Gender"].map(gmap)
    a["cov_education"] = a["Education"]
    b["cov_education"] = b["Education"].map({1.0: "High School or lower", 2.0: "Undergraduate or higher"})
    covs = ["cov_age", "cov_gender", "cov_education", "cov_study"]
    mq = pd.concat([long(a, M, covs), long(b, M, covs)], ignore_index=True)
    assert mq["resp"].between(1, 5).all() and not mq.duplicated(["id", "item"]).any()
    gate(mq)
    mq.to_csv(OUT / "ay_2024_misoquest.csv", index=False)
    print("misoquest", len(mq), mq.id.nunique())

    covs2 = ["cov_age", "cov_gender", "cov_education"]
    state = [c for c in b.columns if c.startswith("DSK") and c.endswith("_Dur")]
    trait = [c for c in b.columns if c.startswith("DSK") and not c.endswith("_Dur")]
    assert len(state) == 20 and len(trait) == 20
    for name, cols in (("stai_state", state), ("stai_trait", trait)):
        t = long(b, cols, covs2, rename={c: c.split("_")[0] for c in cols})
        assert t["resp"].between(1, 4).all() and t["item"].nunique() == 20
        gate(t)
        t.to_csv(OUT / f"ay_2024_{name}.csv", index=False)
        print(name, len(t), t.id.nunique())


if __name__ == "__main__":
    main()
