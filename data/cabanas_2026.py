#!/usr/bin/env python3
# Source: https://zenodo.org/records/20692950
# DOI: 10.5281/zenodo.20692950
# Data: data 061426.xlsx
# License: cc-by-4.0 (verified on the deposit record)
# Reference: Alba Cabañas, M., Gómez García, L. D., & Isaac Roque, D. (2026). Emotional Competence, Entrepreneurial Self-Efficacy, and Entrepreneurial Intention among university students. Zenodo.
#
#  respondents. 3 table(s) ship:
#   cabanas_2026_emotional_competence              21 items, 1-5
#   cabanas_2026_entrepreneurial_intention          3 items, 1-5
#   cabanas_2026_entrep_self_efficacy               5 items, 1-5
#
# Three blocks, all 1-5, named by the deposit's own title. One file per
#   scale, following the batch-B convention for multi-construct
#   questionnaires. `Age` is a 1-4 band, not years, so it ships as
#   cov_age_band.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: not shipped -- bare .xlsx export, no label level. Where the text is: the instrument tables in the paper behind zenodo 20692950.
#
# From the #3077 blank-flag re-mine: this key was written to
# repo_triage_seen_keys.csv before irw#2222 added the flag column, so the key was
# recorded and the verdict never was. It was not a rejection -- nobody had looked.
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402
from irw_triage_updated import load_table  # noqa: E402

# --- raw input -------------------------------------------------------------
# Self-contained by design: fetches the deposit itself and caches it, so it
# re-runs in a fresh checkout (which is what metadata/covariate_labels/
# harvest.py does). Set CABANAS_RAW to point at an already-downloaded copy.
_URL = "https://zenodo.org/api/records/20692950/files/data%20061426.xlsx/content"
_NAME = "data_061426.xlsx"


def _raw():
    override = os.environ.get("CABANAS_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as fh:
            fh.write(r.read())
    return dest


OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

STEM = "cabanas_2026"
BLOCKS = {'emotional_competence': (['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'E13', 'E14', 'E15', 'E16', 'E17', 'E18', 'E19', 'E20', 'E21'], {1, 2, 3, 4, 5}), 'entrepreneurial_intention': (['EI1', 'EI2', 'EI3'], {1, 2, 3, 4, 5}), 'entrep_self_efficacy': (['SE1', 'SE2', 'SE3', 'SE4', 'SE5'], {1, 2, 3, 4, 5})}
COVS = {'University': 'cov_university', 'Country': 'cov_country', 'Type of program': 'cov_program_type', 'Age': 'cov_age_band', 'Entrep': 'cov_entrepreneur', 'Exp': 'cov_experience', 'Gen': 'cov_gender'}
IDCOL = None
SKIP = {}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="data 061426.xlsx")
    print(f"raw: {df.shape}")

    if IDCOL:
        assert df[IDCOL].nunique() == len(df), (
            f"{IDCOL} is not unique ({df[IDCOL].nunique()} of {len(df)}) -- "
            "it cannot be the person id")
        ids = df[IDCOL].astype(str).values
    else:
        # No person identifier is deposited, so the row index IS the person.
        ids = [str(i + 1) for i in range(len(df))]

    # Balance the books: every source column is shipped, a covariate, the id,
    # or skipped for a printed reason.
    shipped = {c for cols, _ in BLOCKS.values() for c in cols}
    accounted = shipped | set(COVS) | set(SKIP) | ({IDCOL} if IDCOL else set())
    for c, why in SKIP.items():
        if c in df.columns:
            print(f"  skip {c!r}: {why}")
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    missing = [c for c in shipped if c not in df.columns]
    assert not missing, f"expected item columns absent: {missing}"

    cov = {v: df[k] for k, v in COVS.items() if k in df.columns}
    written = []
    for suffix, (cols, permitted) in BLOCKS.items():
        long = df[cols].copy()
        long.insert(0, "id", ids)
        for name, series in cov.items():
            long[name] = series.values
        out = long.melt(id_vars=["id"] + list(cov),
                        value_vars=cols, var_name="item", value_name="resp")
        out = out.dropna(subset=["resp"])
        out["resp"] = out["resp"].astype(int)
        # The permitted set is asserted PER TABLE, never inherited from a
        # sibling block -- that is what catches a 1-6 block in a 1-5 family.
        extra = set(out["resp"].unique()) - permitted
        assert not extra, f"{suffix}: resp values outside {sorted(permitted)}: {extra}"
        assert out["item"].nunique() > 1, f"{suffix}: only one distinct item"
        assert out["id"].nunique() >= 100, (
            f"{suffix}: {out['id'].nunique()} unique ids, below the floor of 100")
        out = out[["id", "item", "resp"] + list(cov)]

        pv = {i: set(permitted) for i in cols}
        checks = run_qc(out, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (suffix, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(out, label=f"{STEM}_{suffix}",
                                             profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors,             (suffix, [(f.check, f.message) for f in report.errors])

        name = f"{STEM}_{suffix}"
        assert name not in written, f"duplicate output name {name}"
        written.append(name)
        path = os.path.join(OUT_DIR, name + ".csv")
        out.to_csv(path, index=False, na_rep="NA")
        print(f"  {name}: {out['id'].nunique()} ids x {out['item'].nunique()} "
              f"items = {len(out)} responses -> {path}")
    return written


if __name__ == "__main__":
    convert()
