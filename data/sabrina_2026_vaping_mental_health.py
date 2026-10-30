#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0343502
# DOI: 10.1371/journal.pone.0343502
# Paper: Sabrina, F., Hawlader, M. D. H., Alam, M. N., Faruq, M. F. I.,
#   Bhuiyan, F. P., & Banik, B. (2026). Vaping and mental health: A
#   cross-sectional study among university students in Bangladesh.
#   PLOS ONE 21(3).
# Data: journal.pone.0343502.s001 (S1 File, .xlsx), one sheet
#   'Form Responses 1'. 1,615 students at 7 Bangladeshi universities.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# THREE output tables, one per instrument. The file is a Google Forms export
# and reports 16,383 columns, of which only 55 hold any data at all -- the rest
# are the spreadsheet's empty trailing columns. The script selects by content,
# not by position, so that padding is irrelevant.
#
# The three batteries are three DIFFERENT published instruments on two
# different scales, identifiable from the stems, which this export keeps
# verbatim as its column headers:
#   Q29-Q38  Kessler K10 psychological distress, 1-5
#            ("In the last 4 weeks- About how often did you feel tired out for
#            no good reason?" ... "worthless?") -- the K10's ten items in the
#            published order.
#   Q39-Q48  CES-D-10 (Andresen et al. 1994 short form of Radloff's CES-D),
#            0-3. Includes the two positively-keyed items ("I felt hopeful
#            about the future", "I was happy").
#   Q49-Q55  GAD-7, 0-3 ("Feeling nervous, anxious, or on the edge" ...
#            "Feeling afraid, as if something awful might happen").
# They are not merged: two scales (1-5 and 0-3) and three instruments.
#
# WHETHER THE CES-D-10 REVERSE ITEMS WERE RECODED IS UNKNOWN, and is stated in
# that table's description rather than guessed at. Items 43 and 46 are the
# instrument's two positively-worded items; nothing in the deposit or the
# article says whether the deposited values are as-collected or already
# direction-corrected, and their marginal distributions do not settle it. They
# ship as deposited. This matters for anyone fitting a model where polarity is
# assumed, so it is said out loud instead of being left for them to discover.
#
# `id` is the deposit's own '1. SL' column -- a serial 1..1615, verified unique
# per row, with no embedded information (unlike the Kendall 2018 serial in this
# same batch, which encoded the respondent's city).
#
# SKIP-GATED QUESTIONS ARE NOT IN ANY TABLE. Items 16-19, 22, 23 and 25 were
# asked only of the 248 vapers (or the 144 nicotine users), so their
# non-response is design, not missingness. None of them is part of the three
# instruments and none is shipped. The three batteries were asked of all 1,615
# and have zero missing cells -- asserted, so a later file with a gated
# battery cannot pass silently.
#
# Dropped, each for a reason:
#   items 9, 17, 18, 24, 25  multi-select questions collapsed into ONE numeric
#                            column ("You can select multiple", "multiple
#                            answers"). A single code cannot represent a set,
#                            so these are uninterpretable as either items or
#                            covariates and are not shipped at all.
#   items 13, 14, 15, 16, 19, 20, 21, 22, 23
#                            single nominal/behavioural smoking and vaping
#                            questions -- not a scale, and several are
#                            skip-gated. Kept out rather than shipped as a
#                            pseudo-battery.
#   item 6 (department)      7 departments; a nominal study covariate with no
#                            bearing on the instruments, dropped to keep the
#                            covariate set to what the paper analyses
#
# Covariates kept: gender, exact age (18-26 here, so a single year is not
# identifying in a 1,615-student sample across 7 universities),
# university (an institution code, not geography), academic year,
# socio-economic status, marital status, residence type (item 10 is
# hall/home/mess/other, NOT a place name -- checked, so the geographic ruling
# does not reach it), financial contribution to family, perceived social life,
# self-reported diagnosed mental health problem, alcohol use, recreational drug
# use, and e-cigarette user status.
#
# Item text: SHIPPED for the GAD-7 ONLY. Held for the K10 and the CES-D-10,
# and the three reasons are different in kind.
#   * GAD-7 -- SHIPPED. instrument_rights_register.csv already carries `ship`
#     for the PHQ/GAD screener family ("no permission is required to
#     reproduce, translate, display or distribute"), verified at source three
#     times. The stems come verbatim from this export's own column headers.
#     The four option labels are NOT in the deposit; they are the GAD-7's own
#     published anchors (0 Not at all / 1 Several days / 2 More than half the
#     days / 3 Nearly every day), which is defensible here and nowhere else in
#     this deposit: the GAD-7 has exactly one published anchor set, the
#     observed resp domain is exactly 0-3 with all four levels present, and
#     the identical treatment is already in the corpus
#     (itemtext/fixes/1816_phq_doubling/phq_insomnia_wang2025__items.csv).
#   * CES-D-10 -- HELD, and the obstacle is the OPTIONS, not the stems or the
#     rights. The register carries `ship_with_note` for Radloff's 20-item
#     CES-D on a public-domain/NIMH basis and the short form's items are a
#     subset of Radloff's, so the wording is distributable and the ten stems
#     are in hand verbatim. But the itemtext schema wants option_text per resp
#     code, the deposit states no anchors, and the CES-D-10 circulates with
#     MORE THAN ONE published 0-3 anchor set (the day-range variants differ).
#     Picking one would be inventing the respondent's scale, so it is held
#     rather than guessed. A register row for the short form is written
#     (verdict ship_with_note, carrying the 20-item row's note) so the rights
#     question does not have to be re-derived; only the anchors block it.
#   * K10 -- HELD on rights. NO row existed and no grant was located on
#     2026-10-30 (searched; nothing stating reuse terms). Silence on a named
#     third-party instrument is a hold, per the PANAS precedent. A register
#     row is written, verdict hold.
#
# PII: screened over all 55 populated columns. Every one is numeric -- the
# export carries no free-text, name, email, date or timestamp column at all,
# which is unusual for a Google Form and worth stating.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("SABRINA_RAW", "journal.pone.0343502_S1_File.xlsx")

