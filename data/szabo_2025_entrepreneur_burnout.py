"""Szabó (2025), Mendeley Data -- burnout in entrepreneurs predicted by stress
and harmonious passion.

Source: https://data.mendeley.com/datasets/jkwhf3ys6z
DOI: 10.17632/jkwhf3ys6z
License: CC BY 4.0

184 Hungarian entrepreneurs completing eight instruments.

Tables written
--------------
szabo_2025_passion             184 x 17 items, 1-7
szabo_2025_wellbeing           184 x 12 items, 1-4
szabo_2025_molbi               184 x 10 items, 1-4
szabo_2025_bwas                184 x  7 items, 0-4
szabo_2025_work_addiction      184 x  7 items, 1/2
szabo_2025_family_conflict     184 x  5 items, 1-4
szabo_2025_work_conflict       184 x  5 items, 1-4
szabo_2025_pss4                184 x  4 items, 0-4

Coding notes
------------
* Eight tables for eight instruments. Three response formats are involved
  (1-7, 1-4, 0-4) plus a dichotomous screen, so pooling was never an option.
* **Three families of columns are derived, and each is verified as such
  before being dropped** rather than assumed:
  - `w7_SQ001..017` equals `PS1..PS17` minus 1 (a 0-6 recode of the passion
    scale);
  - `c3_SQ001/005/008/010_num_neg` equals `5 - MOLBI1/5/8/10` (the reverse-
    keyed burnout items);
  - `w2_SQ002/003_num_index_neg` equals `4 -` their unreversed counterparts.
* **`w2_SQ001..004` is the PSS-4**, which the deposit never names. It was
  identified by reconstruction: `w2_001 + w2_002_neg + w2_003_neg + w2_004`
  reproduces the deposit's own `Stress` column exactly for all 184 rows,
  which is the PSS-4's scoring rule including its two reverse-keyed items.
  It ships under its unreversed items as `szabo_2025_pss4`.
* `WA1`..`WA7` are a yes/no work-addiction screen coded 1/2 (not 0/1); the
  source coding is kept, and `WATOTAL` is verified to be their sum.
* **`id` is row position, not the deposit's `id` column.** That column is not
  a person key: 35 of its values appear on two rows each, and those pairs are
  plainly different respondents -- differing in age, gender and responses.
  The closest pair (code 206) still differs on 12 columns, so they are two
  people sharing a code rather than a duplicated record, and both are kept.
* Free-text columns are not shipped: `DescribeOtherReasonsForBusiness` and
  `AnyFormofAddiction` hold short Hungarian answers ("nincs", "Koffein") with
  no names or contact details, so the deposit is not excluded on PII grounds,
  but neither is useful as a covariate.
"""

import os
import re
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/jkwhf3ys6z"
DATASET, VERSION = "jkwhf3ys6z", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"GENDER": "cov_gender", "AGE": "cov_age", "Education": "cov_education",
        "FamilyStatus": "cov_family_status", "Position": "cov_position",
        "FieldOfBusiness": "cov_field", "StageOfBusiness": "cov_business_stage"}
# (table suffix, source prefix, n items, low, high)
BLOCKS = [("passion",         "PS",             17, 1, 7),
          ("wellbeing",       "WB",             12, 1, 4),
          ("molbi",           "MOLBI",          10, 1, 4),
          ("bwas",            "BWAS",            7, 0, 4),
          ("work_addiction",  "WA",              7, 1, 2),
          ("family_conflict", "FamilyConflict",  5, 1, 4),
          ("work_conflict",   "WorkConflict",    5, 1, 4)]
PSS4 = [f"w2_SQ{i:03d}_num_index" for i in range(1, 5)]


