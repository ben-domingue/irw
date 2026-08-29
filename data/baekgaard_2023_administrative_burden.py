"""Administrative burden among Danish welfare recipients facing meetings.

Source: Baekgaard, M. & Madsen, J. K. (2023), Zenodo
10.5281/zenodo.7742956, CC BY 4.0 -- replication data for "Anticipated
administrative burdens: How proximity to upcoming compulsory meetings affect
welfare recipients' experiences". 2,645 respondents, already anonymised.

The .sav carries NO variable labels and no codebook: every item is an opaque
`s14`..`s77`. The item-to-subscale mapping is therefore RECOVERED FROM THE
DATA rather than guessed. The file ships six `*_add` composite columns, and
each turns out to be the arithmetic MEAN (not the sum) of a contiguous item
block -- verified exactly, to floating-point tolerance, on every complete
case:

  mastery_add       = mean(s14..s20)   7 items
  stress_add        = mean(s41..s44)   4 items
  autonomyloss_add  = mean(s45..s48)   4 items
  stigma_add        = mean(s49..s52)   4 items
  learning_add      = mean(s53..s55)   3 items
  compliance_add    = mean(s56..s58)   3 items

Six constructs, six tables: they share the 0-4 response format but measure
different objects (the respondent's own mastery, the stress of the meeting,
loss of autonomy, felt stigma, what was learned, and compliance), so one table
would make `resp` ambiguous about what is being rated.

The remaining 15 items (`s21`..`s32`, `s72`, `s75`, `s77`) belong to no
composite and carry no label, so there is nothing to name them by; they are
left unshipped rather than guessed at -- the same call made for the unnamed
blocks in `ysladomendez_2023_mbi`.
"""
import os

import numpy as np
import pandas as pd
import pyreadstat
import requests

RECORD = 7742956
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
PREFIX = "baekgaard_2023"

SCALE = {0.0, 1.0, 2.0, 3.0, 4.0}
# table suffix -> (composite column, item columns)
BLOCKS = {
    "mastery": ("mastery_add", [f"s{i}" for i in range(14, 21)]),
    "stress": ("stress_add", [f"s{i}" for i in range(41, 45)]),
    "autonomy_loss": ("autonomyloss_add", [f"s{i}" for i in range(45, 49)]),
    "stigma": ("stigma_add", [f"s{i}" for i in range(49, 53)]),
    "learning": ("learning_add", [f"s{i}" for i in range(53, 56)]),
    "compliance": ("compliance_add", [f"s{i}" for i in range(56, 59)]),
}
COVARIATES = {
    "age": "cov_age",
    "gender": "cov_gender",
    "cohabitant": "cov_cohabitant",
    "Meetingattendance": "cov_meeting_attendance",
}


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
    df, _meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)

    d = df.rename(columns=COVARIATES).copy()
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for suffix, (comp, cols) in BLOCKS.items():
        missing = [c for c in cols if c not in df.columns]
        assert not missing, f"{suffix}: missing {missing}"

        observed = {v for v in pd.unique(df[cols].values.ravel())
                    if pd.notna(v)}
        assert observed <= SCALE, \
            f"{suffix}: off-scale response(s) {sorted(observed - SCALE)}"

        # The mapping is only trustworthy because the composite reproduces
        # exactly; re-check it at run time so a changed file cannot pass.
        m = df[cols].notna().all(axis=1) & df[comp].notna()
        assert m.sum() > 0, f"{suffix}: no complete cases to verify against"
        assert np.allclose(df.loc[m, cols].mean(axis=1).values,
                           df.loc[m, comp].values, atol=1e-9), \
            f"{suffix}: {comp} is not the mean of {cols}"

        long = d.melt(id_vars=["id"] + list(COVARIATES.values()),
                      value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)

        table = f"{PREFIX}_{suffix}"
        out = long[["id", "item", "resp"] + list(COVARIATES.values())]
        out.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        total += len(out)
        print(f"{table}: {len(out):,} responses | {out['id'].nunique():,} ids | "
              f"{out['item'].nunique()} items")
    print(f"total: {total:,}")


if __name__ == "__main__":
    main()
