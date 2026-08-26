"""Xu, Tang & Chang (2023), Harvard Dataverse -- working with AI: the impact
of organizational intelligent service.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/C51SE3
DOI: 10.7910/DVN/C51SE3
License: CC0 1.0

Three Chinese samples (223, 232 and 281 respondents) given overlapping sets
of short 7-point scales.

Tables written
--------------
xu_2023_hi    736 respondents x 5 items, 1-7  (studies 1-3)
xu_2023_mi    736 respondents x 5 items, 1-7  (studies 1-3)
xu_2023_pca   736 respondents x 6 items, 1-7  (studies 1-3)
xu_2023_oic   513 respondents x 6 items, 1-7  (studies 2-3)

Coding notes
------------
* **Samples are pooled per instrument, not shipped per study.** Each scale is
  the same item set on the same 1-7 format in every study that administered
  it, so the three studies become `cov_study` within one file per scale
  rather than three near-identical files. `id` is assigned across the pooled
  file and is not the study's own row number.
* Four tables because there are four scales; they are separate constructs
  measured with separate item sets, and `OIC` was not administered in study 1.
* **The scale names are left as the deposit's prefixes.** The deposit ships no
  codebook and the columns carry no labels, so `HI`, `MI`, `PCA` and `OIC`
  cannot be expanded without guessing; the source names are kept so the paper
  can supply item text later.
* `ISSS`, `ICSS`, `ISS` and `OIC` (the 0/1 column, distinct from the `OIC1..6`
  items) are single-item manipulation checks and condition flags, and
  `AVEHI`/`AVEMI`/`AVEPCA`/`AVEOIC` are the scale means.
* Study 3 carries one age of 368; that cell is blanked rather than shipped.
* No deposit-side identifier is usable: study 3's `序号` is a non-contiguous
  entry number with one duplicate, so row position is used throughout.
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

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/C51SE3"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
SCALES = {"HI": 5, "MI": 5, "PCA": 6, "OIC": 6}
COVS = {"Age": "cov_age", "age": "cov_age",
        "Gender": "cov_gender", "gender": "cov_gender",
        "Education": "cov_education", "education": "cov_education",
        "Income": "cov_income", "MonthlyIncome": "cov_income",
        "experience": "cov_ai_experience",
        "Experience": "cov_ai_experience",
        "AIusedexperience": "cov_ai_experience",
        "您从事工作的年限": "cov_years_experience"}
SKIP_EXACT = {"ISS", "OIC", "ISSS", "ICSS", "occupation", "序号"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    files = sorted(((f["dataFile"]["filename"], f["dataFile"]["id"])
                    for f in meta["files"]), key=lambda t: t[0])
    assert len(files) == 3, files

    frames, offset = {}, 0
    for study, (fname, fid) in enumerate(files, start=1):
        raw = s.get(f"{BASE}/api/access/datafile/{fid}",
                    params={"format": "original"}, timeout=600)
        raw.raise_for_status()
        path = f"/tmp/xu_2023_study{study}.sav"
        open(path, "wb").write(raw.content)
        d, _ = pyreadstat.read_sav(path)
        d["id"] = range(offset + 1, offset + len(d) + 1)
        offset += len(d)
        d["cov_study"] = study

        used = {"id", "cov_study"}
        for src, dest in COVS.items():
            if src in d.columns:
                d[dest] = d[src]
                used.add(src)
        if "cov_age" in d.columns:      # study 3 holds one age of 368
            bad_age = ~d["cov_age"].between(16, 90)
            if bad_age.any():
                print(f"  study {study}: blanking {bad_age.sum()} "
                      f"out-of-range age value(s)")
                d.loc[bad_age, "cov_age"] = pd.NA
        for scale, n in SCALES.items():
            items = [c for c in d.columns
                     if re.fullmatch(rf"{scale}\d+", str(c))]
            if not items:
                continue
            assert len(items) == n, (study, scale, items)
            used.update(items)
            frames.setdefault(scale, []).append(
                d[["id", "cov_study"] + sorted(set(COVS.values()) & set(d.columns))
                  + items])
        for c in d.columns:
            if c in used or c in set(COVS.values()):
                continue
            if c in SKIP_EXACT or str(c).startswith("AVE"):
                continue
            raise AssertionError(f"unaccounted column in {fname}: {c}")
        present = [k for k in SCALES
                   if any(re.fullmatch(rf"{k}\d+", str(c)) for c in d.columns)]
        print(f"  study {study} ({fname.strip()}): {len(d)} respondents, "
              f"scales {present}")

    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for scale, parts in frames.items():
        d = pd.concat(parts, ignore_index=True)
        items = [c for c in d.columns if re.fullmatch(rf"{scale}\d+", str(c))]
        long = d.melt(id_vars=[c for c in d.columns if c not in items],
                      value_vars=items, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]
                    + sorted(c for c in long.columns if c.startswith("cov_"))]

        assert long["resp"].between(1, 7).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (scale, [(c.name, c.detail) for c in bad])

        name = f"xu_2023_{scale.lower()}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} respondents x {n_it} items = {len(long)} "
              f"responses, density {len(long) / (n_id * n_it):.3f}, "
              f"studies {sorted(long['cov_study'].unique())}")
    print(f"\n{len(frames)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
