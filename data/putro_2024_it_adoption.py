#!/usr/bin/env python3
# Source: https://doi.org/10.17632/kcvpw2pxh6.1
# DOI: 10.1016/j.heliyon.2024.e25479
#   "Entrepreneurs' creativity, information technology adoption, and
#   continuance intention: Mediation effects of perceived usefulness and ease
#   of use and the moderation effect of entrepreneurial orientation" (Putro &
#   Takahashi, 2024), Heliyon 10:e25479.
# Data: Mendeley Data kcvpw2pxh6 v1 (contributors Adin Kusumo Putro, Yoshi
#       Takahashi), single file "Entrepreneurs' Creativity, Information
#       Technology Adoption, and Continuance Intention.xlsx" (265 x 72).
#       Indonesian entrepreneurs registered at five Yogyakarta tax offices,
#       paper questionnaires, 2022.
# License: CC BY 4.0 (Mendeley Data record's data_licence; article CC BY 4.0).
#
# Item text: not shipped. Both label levels are absent -- the workbook has
#   bare codes (CA1.., EO1.., PUETS1..) and no codebook sheet; the paper
#   prints one sample item per construct (Methods 3.2); its Appendix A
#   (mmc1.docx, checked) holds only CFA fit, reliability and validity
#   tables, no wording. Wording: Hills et al. / Puhakka (creativity),
#   Miller (EO), Davis et al. (TAM), administered in Indonesian
#   (back-translated), which is not in the deposit.
#
# Tables (all 1-7, strongly disagree .. strongly agree, per Methods 3.2):
#   putro_2024_creativity    CA1-CA8 entrepreneurial creativity
#   putro_2024_eo            EO1-EO8 entrepreneurial orientation (Miller)
#   putro_2024_tam_etax      TAM block for the e-tax service (DJP Online):
#                            PUETS1-4, PEOUETS1-4, ITADETS1-4, CONFETS1-3,
#                            CONTETS1-3 (users only), INTETS1-3 (non-users
#                            only) -- 21 items, one questionnaire section
#   putro_2024_tam_emarket   the same 21-item block for e-marketplaces (EMP)
#   The two TAM sections are separate administrations about different
#   technologies, so they ship as separate tables; the user/non-user routing
#   is carried as cov_etax_user / cov_emarket_user (EXPER*1, 1 = yes).
# Covariates: age, gender, education, marital status, tax office (KPP), city,
#   industry, income band, firm size, and per section years of use (EXPER*2).
# id: OBS (unique 1..265). No PII. No duplicate rows. No missing cells on the
#   always-asked blocks; routed blocks are missing by design.

import sys
from pathlib import Path

import pandas as pd
import requests
import io

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/kcvpw2pxh6/files/"
       "1fc0b3f2-6237-4116-a21f-dc010ad49428/file_downloaded")

COVS = {"AGE": "cov_age", "GENDER": "cov_gender", "EDUC": "cov_education",
        "MARR": "cov_marital", "KPP": "cov_tax_office", "CITY": "cov_city",
        "INDUSTRY": "cov_industry", "INCOME": "cov_income",
        "SIZE": "cov_firm_size"}


def tam(suffix):
    return ([f"PU{suffix}{i}" for i in range(1, 5)]
            + [f"PEOU{suffix}{i}" for i in range(1, 5)]
            + [f"ITAD{suffix}{i}" for i in range(1, 5)]
            + [f"CONF{suffix}{i}" for i in range(1, 4)]
            + [f"CONT{suffix}{i}" for i in range(1, 4)]
            + [f"INT{suffix}{i}" for i in range(1, 4)])


SCALES = {
    "putro_2024_creativity": ([f"CA{i}" for i in range(1, 9)], {}),
    "putro_2024_eo": ([f"EO{i}" for i in range(1, 9)], {}),
    "putro_2024_tam_etax": (tam("ETS"), {"EXPERETS1": "cov_etax_user",
                                         "EXPERETS2": "cov_etax_years"}),
    "putro_2024_tam_emarket": (tam("EMP"), {"EXPEREMP1": "cov_emarket_user",
                                            "EXPEREMP2": "cov_emarket_years"}),
}
SKIP = {"OBS": "used as id"}


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (265, 72), d.shape
    acc = set(COVS) | set(SKIP)
    for items, sc in SCALES.values():
        acc |= set(items) | set(sc)
    assert set(d.columns) == acc, set(d.columns) ^ acc
    assert d["OBS"].is_unique
    assert not d.drop(columns="OBS").duplicated().any()
    d = d.rename(columns={"OBS": "id", **COVS})
    names = list(SCALES)
    assert len(set(names)) == len(names)
    total = 0
    for table, (items, sc) in SCALES.items():
        sub = d.rename(columns=sc)
        cov_cols = list(COVS.values()) + list(sc.values())
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=items,
                        var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(1, 7).all()
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: set(range(1, 8)) for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        total += len(long)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    exp = sum(d[items].notna().sum().sum() for items, _ in SCALES.values())
    assert total == exp, (total, exp)


if __name__ == "__main__":
    convert()
