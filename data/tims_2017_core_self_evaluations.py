#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0182745
# DOI: 10.1371/journal.pone.0182745
# Data: S2 File (SPSS .sav)
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0182745.s002
# License: CC BY 4.0 (PLOS ONE)
#
# Tims et al. (2017), "Core self-evaluations and work engagement: Testing a
# perception, action, and development path". The deposit stacks the paper's
# two independently-recruited samples in one file (706 rows): Study 1 in the
# Netherlands (N=303) and Study 2 in Germany (N=404). The `Country` column
# distinguishes them and is carried as cov_country; ids are assigned from the
# row index over the stacked file, so they are distinct across the two
# samples by construction.
#
# Item blocks, all complete (no missing item responses):
#
#   CSE1-CSE12    Core Self-Evaluations Scale (Judge et al.), 12 items, 1-5.
#                 The deposit carries 18 CSE columns: the 12 originals plus
#                 CSE2R/4R/6R/8R/10R/12R, which are the reverse-keyed
#                 recodes of the six negatively-worded items. Only the 12
#                 as-administered columns are shipped -- datastandard.md is
#                 explicit that reverse-scored items are not recoded, and
#                 shipping both copies would double-count six items.
#   RoM1-3, RoK4-7, Netw8-11, Prof12-14, Expl15-17, Contr18-21
#                 career competencies, 21 items across six dimensions
#                 (reflection on motivation / on qualities, networking,
#                 professional profiling, work exploration, career control),
#                 1-5. One instrument, so one table.
#   AUT1-AUT4     autonomy, 1-5
#   SUPSUP1-4     supervisory social support, 1-5
#   STRUC1-5, SOC1-5, CHAL1-5
#                 Job Crafting Scale (Tims et al.), the three expansive
#                 dimensions -- increasing structural job resources,
#                 increasing social job resources, increasing challenging job
#                 demands -- 15 items, 1-5. One instrument, so one table.
#   HIND1-HIND6   hindering job demands, 1-5
#   VIT1-3, DED1-3, ABS1-3
#                 UWES-9 work engagement, 9 items, 1-7
#
# NOTE, recorded rather than reconciled: the article says autonomy and
# supervisory social support were each measured with three items; the deposit
# carries four columns for each. The deposit is shipped as it stands.
#
# Excluded as composites, not responses: the trailing scale-score columns
# (RoM, RoK, Netw, Prof, Expl, Contr, Struc, Soc, Chal, Hind, Vit, Ded, Abs,
# BEVL, CC, CSE, AUT, SuS) and the SPSS @CC_R / @CC_C / @CC_B artefacts.
# These share prefixes with the item columns, so the item patterns below all
# require at least one trailing digit.
#
# Item text: not shipped. Both label levels were checked with pyreadstat.
# Variable labels are present for 50 of 107 columns but are block headers
# rather than stems -- CSE1 is labelled "Core self-evaluations", AUT1
# "Autonomy items", CHAL1 "Items increasing challenging job demands (job
# crafting)" -- and the remaining item columns carry no label at all. Value
# labels exist only for the demographic columns (Country, Sex, Edu, ...), not
# for any item column. The stems are in the source instruments' own
# publications (CSES, the career competencies questionnaire, the Job Crafting
# Scale, UWES-9), all third-party.

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0182745.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Country":  "cov_country",   # 1 = Netherlands (study 1), 2 = Germany (study 2)
    "Age":      "cov_age",
    "Sex":      "cov_sex",
    "Edu":      "cov_education",
    "Contrhrs": "cov_contract_hours",
    "Workhrs":  "cov_work_hours",
    "Tenure":   "cov_tenure",
    "Wexp":     "cov_work_experience",
    "Sector":   "cov_sector",
}

# out_name -> (list of item-column regexes, valid resp range)
SCALES = {
    "tims_2017_cse": ([r"CSE\d+"], (1, 5)),
    "tims_2017_career_competencies": (
        [r"RoM\d+", r"RoK\d+", r"Netw\d+", r"Prof\d+", r"Expl\d+", r"Contr\d+"], (1, 5)),
    "tims_2017_autonomy":            ([r"AUT\d+"], (1, 5)),
    "tims_2017_supervisor_support":  ([r"SUPSUP\d+"], (1, 5)),
    "tims_2017_job_crafting":        ([r"STRUC\d+", r"SOC\d+", r"CHAL\d+"], (1, 5)),
    "tims_2017_hindering_demands":   ([r"HIND\d+"], (1, 5)),
    "tims_2017_uwes":                ([r"VIT\d+", r"DED\d+", r"ABS\d+"], (1, 7)),
}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=180)
    raw.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(raw.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    for out_name, (patterns, (lo, hi)) in SCALES.items():
        item_cols = [c for c in df.columns
                     if any(re.fullmatch(p, str(c)) for p in patterns)]
        if out_name == "tims_2017_cse":
            # drop the reverse-keyed recodes CSE2R/4R/6R/8R/10R/12R
            item_cols = [c for c in item_cols if not str(c).endswith("R")]
        if not item_cols:
            raise SystemExit(f"no item columns matched {patterns}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        checks = run_qc(long)
        failed = [c for c in checks if c.status == "fail"]
        assert not failed, (out_name, [(c.name, c.detail) for c in failed])
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
