#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11227810
# DOI: 10.7717/peerj.17660
#   "Urine manganese, cadmium, lead, arsenic, and selenium among autism spectrum
#   disorder children in Kuala Lumpur" (Rafi'i, Ja'afar, Abd Wahil & Md Hanif,
#   2024), PeerJ 12:e17660.
# Data: PeerJ supplementary file peerj-12-17660-s001.sav (155 x 122), fetched
#       from the Europe PMC supplementaryFiles zip; codebook for the categorical
#       variables in peerj-12-17660-s002.docx. One row per parent-child pair.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. SPSS variable labels identify the block only as
#   "Question N Score Chicago Pb Knowledge Test (CLKT)", q1..q24, scored 0/1.
#   The paper: "Knowledge assessment on Pb exposure among children was
#   conducted using a validated Malay-version questionnaire (Abd Wahil, Ja'afar
#   & Isa, 2022)", self-administered by the parent via an online Google Form.
#   The 24 item stems are in the CLKT (Mehta & Binns 1998) and that Malay
#   validation, not in this deposit.
#
# Tables:
#   rafii_2024_lead_knowledge  parental lead-exposure knowledge (Malay CLKT),
#                              24 items, scored 0 = incorrect / 1 = correct.
#                              totalscore is their sum (verified) and skipped.
#
# The sample is parents of 155 preschoolers in Kuala Lumpur (81 with ASD, 74
# typically developing; cov_asd). Everything else in the file is child health,
# pregnancy, housing/exposure history, urinary metal assays, or SPSS
# regression output (PRE_*, COO_*) -- none of it item responses; parent
# demographics and child age/sex/ASD status are carried as covariates.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11227810/supplementaryFiles"

ITEMS = {f"q{i}score": f"clkt_{i}" for i in range(1, 25)}
COV = {
    "parentage": "cov_parent_age",
    "parentsex": "cov_parent_sex",        # 1 male, 2 female
    "parentrace": "cov_parent_race",      # 1 Malay 2 Chinese 3 Indian 4 other
    "parentedu": "cov_parent_education",  # 1 primary 2 secondary 3 tertiary
    "incomeclass": "cov_income_b40",      # 0 M40/T20, 1 B40
    "residentarea": "cov_outside_kl",     # 1 inside KL, 2 outside
    "kidage": "cov_child_age",
    "kidgender": "cov_child_sex",         # 1 male, 2 female
    "autismstat": "cov_asd",              # 0 TD, 1 ASD
}
DERIVED = ["parentage30", "parentrace2", "kidageyearpoint", "kidagemnth",
           "kidage4", "kidgender2", "autismstat2", "incomeclass2", "paritycat",
           "birthweightcat", "advmatage", "anaemiapreg11", "agehousclas25"]
NOT_ITEMS = [
    "parentincome", "parentheight", "parentweight", "parity", "sibling",
    "birthwght", "familyasd", "kidbirthhosp", "kidbirthstate", "kidprem",
    "gestage", "kidcompli", "bfeed", "bfperiod", "immunstatus", "autismstage",
    "kidspeak", "kidheight", "kidweight", "bmikid", "pregnantage", "modedeliv",
    "hblevel", "gdm", "pih", "comorbidpreg", "othkidautism", "housetype",
    "houseyear", "agehouse", "houseroad", "housefactory", "houseconstru",
    "drinkwater", "parentsmokestat", "riskworkplace", "soilexpos", "suckhand",
    "pica", "washhand", "supplemenvit", "drinkmilk", "eatfruitvege", "eatmeat",
    "exposework"]
LAB = ["pb", "cd", "as", "mn", "se", "pb4", "mdpt", "b", "Cd4", "mdptcd", "bcd",
       "cdcat", "pbcat", "cdlevel", "aslevel"]
MODEL = [f"{p}_{i}" for i in range(1, 8) for p in ("PRE", "COO")]
SKIP = {
    "idrespondent": "study code with letter suffixes (e.g. 137a); replaced by row index",
    "totalscore": "sum of the 24 CLKT items (composite)",
    **{c: "recode/collapse of another column" for c in DERIVED},
    **{c: "child health / pregnancy / housing / exposure history, one "
          "question each, not a scale; not carried" for c in NOT_ITEMS},
    **{c: "urinary metal assay or its binning (lab data)" for c in LAB},
    **{c: "SPSS logistic-regression output" for c in MODEL},
}


def fetch():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(z.read("peerj-12-17660-s001.sav"))
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


def convert():
    d = fetch()
    assert d.shape == (155, 122), d.shape
    cols, accounted = set(d.columns), set(ITEMS) | set(COV) | set(SKIP)
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert (d[list(ITEMS)].sum(axis=1) == d["totalscore"]).all()

    # idrespondent is unique but mixes codes like "137" and "137a"; per the
    # standard, non-numeric ids give way to the row index.
    assert d["idrespondent"].is_unique
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={**ITEMS, **COV})
    covs = list(COV.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    long = d.melt(id_vars=["id"] + covs, value_vars=list(ITEMS.values()),
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert long["resp"].isin([0, 1]).all()
    long = long[["id", "item", "resp"] + covs].reset_index(drop=True)

    name = "rafii_2024_lead_knowledge"
    pv = [0, 1]
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        long, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
