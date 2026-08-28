"""Coach leadership, sport commitment and team cohesion, adolescent handball.

Source: Li, Jilin (2026), Zenodo 10.5281/zenodo.21445573, CC BY 4.0 -- "Coach
Leadership Behavior and Team Cohesion Among Adolescent Handball Players". 223
players.

Three instruments, three tables, all on a 1-5 scale. They are separated
because the respondent is rating three different objects -- the coach, their
own commitment, and the team:

  li_2026_coach_leadership   25 items (jiao lian yuan, coach leadership)
  li_2026_sport_commitment   20 items (yun dong cheng nuo)
  li_2026_team_cohesion      18 items (tuan dui ning ju li)

Eighteen further columns are scores, not items -- 15 subscale dimensions plus
one overall mean per instrument. They are identified by cardinality rather
than by name: every real item takes at most 5 distinct values on the 1-5
scale, while these run 9 to 158 distinct values, so the check does not depend
on transliterating Chinese column names. They cover: the five Leadership
Scale for Sports dimensions (training instruction, democratic behaviour,
autocratic behaviour, social support, rewarding) and the sport-commitment and
cohesion dimensions. They carry the dimension names rather than a numeric
suffix, which is what separates them from the item columns.

Column names are Chinese; the item codes are kept verbatim from the source
so they join to any item text extracted from the same deposit.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 21445573
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {"li_2026_coach_leadership": ("教练员", 25),
          "li_2026_sport_commitment": ("运动承诺", 20),
          "li_2026_team_cohesion": ("团队凝聚力", 18)}
COVARIATES = {"性别": "cov_sex", "年龄": "cov_age",
              "运动年限": "cov_years_playing"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    try:
        df, _m = pyreadstat.read_sav(p, apply_value_formats=False)
    except Exception:
        df, _m = pyreadstat.read_sav(p, apply_value_formats=False,
                                     encoding="latin1")

    item_cols = {}
    for table, (stem, n) in SCALES.items():
        cols = [c for c in df.columns if re.match(rf"^{stem}\d+$", str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    items = set(sum(item_cols.values(), []))
    # Everything else is a covariate or a dimension score; the scores are the
    # columns whose name is a stem with NO numeric suffix.
    scores = [c for c in df.columns
              if c not in items and c not in COVARIATES]
    assert len(scores) == 18, f"expected 18 score columns, found {len(scores)}"
    for c in scores:
        u = df[c].dropna()
        assert u.nunique() > 5, \
            f"{c} has {u.nunique()} levels -- it looks like an item, not a score"
    for cols in item_cols.values():
        for c in cols:
            assert df[c].dropna().nunique() <= 5, \
                f"{c} has more than 5 levels -- it looks like a score, not an item"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in item_cols.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == len(cols), table
        assert long["resp"].between(1, 5).all(), f"{table}: expected 1-5"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
