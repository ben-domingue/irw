"""Arabacı & Akça (2025), Harvard Dataverse -- task diversity, skill diversity,
burnout and turnover intention.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/QBUOHG
DOI: 10.7910/DVN/QBUOHG
License: CC0 1.0

200 employees completing four short scales, all on the same 1-5 format.

Tables written
--------------
arabaci_2025_task_diversity       200 x 3 items, 1-5
arabaci_2025_skill_diversity      200 x 4 items, 1-5
arabaci_2025_burnout              200 x 7 items, 1-5
arabaci_2025_turnover_intention   200 x 3 items, 1-5

Coding notes
------------
* Four tables because there are four named constructs; the shared 1-5 format
  does not make them one instrument. The source column names carry the
  construct name directly ("Burnout1", "Task Diversity1", ...), which is what
  the split follows.
* **The workbook's 201st row is a codebook legend, not a respondent** -- it
  spells out "1= Strongly disagree; 5=Strongly agree" in every item column and
  the demographic codings in the others. It is asserted and dropped, leaving
  200 respondents. (Dataverse's `.tab` conversion drops it too, by coercing it
  to missing, but silently; the `.xlsx` original is read so the drop is
  explicit and the legend is available as documentation.)
* From that legend: `cov_sex` 1=male 2=female; `cov_age_band`
  1=20-29 2=30-39 3=40-49 4=50+; `cov_marital_status` 1=married 2=single;
  `cov_education` 1=elementary 2=high school 3=associate 4=undergraduate;
  `cov_experience` 1=0-5 2=6-10 3=11-15 4=16-20 5=20+ years.
* The deposit carries no identifier column, so `id` is row position.
"""

import io
import os
import re
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/QBUOHG"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
SCALES = [("Task Diversity", "task_diversity", 3),
          ("Skill Diversity", "skill_diversity", 4),
          ("Burnout", "burnout", 7),
          ("Turnover Intention", "turnover_intention", 3)]
COVS = {"Sex": "cov_sex", "Age": "cov_age_band",
        "Marital status": "cov_marital_status",
        "Educational level": "cov_education",
        "Working experience (years)": "cov_experience"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].lower().endswith(".xlsx")]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    d = pd.read_excel(io.BytesIO(raw.content))
    # the workbook's last row is a codebook legend, not a respondent
    legend = d.iloc[-1]
    assert str(legend["Sex"]).startswith("1=male"), legend["Sex"]
    assert str(legend["Burnout1"]).startswith("1= Strongly disagree"), legend
    print("  dropped the trailing legend row; response scale per the "
          "workbook itself: 1 = strongly disagree .. 5 = strongly agree")
    d = d.iloc[:-1].reset_index(drop=True)
    assert len(d) == 200 and d.notna().all().all(), d.shape
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for prefix, suffix, n_expected in SCALES:
        items = [c for c in d.columns
                 if re.fullmatch(rf"{prefix}\d+", str(c))]
        assert len(items) == n_expected, (suffix, items)
        shipped.update(items)

        long = d.melt(id_vars=["id"] + list(COVS), value_vars=items,
                      var_name="item", value_name="resp")
        long = long.rename(columns=COVS)
        long["item"] = long["item"].str.replace(" ", "", regex=False)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + list(COVS.values())]

        assert long["resp"].between(1, 5).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"arabaci_2025_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} employees x {n_it} items = {len(long)} "
              f"responses, density {len(long) / (n_id * n_it):.3f}")

    for c in d.columns:
        assert c in shipped or c in COVS or c == "id", (
            f"unaccounted source column: {c}")
    print(f"\n{len(SCALES)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
