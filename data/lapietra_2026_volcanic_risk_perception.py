"""Volcanic risk perception in the 43 municipalities around Vesuvius.

Source: Lapietra, I., Mele, D. & Dellino, P. (2026), Zenodo
10.5281/zenodo.19473011, CC BY 4.0 -- "Variables and indicators of volcanic
risk perception in the Vesuvius area". 10,905 respondents across three survey
samples.

One table: the 15 questionnaire items (`Q1r1`..`Q1r4`, `Q2`..`Q12`), every one
on the same 1-5 ordinal scale with no missing cells. `Q1` is a four-row matrix
question, hence its `r1..r4` suffixes.

The person key is (`sample`, `record`), NOT `record` alone: `record` restarts
within each of the three samples and repeats 512 times across the file. Using
it by itself would silently merge 512 pairs of different respondents -- the
1.04 density that triage flagged.

The `S1`..`S25` block holds the survey's demographic and control variables,
but the deposit ships no codebook and the columns are unlabelled, so they are
NOT emitted as covariates: naming them would be guesswork. `Municipality` and
`sample` are labelled in the data itself and do ship.
"""
import os

import pandas as pd
import requests

RECORD = 19473011
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "lapietra_2026_volcanic_risk_perception"

ITEMS = ["Q1r1", "Q1r2", "Q1r3", "Q1r4"] + [f"Q{i}" for i in range(2, 13)]
SCALE = {1, 2, 3, 4, 5}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".xlsx"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))

    missing = [c for c in ITEMS if c not in df.columns]
    assert not missing, f"missing item columns: {missing}"

    observed = {int(v) for v in pd.unique(df[ITEMS].values.ravel())
                if pd.notna(v)}
    assert observed <= SCALE, f"off-scale response(s): {sorted(observed - SCALE)}"

    # record repeats across samples; the pair is the person.
    assert not df.duplicated(["sample", "record"]).any(), \
        "(sample, record) is not unique -- person key is wrong"
    d = df.copy()
    d["id"] = d["sample"].astype(int).astype(str) + "_" + \
        d["record"].astype(int).astype(str)
    d["cov_municipality"] = d["Municipality"].astype(str)
    d["cov_sample"] = d["sample"].astype(int)

    long = d.melt(id_vars=["id", "cov_municipality", "cov_sample"],
                  value_vars=ITEMS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)

    out = long[["id", "item", "resp", "cov_municipality", "cov_sample"]]
    os.makedirs(OUT_DIR, exist_ok=True)
    out.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(out):,} responses | {out['id'].nunique():,} ids | "
          f"{out['item'].nunique()} items")


if __name__ == "__main__":
    main()
