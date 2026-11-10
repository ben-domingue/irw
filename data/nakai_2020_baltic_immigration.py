#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/J3AAF8
# DOI: 10.7910/DVN/J3AAF8 (data; no paper DOI on the record)
#   Nakai, R. (2020). "Attitude toward Immigrants and Politics in Estonia and
#   Latvia in 2018." Harvard Dataverse.
# Data: "1b. Rawdata ATIP in EELV (CSV version).csv" (1,013 web-survey
#   respondents, 506 Estonia + 507 Latvia, July 2018), read alongside
#   "2. Codebook and Questionnaire in English.pdf" and "3. Summary Report".
# License: CC0 1.0 (Dataverse record).
#
# CODING CHECK: the codebook prints "No answer / Don't know" as 8 or 88, but
#   the data file stores it as the next code after the scale (5 on the 4-point
#   items, 7 on the 6-point values items). Confirmed against the deposit's
#   own Summary Report: trstarmy by country (29.70/42.97/15.64/5.74/5.94% in
#   Estonia) and vcreative (10.93 ... 0.40, Don't know 2.58%) equal the data's
#   code shares 1..5 / 1..7 to the hundredth. That DK code is dropped.
#
# Item text: not shipped -- the English questionnaire is in the deposit
#   (codebook PDF), but the trust and immigration items are ESS questions and
#   the values items Schwartz PVQ-style portraits (third-party; register
#   SCHWARTZ block); administered in Estonian, Latvian or Russian (a .rar
#   in the deposit). Left for an item-text round.
#
# Tables:
#   nakai_2020_inst_trust   trstarmy, trstpress, trstpolice, trstjulis,
#                           trstgvmnt, trstprty, trstprlmt, trustun; 1 = a
#                           great deal .. 4 = none at all
#   nakai_2020_values       vcreative, vequal, vorder, vsecurity, vtradition;
#                           1 = very much like me .. 6 = not like me at all
#   nakai_2020_immigration  imeuro, immena, imafro, imasia (allow people from
#                           poor countries in ...); 1 = allow many .. 4 = none
# Not shipped: single items on their own scales (polintr, leftright,
#   feelsafe, ecnmhouse, ecnmnation, immigculture, terror, prtyspt);
#   `satisficer` (an attention-check item, not in the codebook); region (an
#   administrative region code, dropped under the 2026-10-20 geography rule);
#   start/end timestamps.
# Covariates: cov_country, cov_gender, cov_birth_year, cov_education,
#   cov_survey_language (codebook labels). id: row index + 1.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://dataverse.harvard.edu/api/access/datafile/3831097?format=original"
SCALES = {
    "nakai_2020_inst_trust": (["trstarmy", "trstpress", "trstpolice", "trstjulis",
                               "trstgvmnt", "trstprty", "trstprlmt", "trustun"], 4),
    "nakai_2020_values": (["vcreative", "vequal", "vorder", "vsecurity", "vtradition"], 6),
    "nakai_2020_immigration": (["imeuro", "immena", "imafro", "imasia"], 4),
}
GENDER = {1: "male", 2: "female", 3: "other"}
EDU = {1: "primary unfinished", 2: "primary", 3: "vocational secondary",
       4: "secondary", 5: "vocational higher / tertiary unfinished",
       6: "tertiary", 7: "quaternary (graduate school)"}
LANG = {0: "Russian", 1: "Estonian/Latvian"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert d.shape == (1013, 38), d.shape
    # the Summary Report's Estonian trstarmy shares, to the hundredth
    ee = d.loc[d["cntry"] == "EE", "trstarmy"].value_counts(normalize=True)
    assert round(ee[1.0] * 100, 2) == 29.70 and round(ee[5.0] * 100, 2) == 5.94

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d["cov_country"] = d["cntry"].map({"EE": "Estonia", "LV": "Latvia"})
    d["cov_gender"] = d["gender"].map(GENDER)
    d["cov_birth_year"] = d["birthyr"]
    d["cov_education"] = d["education"].map(EDU)
    d["cov_survey_language"] = d["language"].map(LANG)
    cov_cols = ["cov_country", "cov_gender", "cov_birth_year", "cov_education",
                "cov_survey_language"]

    for table, (cols, k) in SCALES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        assert set(long["resp"]) <= set(range(1, k + 2)), (table, set(long["resp"]))
        ndk = int((long["resp"] == k + 1).sum())
        long = long[long["resp"] <= k]
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        allowed = set(range(1, k + 1))
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses ({ndk} DK dropped), "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