N_ROWS = 1615
ID_COL = "1. SL"

ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response",
                 "option_text", "resp"]

GAD7_NAME = "Generalized Anxiety Disorder 7-item scale (GAD-7)"
GAD7_INSTRUCTIONS = ("Over the last 2 weeks, how often have you been bothered "
                     "by the following problems?")
# the GAD-7's own published anchors; the deposit states none, and this
# instrument has exactly one published set (see the header)
GAD7_OPTIONS = {0: "Not at all", 1: "Several days",
                2: "More than half the days", 3: "Nearly every day"}

# table -> (first item number, last item number, lo, hi, ship item text)
BATTERIES = {
    "sabrina_2026_k10": (29, 38, 1, 5, False),
    "sabrina_2026_cesd10": (39, 48, 0, 3, False),
    "sabrina_2026_gad7": (49, 55, 0, 3, True),
}

COVS = {
    2: "cov_gender", 3: "cov_age", 4: "cov_university", 5: "cov_academic_year",
    7: "cov_socioeconomic_status", 8: "cov_marital_status",
    10: "cov_residence_type", 11: "cov_financial_contribution",
    12: "cov_social_life_perception", 15: "cov_ecig_user",
    26: "cov_diagnosed_mental_health", 27: "cov_alcohol_use",
    28: "cov_recreational_drug_use",
}


def qnum(col):
    m = re.match(r"\s*(\d+)\s*\.", str(col))
    return int(m.group(1)) if m else None


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} populated columns are "
          f"text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    print("  every populated column is numeric: this Google Forms export "
          "carries no free text, name, email, timestamp or date column at all")


def convert():
    raw = pd.read_excel(RAW, sheet_name="Form Responses 1")
    # 16,383 columns, 55 with data: select by content, never by position
    df = raw[[c for c in raw.columns if raw[c].notna().any()]].copy()
    print(f"{len(df.columns)} populated columns of {len(raw.columns)} in the "
          f"sheet (the rest are the export's empty trailing columns)")
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    by_num = {}
    for c in df.columns:
        n = qnum(c)
        if n is not None:
            by_num.setdefault(n, []).append(c)
    dupes = {n: cs for n, cs in by_num.items() if len(cs) > 1}
    assert not dupes, f"question number appears twice: {dupes}"

    assert df[ID_COL].nunique() == len(df), f"{ID_COL} is not unique"
    df = df.rename(columns={ID_COL: "id"})
    for n, name in COVS.items():
        assert n in by_num, f"covariate question {n} not found"
        df = df.rename(columns={by_num[n][0]: name})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    total = 0
    for name, (first, last, lo, hi, ship_text) in BATTERIES.items():
        nums = list(range(first, last + 1))
        cols = [by_num[n][0] for n in nums]
        stems = {f"Q{n}": str(by_num[n][0]) for n in nums}

        # asked of every respondent: these batteries are not skip-gated
        assert int(df[cols].isna().sum().sum()) == 0, (name, "null cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(lo, hi).all(), \
            (name, sorted(vals.unique()))
        assert set(vals.unique()) == set(range(lo, hi + 1)), \
            (name, "a documented level never appears", sorted(vals.unique()))

        ren = {by_num[n][0]: f"Q{n}" for n in nums}
        long = df.rename(columns=ren).melt(
            id_vars=["id"] + cov_cols, value_vars=list(ren.values()),
            var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == len(nums)
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in ren.values()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

        if ship_text:
            # Full itemtext schema: one row per item x response option. The
            # stem is this export's own column header with the leading question
            # number stripped; the options are the GAD-7's published anchors
            # (see the header for why that is defensible for this instrument
            # and not for the other two).
            rows = []
            for n in nums:
                stem = re.sub(r"^\s*\d+\s*\.\s*", "", str(by_num[n][0])).strip()
                stem = re.sub(r"\s+", " ", stem)
                for code, opt in GAD7_OPTIONS.items():
                    rows.append({
                        "table": name, "section_id": f"{name}_1", "item": f"Q{n}",
                        "instrument": GAD7_NAME, "instructions": GAD7_INSTRUCTIONS,
                        "section_prompt": "NA", "item_text": stem,
                        "correct_response": "NA", "option_text": opt,
                        "resp": code})
            it = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
            assert it["item_text"].str.len().gt(8).all()
            assert sorted(it["resp"].unique()) == [lo + k for k in range(hi - lo + 1)]
            assert len(it) == len(nums) * (hi - lo + 1), len(it)
            # the join key must be shared with the response table
            assert set(it["item"]) == set(long["item"]), "item keys diverge"
            it.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"),
                      index=False)
            print(f"  {name}__items: rows={len(it)} items={it['item'].nunique()} "
                  f"x {hi - lo + 1} options")

    assert total == 27 * N_ROWS, total
    print(f"3 tables, {total} responses (27 items x {N_ROWS} respondents), "
          f"1 item text table (K10 and CES-D-10 held)")


if __name__ == "__main__":
    convert()
