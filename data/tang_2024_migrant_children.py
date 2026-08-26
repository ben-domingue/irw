"""Tang, Xiang & Liu (2024), Scientific Reports -- family migration and the
well-being of Chinese migrant workers' children.

Source: https://europepmc.org/article/PMC/PMC11150384
DOI: 10.1038/s41598-024-63589-5
License: CC BY 4.0

1,682 Chinese vocational (VET) school students, aged 15-21, sampled across
inbound (urban destination) and outbound (rural origin) areas, answering a
battery of social-cognitive well-being scales plus a caregiver-child
relationship battery. Every block is a 1-5 Likert scale.

This deposit was flagged `below_min_n` by the 2026-08-26 weekly PMC sweep --
"only 7 distinct respondents" -- because the file has **no id column at all**,
so the triage id heuristic fell back on a 7-category demographic. The row
index is the respondent; N is 1,682, not 7.

Tables written
--------------
tang_2024_swls                            5 items    (Satisfaction With Life)
tang_2024_academic_satisfaction           6 items
tang_2024_self_efficacy                   5 items
tang_2024_outcome_expectations            5 items
tang_2024_goal_progress                   4 items
tang_2024_panas_positive                  5 items
tang_2024_panas_negative                  7 items
tang_2024_environmental_support           3 items
tang_2024_self_construal                 12 items
tang_2024_caregiver_child_attachment     17 items
tang_2024_caregiver_child_conflict        5 items
tang_2024_caregiver_child_communication   5 items
tang_2024_caregiver_child_regulation      9 items

Coding notes
------------
* **Column prefix -> construct mapping was verified against the paper's own
  per-item tables by matching item means**, not inferred from the prefix:
  the data's `SWB1..SWB5` means (2.85/3.15/3.12/2.43/2.26) reproduce Table 6's
  `LS1..LS5` totals exactly, `ESP1..ESP3` reproduce Table 18, and
  `ES1/3/4/7/8/10/12` reproduce Table 16's `NPA1/3/4/7/8/10/12` -- which fixes
  the `ES` block as the 12-item Chinese PANAS with the paper's own
  positive/negative split (positive = NPA2,5,6,9,11).
* `SC` (12 items) is the self-construal battery. The paper states it was
  administered and then dropped from the analysis on reliability grounds, so
  it has no item table to match against; it is the only measured-but-untabulated
  construct of that length, and the correlation matrix shows the expected two
  weakly-related independence/interdependence halves. `SC11` is absent from
  the deposit; the source names are kept as-is rather than renumbered.
* `CCA` (17 items) is caregiver-child attachment, not co-activity: its
  correlation matrix is cleanly bipolar (items 3,5,7,8,9,14,15 load against
  the rest), which is the trust-and-communication vs. alienation structure of
  an IPPA-type scale, and the paper's Model II names exactly those two
  subscales. It ships as one instrument with the reverse-worded items left
  uncoded, per the data standard.
* `CCCLIT` (4 items) is **not** written. By elimination it should be the
  paper's caregiver-child co-activity variable, but the abbreviation does not
  support that reading and there is no item table to check against, so naming
  it would be a guess. Held for a human call -- see TODO.md.
* `time_fa_leav`/`time_mo_leav` use -99 as "not applicable" (the parent never
  migrated); those cells are set missing rather than shipped as a response
  category. No other column carries a sentinel.
* `Unnamed: 129..132` are a stray Excel descriptive-statistics block (Chinese
  labels 平均/标准差/... and their values) left in the corner of the sheet,
  not data -- dropped.
* No PII: the sheet carries no names, dates of birth, free text, or
  geocoordinates. `orig_place` is a 3-category region code.
"""

import io
import os
import re
import sys
import zipfile

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

PMCID = "PMC11150384"
SUPP = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
        f"{PMCID}/supplementaryFiles")
MEMBER = "41598_2024_63589_MOESM2_ESM.xlsx"
OUTDIR = "irw_output"

# table name -> item columns
TABLES = {
    "tang_2024_swls":                          [f"SWB{i}" for i in range(1, 6)],
    "tang_2024_academic_satisfaction":         [f"AS{i}" for i in range(1, 7)],
    "tang_2024_self_efficacy":                 [f"SE{i}" for i in range(1, 6)],
    "tang_2024_outcome_expectations":          [f"OE{i}" for i in range(1, 6)],
    "tang_2024_goal_progress":                 [f"GP{i}" for i in range(1, 5)],
    # paper's own PANAS split (Tables 14 and 15), verified by item means
    "tang_2024_panas_positive":                [f"ES{i}" for i in (2, 5, 6, 9, 11)],
    "tang_2024_panas_negative":                [f"ES{i}" for i in (1, 3, 4, 7, 8, 10, 12)],
    "tang_2024_environmental_support":         [f"ESP{i}" for i in range(1, 4)],
    "tang_2024_self_construal":                [f"SC{i}" for i in list(range(1, 11)) + [12, 13]],
    "tang_2024_caregiver_child_attachment":    [f"CCA{i}" for i in range(1, 18)],
    "tang_2024_caregiver_child_conflict":      [f"CCC{i}" for i in range(1, 6)],
    "tang_2024_caregiver_child_communication": [f"CCCF{i}" for i in range(1, 6)],
    "tang_2024_caregiver_child_regulation":    [f"CCR{i}" for i in range(1, 10)],
}

