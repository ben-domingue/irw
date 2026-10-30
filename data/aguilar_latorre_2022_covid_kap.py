#!/usr/bin/env python3
# Source: https://zenodo.org/records/14748660
# DOI: 10.5281/zenodo.14748660
# Paper: Aguilar-Latorre, A., Asensio-Martinez, A., Garcia-Sanz, O., &
#   Olivan-Blazquez, B. (2022). Knowledge, Attitudes, Risk Perceptions, and
#   Practices of Spanish Adolescents Toward the COVID-19 Pandemic: Validation
#   and Results of the Spanish Version of the Questionnaire. Frontiers in
#   Psychology, 12, 804531. https://doi.org/10.3389/fpsyg.2021.804531
# Data: "dateset validation.csv" (semicolon-delimited, UTF-8 BOM, 354 Spanish
#   adolescents aged 12-18), plus "meaning - dateset validation.csv", the
#   deposit's own variable-number -> question-wording key.
# License: CC BY 4.0 (stated on the Zenodo record, license id cc-by-4.0)
#
# Why this was a lead and not a shipped table: triage read the file as having
# only 4 item columns, because every item column holds a TEXT Likert label
# ("Parcialmente correcto", "Bastante", "A menudo") rather than a code, so the
# numeric-column heuristic found almost nothing. Reading the labels back to
# their documented order is the whole of the work here.
#
# Three output tables, one per section of the questionnaire, which is also one
# per response scale:
#   K1-K17  knowledge          3 points, 0 = completely incorrect / don't know,
#                              1 = partially correct, 2 = completely correct
#   A1-A10  attitudes and risk perception  5 points, Nada .. Mucho
#   P1-P13  practices          5 points, Nunca .. Siempre
# Item codes are the AUTHORS' own: they are the data file's column headers and
# the same codes label each question in the deposit's meaning file, so code and
# wording are tied by name, not by position.
#
# The knowledge section is deliberately mixed-width and that is documented, not
# a defect: the paper states eight of the knowledge questions offered three
# options and nine offered two (correct vs. incorrect/not knowing). The two
# option items are mapped to 0 and 2, the same values those words take on the
# three-option items, so "2 means completely correct" holds for every item in
# the table. Some items therefore have a narrower observed range than others.
#
# Not shipped: P14-P18. P14-P17 are four unrelated yes/no screening questions
# (recent contact with a symptomatic person, recent travel, increased water
# intake, fewer unnecessary trips) rather than a scale, and P18 is a single
# nominal question about what the respondent would do first on noticing a
# symptom. Also not shipped as covariates: the province of residence (a
# state-level administrative geography -- the 2026-10-20 geographic ruling and
# the 2026-10-29 cov_state ruling that followed it), the free-text country of
# birth (13 values over 354 adolescents, several of them unique; the
# nationality item carries the same information categorically), and the two
# multi-select string columns (who the respondent lives with, which household
# members work), which are not single responses.
#
# Item text: NOT shipped, and the wording is not the obstacle -- it is all in
# this deposit's own meaning file, in the administered Spanish. The rights are.
# The instrument is the authors' Spanish translation of Honarvar, B., et al.
# (2020), "Knowledge, attitudes, risk perceptions, and practices of adults
# toward COVID-19: a population and field-based study from Iran",
# International Journal of Public Health 65, 731-739 (Springer). Under the
# 2026-09-08 translation ruling the thing copied is the Spanish adaptation, and
# a stand-in may ship only from the ORIGINAL's own terms; the Honarvar article
# is a Springer subscription article with no established grant, so the original
# cannot stand in either. Register rows are written for both the original and
# the Spanish translation. The deposit's CC BY covers the depositors' material,
# not the instrument they translated.
#
# PII: screened with an is_string_dtype selector (not dtype == object) over all
# 44 string columns of the raw file; the count is asserted non-zero below. No
# email address, name, phone number, date of birth or postal code. The one
# geographic column is the province, dropped above.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("AGUILAR_RAW", "dateset validation.csv")

# meaning file items 25-41; the paper's three-option wording, plus the
# two-option items' "correct" / "incorrect or not knowing" at the same anchors
KNOWLEDGE = {
    "Completamente incorrecto/NS": 0,
    "Completamente incorrecto": 0,
    "Parcialmente correcto": 1,
    "Completamente correcto": 2,
}
# meaning file items 42-51
ATTITUDE = {"Nada": 1, "Poco": 2, "Algo": 3, "Bastante": 4, "Mucho": 5}
# meaning file items 52-64
PRACTICE = {"Nunca": 1, "Pocas veces": 2, "A veces": 3, "A menudo": 4,
            "Siempre": 5}

TABLES = {
    "aguilar_latorre_2022_covid_knowledge":
        ([f"K{i}" for i in range(1, 18)], KNOWLEDGE, (0, 2)),
    "aguilar_latorre_2022_covid_risk":
        ([f"A{i}" for i in range(1, 11)], ATTITUDE, (1, 5)),
    "aguilar_latorre_2022_covid_practices":
        ([f"P{i}" for i in range(1, 14)], PRACTICE, (1, 5)),
}

