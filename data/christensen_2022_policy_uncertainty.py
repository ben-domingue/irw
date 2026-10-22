"""
Three policy-preference batteries from Love Christensen's pre-registered survey
experiment on how uncertain forecasts move voters: 5,888 US respondents rated
the same three policy proposals -- a minimum-wage increase, a corporate-tax
cut and a trade agreement -- for support, for their own ideal level, and for
how certain they were, after being shown predictions about the proposal's
effects attributed either to non-partisan experts or to a party, or to nobody
(the control arm).

Source: Christensen, Love (2022). How Does Uncertainty Affect Voters'
        Preferences? British Journal of Political Science 52(3): 1186-1204.
        doi 10.1017/S0007123421000247. Replication data on Harvard Dataverse.
DOI: 10.7910/DVN/F9D6TH
Data: https://doi.org/10.7910/DVN/F9D6TH --
        dat_uncertainty_BJPS_cleaned.RData, the analysis file the deposit's
        own 1_data_preparation.R writes from the raw Qualtrics export
License: CC0 1.0 (verified on the Harvard Dataverse record, latestVersion
        .license.name = "CC0 1.0")
Item text: not shipped. The deposit is data plus five R analysis scripts; it
        carries no codebook and no questionnaire, and the article's own
        supplementary PDF (static.cambridge.org, S0007123421000247sup001.pdf)
        is where the item wording is -- one hop outside the deposit. The
        column names give the policy domain and the question type
        (`mw_likert`, `tpp_cert`) but not what was asked, so shipping item
        text needs that appendix. instrument: study-authored experimental
        items, not a published scale.

This deposit was flagged `pii_suspected` on `RecipientLastName` and
`RecipientFirstName`. Those columns are EMPTY -- 0 non-blank values out of
6,132 rows in the raw file, alongside an equally empty `RecipientEmail`. They
are the standard Qualtrics panel placeholders, present in every export and
populated only for an email-list distribution. The screen matched the column
NAME and never looked at the values; see BATCH_LOG 2026-10-21d, where the
detector is changed to require a non-blank value before flagging. The cleaned
analysis file this script reads does not carry those columns at all.

`id` is the row index. The source has two platform identifiers -- `ResponseId`
(a Qualtrics `R_...` response ID) and `rid` (the panel provider's UUID) -- and
both are replaced by the row index rather than hashed, per the 2026-09-20
platform-ID ruling: a hash of an enumerable platform ID is re-linkable from
any other deposit holding the same IDs, while a row index has no preimage.

The arm is a covariate, not `treat`: there are three conditions (Control,
Expert, Partisan) and `treat` is defined as 1/0. `cov_condition` carries the
arm verbatim.

Each outcome is assembled from two columns, which is the deposit's own layout
rather than a reconstruction. 1_data_preparation.R merges the Expert and
Partisan arms' question columns into `mw_likert`/`mw_cert`/`mw_ideal` and
leaves the Control arm in the parallel `*_c` columns. The two are disjoint by
construction, which this script asserts (zero rows carry both) before taking
their union -- so all three arms ship, 5,857-5,879 respondents per item,
rather than the 5,434 the merged column alone would give.

Not shipped from the same file, each for a stated reason:
  *_qual    3 unordered categories (the proposal will increase / not change /
            decrease the outcome). Three unordered options is the nominal
            standard's territory, not core's.
  *_quant   a point forecast in the outcome's own units -- percent for the
            minimum wage and corporate tax, percentage points of GDP for
            trade -- so it is an unbounded quantity estimate on three
            mutually incommensurable scales, not an item response.
  *_forecast_*  nine derived indicators per policy that 1_data_preparation.R
            computes FROM *_quant (uncertain, low, high, center, crossing,
            magnitude, increase, decrease, inc, dec, spread_0, loss_domain).
  the dummy expansions educ_*, income_*, female, democrat, republican,
            independent, partisan and age2, all recomputable from the
            covariates shipped here.

Output: three tables. One question per file -- support, ideal level and
certainty are three different questions, and certainty is on a different
scale.
  christensen_2022_policy_support    3 items, 1-7, 5886 ids, 17579 responses
  christensen_2022_policy_ideal      3 items, 1-7, 5886 ids, 17633 responses
  christensen_2022_policy_certainty  3 items, 1-5, 5886 ids, 17581 responses
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("dat_uncertainty_BJPS_cleaned.RData")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

POLICIES = {"mw": "minimum wage increase",
            "ct": "corporate tax cut",
            "tpp": "trade agreement"}

# question suffix -> (table name, permitted response range)
QUESTIONS = {"likert": ("policy_support", (1, 7)),
             "ideal": ("policy_ideal", (1, 7)),
             "cert": ("policy_certainty", (1, 5))}

COV_MAP = {"Condition": "cov_condition",
           "age": "cov_age",
           "gender": "cov_gender",
           "education": "cov_education",
           "hhi": "cov_household_income",
           "politicalaffiliation": "cov_political_affiliation",
           "partisanship": "cov_partisanship",
           "riskpref": "cov_risk_preference"}


def pii_screen(df: pd.DataFrame) -> None:
    """Values, not names: the whole point of this deposit's false positive."""
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(text_cols) > 0, "screen selected no columns"
    expected = {"ResponseId", "rid", "Condition", "gender", "education",
                "politicalaffiliation", "hhi", "response_day",
                "tpp_treatment_partisan2"}
    assert set(text_cols) <= expected, sorted(set(text_cols) - expected)
    for name in ("RecipientLastName", "RecipientFirstName", "RecipientEmail"):
        assert name not in df.columns, \
            f"{name} is present in the cleaned file; check its VALUES"
    print("  the Qualtrics Recipient* placeholders are absent from the "
          "cleaned analysis file (and empty in the raw export)")


