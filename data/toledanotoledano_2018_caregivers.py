#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/Validity_and_reliability_of_the_Beck_Depression_Inventory_II_BDI-II_in_family_caregivers_of_children_with_chronic_diseases/7394579
# DOI: 10.1371/journal.pone.0206917.s001 (S1 Dataset of the article 10.1371/journal.pone.0206917)
#   Toledano-Toledano, F. & Contreras-Valdez, J. A. (2018). "Validity and reliability of
#   the Beck Depression Inventory II (BDI-II) in family caregivers of children with
#   chronic diseases." PLOS ONE 13(11): e0206917.
# Data: "pone.0206917.s001.xlsx", sheet Hoja1 -- 446 family caregivers x 132 columns:
#       20 background codes, then six contiguous item blocks whose headers are the
#       block name + item number (DepressionItem1..21, QualityOfLifeItem1..26,
#       AnxietyItem1..21, BurdenItem1..22, ParentalStressItem1..12,
#       WellbeingItem1..10). No missing cells anywhere in the item blocks.
#       Sheets Hoja2/Hoja3 are empty.
# License: CC BY 4.0 (verified on the plos.figshare.com deposit page and the figshare
#          API record for article 7394579).
#
# Item text: not shipped. The xlsx has no variable labels and no value labels (it is a
#   plain spreadsheet); the headers are positional block codes ("DepressionItem1"),
#   never stems. The BDI-II wording is proprietary (Pearson) and the five companion
#   instruments are not named in the deposit, so the published Spanish-language
#   instruments would be needed. Where the text actually is: the article's Methods
#   section names the instruments; the item wording is in the respective published
#   scales, not in this deposit.
#
# Item codes: taken from each header's own trailing number, so code k is the source
#   file's item k. Three headers are typos of the same pattern -- "Depresin2",
#   "Depresin13" (missing "sionItem") and "DepressionItem1.1" (pandas' de-duplicated
#   name for a second "DepressionItem1" header, which the column's position shows is
#   item 9: the block runs 1-8, then this column, then 10-21). Each is mapped
#   explicitly below rather than by bare position.
# Tables (one per instrument block, per datastandard.md's one-scale-per-file rule):
#   toledanotoledano_2018_bdi2             21 items, 0-3
#   toledanotoledano_2018_quality_of_life  26 items, 1-5
#   toledanotoledano_2018_anxiety          21 items, 0-4
#   toledanotoledano_2018_caregiver_burden 22 items, 0-4
#   toledanotoledano_2018_parental_stress  12 items, 1-5
#   toledanotoledano_2018_wellbeing        10 items, 0-3
# id: the spreadsheet carries no respondent identifier, so id is the 1-based row index
#   of the de-duplicated frame; it links a caregiver across all six tables.
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
URL = "https://ndownloader.figshare.com/files/13680101"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

BLOCKS = {
    "bdi2": ("Depres", 21, [0, 1, 2, 3]),
    "quality_of_life": ("QualityOfLife", 26, [1, 2, 3, 4, 5]),
    "anxiety": ("Anxiety", 21, [0, 1, 2, 3, 4]),
    "caregiver_burden": ("Burden", 22, [0, 1, 2, 3, 4]),
    "parental_stress": ("ParentalStress", 12, [1, 2, 3, 4, 5]),
    "wellbeing": ("Wellbeing", 10, [0, 1, 2, 3]),
}

# The 20 background columns, in file order, renamed to cov_*.
COVS = {
    "Caregiver'sAge": "cov_caregiver_age",
    "Caregiver'sSex": "cov_caregiver_sex",
    "YearsOfMarried": "cov_years_married",
    "SchoolingFamilyCaregiver": "cov_caregiver_schooling",
    "Patient'sSex": "cov_patient_sex",
    "Caregiver'sReligion": "cov_caregiver_religion",
    "NumberOfChildren": "cov_number_of_children",
    "Occupation": "cov_occupation",
    "Patient'sAge": "cov_patient_age_code",
    "DiagnosisOfTheChild": "cov_child_diagnosis",
    "MedicalService": "cov_medical_service",
    "HospitalizationTime": "cov_hospitalization_time",
    "StateOfTheCountry": "cov_state",
    "CivilStatus": "cov_civil_status",
    "ParentalRole": "cov_parental_role",
    "FamilyTipe": "cov_family_type",
    "Lifecycle": "cov_lifecycle",
    "DiagnosticTime": "cov_diagnostic_time",
    "SupportNetworks": "cov_support_networks",
    "monthly economic income": "cov_monthly_income",
}


