#!/usr/bin/env python3
# Source: https://zenodo.org/records/23410447
# DOI: 10.5281/zenodo.23410447 (data)
#   Tekin C (2026). The mediating roles of organizational justice and organizational trust in the effect of organizational favoritism on organizational commitment [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23410447
# License: CC BY 4.0 (record metadata)
# Data: 'tez son 19.03.2025.sav' (thesis file), 508 Turkish employees, the deposit's ID. Item value labels: 1 =
#   Kesinlikle Katilmiyorum .. 5 = Kesinlikle Katiliyorum. Item columns carry their subscale as a suffix where the
#   thesis kept them (OK1_nepotizm); items without one are kept too, item = the column name.
# Tables: the four instruments (OK 22, OA 20, OB 18, OG 17 items).
# Dropped: the *_1 copies (identical to the raw items except that missing cells are filled with fractional means),
#   subscale/scale means, SD_* and Z* scores. OK14 has one cell coded 6 and OG4 one coded 45 (1-5 scale): both set missing.
# Covariates: the 12 demographic codes, numeric as in the .sav (value labels via metadata/covariate_labels).
# PII: none.
# Item text: only codes + subscale suffixes in the .sav; the thesis questionnaire is not in the deposit.
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/23410447/files/tez%20son%2019.03.2025.sav/content'
N_ROWS = 508
ID_COL = 'ID'
COVS = {'yas': 'cov_age_band',
 'cinsiyet': 'cov_gender',
 'medeni': 'cov_marital',
 'egitim': 'cov_education',
 'yasadigiyer': 'cov_settlement_type',
 'gelir': 'cov_income',
 'gorev': 'cov_role',
 'isytipi': 'cov_hiring_type',
 'birimsure': 'cov_unit_tenure',
 'kidem': 'cov_seniority',
 'isturu': 'cov_org_type',
 'kamu_vs_özel': 'cov_public_private'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'tekin_2025_favoritism': ['OK1_nepotizm',
                           'OK2_nepotizm',
                           'OK3_nepotizm',
                           'OK4_nepotizm',
                           'OK5_nepotizm',
                           'OK6_nepotizm',
                           'OK7',
                           'OK8_nepotizm',
                           'OK9',
                           'OK10_nepotizm',
                           'OK11',
                           'OK12',
                           'OK13',
                           'OK14',
                           'OK15_cinsiyet_ayrımcılığı',
                           'OK16_cinsiyet_ayrımcılığı',
                           'OK17_cinsiyet_ayrımcılığı',
                           'OK18_tribalizm_siyasi_kayırmacılık',
                           'OK19_tribalizm_siyasi_kayırmacılık',
                           'OK20_tribalizm_siyasi_kayırmacılık',
                           'OK21_tribalizm_siyasi_kayırmacılık',
                           'OK22_tribalizm_siyasi_kayırmacılık'],
 'tekin_2025_justice': ['OA1_süreç_dağıtım_adaleti',
                        'OA2_süreç_dağıtım_adaleti',
                        'OA3_süreç_dağıtım_adaleti',
                        'OA4_süreç_dağıtım_adaleti',
                        'OA5_süreç_dağıtım_adaleti',
                        'OA6_süreç_dağıtım_adaleti',
                        'OA7_süreç_dağıtım_adaleti',
                        'OA8_süreç_dağıtım_adaleti',
                        'OA9_süreç_dağıtım_adaleti',
                        'OA10_süreç_dağıtım_adaleti',
                        'OA11_süreç_dağıtım_adaleti',
                        'OA12',
                        'OA13',
                        'OA14',
                        'OA15',
                        'OA16_etkileşimsel_adalet',
                        'OA17_etkileşimsel_adalet',
                        'OA18_etkileşimsel_adalet',
                        'OA19_etkileşimsel_adalet',
                        'OA20_etkileşimsel_adalet'],
 'tekin_2025_commitment': ['OB1_duygusal_normatif',
                           'OB2_duygusal_normatif',
                           'OB3_duygusal_normatif',
                           'OB4_duygusal_normatif',
                           'OB5',
                           'OB6_duygusal_normatif',
                           'OB7',
                           'OB8_devam_bağlılığı',
                           'OB9_devam_bağlılığı',
                           'OB10_devam_bağlılığı',
                           'OB11',
                           'OB12_devam_bağlılığı',
                           'OB13',
                           'OB14',
                           'OB15',
                           'OB16',
                           'OB17_duygusal_normatif',
                           'OB18_duygusal_normatif'],
 'tekin_2025_trust': ['OG1',
                      'OG2_çalışma_arkadaşlarına',
                      'OG3_çalışma_arkadaşlarına',
                      'OG4',
                      'OG5_çalışma_arkadaşlarına',
                      'OG6_çalışma_arkadaşlarına',
                      'OG7_çalışma_arkadaşlarına',
                      'OG8_yöneticiye',
                      'OG9_yöneticiye',
                      'OG10_yöneticiye',
                      'OG11_yöneticiye',
                      'OG12_yöneticiye',
                      'OG13',
                      'OG14_işletmeye_kuruma',
                      'OG15_işletmeye_kuruma',
                      'OG16_işletmeye_kuruma',
                      'OG17_işletmeye_kuruma']}