# source covariate column -> cov_ name (order preserved)
COVS = {
    "age": "cov_age", "male": "cov_male", "science": "cov_science_track",
    "inbound": "cov_inbound_area", "guardian": "cov_guardian",
    "resid_urban": "cov_hukou_urban", "living_urban": "cov_living_urban",
    "parents_home": "cov_parents_at_home", "fa_leaving": "cov_father_migrated",
    "time_fa_leav": "cov_father_migration_time", "mo_leaving": "cov_mother_migrated",
    "time_mo_leav": "cov_mother_migration_time", "distance_fa": "cov_distance_father_km",
    "distance_mo": "cov_distance_mother_km", "freq_fa": "cov_see_father_freq",
    "freq_mo": "cov_see_mother_freq", "caregiver_now": "cov_caregiver_now",
    "caregiver_5": "cov_caregiver_age5", "caregiver_10": "cov_caregiver_age10",
    "commu_parents": "cov_communication_parents", "No._children": "cov_n_children",
    "rank": "cov_sibling_rank", "edu_mo": "cov_mother_education",
    "edu_fa": "cov_father_education", "age_mo": "cov_mother_age_group",
    "age_fa": "cov_father_age_group", "married": "cov_parents_marital_status",
    "No._car": "cov_family_cars", "room": "cov_rooms",
    "freq_of_travel": "cov_travel_freq", "school_perfor": "cov_school_performance",
    "health_statue": "cov_health_status", "smoke": "cov_smokes",
    "wine_drink": "cov_drinks", "live_dorm": "cov_lives_in_dorm",
    "identity": "cov_identity", "orig_place": "cov_origin_region",
}
SENTINEL_NEG99 = ["time_fa_leav", "time_mo_leav"]

SKIP = {
    "CCCLIT": "4-item caregiver-child block with no item table in the paper "
              "and an abbreviation that does not resolve -- held, see TODO.md",
    "UNNAMED": "stray Excel descriptive-statistics block in the sheet corner",
}


def main():
    r = requests.get(SUPP, timeout=600)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        d = pd.read_excel(io.BytesIO(z.read(MEMBER)))
    print(f"raw: {d.shape[0]} rows x {d.shape[1]} columns")

    # no id column in the deposit -- the row is the respondent
    assert not any(c.lower() in ("id", "no", "sn") for c in d.columns)
    d["id"] = range(1, len(d) + 1)

    for c in SENTINEL_NEG99:
        n = int((d[c] == -99).sum())
        d.loc[d[c] == -99, c] = pd.NA
        print(f"  {c}: {n} cells of -99 (not applicable) set missing")

    cov_names = []
    for src, name in COVS.items():
        d[name] = pd.to_numeric(d[src], errors="coerce")
        cov_names.append(name)

    # every source column must be an item, a covariate, or an explicit skip
    all_items = {c for cols in TABLES.values() for c in cols}
    for c in d.columns:
        if c in all_items or c in COVS or c in cov_names or c == "id":
            continue
        if str(c).startswith("Unnamed"):
            reason = SKIP["UNNAMED"]
        else:
            m = re.match(r"^([A-Za-z]+)\d+$", str(c))
            key = m.group(1) if m else str(c)
            assert key in SKIP, f"unaccounted source column: {c}"
            reason = SKIP[key]
        print(f"  skip {c}: {reason}")

    os.makedirs(OUTDIR, exist_ok=True)
    assert len(set(TABLES)) == len(TABLES)
    total = 0
    for table, items in TABLES.items():
        missing = [c for c in items if c not in d.columns]
        assert not missing, (table, missing)
        long = d.melt(id_vars=["id"] + cov_names, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_names]

        assert long["resp"].between(1, 5).all(), table
        assert not long.duplicated(["id", "item"]).any(), table
        assert long["item"].nunique() == len(items), table
        assert long["item"].nunique() > 1, table
        assert long["id"].nunique() >= 100, table
        assert long.groupby("item")["resp"].nunique().min() > 1, table

        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])
        for c in checks:
            if c.status == "warn":
                print(f"  [warn] {table}: {c.name}: {c.detail}")

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} x {n_it} = {len(long)} responses, "
              f"density {len(long) / (n_id * n_it):.3f}")

    print(f"\n{len(TABLES)} tables, {total} responses")


if __name__ == "__main__":
    main()
