"""Köksal (2023), Mendeley Data -- work-related depression, psychological
capital and life satisfaction.

Source: https://data.mendeley.com/datasets/zhcyyxwpr6
DOI: 10.17632/zhcyyxwpr6
License: CC BY 4.0

281 Turkish employees completing the four PsyCap subscales, a life
satisfaction scale, and a short work-related depression checklist.

Tables written
--------------
koksal_2023_psycap                281 x 24 items, 1-6
koksal_2023_life_satisfaction     281 x  5 items, 1-7
koksal_2023_work_depression       281 x  6 items, 1-5

Coding notes
------------
* **Three tables on three response scales.** Psychological Capital is one
  24-item instrument with four six-item subscales -- optimism (`IYMSRLK`),
  resilience (`PDYNK`), hope (`UMUT`) and self-efficacy (`OZYTRLK`) -- all on
  1-6, so it ships as one table with `itemcov_subscale`. Life satisfaction
  (`YSMDYM`) is 1-7 and the depression checklist is 1-5, so each is separate;
  differing response scales are never pooled.
* The depression items are named for their Turkish adjectives (`KARAMSAR`
  pessimistic, `ACINASI` wretched, `UMUTSUZ` hopeless, `ENDISELI` worried,
  `GERGIN` tense, `HUZURSUZ` restless) rather than numbered.
* Source column order interleaves `UMUT4`/`UMUT5`/`UMUT6` before `UMUT3` and
  `OZYTRLK6` before `OZYTRLK3`; items are sorted by number so the item ids
  match the published instrument.
* The seven trailing columns (`PskSrm_ort`, `DEPRESYON`, `YASAM_DOYUMU`,
  `OZ_YETERLİLİK`, `UMUT`, `PSK_DAYANK`, `IYIMSERLİK`) are scale means.
* `s.nu` is the deposit's own case number and is used as `id`.
"""

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/zhcyyxwpr6"
DATASET, VERSION = "zhcyyxwpr6", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"Yas": "cov_age", "Cinsiyet": "cov_sex", "Egitim": "cov_education",
        "Yıl": "cov_tenure_years", "Çalışma": "cov_employment"}
PSYCAP = {"IYMSRLK": "optimism", "PDYNK": "resilience",
          "UMUT": "hope", "OZYTRLK": "self_efficacy"}
DEPRESSION = ["KARAMSAR", "ACINASI", "UMUTSUZ", "ENDISELI", "GERGIN",
              "HUZURSUZ"]
SKIP = {"PskSrm_ort", "DEPRESYON", "YASAM_DOYUMU", "OZ_YETERLİLİK",
        "UMUT", "PSK_DAYANK", "IYIMSERLİK"}


def ship(long, name, lo, hi, extra=()):
    assert long["resp"].between(lo, hi).all(), (
        name, long["resp"].min(), long["resp"].max())
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, (name, [(c.name, c.detail) for c in bad])
    path = os.path.join(OUTDIR, f"{name}.csv")
    assert not os.path.exists(path), name
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} employees x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long) / (n_id * n_it):.3f}")
    return len(long)


def main():
    s = requests.Session()
    s.headers.update(UA)
    listing = s.get(f"https://data.mendeley.com/public-api/datasets/"
                    f"{DATASET}/files?folder_id=root&version={VERSION}",
                    timeout=120).json()
    hit = [f for f in listing if f["filename"].lower().endswith(".sav")]
    assert len(hit) == 1, [f["filename"] for f in listing]
    raw = s.get(hit[0]["content_details"]["download_url"], timeout=600)
    raw.raise_for_status()
    open("/tmp/koksal_psycap.sav", "wb").write(raw.content)
    d, _ = pyreadstat.read_sav("/tmp/koksal_psycap.sav")

    d = d.rename(columns={"s.nu": "id", **COVS})
    covs = list(COVS.values())
    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0

    items, sub_of = [], {}
    for prefix, label in PSYCAP.items():
        cols = sorted([c for c in d.columns
                       if re.fullmatch(rf"{prefix}\d+", str(c))],
                      key=lambda c: int(re.sub(r"\D", "", c)))
        assert len(cols) == 6, (prefix, cols)
        items += cols
        sub_of.update({c: label for c in cols})
    shipped.update(items)
    long = d.melt(id_vars=["id"] + covs, value_vars=items,
                  var_name="item", value_name="resp")
    long["itemcov_subscale"] = long["item"].map(sub_of)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    total += ship(long[["id", "item", "resp", "itemcov_subscale"] + covs],
                  "koksal_2023_psycap", 1, 6)

    for name, cols, lo, hi in [
            ("koksal_2023_life_satisfaction",
             sorted([c for c in d.columns if re.fullmatch(r"YSMDYM\d+", str(c))],
                    key=lambda c: int(re.sub(r"\D", "", c))), 1, 7),
            ("koksal_2023_work_depression", DEPRESSION, 1, 5)]:
        assert cols, name
        shipped.update(cols)
        long = d.melt(id_vars=["id"] + covs, value_vars=cols,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        total += ship(long[["id", "item", "resp"] + covs], name, lo, hi)

    for c in d.columns:
        if c in shipped or c in covs or c == "id":
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: scale mean")
    print(f"\n3 tables, {total:,} responses")


if __name__ == "__main__":
    main()