# The source's demographic headers are the full question text with spaces
# stripped and truncated at 63 characters -- which makes @18 and @20
# byte-identical, so pandas de-duplicates them to "...hasm" and "...hasm.1".
# Address them by their own "@NN." question tag, which is unique and stable,
# never by the truncated text.
#
# question tag -> covariate name. Values are kept as the source's own Spanish
# labels; these are categories, not scales.
DEMOG = {
    "@1.": "cov_sex",
    "@2.": "cov_age",
    "@4.": "cov_spanish_nationality",
    "@5.": "cov_marital_status",
    "@6.": "cov_residence_type",
    "@7.": "cov_household_size",
    "@8.": "cov_has_siblings",
    "@10.": "cov_bedrooms",
    "@11.": "cov_in_education",
    "@12.": "cov_left_school_without_eso",
    "@13.": "cov_education_completed",
    "@14.": "cov_repeated_grade",
    "@16.": "cov_work_contract",
    "@18.": "cov_relative1_education",
    "@21.": "cov_household_receives_aid",
}
# the two untagged follow-ups, addressed by their text (both are unique)
SIBLING_COUNT = "SihasrespondidoSÍalapreguntaanteriorindicaaquícuántoshermanos"
PROVINCE = "¿AquéprovinciaperteneceSelecciónaladelalista"

# dropped deliberately, each for a reason given in the header comment
DROP_GEO_TAGS = ["@3."]                   # free-text country of birth
DROP_MULTISELECT_TAGS = ["@9.", "@15."]   # lives with / household members working
# the two relative-type pickers, and the second relative's education, whose
# header truncates to the same string as @18
DROP_OTHER_TAGS = ["@17.", "@19.", "@20."]
DROP_ITEMS = [f"P{i}" for i in range(14, 19)]

BLANKS = {" ", "", "NS/NC"}


def screen_for_pii(df):
    """Print the denominator, then look for identifiers in every text column.

    Selected with is_string_dtype rather than dtype == object: on frames whose
    text columns arrive as a pandas StringDtype the latter selects nothing and
    a screen that examines no columns reports clean.
    """
    import re
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(txt)} of {len(df.columns)} columns")
    assert txt, "PII screen selected no columns -- the selector is wrong"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"      # email
                     r"|\b\d{5}\b"                        # ES postal code
                     r"|\+?\d{9,}"                        # phone
                     r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")  # date of birth
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str)
            if pat.search(v)]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("PII screen: clean")


def by_tag(columns, tag):
    """The one column whose header carries this "@NN." question tag."""
    hits = [c for c in columns if c.startswith(tag)]
    assert len(hits) == 1, f"tag {tag!r} matched {hits}"
    return hits[0]


def convert():
    df = pd.read_csv(RAW, sep=";", encoding="utf-8-sig", dtype=str)
    raw_cols = list(df.columns)
    screen_for_pii(df)

    assert df["V1"].nunique() == len(df), "V1 is not a unique respondent id"

    def clean(col):
        v = df[col].astype(str).str.strip()
        return v.where(~v.isin(BLANKS))

    cov_src = {}
    for tag, dst in DEMOG.items():
        src = by_tag(raw_cols, tag)
        cov_src[src] = dst
        df[dst] = clean(src)
    df["cov_n_siblings"] = clean(SIBLING_COUNT)
    cov_src[SIBLING_COUNT] = "cov_n_siblings"
    cov_cols = sorted(cov_src.values())

    df = df.rename(columns={"V1": "id"})

    # balance the books: every source column is an item, a covariate, or
    # dropped for a printed reason
    item_cols = {c for cols, _, _ in TABLES.values() for c in cols}
    dropped = ([by_tag(raw_cols, t) for t in DROP_GEO_TAGS + DROP_MULTISELECT_TAGS
                + DROP_OTHER_TAGS] + [PROVINCE] + DROP_ITEMS)
    accounted = item_cols | set(cov_src) | {"V1"} | set(dropped)
    left_out = [c for c in raw_cols if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(dropped)} source columns: 2 geographic (country of "
          f"birth, province), 2 multi-select, {len(DROP_ITEMS)} non-scale "
          f"items (P14-P18), 3 relative pickers/duplicate header")

    os.makedirs(OUT_DIR, exist_ok=True)
    written = set()
    for name, (cols, mapping, (lo, hi)) in sorted(TABLES.items()):
        for c in cols:
            assert c in df.columns, f"{name}: missing item column {c}"
            bad = set(df[c].dropna().astype(str).str.strip()) - set(mapping) - BLANKS
            assert not bad, f"{name}/{c}: unmapped response labels {bad}"

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="label")
        long["label"] = long["label"].astype(str).str.strip()
        long["resp"] = long["label"].map(mapping)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())

        assert name not in written, f"duplicate output table name {name}"
        assert len(name) <= 40, f"{name} is over the 40-character cap"
        written.add(name)

        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() >= 3, (name, long["item"].nunique())

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the
        # validator to run in-script, not just on the output file
        checks = run_qc(long, permitted_values={
            i: list(range(lo, hi + 1)) for i in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
