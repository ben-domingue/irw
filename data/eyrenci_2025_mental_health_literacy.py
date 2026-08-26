"""Eyrenci & Öztürk Turgut (2025), Mendeley Data -- mental health literacy.

Source: https://data.mendeley.com/datasets/dmv73kyjdp
DOI: 10.17632/dmv73kyjdp
License: CC BY 4.0

240 Turkish adults answering a 22-item mental-health-literacy knowledge
scale, scored right/wrong.

Tables written
--------------
eyrenci_2025_mental_health_literacy   240 respondents x 22 items, 0/1

Coding notes
------------
* Knowledge rather than self-report: `resp` is 0/1 correctness on `y1`..`y22`.
* `ters11`..`ters18` are the reverse-scored copies of `y11`..`y18` -- verified
  `ters_n == 1 - y_n` for all eight -- and are not shipped, since they are
  derived rather than administered.
* `bilgiodak`, `kaynakodak` and `RSOYtop` are scored subscale and total
  scores.
* `olguno` is the deposit's case number but repeats for one pair of rows, so
  `id` is row position rather than that column.
* Several free-text clinical columns (`hastur` current illnesses,
  `hasturpsi` psychiatric diagnoses, `psitedaviilac` treatments,
  `calısmayer` occupation) are **not** shipped as covariates. They contain no
  names or contact details, so the deposit is not excluded, but free-text
  health descriptions are not worth carrying into the warehouse as
  covariates.
"""

import os
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/dmv73kyjdp"
DATASET, VERSION = "dmv73kyjdp", 1
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "eyrenci_2025_mental_health_literacy"

ITEMS = [f"y{i}" for i in range(1, 23)]
COVS = {"yas": "cov_age", "cisn": "cov_sex", "egitim": "cov_education",
        "medeni": "cov_marital_status", "cocuk": "cov_has_children",
        "cocuksayı": "cov_n_children", "calısma": "cov_employment",
        "baskafizhas": "cov_physical_illness",
        "baskapsik": "cov_psychiatric_history",
        "saglıkcalısan": "cov_health_worker"}
SKIP_EXACT = {
    "olguno": "deposit case number, not unique across rows",
    "bilgiodak": "scored subscale total",
    "kaynakodak": "scored subscale total",
    "inancodak": "scored subscale total",
    "RSOYtop": "scored total",
    "hasturzaman": "duration of illness, free-text coded",
    "psitedavi": "received psychiatric treatment, free-text coded",
    "int": "information source: internet",
    "tv": "information source: television",
    "gazete": "information source: newspaper",
    "herhangi": "information source: any",
    "tanı": "diagnosis grouping",
    "geliryeni": "recoded income band",
    "yeryeni": "recoded residence",
    "calısmayer": "free-text occupation",
    "hastur": "free-text current illnesses",
    "hasturpsi": "free-text psychiatric diagnoses",
    "psitedaviilac": "free-text treatments",
}


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
    open("/tmp/eyrenci_mhl.sav", "wb").write(raw.content)
    d, _ = pyreadstat.read_sav("/tmp/eyrenci_mhl.sav")

    assert set(ITEMS) <= set(d.columns), sorted(set(ITEMS) - set(d.columns))
    # the ters* columns must be derived, or they would be separate responses
    for i in range(11, 19):
        assert (d[f"ters{i}"] == 1 - d[f"y{i}"]).all(), i

    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    covs = sorted(set(COVS.values()))

    long = d.melt(id_vars=["id"] + covs, value_vars=ITEMS,
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

    n_rev = 0
    for c in d.columns:
        if c in ITEMS or c in covs or c == "id":
            continue
        if str(c).startswith("ters"):
            n_rev += 1
            continue
        assert c in SKIP_EXACT, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP_EXACT[c]}")
    print(f"  skip {n_rev} ters* columns: reverse-scored copies of y11-y18")

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} respondents x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}, "
          f"mean correct {long['resp'].mean():.3f}")


if __name__ == "__main__":
    main()
