"""Bialowolski (2024), Harvard Dataverse -- financial literacy in a gendered
language context (Poland).

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MTQGSF
DOI: 10.7910/DVN/MTQGSF
License: CC0 1.0

4,389 Polish adults answering an 18-item financial-literacy test, scored
right/wrong. Achievement rather than self-report, which is the gap the
2026-08-25 educational-measurement term list was added to fill.

Tables written
--------------
bialowolski_2024_financial_literacy   4,389 respondents x 18 items, 0/1

Coding notes
------------
* The Stata labels read "Poprawność odpowiedzi : FL_n" -- *correctness of the
  answer* -- so `resp` is 0/1 scoring, not the chosen option. The chosen
  options are not deposited.
* Item numbering runs FL_1..FL_19 with FL_18 absent from the file; the source
  names are kept as-is rather than renumbered, so item text can join.
* **Demographics are deposited only as dummy expansions**, one indicator per
  category with the modal category dropped as the regression reference. Each
  set is reconstructed back into a single ordinal covariate by taking the
  index of the indicator that is 1, and the omitted index where none is --
  which is exactly the reference category. The recovered codes are the
  survey's own, in the survey's own order; the Polish category labels are in
  the Stata variable labels of the dummies.
* `finresp` (a -4..5 financial-responsibility index) and the six `sex*ver*`
  columns (the experiment's grammatical-gender manipulation, applied to the
  *wording* rather than answered by the respondent) are not covariates of the
  test-taking and are skipped.
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/MTQGSF"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "bialowolski_2024_financial_literacy"

# prefix -> (covariate name, omitted reference index)
DUMMY_SETS = {
    "age":     ("cov_age_group",      2),
    "edu":     ("cov_education",      3),
    "marit":   ("cov_marital_status", 3),
    "labor":   ("cov_employment",     2),
    "profile": ("cov_field",          2),
    "income":  ("cov_income",         3),
    "nop":     ("cov_hhsize",         2),
    "place":   ("cov_residence",      5),
}
SKIP = {
    "finresp": "derived financial-responsibility index",
    "sexmverm": "grammatical-gender wording manipulation, not a response",
    "sexmverf": "grammatical-gender wording manipulation, not a response",
    "sexmveru": "grammatical-gender wording manipulation, not a response",
    "sexfverm": "grammatical-gender wording manipulation, not a response",
    "sexfverf": "grammatical-gender wording manipulation, not a response",
    "sexfveru": "grammatical-gender wording manipulation, not a response",
}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"] == "for_replication.tab"]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    d = pd.read_stata(io.BytesIO(raw.content), convert_categoricals=False)

    items = [c for c in d.columns if c.startswith("FL_")]
    assert len(items) == 18, sorted(items)
    d["id"] = range(1, len(d) + 1)

    used = set(items) | {"male"}
    d["cov_male"] = d["male"].astype(int)
    covs = ["cov_male"]
    for prefix, (name, ref) in DUMMY_SETS.items():
        cols = sorted([c for c in d.columns
                       if c.startswith(prefix) and c[len(prefix):].isdigit()],
                      key=lambda c: int(c[len(prefix):]))
        assert cols, prefix
        idx = [int(c[len(prefix):]) for c in cols]
        assert ref not in idx, (prefix, ref, idx)
        block = d[cols].astype(int)
        assert block.sum(axis=1).max() <= 1, prefix
        d[name] = block.mul(idx, axis=1).sum(axis=1).replace(0, ref)
        used.update(cols)
        covs.append(name)
        print(f"  {name}: categories {sorted(set(idx) | {ref})} "
              f"(reference {ref} recovered from all-zero rows)")

    long = d.melt(id_vars=["id"] + covs, value_vars=items,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["resp"].isin([0, 1]).all()
    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["resp"].nunique().min() > 1
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]
    for c in checks:
        if c.status == "warn":
            print(f"  [warn] {c.name}: {c.detail}")

    for c in d.columns:
        if c in used or c in covs or c == "id":
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP[c]}")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} respondents x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}, "
          f"mean correct {long['resp'].mean():.3f}")


if __name__ == "__main__":
    main()