def main():
    s = requests.Session()
    s.headers.update(UA)
    listing = s.get(f"https://data.mendeley.com/public-api/datasets/"
                    f"{DATASET}/files?folder_id=root&version={VERSION}",
                    timeout=120).json()
    hit = [f for f in listing if f["filename"].lower().endswith(".xlsx")]
    assert len(hit) == 1, [f["filename"] for f in listing]
    raw = s.get(hit[0]["content_details"]["download_url"], timeout=600)
    raw.raise_for_status()
    open("/tmp/szabo_entre.xlsx", "wb").write(raw.content)
    d = pd.read_excel("/tmp/szabo_entre.xlsx")

    # every dropped family must be provably derived
    for i in range(1, 18):
        assert (d[f"w7_SQ{i:03d}_num_index"] == d[f"PS{i}"] - 1).all(), i
    for i in (1, 5, 8, 10):
        assert (d[f"c3_SQ{i:03d}_num_neg"] == 5 - d[f"MOLBI{i}"]).all(), i
    for i in (2, 3):
        assert (d[f"w2_SQ{i:03d}_num_index_neg"]
                == 4 - d[f"w2_SQ{i:03d}_num_index"]).all(), i
    # and the PSS-4 identification must reproduce the deposit's own total
    pss = (d[PSS4[0]] + d["w2_SQ002_num_index_neg"]
           + d["w2_SQ003_num_index_neg"] + d[PSS4[3]])
    assert (pss == d["Stress"]).all(), "w2 block is not the PSS-4"
    assert (d[[f"WA{i}" for i in range(1, 8)]].sum(axis=1) == d["WATOTAL"]).all()
    print("  verified: w7 = PS-1, c3 = 5-MOLBI, w2_neg = 4-w2, "
          "w2 block reproduces Stress under PSS-4 scoring")

    # the deposit's `id` is NOT a person key: 35 of its values occur on two
    # rows each, and those pairs are different people (different age, gender
    # and responses -- the closest pair, id 206, still differs on 12 columns).
    assert d["id"].nunique() < len(d)
    covs = list(COVS.values())
    d = d.rename(columns={"id": "src_code", **COVS})
    d["id"] = range(1, len(d) + 1)
    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0

    for suffix, prefix, n_expected, lo, hi in BLOCKS + [
            ("pss4", None, 4, 0, 4)]:
        items = (PSS4 if prefix is None else
                 sorted([c for c in d.columns
                         if re.fullmatch(rf"{prefix}\d+", str(c))],
                        key=lambda c: int(re.sub(r"\D", "", c))))
        assert len(items) == n_expected, (suffix, items)
        shipped.update(items)

        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        if prefix is None:
            long["item"] = long["item"].str.replace(
                r"w2_SQ0*(\d+)_num_index", r"PSS4_\1", regex=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"szabo_2025_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} entrepreneurs x {n_it} items = {len(long)} "
              f"responses, resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long) / (n_id * n_it):.3f}")

    # balance the books
    derived = totals = business = free_text = 0
    for c in d.columns:
        if c in shipped or c in covs or c == "id":
            continue
        if c == "src_code":
            print("  skip id: deposit code, repeats across different people")
        elif re.match(r"^(w7_|c3_|w2_)", str(c)):
            derived += 1
        elif c in ("WATOTAL", "WorkAddiction", "HarmoniousPassion",
                   "ObsessivePassion", "CriterionPassion", "MOLBIExhaustion",
                   "MOLBIDisengagement", "Burnout", "Stress", "WellBeing",
                   "WorkCausingFamilyConflict", "FamilyCausingworkWorkConflict",
                   "bergen_holic", "bergen_holic_dch",
                   "WorkAddicted_2_Not_1"):
            totals += 1
        elif not pd.api.types.is_numeric_dtype(d[c]):
            free_text += 1
        else:
            business += 1
    print(f"\n  skipped: {derived} derived recodes/reversals, {totals} scored "
          f"totals and classifications, {business} business/health background "
          f"variables not shipped as covariates, {free_text} free-text columns")
    print(f"\n8 tables, {total:,} responses")


if __name__ == "__main__":
    main()
