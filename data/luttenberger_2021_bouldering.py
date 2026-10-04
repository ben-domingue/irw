#!/usr/bin/env python3
# Source: https://zenodo.org/records/5645184
# DOI: 10.1111/bjc.12347
#   Luttenberger, K., Karg-Hefner, N., Berking, M., Kind, L., Weiss, M.,
#   Kornhuber, J., & Dorscht, L. (2022). Bouldering psychotherapy is not
#   inferior to cognitive behavioural therapy in the group treatment of
#   depression: A randomized controlled trial. British Journal of Clinical
#   Psychology, 61(2), 465-493. (Found by Crossref title search; the deposit
#   carries no related identifier. Open access (CC BY-NC-ND) but behind a
#   bot wall at Wiley and at the FAU repository, so only the Europe PMC
#   abstract, PMID 34791669, was read.)
#   Dataset: Luttenberger, K., Dorscht, L., Kind, L., & Karg-Hefner, N.
#   (2021). Zenodo. https://doi.org/10.5281/zenodo.5645184
# Data: Repository_BPT CBT_Rohdaten.sav (156 rows x 184 columns; German
#       outpatients with a DSM-IV depressive episode, randomised to group
#       bouldering psychotherapy (BPT, 79) or group CBT (77)).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: the t0/t1/t4 item
#   variable labels are short German symptom tags ("t0 PHQ Traurigkeit",
#   "t0 FERUS 1"), not stems; value labels carry the German anchors for every
#   block except SIGMA (none). The screening PHQ (SPHQ1-9) carries full
#   German PHQ-9 stems, but t0phq8 is tagged "Innere Anspannung" while SPHQ8
#   is the psychomotor item, so the tags cannot be trusted to tie code to
#   stem. Stems are in the published German instruments (PHQ-D, GAD-7,
#   SWE, FERUS, SCL-90-R social insecurity (rights block), FKB-20, RSES).
#
# Design (abstract): MADRS (observer-rated via the SIGMA structured
# interview) and PHQ-9 at the start of treatment, at its end, and one year
# after the end of treatment. The file's prefixes give the occasions:
#   wave 1 = screening (SPHQ1-9, PHQ-9 only)
#   wave 2 = t0, pre-treatment
#   wave 3 = t1, post-treatment (10 weeks)
#   wave 4 = t4, 12-month follow-up (SIGMA and PHQ-9 only)
# The deposit holds no t2/t3. SPHQ and t0phq are separate administrations of
# the same nine items (same order: each SPHQk correlates most with t0phqk,
# asserted), so the screening PHQ ships as wave 1 rather than being dropped.
# treat: 1 = BPT (Gruppe_t0t1 = 1), 0 = CBT (Gruppe_t0t1 = 2), the trial's
#   active comparator.
# cov_dropout: Abbruch50_dich (1 = attended < 50% of sessions).
#
# Tables (item codes drop the wave prefix; the file's t4sphq1 typo is phq1):
#   luttenberger_2021_madrs   sigma_1-10, MADRS items 0-6 (standard MADRS
#       format; no value labels in the file -- the abstract names the MADRS,
#       and every observed value is a whole number in 0-6), waves 2-4.
#   luttenberger_2021_phq9    phq1-9, 0-3 (value labels), waves 1-4.
#   luttenberger_2021_gad7    gad_1-7, 0-3 (value labels), waves 2-3.
#   luttenberger_2021_gse     gse_1-10, German General Self-Efficacy, 1-4
#       (value labels: stimmt nicht .. stimmt genau), waves 2-3.
#   luttenberger_2021_ferus   ferus_1-12, FERUS items, 1-5 (value labels:
#       stimmt nicht .. stimmt sehr), waves 2-3. Which FERUS subscale these
#       12 items are is not stated anywhere readable.
#   luttenberger_2021_scl_social  scl_1-9, SCL-90-R interpersonal
#       sensitivity / social insecurity items, 0-4 (value labels), waves 2-3.
#   luttenberger_2021_fkb     fkb_1-10, FKB-20 vital body dynamics items,
#       1-5 (value labels), waves 2-3.
#   luttenberger_2021_rses    ses_1-10, Rosenberg Self-Esteem (German), 0-3
#       (value labels), waves 2-3.
# Permitted sets are the value labels (and 0-6 for SIGMA); every block's
# labels are asserted unchanged across its waves.
#
# Dropped: none besides the design columns above (Gruppe_t0t1 -> treat,
#   Abbruch50_dich -> cov_dropout). No respondent id in the file; id is the
#   row index. No free-text, date or demographic columns (checked).
# The "fractional" cells a naive x % 1 test reports are NaN; every observed
# value is a whole number (asserted).

