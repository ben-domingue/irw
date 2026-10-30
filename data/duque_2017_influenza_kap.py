#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0173983
# DOI: 10.1371/journal.pone.0173983
# Paper: Duque, J., Gaga, S., Clark, D., Muller, M., Kuwane, B., & Cohen, C.
#   (2017). Knowledge, attitudes and practices of South African healthcare
#   workers regarding the prevention and treatment of influenza among
#   HIV-infected individuals. PLOS ONE 12(3).
# Data: journal.pone.0173983.s001 (S1 Table, .xlsx), 1,164 rows x 79 columns.
# License: CC0 1.0 (Crossref licence record for the version of record --
#   https://creativecommons.org/publicdomain/zero/1.0/).
# 1,164 healthcare workers in public clinics and hospitals across 21
# districts/municipalities in 5 of South Africa's 9 provinces.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FIVE output tables, 33 items. This is a KAP survey, so most of its 79
# columns are standalone questions rather than scales; what ships is the five
# multi-option batteries, and every one of their codings is VERIFIED against a
# statistic the paper reports rather than assumed.
#
# THE CODING IS RECONSTRUCTED FROM THE PAPER, THREE WAYS. The deposit carries
# no codebook, so each shipped battery's coding had to be pinned:
#   1. Symptoms. The paper: "most identified runny nose (94%), fever (92%),
#      cough (87%), and sore throat (78%) as symptoms of influenza illness".
#      The deposit's booleans give 93.5 / 91.9 / 87.1 / 78.0 -- so True means
#      "identified", on all four, to the rounding. That also settles the
#      boolean convention for the other three checklist batteries.
#   2. Vaccine access locations. The paper: "only 49% reported access to
#      influenza vaccines at their workplace". Vac_workplace is True for
#      49.3%. Confirms the same True = reported convention on a second
#      battery.
#   3. Reasons to vaccinate, 1-4, where the DIRECTION was the open question.
#      The paper: "Protecting themselves, their families and their patients
#      against influenza were reported as MORE IMPORTANT reasons to get
#      vaccinated than not missing work (p-value <0.01)". Means: the
#      protect-triad averages 3.645 against Dont_miss_work's 3.402. So higher
#      = more important. Had the scale run the other way the inequality would
#      have reversed, which is exactly the trap li_2024_deg_* in this same
#      batch fell into (its scale really does run backwards).
# All three checks are asserted in the script, so a re-deposit with different
# coding fails here instead of shipping an inverted construct.
#
#   duque_2017_flu_symptom_knowledge   8 items, 0/1  checklist of symptoms,
#                                      including the distractors hair loss and
#                                      diarrhoea (29 and 123 endorsements)
#   duque_2017_flu_vaccine_access      4 items, 0/1  where vaccine is available
#   duque_2017_flu_info_sources        9 items, 0/1  where they get influenza
#                                      information
#   duque_2017_flu_campaign_media      6 items, 0/1  where they saw the
#                                      national vaccination campaign
#   duque_2017_flu_vaccination_reasons 6 items, 1-4  importance of each reason
#
# A CHECKLIST IS A BATTERY; A COLLAPSED MULTI-SELECT IS NOT. The four 0/1
# tables come from "circle all that apply" questions rendered as ONE COLUMN
# PER OPTION, which makes each option a yes/no item and the set a legitimate
# battery. That is the opposite of the multi-selects dropped from
# sabrina_2026 and kimuli_2025 in this batch, where a whole pick-list was
# collapsed into a SINGLE numeric column and so could not represent a set at
# all. The distinction is the file layout, not the question wording.
#
# RISK GROUPS (9 items) IS HELD, and it is the one battery no reconstruction
# could pin. Its columns take 1, 2 and a very rare 3 (1-15 responses each), so
# 3 is almost certainly an undocumented "don't know" -- which would make the
# three codes non-ordered, the same shape as kimuli_2025_tb_stigma. The
# difference is that for Kimuli the deposit's own composite PROVED the
# mapping, and here nothing does. The circumstantial evidence is actually
# fairly strong that 1 = "yes, high risk": people with HIV score 1 at 97% in a
# study about influenza in HIV-infected people, while the general population
# -- the one listed group that is NOT high risk -- scores 1 at only 39%. But
# "fairly strong" is not proof, and on a KNOWLEDGE battery getting it backwards
# inverts the construct: every correct answer would ship as incorrect. The
# paper's own summary ("correctly circled at least one of these groups 71% to
# 94% of the time") is an at-least-one statistic that no per-item share
# reproduces. So the battery is left out, with the evidence recorded both ways;
# it is recoverable the moment a codebook surfaces.
#
# GEOGRAPHY AND FREE TEXT ARE DROPPED. `hosp_district` names the district
# (Bojanala, Sekhukhune, Mopani, ... 25 spellings for 21 districts, including
# case variants) -- sub-national administrative geography, excluded under the
# 2026-10-20 ruling. Four free-text columns are dropped too: `month_vac_rec`
# (semicolon-joined month lists), `Opinion_Other`, `med_names` (472 distinct
# drug and remedy write-ins) and `Protect_other`. The last one is worth
# naming: it contains self-disclosed health information ("I am a diabetic
# patient", "Post stemcell transplant no flu vaccine allowed"). No names,
# emails, phone numbers or dates appear in any of them, so this is not a PII
# skip under the rule as written -- but free text is never shipped as `resp`
# and none of it reaches the output.
#
# `id` is the deposit's `ID`, verified unique over all 1,164 rows. The
# companion `IDP` column is entirely empty and is dropped.
#
# Item text: NOT SHIPPED. The deposit's column names are keywords
# (`Runny_Nose`, `Protect_myself`), not stems, and the article reports results
# rather than reproducing the questionnaire. The instrument is a
# study-specific KAP questionnaire, so rights would most likely be clear --
# there is simply no wording to ship.
#
# PII: screened over all 79 columns. The four free-text columns are examined
# and matched against the usual patterns; no email, phone, date or name
# appears. See the geography note above for what is dropped and why.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DUQUE_RAW", "journal.pone.0173983_S1_Table.xlsx")

