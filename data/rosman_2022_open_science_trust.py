#!/usr/bin/env python3
# Source: https://www.psycharchives.org/en/item/cf48d773-6862-4bcc-b690-e210320ee851
# DOI: 10.23668/psycharchives.6495
# Deposit: Rosman, T., Bosnjak, M., Silber, H., Koessler, J., & Heycke, T.
#   (2022). Dataset for: Open Science and public trust in science: Results from
#   two studies. Public Understanding of Science. PsychArchives (ZPID).
# Data: Rosman_et_al_2022_Study_1_data.sav (504 respondents) and
#   Rosman_et_al_2022_Study_2_data.sav (588). The deposit also ships .csv
#   copies of both; the .sav files are read because they carry the variable and
#   value labels, which is where every item stem lives.
# License: CC BY-SA 4.0 (resolved from the PsychArchives record:
#   https://creativecommons.org/licenses/by-sa/4.0/). SA propagates into
#   Derived_License.
#
# Found by the PsychArchives recycled-terms discovery pass of 2026-10-29, which
# is the connector's first real yield: 346 of the oldest, most ordinary terms in
# search_terms_log.csv that had never been run against this source returned 227
# candidates, where 135 freshly-invented terms had returned none.
#
# Triage saw only Study 2 (it opens one file per candidate), so it reported
# 588 x 136. Both studies are here.
#
# Seven output tables. The deciding question for each is whether Study 1 and
# Study 2 administered the SAME instrument on the SAME scale -- the
# collapse-same-instrument rule -- and it is checked against the .sav labels
# rather than assumed:
#
#   rosman_2022_trust_science            5 items, 1-6, BOTH studies, 3 waves'
#                                        worth of occasions in 2 wave values
#   rosman_2022_trust_factors_scientist 14 items, 1-7, BOTH studies
#   rosman_2022_trust_factors_general   14 items, 1-7, BOTH studies
#   rosman_2022_meti_s1                 14 items, 1-5, Study 1 ONLY
#   rosman_2022_meti_s2                 14 items, 1-7, Study 2 ONLY
#   rosman_2022_justification_beliefs   18 items, 1-6, Study 2 only
#   rosman_2022_conspiracy               9 items, 1-6, Study 2 only
#
# WHY THE METI IS TWO TABLES AND NOT ONE. It is the same 14 columns with the
# same names in both files, which is exactly the shape that invites a wrong
# merge. The value labels say otherwise: Study 1 runs the semantic
# differentials on 1-5 and Study 2 on 1-7, and even the anchor adjectives
# differ (S1 "inkompetent - kompetent", S2 "unqualifiziert - qualifiziert").
# A merged table would silently put two response formats on one `resp`. The
# three merged tables above were each confirmed first: identical column names,
# identical stems and identical anchors in both files, with one exception noted
# below that is not a difference.
#
# The `trust_factors_scientist` stems agree across the two studies except
# `trustf_osp_03`, where Study 1's label ends in a full stop and Study 2's does
# not. Same item; the shipped stem would be Study 2's. (Item text is not
# shipped in this batch -- see below -- but the comparison is what licensed the
# merge, so it is recorded here.)
#
# WAVE. Study 2 measured the 5-item trust scale before and after reading four
# study descriptions (`trust_t1_*` and `trust_t2_*`); Study 1 measured it once.
# So `wave` is 1 for Study 1 and for Study 2's pre-measure, 2 for Study 2's
# post-measure. Unbalanced by design: no Study 1 respondent has a wave 2.
#
# ID COLLISION. Both files number respondents from their own `lfdn` and the
# ranges overlap, so every id is prefixed with its study ("s1_33", "s2_33") and
# the study is also kept as `cov_study` -- the stacked-samples rule.
#
# resp = 0 IS DROPPED, in all seven tables. Every item's value labels define
# 1-6 or 1-7 and nothing else, yet a handful of cells across Study 2 hold 0
# (one in `trust_t2_01`, one in `trustf_exp`, one in `consp_01`, and so on).
# `missing_ranges` is empty in both files, so the 0 is not declared -- it is
# this export's no-answer code, the same pattern as the DIALLS deposit in this
# same batch. The count is printed per table.
#
# Item text: NOT shipped, and the wording is all in hand -- every one of these
# 92 items has its full German stem in the .sav's variable labels and its
# German anchors in the value labels. The reason is cost, not availability and
# not rights (study-authored instruments in a CC BY-SA deposit, except the METI
# and the conspiracy-belief scale, which are published instruments needing
# register rows of their own). The administration was German, so the standard
# requires the German wording in `item_text` AND an English translation in the
# `*_translated` columns; producing ~92 translations is IRW-generated content
# that owes its own issues-page entry and provenance, which is a job of its
# own rather than a cheap extraction. Recorded in TODO.md with this exact
# diagnosis so the next pass starts from an answer. Label levels checked: BOTH
# are populated for every shipped item -- variable labels carry the stems,
# value labels carry the six or seven anchors.
#
# Not shipped from these files, each for a reason:
#   - Study 1's `sq1`..`sq8`, eight standalone questions about the importance
#     of open science practices, each its own single-item measure, plus their
#     `_d` dichotomised copies.
#   - Study 1's `reas_*` and `reas_alt_*`: two randomised WORDINGS of the same
#     six reasons-for-trust items (which wording a respondent saw is in `bed`),
#     so the 12 columns are 6 items crossed with a wording manipulation and
#     need a design decision rather than a melt.
#   - Study 2's `txt_*` blocks: four study descriptions x (3 trust items +
#     quality + practical value + multiplism), a crossed vignette design with
#     its own `*_TRUST` composites and manipulation checks.
#   - Study 2's `les_*` (7 single emotion adjectives), the 10 `txt_*`/`studie_*`
#     feedback items about the questionnaire itself, and the manipulation
#     checks.
#   - Both files' `*_other` free-text columns and Study 2's `abitur`
#     (dichotomised `education`).
#
# PII: screened on both files. The only string columns are the two
# `trustf_other` / `trustf_vb_other` free-text boxes, whose job is to collect
# further trust factors; the count is asserted non-zero and no email, name,
# phone or date was found. Neither is shipped.

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW1 = os.environ.get("ROSMAN_S1", "Rosman_et_al_2022_Study_1_data.sav")
RAW2 = os.environ.get("ROSMAN_S2", "Rosman_et_al_2022_Study_2_data.sav")

