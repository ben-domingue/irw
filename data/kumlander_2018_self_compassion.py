"""Self-Compassion Scale (SCS) and BDI-13, two Finnish samples.

Source: Kumlander, Lahtinen et al. (2018), figshare 10.6084/m9.figshare.7426262,
CC BY 4.0 -- supporting data for "Two is more valid than one, but is six even
better? The factor structure of the Self-Compassion Scale (SCS)", PLOS ONE
13(12): e0207706.

Two instruments ship, both from the FIRST wave only:

  kumlander_2018_scs   26 SCS items, 1-5
  kumlander_2018_bdi   13 items of the revised (Raitasalo) BDI, 1-5

**Only `pone.0207706.s006.sav` (n=1,742) is used. `s007.sav` (n=1,497) is a
second measurement wave of the same cohort, not an independent sample** -- its
SPSS variable labels read "Beck Depression Inventory, revised, 1, wave 2", and
every column carries a `_2` suffix against the first file's `_1`. The drop from
1,742 to 1,497 is consistent with attrition.

Neither file carries a respondent identifier, so the waves cannot be joined:
`wave` requires the same `id` on both occasions, and there is no key to build
one. Shipping the second file as additional rows would present ~1,497 repeat
measurements as ~1,497 additional people, inflating the person count by 86%
and breaking the independence any IRT model fitted to the table would assume.
The wave-2 responses are therefore left out rather than misrepresented; they
are recoverable if the authors can supply a linking id.

Two further things in the source that must not reach the output:

* **-999 and -888 are missing codes**, not responses. Melting without
  converting them would put -999 into `resp` on a 1-5 scale.
* **The `scomp*_R` columns are reverse-scored recodes** of the items the SCS
  reverse-keys. They are dropped as derived; the raw responses ship.

`VAR00002` is the respondent's birth year, kept as a covariate.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

ARTICLE = 7426262
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

MISSING_CODES = {-999.0, -888.0}


def fetch_raw(out_dir=None):
    meta = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                        timeout=120).json()
    paths = {}
    for f in meta["files"]:
        if not f["name"].lower().endswith(".sav"):
            continue
        local = os.path.join(out_dir or "/tmp", f["name"])
        if not os.path.exists(local):
            r = requests.get(f["download_url"], timeout=600)
            r.raise_for_status()
            with open(local, "wb") as fh:
                fh.write(r.content)
        paths[f["name"]] = local
    return paths


def read_sav(p):
    try:
        return pyreadstat.read_sav(p, apply_value_formats=False)[0]
    except Exception:
        return pyreadstat.read_sav(p, apply_value_formats=False,
                                   encoding="latin1")[0]


def main(paths=None):
    paths = paths or fetch_raw()
    s1 = read_sav(next(v for k, v in paths.items() if "s006" in k))

    frames, id_offset = [], 0
    for sample, df in (("sample1", s1),):
        suffix = sample[-1]
        rename = {}
        for c in df.columns:
            m = re.match(rf"^(scomp\d+|bdi\d+)_{suffix}$", str(c))
            if m:
                rename[c] = m.group(1)
        df = df.rename(columns=rename)
        for c in ("stype", "gender", "rgender", "VAR00002"):
            for cand in (f"{c}_{suffix}", c):
                if cand in df.columns:
                    df = df.rename(columns={cand: {
                        "stype": "cov_student_type",
                        "gender": "cov_gender", "rgender": "cov_gender",
                        "VAR00002": "cov_birth_year"}[c]})
                    break
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1 + id_offset
        id_offset = int(df["id"].max())
        frames.append(df)

    specs = {
        "kumlander_2018_scs": (r"^scomp\d+$", 26, (1, 5)),
        # The revised (Raitasalo) BDI used here is scored 1-5, not 0-3.
        "kumlander_2018_bdi": (r"^bdi\d+$", 13, (1, 5)),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (pat, n_items, (lo, hi)) in specs.items():
        parts = []
        for df in frames:
            cols = [c for c in df.columns if re.match(pat, str(c))]
            assert len(cols) == n_items, \
                f"{table}: expected {n_items} items, found {len(cols)}"
            covs = [c for c in df.columns if str(c).startswith("cov_")]
            parts.append(df.melt(id_vars=["id"] + covs, value_vars=cols,
                                 var_name="item", value_name="resp"))
        long = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
        # Sentinel missing codes, not responses.
        long = long[~long["resp"].isin(MISSING_CODES)]
        long["resp"] = long["resp"].astype(int)
        covs = sorted(c for c in long.columns
                      if str(c).startswith("cov_"))
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == n_items, table
        assert long["resp"].between(lo, hi).all(), \
            f"{table}: expected {lo}-{hi}, saw " \
            f"{long['resp'].min()}-{long['resp'].max()}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
