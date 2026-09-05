#!/usr/bin/env python3
"""McAuliffe, Bangayan, Callaghan et al. (2025), Communications Psychology --
third-party punishment of unfair sharing in children across six societies.

Article: https://www.nature.com/articles/s44271-025-00220-x
DOI: 10.1038/s44271-025-00220-x
Data: https://osf.io/6nm2s/ (view-only link, token below)
License: CC BY 4.0 (the OSF node's own license record, checked 2026-09-04)
Issue: #949

535 children at seven field sites in six countries each saw 12 allocations
between two third parties and chose to accept it or to reject it (destroying
the allocation). Half the trials showed an equal 3-3 split, half an unequal
6-0 split, and rejecting an unequal split is the third-party punishment the
paper is about. In the `Costly` condition rejecting cost the child a resource
of their own; in the `Free` condition it did not.

One table, not six. The deposit ships one CSV per country, but the design,
the trial count and the response scale are identical across them and the
paper's own analysis rbinds them into a single frame -- so they are pooled
here with `cov_site` and `cov_country` carrying the split, per #949.

**Two items, twelve trials.** The source is wide with a pair of columns per
trial: `tN.dist` is the allocation the child was shown (`E` equal 3-3, `U`
unequal 6-0) and `tN.dec` is what they did (`A` accept, `R` reject). The
allocation is the stimulus, so it becomes `item`; the decision becomes
`resp`, coded 1 = reject/punish and 0 = accept, matching the `punish`
variable the paper's script builds. Each child therefore answers each of the
two items about six times, and `wave` holds the trial position 1-12 that
separates those repeats. There is no unique id/item key without it.

**Vanuatu ages are the superseded ones, and are floored for that reason.**
The paper's analysis script reads `tpix.vanuatu.age.corrected.csv`, a file
that was never deposited -- OSF has only `tpix.vanuatu.csv`, and its comment
at the `age.year.simple` block says the author "corrected the error in the
vanuatu ages". The error is visible: 16 Vanuatu children carry `age.year`
values of 8.5, 8.6, ... 8.9, 8.1, 8.11 ... 8.17 on consecutive rows, which is
a running counter within an age, not an age. So `cov_age` ships as
`floor(age.year)`, which is exactly the paper's own `age.year.simple`
recode, and every one of the 535 floored values falls inside the source's
independently-recorded `age.group` band -- asserted on every build. The
sub-year part is dropped rather than published, since for these 16 it is
meaningless and for the rest `cov_age_exact` carries a real decimal age
anyway.

`cov_age_exact` is the source's `age.calc` and exists only for Canada, India,
Peru and the USA; Uganda and Vanuatu recorded `.` for every child.

**Two cells in the source are uninterpretable and are dropped:**
`uganda.69` trial 12 and `usa.55` trial 2 hold a distribution code (`U`, `E`)
in the *decision* column. There is no way to recover what the child did, so
those two responses are dropped alongside the `.` missings.

Not reproduced here: the paper's reshape lists `t11` twice and omits `t10`
(lines 30-45 of the OSF script), so its long frames are missing trial 10.
That is a bug in the analysis, not in the data; all 12 trials are kept.
"""
from __future__ import annotations

import math
import os
import re
import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = Path(__file__).resolve().parent
RAW = BASE / "mcauliffe_2025_thirdpartypunishment_raw"
OUT = BASE.parent / "automated_finding" / "irw_output"

VIEW_ONLY = "83989fdb987d428dabf796df541b7829"
OSF_LIST = ("https://api.osf.io/v2/nodes/6nm2s/files/osfstorage/"
            f"?view_only={VIEW_ONLY}&page%5Bsize%5D=100")

TABLE = "mcauliffe_2025_thirdpartypunishment"

# tN.dist -> item.  The source's own vocabulary is equal / unequal (`eq.uneq`).
DIST = {"E": "equal_3_3", "U": "unequal_6_0"}
# tN.dec -> resp.  1 = reject the allocation = third-party punishment.
DEC = {"A": 0, "R": 1}
GENDER = {"F": "Female", "M": "Male"}
# Two Vanuatu field sites; every other site is its own country.
COUNTRY = {"Vanuatu_Efate": "Vanuatu", "Vanuatu_Tanna": "Vanuatu"}

