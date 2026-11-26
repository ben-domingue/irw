#!/usr/bin/env python3
# Source: https://zenodo.org/records/22693332
# DOI: 10.5281/zenodo.22693332 (data)
#   Ozen S (2026). Interrelationships between pruritus, fatigue, and daytime sleepiness in patients undergoing hemodialysis: implications for symptom management [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22693332
# License: CC BY 4.0 (record metadata)
# Data: 'Regresyon_Temiz sav 5.09.2026.sav', 127 hemodialysis patients with pruritus at five centres in Turkiye; id = row
#   order. UYKU1-8 = Epworth Sleepiness Scale, YSO1-9 = Fatigue Severity Scale (value labels 0-7), KO* = 5-D Itch Scale.
# Tables: Epworth and FSS.
# Not shipped: the 5-D Itch items (codes disagree with their value labels), totals, dummies, regression diagnostics.
# Covariates: age, sex, education, marital, employment, income, smoking, kidney-failure and dialysis duration, dialysis session, Kt/V.
# PII: none.
# Item text: value labels only (response options); stems are the published ESS / FSS (Turkish versions).
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
URL = 'https://zenodo.org/api/records/22693332/files/Regresyon_Temiz%20sav%205.09.2026.sav/content'
N_ROWS = 127
ID_COL = None
COVS = {'Yaş': 'cov_age',
 'cinsiyet': 'cov_sex',
 'Egitimdurumu': 'cov_education',
 'MedeniDurum': 'cov_marital',
 'Çalışmadurumu': 'cov_employed',
 'Gelirdüzeyi': 'cov_income',
 'sigaraiçmedurumu': 'cov_smoking',
 'böbrekyetmezliğisüresi': 'cov_kidney_failure_duration',
 'nekadarsüredirdiyalizegiriyo': 'cov_dialysis_duration',
 'diyalizegirdiğiseans': 'cov_dialysis_session',
 'KAndeğeri': 'cov_ktv'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'ozen_2026_epworth': ['UYKU1', 'UYKU2', 'UYKU3', 'UYKU4', 'UYKU5', 'UYKU6', 'UYKU7', 'UYKU8'],
 'ozen_2026_fss': ['YŞÖ1', 'YŞÖ2', 'YŞÖ3', 'YŞÖ4', 'YŞÖ5', 'YŞÖ6', 'YŞÖ7', 'YŞÖ8', 'YŞÖ9']}
# (lo, hi) response range per table
RANGES = {'ozen_2026_epworth': (0, 3), 'ozen_2026_fss': (0, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Neişyaptığı': 'composite, dummy, regression diagnostic or constant column',
 'haftadakaçseansdiyalizegiriyor': 'composite, dummy, regression diagnostic or constant column',
 'hemodiyalizdekalmasüresinekadar': 'composite, dummy, regression diagnostic or constant column',
 'KAşıntınızoluyormu': 'composite, dummy, regression diagnostic or constant column',
 'Kaşıntınızvarsadahaçoknezamanoluyor': 'composite, dummy, regression diagnostic or constant column',
 'UYKUÖLÇEĞİTOPLAM': 'composite, dummy, regression diagnostic or constant column',
 'YORGUNLUKŞİDDETÖLÇEĞİTOPLAM': 'composite, dummy, regression diagnostic or constant column',
 'KAŞINTOPLAM': 'composite, dummy, regression diagnostic or constant column',
 'KÖ1': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
        'selected for pruritus), so not shipped',
 'KÖ2': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
        'selected for pruritus), so not shipped',
 'KÖ3': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
        'selected for pruritus), so not shipped',
 'KÖ4': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
        'selected for pruritus), so not shipped',
 'KÖ41': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
         'selected for pruritus), so not shipped',
 'KÖ42': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
         'selected for pruritus), so not shipped',
 'KÖ43': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
         'selected for pruritus), so not shipped',
 'KÖ44': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
         'selected for pruritus), so not shipped',
 'KÖ5': '5-D Itch item: the stored codes disagree with the value labels (e.g. code 1 labelled "none" on a sample '
        'selected for pruritus), so not shipped',
 'KAŞINTITOPLAM': 'composite, dummy, regression diagnostic or constant column',
 'Boyut4': 'composite, dummy, regression diagnostic or constant column',
 'kaşıntı_toplam': 'composite, dummy, regression diagnostic or constant column',
 'FSS_Toplam': 'composite, dummy, regression diagnostic or constant column',
 'Cinsiyet_Erkek': 'composite, dummy, regression diagnostic or constant column',
 'Eğitim_Okuryazardeğil': 'composite, dummy, regression diagnostic or constant column',
 'Eğitim_İlköğretim': 'composite, dummy, regression diagnostic or constant column',
 'Seans_Öğle': 'composite, dummy, regression diagnostic or constant column',
 'Kaşıntı_Sırasında': 'composite, dummy, regression diagnostic or constant column',
 'Kaşıntı_Sonrasında': 'composite, dummy, regression diagnostic or constant column',
 'Kaşıntı_Tümdönemler': 'composite, dummy, regression diagnostic or constant column',
 'ZRE_1': 'composite, dummy, regression diagnostic or constant column',
 'MAH_1': 'composite, dummy, regression diagnostic or constant column',
 'COO_1': 'composite, dummy, regression diagnostic or constant column',
 'LEV_1': 'composite, dummy, regression diagnostic or constant column'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


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
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
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
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
