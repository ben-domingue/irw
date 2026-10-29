"""
Five instruments administered in Greek to 410 nurses: gaslighting at work,
psychological distress (PHQ-4), resilience, quiet quitting and work engagement.

Source: Galanis, P. (2025). Workplace gaslighting increases nurses job burnout
        [Dataset]. figshare.
DOI: 10.6084/m9.figshare.28868615.v1
Data: https://doi.org/10.6084/m9.figshare.28868615.v1
        ("Workplace gaslighting increases nurses job burnout.sav")
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")
Item text: IN HAND but NOT SHIPPED in this batch -- a rights hold, not an
        availability gap, and the one thing a later pass must not re-derive.
        The .sav is unusually complete: 66 of 67 variables carry a variable
        label, every item's label IS its full Greek stem, and 51 variables
        carry value labels giving the Greek anchor wording for every response
        option. So extraction is cheap and the administered (Greek) wording is
        recoverable in full. What is NOT established is rights. Of the five
        instruments, `itemtext/instrument_rights_register.csv` carries exactly
        two: the PHQ/GAD screener family is `ship`, and the Utrecht Work
        Engagement Scale is `block`. The Gaslighting at Work Scale, the
        resilience scale and the Quiet Quitting Scale have no row at all, and
        silence does not ship (ben-domingue, 2026-10-15). On top of that these
        are GREEK adaptations, so the 2026-09-08 ruling applies -- the test is
        the terms of the thing actually copied, i.e. the translation. See the
        TODO.md entry this batch leaves: three register rows and one fallback
        decision, then four of the five tables can ship from this same file.

The GWS block needs reading carefully, which is why item codes keep the source
column names rather than being renumbered. The deposit ships EIGHTEEN distinct
gaslighting items in two differently-numbered groups:

  * `GWS_item_1` .. `GWS_item_11` -- eleven items whose labels are numbered
    1..11, i.e. the retained scale in its final numbering.
  * `GWS_4`, `GWS_7`, `GWS_9`, `GWS_10`, `GWS_11`, `GWS_15`, `GWS_17` -- seven
    further items whose labels are numbered 4, 7, 9, 10, 11, 15 and 17, i.e.
    items carrying their ORIGINAL numbering from a longer form.

The two groups overlap in NUMBER and not in CONTENT: `GWS_item_4` is "accuses
you of lying when you disagree with him/her" while `GWS_4` is "makes you feel
you are not perceiving things correctly"; `GWS_item_7` is "ignores your
complaints" while `GWS_7` is "makes you doubt whether you remember things
correctly". All eighteen labels were read and all eighteen are distinct. So the
codes must not be read as numbers -- `gws_4` and `gws_item_4` are two different
items -- and they are shipped as one table because they are one instrument on
one response scale, administered together.

Two single-item measures become covariates rather than one-item tables (a table
with one distinct item is never shipped): the 0-10 burnout self-rating
(`cov_burnout_single_item_0_10`, anchored "not tired at all" to "extremely
tired") and the six-point turnover-intention question
(`cov_turnover_intention`).

PII: none. Every column is numeric, there is no identifier, name, date or
geographic column, and the screen below prints its denominator. The deposit's
own `id` is a 1..410 serial and is replaced by the row index anyway.

Output: five tables, 13,120 responses.
  * galanis_2025_gaslighting_work -- 18 items, resp 1-5
  * galanis_2025_phq4            --  4 items, resp 0-3
  * galanis_2025_resilience      --  6 items, resp 1-5
  * galanis_2025_quiet_quitting  --  9 items, resp 1-5
  * galanis_2025_work_engagement --  3 items, resp 0-6
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("Workplace gaslighting increases nurses job burnout.sav"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

GWS_RETAINED = [f"GWS_item_{i}" for i in range(1, 12)]
GWS_ORIGINAL = [f"GWS_{i}" for i in (4, 7, 9, 10, 11, 15, 17)]

BLOCKS = {
    "galanis_2025_gaslighting_work": (GWS_RETAINED + GWS_ORIGINAL, [1, 2, 3, 4, 5]),
    "galanis_2025_phq4": ([f"PHQ{i}" for i in range(1, 5)], [0, 1, 2, 3]),
    "galanis_2025_resilience": ([f"Resilience{i}" for i in range(1, 7)],
                                [1, 2, 3, 4, 5]),
    "galanis_2025_quiet_quitting": ([f"QQS_{i}" for i in range(1, 10)],
                                    [1, 2, 3, 4, 5]),
    "galanis_2025_work_engagement": ([f"UWES_{i}" for i in range(1, 4)],
                                     [0, 1, 2, 3, 4, 5, 6]),
}

COV_MAP = {
    "φύλο": "cov_gender",
    "ηλικία": "cov_age",
    "εκπαιδευτικό": "cov_education",
    "προϋπηρεσία": "cov_years_experience",
    "σκορ_εξουθενωσης_0_10": "cov_burnout_single_item_0_10",
    "προθεση_αποχωρησης": "cov_turnover_intention",
}

DROP = {
    "id": "the deposit's own 1..410 serial, replaced by the row index",
    "επάγγελμα": "profession -- constant (every respondent is coded 1, "
        "'Νοσηλευτής'/nurse), so it carries no information",
    "GWS_συνολικο_σκορ": "depositor-computed GWS mean score",
    "GWS_loss_self_trust": "depositor-computed GWS subscale mean",
    "GWS_abuse_of_power": "depositor-computed GWS subscale mean",
    "PHQ_total": "depositor-computed PHQ-4 total",
    "PHQ_categories": "depositor-computed PHQ-4 severity band",
    "PHQ_anxiety": "depositor-computed PHQ-4 anxiety subscore",
    "PHQ_anxiety_categories": "depositor-computed anxiety screen cut-off",
    "PHQ_depression": "depositor-computed PHQ-4 depression subscore",
    "PHQ_depression_categories": "depositor-computed depression screen cut-off",
    "total_score": "depositor-computed QQS mean score (its variable label "
        "says so: 'QQS_mean_score_1_5')",
    "score_detachment": "depositor-computed QQS subscale mean",
    "score_lack_initiative": "depositor-computed QQS subscale mean",
    "score_lack_motivation": "depositor-computed QQS subscale mean",
    "QQS_dichotomous": "depositor-computed quiet-quitter cut-off",
    "resilience_score": "depositor-computed resilience mean",
    "UWES_score": "depositor-computed work-engagement mean",
    "turnover_dichotomous": "depositor-computed cut-off on "
        "προθεση_αποχωρησης, which ships as cov_turnover_intention",
    "ΔΟ": "entirely empty (0 non-missing values) and unlabelled",
    "filter_$": "an SPSS filter variable, label 'φύλο = 0 (FILTER)'",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 410, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)} -- "
          "item text is CHEAP here and is held on rights, see the docstring")

    # The eighteen GWS stems must be eighteen different stems. This is the
    # claim the two numbering schemes could silently break.
    stems = {c: (meta.column_names_to_labels.get(c) or "").strip()
             for c in GWS_RETAINED + GWS_ORIGINAL}
    assert all(stems.values()), [c for c, s in stems.items() if not s]
    assert len(set(stems.values())) == 18, \
        f"GWS stems are not all distinct: {len(set(stems.values()))} unique"
    print("GWS: 18 distinct stems over the two numbering groups "
          f"({len(GWS_RETAINED)} renumbered 1-11 + {len(GWS_ORIGINAL)} keeping "
          "their original numbers); gws_4 and gws_item_4 are different items")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id"}
                 | {c for cols, _p in BLOCKS.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, (cols, permitted) in BLOCKS.items():
        assert all(c in df.columns for c in cols), (table, cols)
        codes = {c: c.lower().replace("$", "") for c in cols}
        assert len(set(codes.values())) == len(cols), codes
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        if before != len(long):
            print(f"{table}: dropped {before - len(long)} cell(s) of {before} "
                  f"outside the documented response set {permitted}")
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
