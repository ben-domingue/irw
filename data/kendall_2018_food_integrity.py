#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0195817
# DOI: 10.1371/journal.pone.0195817
# Paper: Kendall, H., Naughton, P., Kuznesof, S., Raley, M., Dean, M.,
#   Clark, B., Stolz, H., Home, R., Chan, M. Y., Zhong, Q., Brereton, P., &
#   Frewer, L. J. (2018). Food fraud and the perceived integrity of European
#   food imports into China. PLOS ONE 13(5): e0195817.
# Data: journal.pone.0195817.s001 (S1 Dataset, .xlsx). Two sheets --
#   'Data View' (850 rows x 110 columns) and 'Variable View' (109 rows), an
#   SPSS-style export whose second sheet carries the verbatim question wording
#   for every variable.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 850 urban Chinese consumers, face-to-face interviews.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# NINE output tables. The questionnaire is a single bespoke instrument, but it
# is not a single SCALE: it carries eight distinct target-crossed batteries on
# one 5-point agree/disagree scale plus one three-statement battery on a 1-10
# scale. Each battery has its own stem and its own construct, so each is its
# own table -- the same treatment the rosman_2022_* and lee_whiting_2025_*
# deposits got, and for the same reason. The split is not cosmetic: merging
# Q7_2 into any of the others would put a 1-10 scale on the same `resp` as a
# 1-5 one.
#
# Q3_3 AND Q3_4 ARE NOT A MERGE CASE, which is worth stating because they look
# like one: both ask about the SAME list of eight organisations and both run
# 1-5. But the stems differ in construct, not in wording --
#   3.3 "... can be trusted to PROTECT THE CONSUMER FROM adulterated and
#        unsafe food and drink"
#   3.4 "... can be trusted to PROVIDE CONSUMERS WITH ACCURATE INFORMATION
#        about the authenticity of food and drink"
# -- protection versus disclosure. This is the inverse of the
# lee_whiting_2025_trust_actors merge, where ONE stem was asked about many
# actors and the actors became the items. Here two stems are asked about one
# fixed actor list, so the actors are the items in each of two tables. The
# script asserts the two stems still differ; if a future read finds them equal,
# that fires rather than the merge question being silently settled.
#
# NO MISSING DATA AND NO SENTINELS, verified rather than assumed: all nine
# batteries have zero null cells and every observed value falls inside its
# documented range (1-5, or 1-10 for Q7_2). So unlike three of the five
# deposits in the 2026-10-29f batch there is no undeclared no-answer code to
# strip here -- asserted below so a later file with one cannot pass silently.
#
# S1 (CITY OF RESIDENCE) IS DROPPED, not shipped as a covariate. It is
# sub-national administrative geography, which the 2026-10-20 geographic ruling
# and the 2026-10-29 cov_state ruling exclude -- and a city is finer-grained
# than the province that ruling was written about, so it is excluded a
# fortiori. Three cities over 850 respondents would also be a strong
# re-identification handle in combination with the retained age, gender and
# income bands.
#
# Also dropped, each for a reason:
#   QrNo1                     the questionnaire serial -- becomes id. Its own
#                             label documents it as "One City Number+One Round
#                             Number+Three Swift Number", i.e. it ENCODES the
#                             city that is being dropped above. So it is NOT
#                             used as id; the row index is used instead, and
#                             the serial is discarded entirely.
#   S7_1_*, S7_2_*, S8_*      multi-select "what have you bought / intend to
#                             buy" pick lists and interviewer-recorded
#                             respondent-type flags -- nominal, and the S7/S8
#                             columns are picks, not items
#   AGE                       exact age in years; the S5 age band is kept
#                             instead (a single year plus city plus income is a
#                             re-identification risk, and the band is what the
#                             paper analyses)
#
# Item text: AVAILABLE and NOT YET SHIPPED. Every one of the 77 item columns
# has its verbatim stem and target in the 'Variable View' sheet, and the
# instrument is the authors' own -- a bespoke questionnaire developed for this
# EU-China project, not a third-party scale -- so it arrives under the
# article's CC BY 4.0 and is shippable. Two things make it a job rather than a
# free extraction, and it is queued in TODO.md instead of being rushed: the
# labels are mojibaked (GBK/CP1252 round-trip damage: the curly quotes in
# "by 'adulterated food and drink'" arrive as the bytes for GBK's quote
# characters, so a naive read ships corrupted text), and a crossed battery
# needs the stem split from the target so that `item_text` is the target and
# the stem becomes the section text. A provenance row recording AVAILABLE is
# written with this batch.
#
# PII: screened over all 110 columns. No names, emails, phone numbers or free
# text. The two identifiers that did need handling are handled above and not
# shipped: the city column and the city-encoding questionnaire serial.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KENDALL_RAW", "journal.pone.0195817_S1_Dataset.xlsx")

