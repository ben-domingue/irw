"""
Seven climate-change attitude and behaviour blocks answered by 652 Bangladeshi
adults, split between slow-onset and rapid-onset climate-exposure regions.

Source: Akter, F. (2026). Direct and indirect influences of social-cognitive
        and experiential factors on pro-environmental behaviour [Data set].
        Monash University (Bridges).
DOI: 10.26180/33183470
Data: https://bridges.monash.edu/articles/dataset/33183470 (file
        "Final Data.sav")
License: CC BY 4.0 (verified on the figshare API record, license.name)
Item text: shipped, from the .sav's own labels. BOTH levels are present and
        both were used: variable labels give each item's stem (49 of 84
        columns carry one, which is every item column), and value labels give
        each block's anchors (59 variables carry them). Administered in
        English.

**Seven tables, one per labelled block**, per datastandard.md's "Multiple
scales in one file". The blocks do not share a scale -- three different anchor
sets are in play (1-5 agreement, 1-7 government support, 1-6 agreement, 0-6
frequency) and the value labels are what establish that, not the prefixes.

**`Social_norms_Q` is reverse-keyed relative to every other agreement block**
and is shipped as the deposit coded it: 1 is "Strongly agree" there, while in
`Self_efficacy_Q`, `Risk_Perception_Q` and `Adaptation_to_Climate_Change_Q` 1
is "Strongly Disagree". Recoding it to match would silently rewrite the
depositor's data; the anchors ship with the item text, so the direction is
explicit to anyone reading the table.

Not shipped from this file:
  * `Knowledge_Q1`-`Knowledge_Q5` -- a mixed block: some columns are coded 1-3,
    one is a free-typed multi-select of information sources ("Newspaper/
    Magazines, Social Media (FB/YT/IG)"). Not one scale, and the free-text
    column is not an item.
  * `K1`-`K4` -- binary 0/1 with NO variable label of any kind, so there is
    nothing to say about what they asked.
  * The single-item measures (`Belief_certainty`, `Perceived_vulnerability_Q`,
    `Total_knowledge`, ...), which belong to no block and are below the
    three-item floor on their own.

PII: no names or emails. Two kinds of column are dropped rather than carried:
  * `District_origin`, `Present_residence_district` and their two division
    columns -- geographic/administrative codes (64 and 41 Bangladeshi
    districts). The 2026-10-20 ruling says drop the column and ship the rest,
    in no form, not even coarsened; the two binary region-TYPE columns
    (slow-onset vs rapid-onset exposure), which are the study's design
    variable rather than a location, are kept.
  * `Occupation`, `Department`, `Fathers_occupation` and `Mothers_occupation`
    -- free-typed job titles and fields of work (132 distinct occupations).
    Under the 2026-10-21 ruling a short free-text self-report column is
    dropped rather than shipped; `Education_level` and
    `Monthly_income_range`, which are coded, are kept. The last three were
    found by the screen below rather than by reading the column list, which
    is what the assertion is for.
The screen below prints its denominator.

Output: seven tables, 19,560 responses -- 652 respondents, 30 items.
  * akter_2026_climate_social_norms       3 items, resp 1-5
  * akter_2026_climate_incentives         3 items, resp 1-7
  * akter_2026_climate_self_efficacy      3 items, resp 1-6
  * akter_2026_climate_risk_perception    6 items, resp 1-6
  * akter_2026_climate_adaptation         4 items, resp 1-6
  * akter_2026_proenv_private_behaviour   6 items, resp 0-6
  * akter_2026_proenv_public_behaviour    5 items, resp 0-6
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Final Data.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# table -> (source prefix, item count, permitted values)
BLOCKS = {
    "akter_2026_climate_social_norms": ("Social_norms_Q", 3, [1, 2, 3, 4, 5]),
    "akter_2026_climate_incentives": (
        "Perceived_Incentives_Q", 3, [1, 2, 3, 4, 5, 6, 7]),
    "akter_2026_climate_self_efficacy": (
        "Self_efficacy_Q", 3, [1, 2, 3, 4, 5, 6]),
    "akter_2026_climate_risk_perception": (
        "Risk_Perception_Q", 6, [1, 2, 3, 4, 5, 6]),
    "akter_2026_climate_adaptation": (
        "Adaptation_to_Climate_Change_Q", 4, [1, 2, 3, 4, 5, 6]),
    "akter_2026_proenv_private_behaviour": (
        "Pro_Envo_Private_Behav_Q", 6, [0, 1, 2, 3, 4, 5, 6]),
    "akter_2026_proenv_public_behaviour": (
        "Pro_Envo_Public_Behav_Q", 5, [0, 1, 2, 3, 4, 5, 6]),
}

COV_MAP = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Age_range": "cov_age_range",
    "Education_level": "cov_education_level",
    "Monthly_income_range": "cov_monthly_income_range",
    "Area_of_residence": "cov_area_of_residence",
    "Region_type_O": "cov_region_type_origin",
    "Region_Type_P": "cov_region_type_present",
    "exposure_type_origin": "cov_exposure_type_origin",
    "exposure_type_present_residence": "cov_exposure_type_present",
}

DROP = {
    "District_origin": "a geographic code (64 districts) -- 2026-10-20 ruling",
    "District_origin_division": "a geographic code -- 2026-10-20 ruling",
    "Present_residence_district":
        "a geographic code (41 districts) -- 2026-10-20 ruling",
    "Present_residence_division": "a geographic code -- 2026-10-20 ruling",
    "Occupation": "free-typed job title, 132 distinct -- 2026-10-21 ruling",
    "Serial": "the deposit's row serial; id is assigned here instead",
    "Department": "free-typed department/field of work -- 2026-10-21 ruling",
    "Fathers_occupation":
        "free-typed parental job title -- 2026-10-21 ruling",
    "Mothers_occupation":
        "free-typed parental job title -- 2026-10-21 ruling",
    "Knowledge_Q2":
        "free-typed multi-select of information sources, not an item",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {sorted(text_cols)}")
    assert text_cols, "no string columns selected -- screen is not working"
    banned = re.compile(r"name|email|phone|postal|zip|birth|dob", re.I)
    hits = [c for c in df.columns if banned.search(c)]
    assert not hits, f"identifier-shaped column(s): {hits}"
    # Every string column must be either dropped above or a coded covariate.
    carried = [c for c in text_cols if c not in DROP]
    print(f"  string columns carried forward: {carried}")
    assert not carried, carried


def main() -> None:
    df, meta = pyreadstat.read_sav(str(SRC))
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 652, len(df)

    labels = meta.column_names_to_labels
    value_labels = meta.variable_value_labels
    print(f"variable labels: {sum(1 for c in df.columns if (labels.get(c) or '').strip())}"
          f" of {len(df.columns)}; value-labelled variables: {len(value_labels)}")

    item_cols = {}
    for table, (prefix, n, permitted) in BLOCKS.items():
        cols = sorted((c for c in df.columns
                       if re.fullmatch(rf"{re.escape(prefix)}\d+", c)),
                      key=lambda c: int(re.sub(r"\D", "", c)))
        assert len(cols) == n, (table, len(cols), n, cols)
        # Both label levels must be there -- the item text depends on both.
        for c in cols:
            assert (labels.get(c) or "").strip(), f"{c} has no variable label"
        anchors = value_labels.get(cols[0]) or {}
        assert sorted(int(k) for k in anchors) == permitted, (table, anchors)
        print(f"{table}: {n} items, anchors "
              f"{anchors[float(permitted[0])]!r}..{anchors[float(permitted[-1])]!r}")
        item_cols[table] = cols

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = set(COV_MAP) | set(covs) | {"id"} | set(DROP)
    accounted |= {c for cs in item_cols.values() for c in cs}
    leftover = sorted(c for c in df.columns if c not in accounted)
    for col, why in DROP.items():
        assert col in df.columns, col
        print(f"dropped {col} -- {why}")
    print(f"not used ({len(leftover)} column(s), none part of a shipped "
          f"block): {leftover}")

    total = 0
    for table, cols in item_cols.items():
        total += write(df, table, cols, covs, BLOCKS[table][2])
    print(f"total responses across {len(item_cols)} tables: {total:,}")


def write(df: pd.DataFrame, table: str, cols: list, covs: list,
          permitted: list) -> int:
    codes = {c: c.lower() for c in cols}
    assert len(set(codes.values())) == len(cols), codes
    long = df[["id"] + covs + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()]
    long["resp"] = long["resp"].astype(int)

    outside = sorted(set(long["resp"].unique()) - set(permitted))
    assert not outside, f"{table}: resp outside {permitted}: {outside}"

    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:150]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> {table}: rows={len(long):,} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={min(long['resp'])}-{max(long['resp'])}")
    return len(long)


if __name__ == "__main__":
    main()
