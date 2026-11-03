#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273254
# DOI: 10.1371/journal.pone.0273254
# Paper: Hazell, C. M., Fixsen, A., & Berry, C. (2022). Is it time to change
#   the approach of mental health stigma campaigns? An experimental
#   investigation of the effect of campaign wording on stigma and
#   help-seeking intentions. PLOS ONE 17(8): e0273254.
# Data: journal.pone.0273254.s001 (S1 File, .sav), 1,046 adults aged 16+
#   recruited online (social media, forums, snowball), 2018.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# Design: pre-post. Each measure was completed (T0), the participant viewed
# one of two randomised anti-stigma posters, then completed the same
# measures again (T1). `wave` = 1 (T0, columns AQ1.., IAMHS1..) and 2 (T1,
# columns AQpost1.., IAMHSpost1..); the item ids drop the "post" so the same
# item carries the same id in both waves.
#
# TWO output tables:
#   hazell_2022_aq      Attribution Questionnaire, 20-item version (Corrigan
#                       et al.), AQ1-AQ20, 1-9 with item-specific anchors
#                       (e.g. 1 "Not at all" .. 9 "Very much"; AQ12 1
#                       "Definitely would not help" .. 9 "Definitely would
#                       help"; AQ18/AQ20 1 "Definitely" .. 9 "Definitely
#                       not"). As deposited, nothing reversed.
#   hazell_2022_iasmhs  Inventory of Attitudes toward Seeking Mental Health
#                       Services (Mackenzie et al. 2004), 24 items,
#                       IAMHS1-IAMHS24, 0 "Disagree" .. 4 "Agree". As
#                       deposited, nothing reversed.
#
# THE RANDOMISED ARM IS NOT SHIPPED. `Experimental_Group` is 1 = "Them and
# Us" (categorical) poster vs 2 = "All together" (non-categorical) poster:
# two active arms, no control. datastandard.md defines `treat` as 1 =
# treatment / 0 = control and forbids hiding an arm in a cov_*; this is the
# same open question as lin_2026_advertising_literacy (TODO.md, "what does
# `treat` do in a multi-arm design?"), so it is left out, not guessed.
#
# Covariates: age, gender, ethnicity, country of residence, education,
# employment status, first language, and personal experience of mental
# health problems (1 Never .. 7 A great deal), all with the .sav's own value
# labels. Dropped: consent checkboxes (constant), the free-text *_other
# fields, Where_hear (free-text recruitment source), attention checks,
# familiarity slider, filter_$, Country_Dummy (derivable), sexuality,
# religion, marital status, accommodation, Sussex_UG, Exp_MH_others, and
# all derived subscale/total scores.
#
# PII: Where_hear ("Where did you hear about this questionnaire?") holds a
# handful of first names and full names -- of recruiters (a research
# assistant who posted the advert) and of public figures whose tweets shared
# it (journalists, a comedian). None names a respondent and the column's job
# is a recruitment channel, so this is INCIDENTAL under SKILL.md's rule; the
# column is not carried in any form. No email addresses (screened).
#
# Item text: NOT SHIPPED. Both label levels are present and complete
#   (variable labels hold every stem; value labels the anchors), but both are
#   named third-party instruments with no grant in
#   itemtext/instrument_rights_register.csv: AQ (Corrigan et al. 2003) and
#   IASMHS (Mackenzie, Knox, Gekoski & Macaulay 2004) -- HELD 2026-11-02,
#   register rows written. Text is one hop away in this .sav.

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HAZELL_RAW", "journal.pone.0273254.s001.sav")
N_ROWS = 1046

COVS = {"Age": "cov_age", "Gender": "cov_gender", "Ethnicity": "cov_ethnicity",
        "Country_residence": "cov_country", "Education": "cov_education",
        "Employment_status": "cov_employment", "First_language": "cov_first_language",
        "Exp_MH_personal": "cov_mh_experience_personal"}
DROP = ["Consent_%d" % i for i in range(1, 9)] + [
    "Gender_other", "Country_birth", "Country_birth_other", "Marital_status", "Religion",
    "Religion_other", "Sexuality", "Sexuality_other", "Accommodation", "Sussex_UG",
    "Exp_MH_others", "Where_hear", "Experimental_Group", "Attention_Check1",
    "Attention_Check1ANSWER", "Attention_Check2", "Attention_Check2ANSWER", "Attention_Check3",
    "Attention_Check3ANSWER", "Attention_CheckCommon", "Attention_CheckFamiliar", "filter_$",
    "Country_Dummy"]
BLOCKS = {"aq": ("AQ", "AQpost", 20, range(1, 10)), "iasmhs": ("IAMHS", "IAMHSpost", 24, range(0, 5))}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(txt) == 4
    email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
    for c in txt:
        hits = [v for v in df[c] if "@" in str(v) or re.search(r"\b\d{6,}\b", str(v))]
        print(f"  {c}: {len(hits)} '@'/long-number hits {hits}")
        assert not any(email.search(v) for v in hits)  # one hit is a Twitter handle, not an email
    vl = meta.variable_value_labels
    df["id"] = range(1, N_ROWS + 1)
    cov_cols = list(COVS.values())
    for src, dst in COVS.items():
        if src == "Age":
            df[dst] = df[src]
        else:
            df[dst] = df[src].map(vl[src])
            assert df[dst].notna().sum() == df[src].notna().sum(), src
    derived = [c for c in df.columns if c.endswith(("_TOTAL", "_PSYCHOPEN", "_HELPSEEK", "_INDIFFSTIG"))
               or re.match(r"AQ_(post)?[A-Z]+$", c)]
    used = set(COVS) | set(DROP) | set(derived)
    names, total = [], 0
    for block, (pre, post, k, scale) in BLOCKS.items():
        parts = []
        for wave, pfx in ((1, pre), (2, post)):
            cols = [f"{pfx}{i}" for i in range(1, k + 1)]
            used |= set(cols)
            w = df[["id"] + cov_cols + cols].rename(columns={f"{pfx}{i}": f"{pre}{i}" for i in range(1, k + 1)})
            w = w.melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
            w["wave"] = wave
            parts.append(w)
        long = pd.concat(parts).dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(scale), set(long["resp"])
        long = long[["id", "item", "resp", "wave"] + cov_cols].sort_values(["id", "wave", "item"])
        assert not long.duplicated(["id", "item", "wave"]).any()
        items = sorted(long["item"].unique())
        checks = run_qc(long, permitted_values={c: list(scale) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"hazell_2022_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(items)} "
              f"waves={long.groupby('wave').size().to_dict()}")
    assert len(set(names)) == len(names)
    missing = set(meta.column_names) - used
    assert not missing, missing
    print(f"total responses {total}; derived score columns dropped: {len(derived)}")


if __name__ == "__main__":
    convert()
