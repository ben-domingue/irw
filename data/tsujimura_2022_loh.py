#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/AHCDXA
# DOI: 10.5534/wjmh.210171
#   Tsuru, T., Tsujimura, A., Mizushima, K., Kurosawa, M., Kure, A. et al.
#   (2023). "International Prostate Symptom Score and Quality of Life Index
#   for Lower Urinary Tract Symptoms Are Associated with Aging Males
#   Symptoms Rating Scale for Late-Onset Hypogonadism Symptoms." World
#   Journal of Men's Health 41(1). (PMC9826917)
#   Dataset: Tsujimura, A. (2022). Harvard Dataverse, V1.
# Data: Dataverse datafile 5708899, "data sheet.sav" (format=original; 1,688
#       rows x 70 columns; Japanese men with late-onset hypogonadism
#       symptoms seen at Juntendo Urayasu Hospital or an affiliated clinic,
#       Nov 2016 - Apr 2018).
# License: CC0 1.0 (Dataverse dataset licence).
#
# Item text: not shipped. Both label levels checked: no value labels on any
#   column; variable labels only on PRE_1/SEP_1 (regression outputs). The
#   item columns are SPSS defaults (VAR00003 ...), so the stems are in the
#   published instruments (Japanese IPSS/QOL index, BDI, SHIM, AMS). BDI
#   wording must not ship: irw-validate's rights register lists it
#   (Pearson, verdict block); response data is fine.
#
# Blocks. The paper names the questionnaires (AMS, IPSS + QOL index, SHIM,
#   EHS, BDI) but prints no item list, so each block is identified by its
#   total column, and each block's items sum exactly to it in every complete
#   row (asserted):
#   tsujimura_2022_ipss   ipss_1..ipss_7 = VAR00025..VAR00030, 夜間排尿回数
#                         (nocturia), plus ipss_qol = QOL. The in-block
#                         order is pinned by the subscores: 蓄尿 (storage) =
#                         VAR00026 + VAR00028 + nocturia = IPSS items 2, 4, 7
#                         and 排尿 (voiding) = VAR00025 + 27 + 29 + 30 = items
#                         1, 3, 5, 6 (asserted). IPSS items 0-5; the QOL
#                         index is the form's eighth question, 0-6 (Barry et
#                         al. 1992). It is a single item, so it ships inside
#                         the IPSS table rather than as a table of its own.
#   tsujimura_2022_bdi    bdi_1..bdi_21 = VAR00003..VAR00023 (sum = BDI),
#                         0-3. The order within the block is positional (no
#                         subscore to pin it).
#   tsujimura_2022_shim   shim_1..shim_5 = VAR00036..VAR00040 (sum = SHIM).
#                         SHIM / IIEF-5 (Rosen et al. 1999): item 1 is 1-5,
#                         items 2-5 are 0-5 (0 = no sexual activity / did not
#                         attempt). Order positional.
#   tsujimura_2022_ams    AMS1..AMS17 (source names; sum = AMS), 1-5
#                         (Heinemann et al. 1999). The psychological,
#                         somatic and sexual subscores (精神, 身体, 性) equal
#                         the standard AMS item sets (asserted), which
#                         confirms the AMS numbering.
#   The response ranges are those of the published instruments; the paper
#   itself does not print them.
#
# Cleaning (cells outside the instrument's range -> NA; the deposit's own
#   totals include them):
#   - AMS: 27 cells coded 0 across 8 respondents (0 is not an AMS option;
#     one AMS total is 13, below the possible minimum of 17).
#   - BDI: one 5 (bdi_20) and one 4 (bdi_21).
#   - SHIM: three 0s on shim_1 (item 1 has no 0 option).
#
# Dropped: BDI, IPSS, 排尿, 蓄尿, SHIM, AMS, 精神, 身体, 性 (totals and
#   subscores); EHS (Erection Hardness Score, a single item); PRE_1, SEP_1
#   (predicted AMS and its standard error from the authors' regression).
# id: row index. The ID column holds hospital patient numbers, which are
#   replaced and not shipped.
# Covariates: cov_age (年齢), cov_testosterone_ng_ml (T), cov_dheas_ug_dl,
#   cov_igf1_ng_ml, cov_cortisol_ug_dl (コルチゾール), cov_psa_ng_ml.

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://dataverse.harvard.edu/api/access/datafile/5708899"
       "?format=original")