def main() -> None:
    import pyreadr
    result = pyreadr.read_r(str(SRC))
    df = result["dat"]
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 5888, len(df)

    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src].values
    covs = list(COV_MAP.values())

    used = set(COV_MAP)
    skipped: dict[str, str] = {
        "ResponseId": "Qualtrics response ID -- a platform participant "
                      "identifier, replaced by the row index",
        "rid": "panel provider's respondent UUID -- a platform participant "
               "identifier, replaced by the row index",
        "response_day": "date of response; single-wave experiment",
        "age2": "age squared -- a transformation of cov_age",
        "female": "dummy recomputable from cov_gender",
        "partisan": "dummy recomputable from cov_political_affiliation",
        "tpp_treatment_partisan2": "which party endorsed the trade forecast, "
                                   "a sub-arm of the Partisan condition only "
                                   "(2,746 of 5,888 rows)",
        "tpp_rep_high": "indicator for the Republican-endorsed high forecast "
                        "arm, derived from tpp_treatment_partisan2",
        "tpp_dem_high": "indicator for the Democrat-endorsed high forecast "
                        "arm, derived from tpp_treatment_partisan2",
    }
    for c in ("educ_college_degree", "educ_highschool_voc_degree",
              "educ_no_highschool"):
        skipped[c] = "dummy expansion recomputable from cov_education"
    for c in ("income_less50K", "income_50K100K", "income_100K150K",
              "income_150Kabove"):
        skipped[c] = "dummy expansion recomputable from cov_household_income"
    for c in ("democrat", "republican", "independent", "strong_dem",
              "strong_rep", "indep_lean"):
        skipped[c] = ("party-identification dummy or follow-up recomputable "
                      "from cov_political_affiliation / cov_partisanship")

    blocks: dict[str, pd.DataFrame] = {}
    for suffix, (table, (lo, hi)) in QUESTIONS.items():
        cols = {}
        for policy in POLICIES:
            merged, control = f"{policy}_{suffix}", f"{policy}_{suffix}_c"
            for c in (merged, control):
                assert c in df.columns, c
                used.add(c)
            a, b = df[merged], df[control]
            overlap = int((a.notna() & b.notna()).sum())
            assert overlap == 0, (merged, control, overlap)
            combined = a.where(a.notna(), b)
            vals = sorted(combined.dropna().unique())
            assert set(vals) <= set(range(lo, hi + 1)), (merged, vals)
            print(f"  {merged} ({int(a.notna().sum())} Expert+Partisan) + "
                  f"{control} ({int(b.notna().sum())} Control) -> "
                  f"{int(combined.notna().sum())}, 0 overlap")
            cols[f"{policy}_{suffix}"] = combined.values
        blocks[suffix] = pd.DataFrame(cols)

    # Everything else: the qual / quant / derived-forecast machinery.
    for c in df.columns:
        if c in used or c in skipped:
            continue
        if c.endswith("_qual") or c.endswith("_qual_c"):
            skipped[c] = ("3 unordered categories (increase / no change / "
                          "decrease) -- nominal standard, not core")
        elif c.endswith("_qual_increase"):
            skipped[c] = "dummy recomputable from the *_qual column"
        elif "_quant" in c:
            skipped[c] = ("point forecast in the outcome's own units, "
                          "unbounded and not commensurable across the three "
                          "policies -- a quantity estimate, not an item "
                          "response")
        elif "_forecast" in c or c.endswith(("_spread_0", "_loss_domain")):
            skipped[c] = ("indicator the deposit's 1_data_preparation.R "
                          "derives from the *_quant forecast")
        else:
            skipped[c] = "UNCLASSIFIED"
    unclassified = [c for c, why in skipped.items() if why == "UNCLASSIFIED"]
    assert not unclassified, f"unaccounted source columns: {unclassified}"
    print(f"  skipped {len(skipped)} source columns; by reason: "
          f"{pd.Series(list(skipped.values())).str[:40].value_counts().to_dict()}")
    for c, why in sorted(skipped.items()):
        print(f"    skipped column {c}: {why}")

    for suffix, (table_suffix, (lo, hi)) in QUESTIONS.items():
        wide = pd.concat([out, blocks[suffix]], axis=1)
        long = wide.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        long = long.dropna(subset=["resp"]).copy()
        long["resp"] = long["resp"].astype(int)
        long["itemcov_policy"] = long["item"].str.split("_").str[0].map(POLICIES)
        assert long["itemcov_policy"].notna().all()
        long = long[["id", "item", "resp", "itemcov_policy"] + covs] \
            .sort_values(["id", "item"])
        table = f"christensen_2022_{table_suffix}"
        assert long["id"].nunique() >= 100, (table, long["id"].nunique())
        assert long["item"].nunique() == 3, table
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
