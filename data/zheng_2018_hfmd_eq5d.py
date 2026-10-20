"""
Zheng et al. (2018) — EQ-5D health-related quality of life in Chinese
paediatric hand, foot and mouth disease (HFMD) patients.

Source: Dryad, "Data from: Economic costs and health-related quality of life
        for hand, foot and mouth disease (HFMD) patients in China".
        Yaming Zheng (Chinese CDC), Mark Jit (PHE), et al. Published 2018-09-08.
DOI:    10.5061/dryad.6vs80  (mirrored as Zenodo 10.5281/zenodo.4977714)
Data:   HFMD-orignal.xlsx, Sheet1, 3,500 patients x 66 columns. Fetched from
        Zenodo (zenodo.org/api/records/4977714) because the Dryad v2 download
        endpoint returns HTTP 401 for an anonymous client.
License: CC0 1.0 (Dryad API: license == spdx.org/licenses/CC0-1.0.html;
        Zenodo metadata.license.id == "cc-zero").

Item text: NOT shipped. The four dimensions are the EQ-5D (-Y) descriptive
        system, a third-party licensed instrument (EuroQol Research
        Foundation); the deposit carries only the bare column names
        (`mobility`, `daily_activity`, `pain`, `anxiety`), no stems or
        option wording, so there is nothing to transcribe that would not be
        the copyrighted instrument text. Response table only.

Geographic columns DROPPED under the 2026-10-20 ruling (geographic/
        administrative codes are not carried into the IRW in any form — not
        as cov_*, not hashed, not truncated):
            addressid   (2,490 distinct 8-digit hierarchical Chinese address
                          codes; county/township level)
        Sheet2 of the workbook holds four bare 8-digit values of the same
        kind with no header row and no linkage; it is dropped for the same
        reason. Names/emails: none present (string-column PII screen below).

Notes
-----
* No respondent identifier survives the address-code drop, so `id` is the
  1-based row index of Sheet1 (per IRW practice for register-number-keyed
  clinical files).
* `mobility` runs 1-4 while the other three dimensions run 1-3. The level-4
  responses are 567 of 3,500 (16.2%), so this is a real fourth response
  option in this administration (the deposit documents no codebook), not the
  isolated data-entry anomaly it first looks like. It is shipped as 1-4.
  HUMAN CALL: if the source paper shows 4 is a missing/"unable to assess"
  code rather than a worst-health level, those 567 cells should be dropped.
* `eq_vas` (0-100 visual analogue scale) is NOT shipped: it is a single
  item on a response scale incompatible with the four 1-3 ordinal
  dimensions, and IRW does not accept a one-item table.
* The remaining ~55 columns are health-economics cost/resource-use
  quantities (yuan, days off work, visits), not item responses.
"""

import sys
import os

sys.path.insert(0, "/home/ben/.local/lib/python3.12/site-packages")

import numpy as np
import pandas as pd

XLSX = sys.argv[1]
OUTDIR = sys.argv[2]

ITEMS = ["mobility", "daily_activity", "pain", "anxiety"]
COVS = {
    "gender": "cov_gender",
    "age_group": "cov_age_group",
    "severity": "cov_severe_case",
    "urban": "cov_urbanicity",
    "patienttype": "cov_patient_type",
    "treatment": "cov_treatment_setting",
    "LAB": "cov_serotype",
    "duration_of_illness": "cov_duration_of_illness_days",
}
GEO = ["addressid"]

df = pd.read_excel(XLSX, sheet_name="Sheet1")
print(f"source shape: {df.shape}")

# ---------------------------------------------------------------- PII screen
# NOTE: pd.api.types.is_string_dtype, NOT `dtype == object`.
string_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
print(f"PII screen: examined {len(string_cols)} string column(s): {string_cols}")
assert len(string_cols) > 0, "PII screen examined zero columns — screen is broken"

EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
NAME_HINT = ("name", "email", "mail", "surname", "firstname", "lastname",
             "contact", "phone", "patientid", "idcard")
