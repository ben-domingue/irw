#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.14138660
# DOI: 10.1186/s12889-022-13328-0
# "Validation of the medium and short version of CENSOPAS-COPSOQ: a
# psychometric study in the Peruvian population" (Lucero-Perez, Sabastizagal,
# Astete-Cornejo, Burgos, Villarreal-Zegarra & Moncada, 2022), BMC Public
# Health 22:910 (PMC9077908).
# Data: figshare 14138660 (depositor David Villarreal-Zegarra), file
#       "5. Database.xlsx", sheet "TODO R": 1,707 rows x 72 columns
#       (3 coded covariates + the 69 items of the CENSOPAS-COPSOQ medium
#       version, istas25a..istas30n). The deposit's other file, CENSOPAS.pdf,
#       is the bilingual questionnaire.
# License: CC BY 4.0 (figshare record licence; article also CC BY 4.0 with the
#          BMC CC0 data waiver). Data Availability: "The database is available
#          at https://doi.org/10.6084/m9.figshare.14138660".
#
# Item text: not shipped. Stems ARE cheap -- CENSOPAS.pdf in the same deposit
#   gives Spanish + English wording keyed 25a..30n, i.e. exactly the istas<code>
#   columns. The response options are what block it: the paper says "response
#   options ranging from always (5 points) to never (1 point)", but the file is
#   not coded that way for every item (e.g. 25g "enough time to do your work?"
#   correlates +0.13 with 25a "work very fast?", and 26g "committed to your
#   work?" has 1,108/1,707 at 1), so some items are stored reverse (risk-
#   direction) scored and which ones is undocumented. Attaching always/never
#   anchors would invert them on an unknown subset. Label levels checked: xlsx
#   has no variable or value labels (headers are bare codes); the PDF has
#   stems only, no per-item scoring direction.
#
# One instrument, one table: the 69-item medium version (20 subdimensions per
# the paper's Table 1). The 31-item short version is a subset of these same
# columns, so it is not a second table. resp 1-5 as stored; direction varies
# across items (see above) but is consistent within each item.
#
# Duplicated respondents: 67 rows are exact copies (all 3 covariates and all
# 69 items) of an earlier row, in 16 clusters -- three clusters of 11-16
# identical rows sit in rows 719-918. The response vectors use 4-5 distinct
# values across 69 items, so these are not straight-liners; identical
# 69-item patterns are duplication, not agreement. Kept the first row of each
# cluster, dropped the 66/67 copies -> N = 1,640.
#
# Covariates: Ocup (1/2), SECTOR_ECONOMICO (1-6; the paper's "six of the most
# important economic activities in Peru"), Region (1/2). No codebook for any of
# them; the paper reports three natural regions (35/33.4/31.6%) which Region's
# two codes (1,168/539) do not match, so codes are shipped raw and unlabeled.
# No id column -> row index (1-based, of the original file). No PII: the paper
# states "no information was included in the database that would allow them to
# be identified". No imputation language in the paper; 12 blank item cells are
# dropped.

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
XLSX_URL = "https://ndownloader.figshare.com/files/35100616"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "luceroperez_2022_copsoq"

COV = {"Ocup": "cov_occupation", "SECTOR_ECONOMICO": "cov_sector",
       "Region": "cov_region"}
SCALE = {1, 2, 3, 4, 5}


def convert() -> None:
    r = requests.get(XLSX_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(BytesIO(r.content), sheet_name="TODO R")
    assert df.shape == (1707, 72), df.shape

    items = [c for c in df.columns if c.startswith("istas")]
    assert len(items) == 69
    # Balance the books.
    unaccounted = [c for c in df.columns if c not in set(items) | set(COV)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df.insert(0, "id", range(1, len(df) + 1))
    dup = df.duplicated(subset=list(COV) + items, keep="first")
    print(f"  [drop] {int(dup.sum())} rows that exactly duplicate an earlier "
          f"row on all 72 source columns")
    assert dup.sum() == 67
    df = df[~dup]

    d = df[["id"] + list(COV) + items].rename(columns=COV)
    long = d.melt(id_vars=["id"] + list(COV.values()), value_vars=items,
                  var_name="item", value_name="resp")
    n_blank = long["resp"].isna().sum()
    long = long.dropna(subset=["resp"]).copy()
    print(f"  [drop] {n_blank} blank item cells")
    assert (long["resp"] % 1 == 0).all(), "fractional resp"
    long["resp"] = long["resp"].astype(int)
    for c in COV.values():
        long[c] = long[c].astype(int)
    long["item"] = long["item"].str.replace("istas", "copsoq_", regex=False)
    long = long[["id", "item", "resp"] + list(COV.values())]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert set(long["resp"]).issubset(SCALE), "resp outside 1-5"
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 69
    names = [TABLE]
    assert len(names) == len(set(names)), "duplicate output filenames"

    item_codes = sorted(long["item"].unique())
    qc = run_qc(long, permitted_values=SCALE)
    for c in qc:
        if c.status != "pass":
            print(f"  [qc {c.status}] {c.name}: {c.detail}")
    assert not [c for c in qc if c.status == "fail"], "run_qc fail"
    report = irw_validate.validate_frame(
        long, label=TABLE, profile="upload",
        context={"permitted_values": {i: SCALE for i in item_codes}})
    print(report)
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