N_TRIALS = 12


def fetch() -> list[Path]:
    """Download the six per-country CSVs from OSF, cached on disk."""
    RAW.mkdir(parents=True, exist_ok=True)
    import json
    with urllib.request.urlopen(OSF_LIST) as fh:
        listing = json.load(fh)
    paths = []
    for entry in listing["data"]:
        name = entry["attributes"]["materialized_path"].lstrip("/")
        if not name.endswith(".csv"):
            continue
        dest = RAW / name
        if not dest.exists():
            urllib.request.urlretrieve(entry["links"]["download"], dest)
        paths.append(dest)
    if len(paths) != 6:
        raise RuntimeError(f"expected 6 country CSVs on OSF, found {len(paths)}")
    return sorted(paths)


def _age_group_bounds(label: str) -> tuple[int, int]:
    lo, hi = re.search(r"\((\d+)-(\d+)\)", label).groups()
    return int(lo), int(hi)


def build() -> pd.DataFrame:
    wide = pd.concat([pd.read_csv(p, encoding="utf-8-sig", dtype=str)
                      for p in fetch()], ignore_index=True)

    assert wide["new.id"].notna().all(), "new.id has nulls"
    assert wide["new.id"].nunique() == len(wide), \
        f"new.id not unique: {wide['new.id'].nunique()} of {len(wide)}"

    age_year = pd.to_numeric(wide["age.year"], errors="coerce")
    assert age_year.notna().all(), "age.year has non-numeric values"
    cov_age = age_year.apply(math.floor).astype(int)

    # The floor is only safe because an independent column agrees with it.
    for aid, group, value in zip(wide["new.id"], wide["age.group"], cov_age):
        lo, hi = _age_group_bounds(group)
        if not lo <= value <= hi:
            raise RuntimeError(
                f"{aid}: floor(age.year)={value} outside age.group {group!r}")

    people = pd.DataFrame({
        "id": wide["new.id"],
        "cov_age": cov_age,
        "cov_age_exact": pd.to_numeric(wide["age.calc"], errors="coerce"),
        "cov_age_group": wide["age.group"],
        "cov_gender": wide["gender"].str.strip().map(GENDER),
        "cov_condition": wide["condition"].str.strip(),
        "cov_site": wide["site"].str.strip(),
    })
    people["cov_country"] = people["cov_site"].map(
        lambda s: COUNTRY.get(s, s))
    assert people["cov_gender"].notna().all(), "unmapped gender code"
    assert set(people["cov_condition"]) == {"Costly", "Free"}, \
        f"unexpected conditions: {sorted(set(people['cov_condition']))}"

    trials = []
    dropped = {"missing": 0, "uninterpretable": []}
    for trial in range(1, N_TRIALS + 1):
        dist = wide[f"t{trial}.dist"].fillna(".").str.strip()
        dec = wide[f"t{trial}.dec"].fillna(".").str.strip()
        block = people.copy()
        block["item"] = dist.map(DIST).values
        block["resp"] = dec.map(DEC).values
        block["wave"] = trial
        keep = block["item"].notna() & block["resp"].notna()
        for aid, d, c in zip(wide["new.id"][~keep], dist[~keep], dec[~keep]):
            if d == "." or c == ".":
                dropped["missing"] += 1
            else:
                dropped["uninterpretable"].append((aid, trial, d, c))
        trials.append(block[keep])

    long = pd.concat(trials, ignore_index=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_age", "cov_age_exact",
                 "cov_age_group", "cov_gender", "cov_condition", "cov_site",
                 "cov_country"]]
    long = long.sort_values(["id", "wave"], kind="stable").reset_index(drop=True)

    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"sites={long['cov_site'].nunique()}")
    print(f"  of {len(wide) * N_TRIALS} possible responses: "
          f"{dropped['missing']} missing, "
          f"{len(dropped['uninterpretable'])} uninterpretable "
          f"{dropped['uninterpretable']}")
    print("  resp:", long["resp"].value_counts().to_dict())
    print("  item:", long["item"].value_counts().to_dict())
    return long


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    long = build()

    assert long["resp"].isin([0, 1]).all()
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    path = OUT / f"{TABLE}.csv"
    long.to_csv(path, index=False)
    print("wrote", path)


if __name__ == "__main__":
    main()