TRUSTF = ["trustf_osp_01", "trustf_osp_02", "trustf_osp_03", "trustf_osp_04",
          "trustf_osp_05", "trustf_exp", "trustf_int", "trustf_ben",
          "trustf_publ", "trustf_comm", "trustf_press", "trustf_qrp1",
          "trustf_qrp2", "trustf_qrp3"]
TRUSTF_VB = ["trustf_vb_" + c[len("trustf_"):] for c in TRUSTF]
METI = (["meti_exp_%02d" % i for i in range(1, 7)]
        + ["meti_int_%02d" % i for i in range(1, 5)]
        + ["meti_ben_%02d" % i for i in range(1, 5)])
JUST = [f"just_{a}_{d}_{i:02d}" for d in ("med", "psy")
        for a in ("pj", "au", "ms") for i in range(1, 4)]
CONSP = ["consp_%02d" % i for i in range(1, 10)]
TRUST5 = ["trust_%02d" % i for i in range(1, 6)]

DEMOG = {"sex": "cov_sex", "age": "cov_age_range", "education": "cov_education"}
S2_ONLY_COV = {"exp_funding": "cov_exp_funding", "exp_OSP": "cov_exp_osp"}


def screen_for_pii(df, which):
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen ({which}): examined {len(txt)} of {len(df.columns)} "
          f"columns: {txt}")
    assert txt, f"PII screen ({which}) selected no columns -- selector is wrong"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
                     r"|\+?\d{9,}"
                     r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str)
            if pat.search(v)]
    assert not hits, f"PII screen ({which}) hit: {hits[:5]}"
    print(f"PII screen ({which}): clean")


def labelled(df, meta, src):
    labels = meta.variable_value_labels.get(src)
    return df[src].map(labels) if labels else df[src]


def covariates(df, meta, study):
    out = pd.DataFrame(index=df.index)
    out["cov_study"] = study
    for src, dst in DEMOG.items():
        out[dst] = labelled(df, meta, src)
    for src, dst in S2_ONLY_COV.items():
        out[dst] = labelled(df, meta, src) if src in df.columns else pd.NA
    out["id"] = study + "_" + df["lfdn"].astype(int).astype(str)
    return out


def melt_block(df, cov, cols, wave=None):
    """Long form for one item block, with a `wave` only when one is given."""
    keep = cov.copy()
    for c in cols:
        keep[c] = df[c]
    long = keep.melt(id_vars=list(cov.columns), value_vars=cols,
                     var_name="item", value_name="resp")
    if wave is not None:
        long["wave"] = wave
    return long


