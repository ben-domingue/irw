#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/CCMJTJ
# DOI: 10.7910/DVN/CCMJTJ (dataset; paper: Kasparek, Cikara, Hatzenbuehler & McLaughlin,
#   "Childhood violence exposure and social information processing in young adults: Does
#   relationship with the perpetrator matter?" -- no paper DOI on the record)
# Data: Harvard Dataverse 10.7910/DVN/CCMJTJ (2025): KasparekEtAl_2025_SEESAW_Data_v2revision
#       (file 12014410, original CSV): 455 US young adults (18-25, Prolific) x 127 columns;
#       KasparekEtAl_2025_SEESAW_DataDescriptions.xlsx (file 12014415): the question text,
#       response levels and description of every column. The IAT trial file (12014411) is
#       not used (reaction-time process data).
# License: CC BY-NC-SA 4.0 (Dataverse record).
#
# Item text: shipped for phq8, gad7, bhs, bpaq, jvq (DataDescriptions.xlsx: full question
#   text per column and the level labels; see
#   automated_finding/itemtext_verification/make_itemtext_kasparek_2025.py). Not shipped
#   for audit although the same file has it: AUDIT is ship_with_note in the rights
#   register and awaits a ruling.
#
# Tables (item codes are the deposit's column names):
#   kasparek_2025_phq8   phq_1-8    0-3   PHQ-9 items 1-8 (item 9 not administered), "over
#                                         the last month"
#   kasparek_2025_gad7   gad_1-7    0-3   GAD-7, "over the last month"
#   kasparek_2025_bhs    bhs_1-5    0-4   Brief Hypervigilance Scale
#   kasparek_2025_audit  audit_1-10       AUDIT; codes as documented: audit_1 0/1/2/3/5 (the
#                                         codebook gives "5 = 4 or more times a week"; 4 is
#                                         unused), audit_2-8 0-4, audit_9-10 0/2/4.
#                                         audit_2-10 blank for the 156 who never drink.
#   kasparek_2025_bpaq   bp_1-29    1-5   Buss-Perry Aggression Questionnaire
#   kasparek_2025_jvq    jvq_{4,5,9,10,14,19,27,28,29,30}_di  0/1  Juvenile Victimization
#                                         Questionnaire screeners (childhood violence types
#                                         endorsed in the jvq_cl checklist; 1 = endorsed)
# Skipped: subjectID (Prolific ID -- replaced by the row index, never hashed; ruled
#   2026-09-20); the two attention checks (bhs_check, bp_check; everyone passed); the
#   PHQ/GAD difficulty items (phq_10, gad_8: a different question and format); totals;
#   jvq_cl (the multi-select string the *_di columns decode) and the jvq_kin_* follow-ups
#   (asked only for endorsed types); the minimal-group manipulation and identification
#   sliders; IAT D scores; free-text language description; derived exposure groupings
#   other than those kept as covariates.
# Covariates: cov_gender (1 cisgender, 2 non-binary/genderqueer, 3 transgender), cov_race
#   (codebook codes 1-7), cov_parent_education (1-6), cov_age, cov_sex (Prolific profile),
#   cov_n_violence_types (num_all_violence), cov_perpetrator_group (perp_status). 999 ->
#   missing.

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "kasparek_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/12014410?format=original"

JVQ = [4, 5, 9, 10, 14, 19, 27, 28, 29, 30]
AUDIT_PV = {"audit_1": {0, 1, 2, 3, 5}, **{f"audit_{i}": set(range(5)) for i in range(2, 9)},
            "audit_9": {0, 2, 4}, "audit_10": {0, 2, 4}}
TABLES = {
    "kasparek_2025_phq8": {f"phq_{i}": set(range(4)) for i in range(1, 9)},
    "kasparek_2025_gad7": {f"gad_{i}": set(range(4)) for i in range(1, 8)},
    "kasparek_2025_bhs": {f"bhs_{i}": set(range(5)) for i in range(1, 6)},
    "kasparek_2025_audit": AUDIT_PV,
    "kasparek_2025_bpaq": {f"bp_{i}": set(range(1, 6)) for i in range(1, 30)},
    "kasparek_2025_jvq": {f"jvq_{i}_di": {0, 1} for i in JVQ},
}
COVS = {"Gender": "cov_gender", "Race_ethnicity": "cov_race",
        "Highest_parent_edu": "cov_parent_education", "Age": "cov_age", "Sex": "cov_sex",
        "num_all_violence": "cov_n_violence_types", "perp_status": "cov_perpetrator_group"}


def fetch() -> Path:
    p = RAW_DIR / "seesaw_data_v2revision.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (455, 127), d.shape
    assert d["subjectID"].is_unique
    items = [c for pv in TABLES.values() for c in pv]
    skipped = [c for c in d.columns if c not in set(items) | set(COVS)]
    print(f"  skip {len(skipped)} columns (Prolific ID, attention checks, difficulty items, "
          "totals, JVQ checklist/follow-ups, group manipulation, IAT scores, free text)")
    assert (d["bhs_check"] == 2).all() and (d["bp_check"] == 4).all()
    for c in skipped:
        assert re.match(r"(subjectID|bhs_check|bp_check|phq_10|gad_8|.*_tot|jvq_cl|jvq_kin_\d+|"
                        r"num_kingroup_violence|Fluent\.languages|nationality|language.*|"
                        r"colorblindness|exposure_group_detailed\.y|di_violence_.*|Team_.*|"
                        r"[ER]_identification_.*|.*group_identification_score.*|d_crit|"
                        r"D_[IO]G_valence)$", c), c
    d = d.drop(columns=["subjectID"]).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)  # row index replaces the Prolific ID
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in ("cov_gender", "cov_race", "cov_parent_education"):
        d[c] = d[c].where(d[c] != 999).astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, pv in TABLES.items():
        its = list(pv)
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        for it in its:
            assert t.loc[t["item"] == it, "resp"].isin(pv[it]).all(), (name, it)
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