import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/5645184/files/"
       "Repository_BPT%20CBT_Rohdaten.sav/content")

WAVES = {"S": 1, "t0": 2, "t1": 3, "t4": 4}
# table -> (item stem in output, {wave prefix: column pattern}, permitted)
BLOCKS = {
    "luttenberger_2021_madrs": ("sigma_{}", 10, {
        "t0": "t0sigma_{}", "t1": "t1sigma_{}", "t4": "t4sigma_{}"},
        range(0, 7)),
    "luttenberger_2021_phq9": ("phq{}", 9, {
        "S": "SPHQ{}", "t0": "t0phq{}", "t1": "t1phq{}", "t4": "t4phq{}"},
        range(0, 4)),
    "luttenberger_2021_gad7": ("gad_{}", 7, {
        "t0": "t0gad_{}", "t1": "t1gad_{}"}, range(0, 4)),
    "luttenberger_2021_gse": ("gse_{}", 10, {
        "t0": "t0gse_{}", "t1": "t1gse_{}"}, range(1, 5)),
    "luttenberger_2021_ferus": ("ferus_{}", 12, {
        "t0": "t0ferus_{}", "t1": "t1ferus_{}"}, range(1, 6)),
    "luttenberger_2021_scl_social": ("scl_{}", 9, {
        "t0": "t0scl_{}", "t1": "t1scl_{}"}, range(0, 5)),
    "luttenberger_2021_fkb": ("fkb_{}", 10, {
        "t0": "t0fkb_{}", "t1": "t1fkb_{}"}, range(1, 6)),
    "luttenberger_2021_rses": ("ses_{}", 10, {
        "t0": "t0ses_{}", "t1": "t1ses_{}"}, range(0, 4)),
}
DESIGN = {"Gruppe_t0t1", "Abbruch50_dich"}


def col_name(pattern, k):
    c = pattern.format(k)
    return "t4sphq1" if c == "t4phq1" else c


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
    assert d.shape == (156, 184), d.shape
    assert d["Gruppe_t0t1"].value_counts().to_dict() == {1.0: 79, 2.0: 77}
    assert set(d["Abbruch50_dich"].dropna()) <= {0.0, 1.0}
    assert not d.duplicated().any()

    # Balance the books.
    used = set(DESIGN)
    for _, (_, k, pats, _) in BLOCKS.items():
        for p in pats.values():
            used |= {col_name(p, i) for i in range(1, k + 1)}
    assert used == set(d.columns), used ^ set(d.columns)
    assert all(pd.api.types.is_numeric_dtype(d[c]) for c in d.columns)
    vals = d.drop(columns=list(DESIGN)).stack().dropna()
    assert (vals % 1 == 0).all()

    # Screening PHQ and t0 PHQ are the same items in the same order.
    sp = d[[f"SPHQ{i}" for i in range(1, 10)]]
    t0 = d[[f"t0phq{i}" for i in range(1, 10)]]
    cr = pd.concat([sp, t0], axis=1).corr().iloc[:9, 9:].values
    assert (cr.argmax(axis=1) == np.arange(9)).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["treat"] = (d["Gruppe_t0t1"] == 1).astype(int)
    d["cov_dropout"] = d["Abbruch50_dich"].astype("Int64")

    names = []
    for table, (stem, k, pats, rng) in BLOCKS.items():
        allowed = set(rng)
        labels = None
        parts = []
        for wp, p in pats.items():
            cols = [col_name(p, i) for i in range(1, k + 1)]
            vl = meta.variable_value_labels.get(cols[0])
            if table != "luttenberger_2021_madrs":
                for c in cols:
                    assert meta.variable_value_labels.get(c) == vl, c
                assert set(vl) == allowed, (table, vl)
                labels = labels or vl
                assert vl == labels, (table, wp)
            else:
                assert all(c not in meta.variable_value_labels for c in cols)
            part = d[["id", "treat", "cov_dropout"] + cols].rename(
                columns={c: stem.format(i + 1) for i, c in enumerate(cols)})
            part = part.melt(id_vars=["id", "treat", "cov_dropout"],
                             var_name="item", value_name="resp")
            part["wave"] = WAVES[wp]
            parts.append(part)
        long = pd.concat(parts, ignore_index=True)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp", "wave", "treat", "cov_dropout"]]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item", "wave"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == k > 1
        pv = {stem.format(i): allowed for i in range(1, k + 1)}
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
              f"waves={sorted(long['wave'].unique())} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