N_ROWS = 850

# group prefix -> (table name, lo, hi, expected item count)
BATTERIES = {
    "Q1_1": ("kendall_2018_food_worry", 1, 5, 9),
    "Q3_3": ("kendall_2018_trust_protect", 1, 5, 8),
    "Q3_4": ("kendall_2018_trust_information", 1, 5, 8),
    "Q4_1": ("kendall_2018_adulteration_risks", 1, 5, 12),
    "Q4_2": ("kendall_2018_authenticity_benefits", 1, 5, 14),
    "Q5_1": ("kendall_2018_quality_cues", 1, 5, 11),
    "Q6_1": ("kendall_2018_origin_importance", 1, 5, 9),
    "Q7_1": ("kendall_2018_purchase_attitudes", 1, 5, 3),
    "Q7_2": ("kendall_2018_purchase_intention", 1, 10, 3),
}

COVS = {"S4": "cov_gender", "S5": "cov_age_band", "S6": "cov_income_band",
        "Q9_3": "cov_education", "Q9_4": "cov_parent_education",
        "Q9_5": "cov_grocery_spend_band"}

DROP_EXACT = {
    "QrNo1": "questionnaire serial -- ENCODES the dropped city; discarded",
    "S1": "city of residence -- sub-national geography (see header)",
    "AGE": "exact age in years -- the S5 band is kept instead",
}
DROP_PREFIX = ("S7_", "S8_")


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    pat = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(pat, regex=True, case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("  clean. The two real identifiers in this file -- the city column "
          "and the city-encoding questionnaire serial -- are dropped, not "
          "shipped (see header)")


def assert_stems_still_differ(labels):
    """Q3_3 and Q3_4 share their eight targets and their 1-5 scale. They are
    two tables because the stems ask different things. Pin that, so the merge
    question is reopened by a failure rather than settled by silence."""
    a, b = str(labels["Q3_3_T1"]), str(labels["Q3_4_T1"])
    assert a != b, "Q3_3 and Q3_4 stems are identical -- reopen the merge call"
    assert "protect the consumer from" in a.lower(), a[:120]
    assert "accurate information" in b.lower(), b[:120]
    print("Q3_3 / Q3_4 stems confirmed distinct (protection vs disclosure), "
          "so they stay two tables over the same eight organisations")


def convert():
    xl = pd.ExcelFile(RAW)
    df = xl.parse("Data View")
    vv = xl.parse("Variable View")
    labels = dict(zip(vv.iloc[:, 0].astype(str), vv.iloc[:, 1]))
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    assert_stems_still_differ(labels)

    groups = {}
    for c in df.columns:
        m = re.match(r"^(Q\d+_\d+)_", str(c))
        if m and m.group(1) in BATTERIES:
            groups.setdefault(m.group(1), []).append(c)

    accounted = set(COVS) | set(DROP_EXACT)
    for cols in groups.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns
                if c not in accounted and not str(c).startswith(DROP_PREFIX)]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {sum(1 for c in df.columns if str(c).startswith(DROP_PREFIX))} "
          f"S7_/S8_ multi-select and respondent-type columns, plus "
          f"{len(DROP_EXACT)} named columns")

    # the serial encodes the dropped city, so id is the row index instead
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    written = set()
    for prefix, (name, lo, hi, n_items) in BATTERIES.items():
        cols = sorted(groups[prefix], key=lambda c: str(c))
        assert len(cols) == n_items, (prefix, len(cols), n_items)
        assert name not in written and len(name) <= 40, name
        written.add(name)

        # no sentinels and no missing cells -- verified, not assumed
        assert int(df[cols].isna().sum().sum()) == 0, (name, "null cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "non-numeric cell")
        assert vals.between(lo, hi).all(), (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS, (name, long["id"].nunique())
        assert long["item"].nunique() == n_items
        assert not long.duplicated(["id", "item"]).any()

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:165]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

    assert total == 77 * N_ROWS, total
    print(f"{len(BATTERIES)} tables, {total} responses "
          f"(77 items x {N_ROWS} respondents, no missing cells)")


if __name__ == "__main__":
    convert()
