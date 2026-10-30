#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341565
# DOI: 10.1371/journal.pone.0341565
# Paper: Oppong, P. B., Ofori, D., Wunu, P., Nyamah, E. Y., Nyamah, E. Y.,
#   Boateng, J. K. G. A., & Agyapong, G. K. Q. (2026). A multidimensional
#   procurement literacy instrument: Development and validation among
#   undergraduate procurement students in Ghana. PLOS ONE 21(2).
# Data: figshare 10.6084/m9.figshare.30931064 -- "PMLI plosone data.csv",
#   554 rows x 75 columns. Downloaded from
#   https://ndownloader.figshare.com/files/60544547
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on figshare, so the article's CC BY cannot grant it.
# api.figshare.com/v2/articles/30931064 reports CC BY 4.0. Third deposit in
# this batch needing that separate check (see also
# hocine_2016_psychosocial_stressors and zhang_2025_fear_of_falling).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table. 554 undergraduate procurement students in Ghana, across
# three institutions.
#
# ONE table, not eight. The Procurement Literacy Instrument (PMLI) is a single
# instrument whose 51 items sit in eight dimensions -- LEG 6 (legal/regulatory),
# PLAN 7 (planning), SUP 7 (supplier management), TRAN 6 (transparency),
# ETH 7 (ethics), DIG 6 (digital), FAM 6 (familiarity), BEH 6 (behaviour) --
# all administered on one 5-point scale to one sample. That is a subscale
# structure, so it ships as one table with the dimension recoverable from the
# item code prefix, per the collapse-same-instrument rule. Same treatment as
# padchasuwan_2026_sexual_health_literacy and
# hocine_2016_psychosocial_stressors in this batch.
#
# A NAMING HAZARD IN THIS FILE, worth stating because it is the kind of thing
# that silently halves a table: seven of the eight dimension prefixes ALSO
# exist as standalone composite columns with exactly the same name --
# `PLAN`, `SUP`, `LEG`, `DIG`, `FAM`, `BEH` and `PIE` are subscale/overall
# means (fractional, e.g. PIE runs 1.0-4.8), sitting in the same header row as
# the items `PLAN1`..`PLAN7`. A prefix match would swallow them. The item
# selector therefore requires a trailing digit, and the script asserts the
# exact per-dimension counts so that a composite joining the item set, or an
# item leaving it, fails loudly. (Note `TRAN` and `ETH` have no composite
# column -- the deposit is not even consistent about which it includes, which
# is another reason not to infer them.)
#
# MISSINGNESS IS GENUINELY ITEM-LEVEL HERE, unlike the whole-scale GDS-15
# nonresponse in zhang_2025_fear_of_falling, and it is NOT treated as
# droppable-by-respondent: 442 of 554 respondents answered all 51 items, and
# the remaining 112 skipped between 1 and 44 of them. Every respondent
# answered at least one item (asserted), so all 554 appear in the table, and
# only the skipped cells are absent. Dropping whole respondents would have
# discarded ~20% of the sample for leaving one box blank.
#
# Dropped, each for a reason:
#   PIE, PLAN, SUP, LEG, DIG, FAM, BEH   composite means (see above)
#   Gender1, EthicsPeers1, EconomicStatus2, EthicsDifficulty1, CorruptionPP1
#                                        recoded duplicate copies of the
#                                        demographic columns that are kept
#   ID                                   record number -- becomes id
#
# Covariates kept: gender, level of study, GPA band, economic status, ethics
# of peers, ethics difficulty, perceived corruption in public procurement,
# mode of study, moral/ethics outlook, work experience, and institution. Nine
# of these arrive as TEXT category labels rather than codes ("Female",
# "Moderate income", "Mixed (some ethical, some unethical)"), which is why the
# PII screen below selects and checks them instead of asserting the file is
# all-numeric: each is a closed vocabulary of at most 8 values, with no free
# text, and the labels ship verbatim rather than being recoded into numbers
# that would need a key nobody has.
#
# `Institution:` is a code 1-3 for three Ghanaian universities -- an
# institution identifier, not geography, so the 2026-10-20 geographic ruling
# does not reach it; it is kept with its trailing colon stripped.
#
# ONE COVARIATE IS INTERNALLY INCONSISTENT and is shipped with that said
# rather than quietly cleaned: `GPA` holds eight distinct band labels drawn
# from what are plainly TWO different option sets -- "3.0 - 3.9" and
# "2.0 - 2.4" alongside "3.0 - 3.5", "3.6-4.0" and "4.0-5.0". The bands
# overlap, and a 4.0-5.0 band cannot belong to the same scheme as a 3.6-4.0
# one, so this column is not usable as an ordered variable. It ships as the
# verbatim label because the label is what was actually recorded, and the
# table description says it mixes two schemes. Dropping it would hide a fact
# about the instrument's administration; silently collapsing the bands would
# invent one.
#
# Item text: NOT SHIPPED, and as with padchasuwan_2026 in this batch the
# obstacle is the MAPPING, not rights. This is a scale-development paper, the
# instrument is the authors' own, and it arrives under CC BY 4.0 -- so the
# wording is distributable and a register row records that. But the deposit
# carries no wording (columns are bare codes LEG1..BEH6), the stems live in
# the article's own validation tables, and those tables present RETAINED items
# against their loadings rather than a key from printed stem to deposited
# column code. Without that key a code-to-stem mapping cannot be established
# from this source, and a mis-ordering inside a dimension is exactly what an
# itemtext table must not ship. Queued in TODO.md with that diagnosis.
#
# PII: screened over all 75 columns. Every one is numeric; no names, emails,
# dates, free text, or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("OPPONG_RAW", "PMLI plosone data.csv")