def finish(name, long, lo, hi, cov_cols, has_wave):
    before = long["resp"].notna().sum()
    long = long[long["resp"].notna() & (long["resp"] != 0)].copy()
    zeros = before - len(long)
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(lo, hi).all(), (name, sorted(long["resp"].unique()))
    assert long["id"].nunique() >= 100, (name, long["id"].nunique())
    assert long["item"].nunique() >= 3, (name, long["item"].nunique())
    # a covariate that is entirely missing for this table's respondents is
    # noise, not information: the two experimental conditions exist only in
    # Study 2, so a Study-1-only table carries neither
    keep_cov = [c for c in cov_cols if long[c].notna().any()]
    empty = [c for c in cov_cols if c not in keep_cov]
    if empty:
        print(f"  {name}: dropped all-missing covariate(s) {empty}")
    order = ["id", "item", "resp"] + (["wave"] if has_wave else []) + keep_cov
    long = long[order]

    # gate before writing -- the contract check requires the
    # validator to run in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1)) for i in long['item'].unique()})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:180]}")

    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()} (dropped {zeros} cells coded 0)")


def convert():
    d1, m1 = pyreadstat.read_sav(RAW1)
    d2, m2 = pyreadstat.read_sav(RAW2)
    screen_for_pii(d1, "study 1")
    screen_for_pii(d2, "study 2")

    for df, which in ((d1, "study 1"), (d2, "study 2")):
        assert df["lfdn"].nunique() == len(df), f"{which}: lfdn is not unique"

    # the three merges, each licensed by a check rather than an assumption
    for cols, nm in ((TRUSTF, "trustf"), (TRUSTF_VB, "trustf_vb")):
        for c in cols:
            assert c in d1.columns and c in d2.columns, (nm, c)
            a = m1.variable_value_labels.get(c)
            b = m2.variable_value_labels.get(c)
            assert a == b, f"{nm}/{c}: anchors differ between studies"
        print(f"{nm}: 14 columns, identical anchors in both studies -> merged")
    assert (m1.variable_value_labels.get("trust_01")
            == m2.variable_value_labels.get("trust_t1_01")), \
        "trust scale anchors differ between studies"
    assert (m1.variable_value_labels.get("meti_exp_01")
            != m2.variable_value_labels.get("meti_exp_01")), \
        "METI anchors now agree across studies -- re-check whether to merge"
    print("meti: anchors DIFFER (1-5 vs 1-7) -> two tables, not merged")

    c1 = covariates(d1, m1, "s1")
    c2 = covariates(d2, m2, "s2")
    cov_cols = [c for c in c1.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. trust in science, both studies, with a wave
    parts = [melt_block(d1, c1, TRUST5, wave=1)]
    for suffix, wave in (("t1", 1), ("t2", 2)):
        cols = [f"trust_{suffix}_{i:02d}" for i in range(1, 6)]
        part = melt_block(d2, c2, cols, wave=wave)
        # strip the occasion out of the item code: the same five items were
        # asked at both occasions, and `wave` is what distinguishes them
        part["item"] = part["item"].str.replace(f"_{suffix}_", "_", regex=False)
        parts.append(part)
    trust = pd.concat(parts, ignore_index=True)
    assert set(trust["item"]) == set(TRUST5), sorted(set(trust["item"]))
    finish("rosman_2022_trust_science", trust, 1, 6, cov_cols, True)

    # 2-3. the two trust-factor batteries, both studies, no wave
    for name, cols in (("rosman_2022_trust_factors_scientist", TRUSTF),
                       ("rosman_2022_trust_factors_general", TRUSTF_VB)):
        both = pd.concat([melt_block(d1, c1, cols), melt_block(d2, c2, cols)],
                         ignore_index=True)
        finish(name, both, 1, 7, cov_cols, False)

    # 4-5. METI, one table per study because the scale differs
    finish("rosman_2022_meti_s1", melt_block(d1, c1, METI), 1, 5, cov_cols, False)
    finish("rosman_2022_meti_s2", melt_block(d2, c2, METI), 1, 7, cov_cols, False)

    # 6-7. study 2 only
    finish("rosman_2022_justification_beliefs", melt_block(d2, c2, JUST),
           1, 6, cov_cols, False)
    finish("rosman_2022_conspiracy", melt_block(d2, c2, CONSP),
           1, 6, cov_cols, False)

    # balance the books, per file
    shipped = {
        "study 1": set(TRUST5) | set(TRUSTF) | set(TRUSTF_VB) | set(METI),
        "study 2": (set(f"trust_{s}_{i:02d}" for s in ("t1", "t2")
                        for i in range(1, 6))
                    | set(TRUSTF) | set(TRUSTF_VB) | set(METI) | set(JUST)
                    | set(CONSP)),
    }
    for (df, which) in ((d1, "study 1"), (d2, "study 2")):
        used = shipped[which] | set(DEMOG) | set(S2_ONLY_COV) | {"lfdn"}
        left = [c for c in df.columns if c not in used]
        print(f"{which}: shipped {len(shipped[which])} item columns, "
              f"left {len(left)} unshipped (see the header for why): "
              f"{sorted(left)}")


if __name__ == "__main__":
    convert()
