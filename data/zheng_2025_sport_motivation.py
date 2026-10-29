"""
The 28-item Sport Motivation Scale, in Chinese, answered by 571 Chinese primary
and junior-high students aged 10-14.

Source: Zheng, W., Zhao, Y., & Wu, Q. (2025). Motivation and Physical Activity
        across Chinese Adolescents: Based on Latent Profile Analysis [Dataset].
        figshare.
DOI: 10.6084/m9.figshare.29316266.v1
Data: https://doi.org/10.6084/m9.figshare.29316266.v1 ("Data.sav")
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")
Item text: IN HAND but NOT SHIPPED -- a rights hold. The .sav carries the full
        CHINESE stem of every one of the 28 motivation items as its variable
        label ("因为了解更多关于这项运动的知识让我感到愉快。") and the five
        Chinese anchors as value labels (完全不符 / 不符合 / 说不清楚 / 符合 /
        完全符合), so extraction is a cheap-gate `data_labels` job and the
        administered wording is fully recoverable. What is missing is rights:
        the Sport Motivation Scale had NO row in
        itemtext/instrument_rights_register.csv, and silence does not ship
        (ben-domingue 2026-10-15). This batch writes that row with verdict
        `hold`. The administration is Chinese, so the 2026-09-08
        translated-adaptation ruling also applies: the terms that govern are
        those of the Chinese version actually copied, and the original's own
        terms would have to be quoted before the English could ship as a
        stand-in.

The instrument is identified from the SUBSCALE STRUCTURE, not from the
deposit's label. The deposit computes seven four-item subscale means and names
them in Chinese -- 求知 (to know), 成就 (accomplishment), 刺激 (stimulation),
认同 (identification), 内摄 (introjection), 外部调节 (external regulation) and
无动机 (amotivation). Seven subscales of four items each, in exactly that
self-determination ordering, is the Sport Motivation Scale (SMS-28; Pelletier,
Fortier, Vallerand, Tuson, Briere & Blais 1995), and the stems match: the
amotivation items read "I used to have good reasons for doing sport, but now I
am asking myself if I should continue", the external-regulation items "to show
others how good I am at my sport".

ONE table, not seven. The seven subscales share one response format and one
administration, and the deposit's own column numbering (MO1..MO28, shuffled in
the file so that each subscale's four items sit together) is the instrument's
own item order. The item codes keep those source names, so a user who wants the
subscales can take them from the deposit's grouping, which this script prints.

The 9-question physical-activity block is NOT shipped. `I1`..`I9` are an
IPAQ-style activity recall whose units are MIXED WITHIN the block -- I1, I3, I5
and I8 are counts of days, I2, I4, I6, I7 and I9 are durations in minutes, and
the minute items run from 0 into the hundreds. One table would mix two
incompatible response scales; splitting by unit would make two tables of
four-ish behaviour-recall questions rather than a measured battery. Its nine
`ZI*` z-scores and the `ZPA` composite are dropped with it.

PII: none. Every column is numeric, there is no name, date, identifier or
geographic column, and the screen below prints its denominator. Height and
weight are self-reported body measurements with no identifier attached and
ship as covariates.

Output: one table, 15,936 responses -- 571 respondents x 28 items, 1-5.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "zheng_2025_sport_motivation"
PERMITTED = [1, 2, 3, 4, 5]

# The deposit's own subscale grouping, read off the file's column ORDER (each
# subscale's four items sit together, followed by its computed mean). Printed
# rather than shipped: it is the deposit's grouping, not a claim of ours.
SUBSCALES = {
    "to know (求知)": ["MO2", "MO4", "MO23", "MO27"],
    "accomplishment (成就)": ["MO8", "MO12", "MO15", "MO20"],
    "stimulation (刺激)": ["MO1", "MO13", "MO18", "MO25"],
    "identification (认同)": ["MO7", "MO11", "MO17", "MO24"],
    "introjection (内摄)": ["MO9", "MO14", "MO21", "MO26"],
    "external regulation (外部调节)": ["MO6", "MO10", "MO16", "MO22"],
    "amotivation (无动机)": ["MO3", "MO5", "MO19", "MO28"],
}

COV_MAP = {
    "school": "cov_school_level",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "High": "cov_height_cm",
    "Weight": "cov_weight_kg",
    "Eyes": "cov_myopia_or_astigmatism",
}

ACTIVITY = [f"I{i}" for i in range(1, 10)]
ACTIVITY_Z = [f"ZI{i}" for i in range(1, 10)]
SUBSCALE_MEANS = ["Know", "Acco", "Expe", "Exte", "Iden", "Intr", "Amo"]

DROP = {
    "ZPA": "a z-score of the physical-activity composite, which is itself "
        "derived from the unshipped I1..I9 block",
    "Group": "the paper's latent-profile class (1-3), derived FROM these same "
        "28 items -- a result, not a covariate",
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
    assert len(df) == 571, len(df)

    items = [c for s in SUBSCALES.values() for c in s]
    assert len(items) == 28 and len(set(items)) == 28
    assert all(c in df.columns for c in items), items
    # Every item must carry a Chinese stem and the same five anchors; that is
    # what makes the item text cheap, and what the hold is about.
    for c in items:
        assert (meta.column_names_to_labels.get(c) or "").strip(), c
        assert len(meta.variable_value_labels.get(c, {})) == 5, c
    anchors = {tuple(sorted(meta.variable_value_labels[c].items()))
               for c in items}
    assert len(anchors) == 1, "the 28 items do not share one anchor set"
    print(f"all 28 motivation items carry a Chinese stem and the same five "
          f"anchors: {[v for _k, v in sorted(meta.variable_value_labels[items[0]].items())]}")
    for name, cols in SUBSCALES.items():
        print(f"  deposit subscale {name}: {', '.join(cols)}")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | set(items) | {"id"}
                 | set(ACTIVITY) | set(ACTIVITY_Z) | set(SUBSCALE_MEANS))
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")
    print(f"skipped {len(ACTIVITY)} I1..I9 physical-activity column(s): an "
          "IPAQ-style recall whose units are mixed WITHIN the block (days for "
          "I1/I3/I5/I8, minutes for the rest), so one table would mix two "
          "incompatible response scales")
    print(f"skipped {len(ACTIVITY_Z)} ZI* z-score(s) of that block")
    print(f"skipped {len(SUBSCALE_MEANS)} depositor-computed subscale mean(s): "
          f"{SUBSCALE_MEANS}")

    codes = {c: c.lower() for c in items}
    assert len(set(codes.values())) == 28
    long = df[["id"] + covs + items].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    if before != len(long):
        print(f"dropped {before - len(long)} cell(s) of {before} outside "
              f"{PERMITTED}")
    write(long, covs)


def write(long: pd.DataFrame, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
