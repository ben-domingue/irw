#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9883526
# DOI: 10.1038/s41598-023-28636-7
#   "Psychometric properties of the 12-item Stroke-Specific Quality of Life
#   Scale among stroke survivors in Hong Kong" (Fong, Lo & Ho, 2023),
#   Scientific Reports 13:1510.
# Data: Scientific Reports supplementary file 41598_2023_28636_MOESM1_ESM.xlsx
#       ("Supplementary Dataset_TCT Fong", 184 x 137, one row per respondent),
#       fetched from the Europe PMC supplementaryFiles zip (the zip holds only
#       this workbook and the article figure).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. Both label levels checked: the workbook has no
#   variable labels or value labels (plain .xlsx, headers are positional codes
#   such as T0_SRQOL01, T0_HADS07). The paper prints no item wording; it names
#   the instruments (Chinese SSQOL-12, HADS, 6-item State Hope Scale, Rosenberg
#   SES, SF-12) and gives the anchors in Methods. The wording would have to come
#   from the cited published instruments (Chinese versions, administered in
#   Chinese), i.e. positional labels + an off-deposit source.
#
# Sample: 184 community-dwelling stroke survivors aged 18-64 in Hong Kong,
# baseline (T0); 148 completed the SSQOL-12 again two months later (T1).
#
# Tables (item = source header with its T0_/T1_ wave prefix removed):
#   fong_2023_ssqol12  SSQOL-12, 12 items, 1 = agree completely ... 5 = disagree
#                      completely; T0 and T1 stacked, wave = 1 (baseline) / 2
#                      (2-month follow-up)
#   fong_2023_hads     Hospital Anxiety and Depression Scale, 14 items, stored
#                      1-4 (4-point format as administered; see below)
#   fong_2023_shs      State Hope Scale, 6 items, 1 = Definitely false ...
#                      8 = Definitely true
#   fong_2023_rses     Rosenberg Self-Esteem Scale, 10 items, 1 = Disagree very
#                      much ... 4 = Agree very much
#   fong_2023_sf12     SF-12 Health Survey, 12 items on their own formats
#                      (1-5, 1-3, 0/1 yes-no for items 4-7, 1-6)
#
# 999999 is the workbook's missing code; it is set to missing per cell.
# The HADS, RSE and SF-12 items are shipped as stored (unreversed): the
# workbook's *R copies are derived (HADSnnR = HADSnn - 1 or 4 - HADSnn, asserted
# below; RSEnnR reversed), and the sf*phy/sf*men columns are SF-12 scoring
# weights; all of those and every total/subscale score are skipped.
# The simplified modified Rankin Scale questionnaire (T0_MRS01-05) is skipped:
# it is a branching yes/no decision tree whose later questions are only asked
# conditionally (MRS05 has 6 answers, all "1"), not a set of parallel items;
# T0_MRS is the derived mRS grade.
#
# id: `Caseno` is a study case number with a 999999 sentinel on one row; the
# row index is used instead (never a hash), per the identifier ruling.
# No imputation (every item cell is an integer; the paper states missing data
# were handled under MAR in the model, not filled in), no duplicate rows.

import io
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "fong_2023_ssqol"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9883526/supplementaryFiles"
FNAME = "41598_2023_28636_MOESM1_ESM.xlsx"


def fetch() -> pd.DataFrame:
    p = RAW_DIR / FNAME
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FNAME))
    return pd.read_excel(p)


def codes(prefix, n):
    return [f"{prefix}{i:02d}" for i in range(1, n + 1)]