def screen_for_pii(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] examined {df.shape[1]} columns, {len(text_cols)} of them string-typed")
    assert df.shape[1] > 0
    pats = {
        "email": r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}",
        "phone": r"\+?\d[\d \-()]{8,}",
        "postal": r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$",
        "ip": r"^\d{1,3}(\.\d{1,3}){3}$",
        "date": r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}",
    }
    hits = []
    for c in text_cols:
        v = df[c].dropna().astype(str)
        for k, p in pats.items():
            if v.str.contains(p, regex=True, na=False).any():
                hits.append((c, k))
    assert not hits, hits
    print("[pii] no name/email/phone/postal/IP/date pattern in any string column")


def item_map(df: pd.DataFrame, prefix: str, n: int) -> dict[str, str]:
    """Source column -> item code, from the header's own trailing number."""
    cols = [c for c in df.columns if str(c).strip().startswith(prefix)]
    assert len(cols) == n, (prefix, len(cols), n)
    out: dict[str, str] = {}
    for pos, c in enumerate(cols):
        name = str(c).strip()
        if name == "DepressionItem1.1":
            k = 9  # pandas-deduplicated duplicate header; position 9 in the 1-21 block
            assert pos == 8, pos
        else:
            m = re.search(r"(\d+)$", name)
            assert m, name
            k = int(m.group(1))
        code = f"{prefix.lower()}_{k}" if prefix != "Depres" else f"bdi_{k}"
        assert code not in out.values(), (prefix, code)
        out[c] = code
    assert sorted(int(v.rsplit("_", 1)[1]) for v in out.values()) == list(range(1, n + 1))
    return out


def emit(name: str, t: pd.DataFrame, pv: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item"]).any(), name
    assert t["id"].nunique() >= 100, (name, t["id"].nunique())
    assert t["item"].nunique() >= 3, (name, t["item"].nunique())
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:160]}")
    rep = irw_validate.validate_frame(t, label=name, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, (name, [(f.check, f.message) for f in rep.errors])
    for f in rep.warnings:
        print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Hoja1")
    assert df.shape == (446, 132), df.shape
    screen_for_pii(df)

    # Five rows are byte-identical across all 132 integer columns, which cannot happen
    # by chance over 111 items; they are duplicated data entry, so keep the first.
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[dedupe] dropped {before - len(df)} fully identical 132-column rows")

    df.insert(0, "id", range(1, len(df) + 1))
    cov = df.rename(columns=COVS)[["id"] + list(COVS.values())]

    # Book-keeping: every source column is either an item, a covariate, or skipped
    # with a reason.
    accounted = set(COVS)
    tables = {}
    for short, (prefix, n, pv) in BLOCKS.items():
        m = item_map(df, prefix, n)
        accounted |= set(m)
        long = (df[["id"] + list(m)]
                .rename(columns=m)
                .melt(id_vars="id", var_name="item", value_name="resp"))
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long.merge(cov, on="id", how="left")
        long = long[["id", "item", "resp"] + list(COVS.values())].reset_index(drop=True)
        tables[f"toledanotoledano_2018_{short}"] = (long, pv)

    leftover = [c for c in df.columns if c not in accounted and c != "id"]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print(f"[books] {len(accounted)} source columns accounted for "
          f"({len(COVS)} covariates + {sum(b[1] for b in BLOCKS.values())} items), 0 skipped")

    assert len(set(tables)) == len(tables)
    for name, (t, pv) in tables.items():
        emit(name, t, pv)


if __name__ == "__main__":
    convert()