N_ROWS = 1164

SYMPTOMS = ["Runny_Nose", "Cough", "Difficulty_Breath", "Diarrhoea", "Fever",
            "Hair_loss", "Sore_throat", "Chills"]
ACCESS = ["Vac_workplace", "Vac_clinic", "Vac_privateGP", "Vac_pharm"]
SOURCES = ["Scientific", "university", "internet", "newspaper",
           "train_seminars", "train_outside", "libraries", "colleagues", "FnF"]
MEDIA = ["Television", "radio", "internet2", "newspaper2", "colleagues2", "FnF2"]
REASONS = ["Protect_myself", "Protect_patients", "Protect_family",
           "Hosp_requires", "Dont_miss_work", "Free_of_charge"]
# held -- see the header
RISK_GROUPS = ["preg_women", "HC_workers", "Older_65", "Pers_HIV", "Pers_TB",
               "Pers_asthma", "Gen_pop", "Young_child", "Chronic_med"]

BOOL_TABLES = {
    "duque_2017_flu_symptom_knowledge": SYMPTOMS,
    "duque_2017_flu_vaccine_access": ACCESS,
    "duque_2017_flu_info_sources": SOURCES,
    "duque_2017_flu_campaign_media": MEDIA,
}
COVS = {"hosp_type": "cov_facility_type", "hosp_role": "cov_role",
        "Med_aid": "cov_medical_aid"}
FREE_TEXT = ["month_vac_rec", "Opinion_Other", "med_names", "Protect_other"]
GEOGRAPHY = ["hosp_district"]

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(strings)} string column(s) of "
          f"{len(df.columns)}")
    hits = [(c, v[:40]) for c in strings
            for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print(f"  clean. {len(FREE_TEXT)} free-text columns present and dropped "
          f"(one holds self-disclosed health information); "
          f"{len(GEOGRAPHY)} district column dropped under the geographic ruling")


def verify_coding(df):
    """Three independent reconstructions of the paper's own reported
    statistics. Each pins a coding the deposit never documents."""
    # 1. symptoms: the paper's Table 2 percentages
    want = {"Runny_Nose": 94, "Fever": 92, "Cough": 87, "Sore_throat": 78}
    got = {c: 100 * df[c].sum() / df[c].notna().sum() for c in want}
    for c, pct in want.items():
        assert abs(got[c] - pct) <= 1.0, (
            f"{c} is {got[c]:.1f}% but the paper reports {pct}% identifying it "
            f"as an influenza symptom -- True may not mean 'identified'")
    print("coding check 1/3 PASS: symptom shares "
          f"{ {c: round(v, 1) for c, v in got.items()} } reproduce the paper's "
          f"94/92/87/78, so True = 'identified'")

    # 2. access: "only 49% reported access ... at their workplace"
    wp = 100 * df["Vac_workplace"].sum() / df["Vac_workplace"].notna().sum()
    assert abs(wp - 49) <= 1.0, f"Vac_workplace is {wp:.1f}%, paper says 49%"
    print(f"coding check 2/3 PASS: Vac_workplace {wp:.1f}% reproduces the "
          f"paper's 49%, confirming True = 'reported' on a second battery")

    # 3. reasons: direction. The paper ranks the protect-triad ABOVE
    #    not-missing-work, so higher must mean more important.
    triad = df[["Protect_myself", "Protect_family", "Protect_patients"]] \
        .mean().mean()
    miss = df["Dont_miss_work"].mean()
    assert triad > miss, (
        f"protect-triad mean {triad:.3f} is not above Dont_miss_work "
        f"{miss:.3f}; the paper says the triad is MORE important, so the "
        f"1-4 scale may run in the opposite direction")
    print(f"coding check 3/3 PASS: protect-triad mean {triad:.3f} > "
          f"Dont_miss_work {miss:.3f}, matching the paper's ranking, so "
          f"higher = more important")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    verify_coding(df)

    assert df["IDP"].isna().all(), "IDP is no longer empty -- recheck it"
    assert df["ID"].nunique() == len(df), "ID is not unique"
    print(f"holding the {len(RISK_GROUPS)}-item risk-groups battery: its third "
          f"code is undocumented and no reported statistic pins which of 1/2 "
          f"means 'yes' (see header)")

    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols in BOOL_TABLES.items():
        for c in cols:
            vals = set(df[c].dropna().unique())
            assert vals <= {True, False}, (c, vals)
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        total += _write(name, long, cols, 0, 1)

    for c in REASONS:
        vals = set(pd.to_numeric(df[c], errors="coerce").dropna().unique())
        assert vals <= {1, 2, 3, 4}, (c, vals)
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=REASONS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    total += _write("duque_2017_flu_vaccination_reasons", long, REASONS, 1, 4)

    print(f"5 tables, {total} responses (33 items x {N_ROWS} respondents, "
          f"less per-cell nonresponse; the 9-item risk-groups battery is held)")


def _write(name, long, cols, lo, hi):
    cov_cols = sorted(COVS.values())
    assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())
    assert long["id"].nunique() >= 100, (name, long["id"].nunique())
    assert long["item"].nunique() == len(cols)
    assert not long.duplicated(["id", "item"]).any()
    assert len(name) <= 40, name
    long = long[["id", "item", "resp"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                            for i in cols})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")
    return len(long)


if __name__ == "__main__":
    convert()