NOCT = "夜間排尿回数"
IPSS_SRC = [f"VAR{i:05d}" for i in range(25, 31)] + [NOCT]
BDI_SRC = [f"VAR{i:05d}" for i in range(3, 24)]
SHIM_SRC = [f"VAR{i:05d}" for i in range(36, 41)]
AMS = [f"AMS{i}" for i in range(1, 18)]

RENAME = {**{c: f"ipss_{k}" for k, c in enumerate(IPSS_SRC, 1)},
          "QOL": "ipss_qol",
          **{c: f"bdi_{k}" for k, c in enumerate(BDI_SRC, 1)},
          **{c: f"shim_{k}" for k, c in enumerate(SHIM_SRC, 1)}}

TABLES = {
    "tsujimura_2022_ipss": {**{f"ipss_{k}": set(range(0, 6))
                               for k in range(1, 8)},
                            "ipss_qol": set(range(0, 7))},
    "tsujimura_2022_bdi": {f"bdi_{k}": set(range(0, 4)) for k in range(1, 22)},
    "tsujimura_2022_shim": {"shim_1": set(range(1, 6)),
                            **{f"shim_{k}": set(range(0, 6))
                               for k in range(2, 6)}},
    "tsujimura_2022_ams": {c: set(range(1, 6)) for c in AMS},
}
TOTALS = {"BDI": BDI_SRC, "IPSS": IPSS_SRC, "SHIM": SHIM_SRC, "AMS": AMS,
          "蓄尿": ["VAR00026", "VAR00028", NOCT],
          "排尿": ["VAR00025", "VAR00027", "VAR00029", "VAR00030"],
          "精神": ["AMS6", "AMS7", "AMS8", "AMS11", "AMS13"],
          "身体": ["AMS1", "AMS2", "AMS3", "AMS4", "AMS5", "AMS9", "AMS10"],
          "性": ["AMS12", "AMS14", "AMS15", "AMS16", "AMS17"]}
OTHER_DROPPED = {"EHS", "PRE_1", "SEP_1", "ID"}
COVS = {"年齢": "cov_age", "T": "cov_testosterone_ng_ml",
        "DHEAS": "cov_dheas_ug_dl", "IGF1": "cov_igf1_ng_ml",
        "コルチゾール": "cov_cortisol_ug_dl", "PSA": "cov_psa_ng_ml"}
EXPECTED_OOR = {"tsujimura_2022_ams": 27, "tsujimura_2022_bdi": 2,
                "tsujimura_2022_shim": 3}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (1688, 70), d.shape

    # Balance the books.
    items = set(IPSS_SRC) | {"QOL"} | set(BDI_SRC) | set(SHIM_SRC) | set(AMS)
    known = items | set(TOTALS) | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not meta.variable_value_labels
    assert d["ID"].is_unique

    for tot, cols in TOTALS.items():
        ok = d[cols].notna().all(axis=1)
        assert (d.loc[ok, cols].sum(axis=1) == d.loc[ok, tot]).all(), tot
    assert not d.drop(columns="ID").duplicated().any()

    d = d.drop(columns=["ID"]).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={**RENAME, **COVS})
    cov_cols = list(COVS.values())

    # Out-of-range cells -> NA (counted, so a changed deposit fails loudly).
    oor = {}
    for table, spec in TABLES.items():
        for it, allowed in spec.items():
            bad = d[it].notna() & ~d[it].isin(allowed)
            oor[table] = oor.get(table, 0) + int(bad.sum())
            d.loc[bad, it] = pd.NA
    oor = {k: v for k, v in oor.items() if v}
    assert oor == EXPECTED_OOR, oor

    names = []
    for table, spec in TABLES.items():
        its = list(spec)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            assert not set(g["resp"]) - spec[it], (table, it)
        pv = {i: spec[i] for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        long["cov_age"] = long["cov_age"].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
