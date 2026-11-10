#!/usr/bin/env python3
# Source: https://www.psycharchives.org/handle/20.500.12034/8195 (data item)
# DOI: 10.23668/psycharchives.12668
#   Fezzey, T. (2023). "Datasets for: All The Working World's A Stage:
#   Narcissism, Work Values, and Vocational Preferences." PsychArchives.
# Data: Dataset.csv (386 rows x 160 columns; online sample of full-time US
#   employees) + Codebook.csv (construct -> item column). narc_revision.csv in
#   the same item (385 rows, no header row) is a later working copy and is
#   not used.
# License: CC BY 4.0 (dc.rights.uri on the PsychArchives item).
#
# Checked against the abstract: "an online sample of 386 full-time U.S.
#   employees" -- 386 rows (matches).
#
# Item text: not shipped -- the deposit has codes and construct names only
#   (Codebook.csv), no wording. NARQ (Back et al. 2013), the O*NET Interest
#   Profiler / RIASEC items and the work-values items are published
#   instruments; wording would come from their sources.
#
# Tables:
#   fezzey_2023_narq            NARC_1-18, 1-6 (admiration 1-9, rivalry 10-18;
#                               one instrument, one table)
#   fezzey_2023_riasec60        RIASEC_1-60, 1-4 ("Supplemental RIASEC ONET
#                               60 items" in the codebook)
#   fezzey_2023_voc_interests   54 Voc_Interests_<n>_<RIASEC letter> items, 1-5
#                               (9 per Holland type; the code keeps the type)
#   fezzey_2023_work_values     20 WV<n>_<value> items, 1-7 (achievement,
#                               status, altruism, safety, comfort, autonomy)
# -99 (missing) dropped: 4 cells.
# Dropped columns: Duration__in_seconds_, ResponseId (Qualtrics response id,
#   replaced by the row index); Ethnicity, Work_status, Edu, Income and
#   Gender are numeric codes with no labels in the deposit.
# Covariates: cov_age.
# irw_lint_covariates.py reports WV4_status / WV5_status / WV12_status as
#   "marital_status" covariates: a false positive on the word "status". They
#   are the codebook's three "Status" work-value items, 1-7 like the rest.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://www.psycharchives.org/rest/bitstreams/"
            "b61dec13-0a79-48ac-b557-a441ec0dc52f/retrieve")
SCALES = {
    "fezzey_2023_narq": (re.compile(r"^NARC_\d+$"), set(range(1, 7)), 18),
    "fezzey_2023_riasec60": (re.compile(r"^RIASEC_\d+$"), set(range(1, 5)), 60),
    "fezzey_2023_voc_interests": (re.compile(r"^Voc_Interests_\d+_[RIASEC]$"), set(range(1, 6)), 54),
    "fezzey_2023_work_values": (re.compile(r"^WV\d+_[a-z]+$"), set(range(1, 8)), 20),
}
DROP = {"Duration__in_seconds_", "ResponseId", "Ethnicity", "Work_status",
        "Edu", "Income", "Gender", "Age"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), encoding="utf-8-sig")
    assert d.shape == (386, 160), d.shape
    d = d.reset_index(drop=True).copy()
    d = pd.concat([pd.DataFrame({"id": d.index + 1, "cov_age": d["Age"]}), d], axis=1)

    used = set()
    for table, (pat, allowed, n) in SCALES.items():
        cols = [c for c in d.columns if pat.match(c)]
        assert len(cols) == n, (table, len(cols))
        used |= set(cols)
        long = d.melt(id_vars=["id", "cov_age"], value_vars=cols,
                      var_name="item", value_name="resp")
        long = long[long["resp"] != -99].dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - allowed, (table, set(long["resp"]) - allowed)
        long = long[["id", "item", "resp", "cov_age"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
    left = set(d.columns) - used - DROP - {"id", "cov_age"}
    assert not left, left


if __name__ == "__main__":
    main()