pii_hits = []
for c in string_cols:
    s = df[c].dropna().astype(str)
    if s.empty:
        continue
    if s.str.contains(EMAIL, regex=True, na=False).any():
        pii_hits.append((c, "email pattern in values"))
    if any(h in c.lower() for h in NAME_HINT):
        pii_hits.append((c, "name/contact-like column"))
print(f"PII screen: {len(pii_hits)} hit(s): {pii_hits}")
assert not pii_hits, f"PII detected — stop, do not ship: {pii_hits}"

# -------------------------------------------------------------- build table
d = df.copy()
d["id"] = np.arange(1, len(d) + 1)

n4 = int((d["mobility"] == 4).sum())
print(f"mobility: {n4} of {len(d)} responses at level 4 "
      f"({100*n4/len(d):.1f}%) — kept as a real fourth ordinal level, not an "
      f"anomaly; the other three dimensions are 1-3")

cov = d[["id"] + list(COVS)].rename(columns=COVS)
cov["cov_serotype"] = cov["cov_serotype"].astype("string").str.replace(
    r"\s+", " ", regex=True).str.strip()
cov["cov_severe_case"] = cov["cov_severe_case"].map({"Y": 1, "N": 0})

long = d[["id"] + ITEMS].melt(id_vars="id", var_name="item", value_name="resp")
long = long.dropna(subset=["resp"])
long["resp"] = long["resp"].astype(int)

out = long.merge(cov, on="id", how="left")
out = out[["id", "item", "resp"] + list(COVS.values())]
out = out.sort_values(["id", "item"]).reset_index(drop=True)

NAME = "zheng_2018_hfmd_eq5d"
assert len(NAME) <= 40, NAME
for it, g in out.groupby("item"):
    print(f"  resp range {it}: {int(g.resp.min())}-{int(g.resp.max())}, "
          f"levels {sorted(g.resp.unique())}")
assert out["resp"].between(1, 4).all(), "resp outside 1-4"
assert out["id"].nunique() >= 100, "fewer than 100 ids"
assert out["item"].nunique() >= 3, "fewer than 3 items"
assert not out[["id", "item"]].duplicated().any(), "duplicate id/item"
path = os.path.join(OUTDIR, NAME + ".csv")
out.to_csv(path, index=False)
print(f"{NAME}: {len(out)} rows, {out['id'].nunique()} ids, "
      f"{out['item'].nunique()} items -> {path}")

# ----------------------------------------------------- balance the books
used = set(ITEMS) | set(COVS)
reasons = {}
for c in df.columns:
    if c in used:
        continue
    if c in GEO:
        reasons[c] = "DROPPED: geographic/administrative code (2026-10-20 ruling)"
    elif c == "eq_vas":
        reasons[c] = ("skipped: single 0-100 VAS item, scale incompatible with the "
                      "ordinal dimensions and a one-item table is not acceptable")
    elif c in ("TIME_OF_ILLNESS", "MAIN_DIAGNOSIS"):
        reasons[c] = "skipped: clinical episode metadata, not an item response"
    else:
        reasons[c] = ("skipped: health-economics cost / resource-use quantity "
                      "(cost, days off work, visits, accompaniment), not an item response")
assert set(reasons) | used == set(df.columns), "column accounting incomplete"
assert len(reasons) + len(used) == len(df.columns), "books do not balance"

from collections import Counter
print(f"\ncolumn accounting (all {len(df.columns)} source columns):")
print(f"  OUTPUT: {len(used)} ({len(ITEMS)} items + {len(COVS)} covariates); "
      f"id is the 1-based row index")
for r, n in Counter(reasons.values()).most_common():
    print(f"  {n:5d}  {r}")
print("books balance.")
print("Sheet2 (3 rows x 1 column of bare 8-digit address codes, no header, no "
      "linkage) dropped as geographic under the same ruling.")