# (lo, hi) response range per table
RANGES = {'tekin_2025_favoritism': (1, 5),
 'tekin_2025_justice': (1, 5),
 'tekin_2025_commitment': (1, 5),
 'tekin_2025_trust': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'tekin_2025_favoritism': [6], 'tekin_2025_trust': [45]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'OK': 'composite / standardised score',
 'OK_nepotizm': 'composite / standardised score',
 'OK_cinsiyet_ayrımcılığı': 'composite / standardised score',
 'OK_tribalizm_siyasi_kayırmacılık': 'composite / standardised score',
 'OA': 'composite / standardised score',
 'OA_süreç_dağıtım_adaleti': 'composite / standardised score',
 'OA_etkileşimsel_adalet': 'composite / standardised score',
 'OG': 'composite / standardised score',
 'OG_çalışma_arkadaşlarına': 'composite / standardised score',
 'OG_yöneticiye': 'composite / standardised score',
 'OG_işletmeye_kuruma': 'composite / standardised score',
 'OB': 'composite / standardised score',
 'OB_duygusal_normatif': 'composite / standardised score',
 'OB_devam_bağlılığı': 'composite / standardised score',
 'SD_OK': 'composite / standardised score',
 'SD_OA': 'composite / standardised score',
 'SD_OB': 'composite / standardised score',
 'SD_OG': 'composite / standardised score',
 'OK1_1': 'mean-imputed copy of the raw item',
 'OK2_1': 'mean-imputed copy of the raw item',
 'OK3_1': 'mean-imputed copy of the raw item',
 'OK4_1': 'mean-imputed copy of the raw item',
 'OK5_1': 'mean-imputed copy of the raw item',
 'OK6_1': 'mean-imputed copy of the raw item',
 'OK7_1': 'mean-imputed copy of the raw item',
 'OK8_1': 'mean-imputed copy of the raw item',
 'OK9_1': 'mean-imputed copy of the raw item',
 'OK10_1': 'mean-imputed copy of the raw item',
 'OK11_1': 'mean-imputed copy of the raw item',
 'OK12_1': 'mean-imputed copy of the raw item',
 'OK13_1': 'mean-imputed copy of the raw item',
 'OK14_1': 'mean-imputed copy of the raw item',
 'OK15_1': 'mean-imputed copy of the raw item',
 'OK16_1': 'mean-imputed copy of the raw item',
 'OK17_1': 'mean-imputed copy of the raw item',
 'OK18_1': 'mean-imputed copy of the raw item',
 'OK19_1': 'mean-imputed copy of the raw item',
 'OK20_1': 'mean-imputed copy of the raw item',
 'OK21_1': 'mean-imputed copy of the raw item',
 'OK22_1': 'mean-imputed copy of the raw item',
 'OA1_1': 'mean-imputed copy of the raw item',
 'OA2_1': 'mean-imputed copy of the raw item',
 'OA3_1': 'mean-imputed copy of the raw item',
 'OA4_1': 'mean-imputed copy of the raw item',
 'OA5_1': 'mean-imputed copy of the raw item',
 'OA6_1': 'mean-imputed copy of the raw item',
 'OA7_1': 'mean-imputed copy of the raw item',
 'OA8_1': 'mean-imputed copy of the raw item',
 'OA9_1': 'mean-imputed copy of the raw item',
 'OA10_1': 'mean-imputed copy of the raw item',
 'OA11_1': 'mean-imputed copy of the raw item',
 'OA12_1': 'mean-imputed copy of the raw item',
 'OA13_1': 'mean-imputed copy of the raw item',
 'OA14_1': 'mean-imputed copy of the raw item',
 'OA15_1': 'mean-imputed copy of the raw item',
 'OA16_1': 'mean-imputed copy of the raw item',
 'OA17_1': 'mean-imputed copy of the raw item',
 'OA18_1': 'mean-imputed copy of the raw item',
 'OA19_1': 'mean-imputed copy of the raw item',
 'OA20_1': 'mean-imputed copy of the raw item',
 'OB1_1': 'mean-imputed copy of the raw item',
 'OB2_1': 'mean-imputed copy of the raw item',
 'OB3_1': 'mean-imputed copy of the raw item',
 'OB4_1': 'mean-imputed copy of the raw item',
 'OB5_1': 'mean-imputed copy of the raw item',
 'OB6_1': 'mean-imputed copy of the raw item',
 'OB7_1': 'mean-imputed copy of the raw item',
 'OB8_1': 'mean-imputed copy of the raw item',
 'OB9_1': 'mean-imputed copy of the raw item',
 'OB10_1': 'mean-imputed copy of the raw item',
 'OB11_1': 'mean-imputed copy of the raw item',
 'OB12_1': 'mean-imputed copy of the raw item',
 'OB13_1': 'mean-imputed copy of the raw item',
 'OB14_1': 'mean-imputed copy of the raw item',
 'OB15_1': 'mean-imputed copy of the raw item',
 'OB16_1': 'mean-imputed copy of the raw item',
 'OB17_1': 'mean-imputed copy of the raw item',
 'OB18_1': 'mean-imputed copy of the raw item',
 'OG1_1': 'mean-imputed copy of the raw item',
 'OG2_1': 'mean-imputed copy of the raw item',
 'OG3_1': 'mean-imputed copy of the raw item',
 'OG4_1': 'mean-imputed copy of the raw item',
 'OG5_1': 'mean-imputed copy of the raw item',
 'OG6_1': 'mean-imputed copy of the raw item',
 'OG7_1': 'mean-imputed copy of the raw item',
 'OG8_1': 'mean-imputed copy of the raw item',
 'OG9_1': 'mean-imputed copy of the raw item',
 'OG10_1': 'mean-imputed copy of the raw item',
 'OG11_1': 'mean-imputed copy of the raw item',
 'OG12_1': 'mean-imputed copy of the raw item',
 'OG13_1': 'mean-imputed copy of the raw item',
 'OG14_1': 'mean-imputed copy of the raw item',
 'OG15_1': 'mean-imputed copy of the raw item',
 'OG16_1': 'mean-imputed copy of the raw item',
 'OG17_1': 'mean-imputed copy of the raw item',
 'ZOK': 'composite / standardised score',
 'ZOA': 'composite / standardised score',
 'ZOG': 'composite / standardised score',
 'ZOB': 'composite / standardised score',
 'zoaxzog': 'composite / standardised score',
 'ilk_ok': 'composite / standardised score',
 'ilk_oa': 'composite / standardised score',
 'ilk_ob': 'composite / standardised score',
 'ilk_og': 'composite / standardised score',
 'Zilk_ok': 'composite / standardised score',
 'Zilk_oa': 'composite / standardised score',
 'Zilk_ob': 'composite / standardised score',
 'Zilk_og': 'composite / standardised score'}


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