def main() -> None:
    d = fetch()
    assert d.shape == (184, 137), d.shape
    d = d.replace(999999, np.nan)
    d.insert(0, "id", np.arange(1, len(d) + 1))

    # derived HADS copies: check before skipping them
    for i in range(1, 15):
        a, b = d[f"T0_HADS{i:02d}"], d[f"T0_HADS{i:02d}R"]
        m = a.notna()
        assert ((b[m] == a[m] - 1).all() or (b[m] == 4 - a[m]).all()), i

    tables = {
        "fong_2023_hads": (codes("HADS", 14), {1, 2, 3, 4}),
        "fong_2023_shs": (codes("ASHS", 6), set(range(1, 9))),
        "fong_2023_rses": (codes("RSE", 10), {1, 2, 3, 4}),
        "fong_2023_sf12": (codes("SF12", 12), None),
    }
    sf12_pv = {"SF1201": {1, 2, 3, 4, 5}, "SF1202": {1, 2, 3}, "SF1203": {1, 2, 3},
               "SF1204": {0, 1}, "SF1205": {0, 1}, "SF1206": {0, 1}, "SF1207": {0, 1},
               "SF1208": {1, 2, 3, 4, 5}, "SF1209": set(range(1, 7)),
               "SF1210": set(range(1, 7)), "SF1211": set(range(1, 7)),
               "SF1212": set(range(1, 7))}

    cov = {"DI_GENDER": "cov_gender", "DI_AGE": "cov_age",
           "DI_DOA_D": "cov_stroke_duration_months",
           "DI_ST": "cov_stroke_type", "DI_EL": "cov_education_level",
           "DI_MS": "cov_marital_status"}
    d = d.rename(columns=cov)
    cov_cols = list(cov.values())

    used = {"Caseno"} | set(cov)
    used |= {f"T0_{c}" for items, _ in tables.values() for c in items}
    used |= {f"T{w}_{c}" for w in (0, 1) for c in codes("SRQOL", 12)}
    skipped = {}
    for c in d.columns:
        if c in ("id",) or c in cov_cols:
            continue
        if re.fullmatch(r"T0_(HADS\d\dR|RSE\d\dR)", c):
            skipped[c] = "reverse/rescored copy of a shipped item"
        elif re.fullmatch(r"T0_sf\d+(phy|men)", c):
            skipped[c] = "SF-12 scoring weight (derived)"
        elif re.fullmatch(r"T0_MRS0\d", c):
            skipped[c] = "simplified mRS branching decision-tree question (see header)"
        elif c in ("T0_MRS", "T0_ASHS", "T0_RSE", "T0_HADS_A", "T0_HADS_D",
                   "T0_sfphysco", "T0_sfmensco", "T0_sf12", "T0_SRQOL_PHY",
                   "T1_SRQOL_PHY", "T0_SRQOL_PSY", "T1_SRQOL_PSY", "T0_SRQOL",
                   "T1_SRQOL"):
            skipped[c] = "total / subscale score (composite)"
        elif c == "T1dropout":
            skipped[c] = "attrition flag (follow-up participation)"
        elif c == "DI_D":
            skipped[c] = "undocumented 0/1 demographic code (meaning not given in paper)"
        elif c == "Caseno":
            pass
        elif c not in used:
            raise AssertionError(f"unaccounted column {c}")
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")
    accounted = used | set(skipped)
    orig = set(d.columns) - {"id"} - set(cov_cols) | set(cov)
    assert orig == accounted, orig ^ accounted

    out = {}
    for name, (items, pv) in tables.items():
        t = d.rename(columns={f"T0_{c}": c for c in items})
        t = t.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        out[name] = (t, {i: pv for i in items} if pv else sf12_pv, None)

    # SSQOL-12, two waves
    parts = []
    for w in (0, 1):
        items = codes("SRQOL", 12)
        t = d.rename(columns={f"T{w}_{c}": c for c in items})
        t = t.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        t["wave"] = w + 1
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    out["fong_2023_ssqol12"] = (t, {i: {1, 2, 3, 4, 5} for i in codes("SRQOL", 12)}, "wave")

    names = list(out)
    assert len(names) == len(set(names))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv, wave) in out.items():
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        lead = ["id", "item", "resp"] + (["wave"] if wave else [])
        t = t[lead + cov_cols].sort_values(lead[:1] + (["wave"] if wave else []) + ["item"])
        keys = ["id", "item"] + (["wave"] if wave else [])
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100, name
        for i, s in pv.items():
            got = set(t.loc[t["item"] == i, "resp"])
            assert got <= s, (name, i, got)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
