"""
Twelve moral-relevance items from a US national sample of 1,000 adults
surveyed by YouGov/Polimetrix in Spring 2011 -- two items for each of the six
moral foundations (harm/care, fairness, loyalty, authority, purity, liberty) --
collected alongside ideology, party identification and demographics as part of
a larger study of ideology and American foreign policy attitudes.

Source: Gries, Peter (2011). Replication data for: Moral Foundations
        Questionnaire: US national representative sample data Spring 2011.
        Harvard Dataverse, V1. University of Oklahoma.
DOI: 10.7910/DVN/EL4KPR
Data: https://doi.org/10.7910/DVN/EL4KPR --
        Gries.Spring.2011.MFQ.YouGov.US.data.xls (the only file in the
        deposit; no codebook)
License: CC0 1.0 (verified on the Harvard Dataverse record, latestVersion
        .license.name = "CC0 1.0")
Item text: not shipped. The deposit is a single data file with no codebook,
        questionnaire or README, and the column names (`moral_harm`,
        `moral_just`, ...) name the foundation rather than the question. The
        wording is in the Moral Foundations Questionnaire's own relevance
        section (moralfoundations.org / Graham, Haidt & Nosek 2009), which is
        a separate instrument a hop away from this deposit -- and the register
        row that covers the MFQ family is for the MFQ-2 (Atari et al. 2023),
        not for the 2009 MFQ this predates. Identifying WHICH two relevance
        items per foundation were used needs the questionnaire as fielded,
        which the deposit does not include.

This deposit read as `download_failed` in the 2026-10-21 sweep with "Excel
file format cannot be determined". The file is a BIFF2/3/4 workbook -- Excel
2.x-4.0, a container pandas does not sniff for -- and xlrd reads it fine; the
reader now falls back to engine="xlrd" on exactly that error.

PII: no names, emails, dates of birth, phone numbers or platform IDs. Two
geographic columns ARE dropped and are not carried forward in any form, not as
cov_*, not hashed, not truncated to a coarser prefix: `casscountyfips` (504
distinct county FIPS codes) and `countyname` (505 distinct "County ST"
strings). A county of residence beside age, race, education and income in the
same row is the re-identification surface the 2026-10-20 geographic-code
ruling is about. `inputstate`, `REGION_4`, `REGION_9` and `SOUTH` are kept:
a state or a census region is standard survey demography at 50-6,000x the
population of a county, and the ruling's concern is block-to-county level
locating.

`id` is the deposit's own `caseid` (1,000 unique values in 9-1543, i.e. this
sample is a subset of the larger study's case numbering). It is a survey case
number, not a platform account ID, so it is kept as given.

The six `*_2` columns (HARM_2, FAIR_2, LOYALTY_2, AUTHORITY_2, PURITY_2,
LIBERTY_2) are the two-item MEANS per foundation -- composites, dropped. The
giveaway is arithmetic rather than assumed: each equals the mean of its own
two `moral_*` items on every row, which the script asserts before dropping
them. CONSERV_2 and CONSERV_5pt are likewise derived from `libcon`.

The workbook also carries five all-blank spacer columns whose headers are runs
of a single letter (`dddddddddddddddddddddd`, `ttttt...`), used as visual
separators between variable groups in Excel. They hold no data and are
dropped.

Output: one table, 12 items on a 1-7 relevance scale, 1,000 respondents.
  gries_2011_moral_foundations  12 items, 1-7, 1000 ids, 12000 responses
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("Gries.Spring.2011.MFQ.YouGov.US.data.xls")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "gries_2011_moral_foundations"

# Two relevance items per foundation, in the deposit's own order.
ITEMS = ["moral_harm", "moral_comp",     # harm / care
         "moral_just", "moral_fair",     # fairness
         "moral_loyl", "moral_duty",     # ingroup loyalty
         "moral_auth", "moral_obey",     # authority
         "moral_pure", "moral_chas",     # purity
         "moral_libr", "moral_free"]     # liberty

# Each mean column and the two items it averages -- asserted, not assumed.
MEANS = {"HARM_2": ("moral_harm", "moral_comp"),
         "FAIR_2": ("moral_just", "moral_fair"),
         "LOYALTY_2": ("moral_loyl", "moral_duty"),
         "AUTHORITY_2": ("moral_auth", "moral_obey"),
         "PURITY_2": ("moral_pure", "moral_chas"),
         "LIBERTY_2": ("moral_libr", "moral_free")}

COV_MAP = {"weight1000": "cov_survey_weight",
           "AGE": "cov_age",
           "MALE": "cov_male",
           "race": "cov_race",
           "BLACK": "cov_black",
           "HISPANIC": "cov_hispanic",
           "EDUC": "cov_education",
           "INCOME_NEW": "cov_income",
           "inputstate": "cov_state",
           "REGION_4": "cov_region_4",
           "REGION_9": "cov_region_9",
           "SOUTH": "cov_south",
           "libcon": "cov_lib_con_0_100",
           "ideo5_new": "cov_ideology_5pt",
           "LIBCON_20": "cov_lib_con_extreme",
           "DEMREP": "cov_dem_rep",
           "pid7": "cov_party_id_7pt",
           "pid3": "cov_party_id_3pt"}

DROPPED_GEO = {
    "casscountyfips": "county FIPS code (504 distinct) -- geographic code, "
                      "DROPPED under the 2026-10-20 ruling, not carried "
                      "forward in any form",
    "countyname": "county name and state (505 distinct) -- geographic code, "
                  "DROPPED, not carried forward in any form",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0, "nothing to screen"
    # countyname is the only text column, and it is dropped below.
    assert set(text_cols) <= {"countyname"}, text_cols


def main() -> None:
    # engine="xlrd" explicitly: this is a BIFF2/3/4 workbook, and pandas'
    # container sniffing does not recognise it.
    df = pd.read_excel(SRC, engine="xlrd")
    print("raw shape", df.shape)
    pii_screen(df)

    for c in ITEMS:
        assert c in df.columns, c
        vals = sorted(df[c].dropna().unique())
        assert vals == list(range(1, 8)), (c, vals)

    assert df["caseid"].is_unique, "caseid repeats"
    out = pd.DataFrame({"id": df["caseid"].astype(int)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src]
    covs = list(COV_MAP.values())

    # Establish that the *_2 columns are composites rather than assuming it.
    for mean_col, (a, b) in MEANS.items():
        pair = df[[mean_col, a, b]].dropna()
        recomputed = pair[[a, b]].mean(axis=1)
        assert (recomputed - pair[mean_col]).abs().max() < 1e-9, mean_col
        print(f"  {mean_col} == mean({a}, {b}) on all {len(pair)} rows "
              "-- composite, dropped")

    spacers = [c for c in df.columns
               if re.fullmatch(r"(.)\1{4,}\d*", str(c))]
    for c in spacers:
        assert df[c].isna().all(), f"spacer column {c} is not empty"

    skipped = dict(DROPPED_GEO)
    skipped.update({c: f"two-item mean of {a} and {b} -- a composite, not a "
                       "response (verified arithmetically above)"
                    for c, (a, b) in MEANS.items()})
    skipped.update({c: "all-blank spacer column used as a visual separator "
                       "in the workbook" for c in spacers})
    skipped["CONSERV_2"] = ("standardised ideology score derived from libcon "
                            "-- a transformation, not a response")
    skipped["CONSERV_5pt"] = ("ideology banded to 5 points from libcon -- a "
                              "transformation, not a response")
    used = {"caseid"} | set(COV_MAP) | set(ITEMS)
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped column {c}: {why}")

    wide = pd.concat([out, df[ITEMS]], axis=1)
    long = wide.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    assert long["id"].nunique() >= 100 and long["item"].nunique() == 12

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:180]}")

    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