TABLE = "oppong_2026_procurement_literacy"
N_ROWS = 554
LO, HI = 1, 5

DIMENSIONS = {"LEG": 6, "PLAN": 7, "SUP": 7, "TRAN": 6,
              "ETH": 7, "DIG": 6, "FAM": 6, "BEH": 6}

COVS = {"Gender": "cov_gender", "LoS": "cov_level_of_study",
        "GPA": "cov_gpa_band", "EconomicStatus": "cov_economic_status",
        "EthicsPeers_": "cov_ethics_of_peers",
        "EthicsDifficulty": "cov_ethics_difficulty",
        "Corruptioninpp": "cov_perceived_corruption",
        "Mos": "cov_mode_of_study",
        "Moralethicsoutlook_": "cov_moral_ethics_outlook",
        "Workexperience": "cov_work_experience",
        "Institution:": "cov_institution"}

# composites that share a name with a dimension prefix -- the whole hazard
COMPOSITES = ["PIE", "PLAN", "SUP", "LEG", "DIG", "FAM", "BEH"]
RECODES = ["Gender1", "EthicsPeers1", "EconomicStatus2",
           "EthicsDifficulty1", "CorruptionPP1"]


PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    """Nine covariates are text category labels, so this screens them rather
    than asserting the file is numeric. A closed vocabulary is the thing being
    checked: a free-text column would show many distinct values, and that is
    what the cardinality assert is for."""
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: examined {len(txt)} text column(s) of "
          f"{len(df.columns)}: {txt}")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    wide = {c: df[c].nunique() for c in txt if df[c].nunique() > 10}
    assert not wide, f"not a closed vocabulary -- possible free text: {wide}"
    print("  all text columns are closed category vocabularies (<=8 values "
          "each), no free text; no name, email, date or geographic column")


def select_items(df):
    """Require a trailing digit. `PLAN` (a composite mean) and `PLAN1`..`PLAN7`
    (items) are both columns here, so a bare prefix match would pull the
    composite into the item set."""
    items = {}
    for c in df.columns:
        m = re.match(r"^(LEG|PLAN|SUP|TRAN|ETH|DIG|FAM|BEH)(\d+)$", str(c))
        if m:
            items.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in items.items()}
    assert got == DIMENSIONS, (
        f"dimension counts are {got}, expected {DIMENSIONS} -- a composite may "
        f"have joined the item set, or an item left it")
    for comp in COMPOSITES:
        assert comp in df.columns, f"expected composite column {comp} is gone"
        frac = pd.to_numeric(df[comp], errors="coerce").dropna() % 1 != 0
        assert frac.any(), (
            f"{comp} holds no fractional value -- it may not be a mean, "
            f"recheck before dropping it")
    print(f"51 items in 8 dimensions: " +
          ", ".join(f"{k} {v}" for k, v in DIMENSIONS.items()))
    print(f"  dropped {len(COMPOSITES)} composite columns that share a name "
          f"with a dimension prefix ({', '.join(COMPOSITES)}), each confirmed "
          f"fractional, plus {len(RECODES)} recoded demographic duplicates")
    return [c for cols in items.values() for c in cols]


def convert():
    df = pd.read_csv(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    items = select_items(df)
    assert len(items) == 51, len(items)

    accounted = set(items) | set(COVS) | set(COMPOSITES) | set(RECODES) | {"ID"}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    vals = pd.to_numeric(df[items].stack(), errors="coerce").dropna()
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    assert (vals % 1 == 0).all(), "a fractional value reached the item set"

    # item-level nonresponse: keep every respondent who answered anything
    assert df[items].notna().any(axis=1).all(), \
        "a respondent answered no items at all"
    complete = int(df[items].notna().all(axis=1).sum())
    skipped = int(df[items].isna().sum().sum())
    print(f"item-level nonresponse: {complete} of {N_ROWS} respondents "
          f"answered all 51 items; {N_ROWS - complete} skipped between 1 and "
          f"{int(df[items].isna().sum(axis=1).max())} items. {skipped} cells "
          f"dropped, no respondent dropped")

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_ROWS, long["id"].nunique()
    assert long["item"].nunique() == 51
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 51 * N_ROWS - skipped, len(long)
    assert len(TABLE) <= 40, TABLE

    long = long[["id", "item", "resp"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:175]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
