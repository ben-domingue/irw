#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/sk9mpyt4tv/1
# DOI: 10.17632/sk9mpyt4tv.1
# Data: Data EAR.xlsx
# License: CC BY 4.0 (verified on the deposit record)
# Reference: González Jimarez, A. (2026). Unidimensional, bidimensional, or bifactorial? Structural analysis of a self-esteem/anxiety measure. Mendeley Data.
#
#  respondents. 1 table(s) ship:
#   gonzalez_jimarez_2026_ear                               10 items, 1-4
#
# EAR1-EAR10, 10 items 1-4. No register row matches this block.
# The three fractional `Autoestima*` columns are subscale MEANS, which
#   is why a prefix scan saw fractional values here -- the items
#   themselves are clean integers.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: not shipped -- bare .xlsx, no label level; Spanish administration. Where the text is: the scale table in the paper behind the deposit.
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
# harvest.py does). Set GONZALEZ_EAR_RAW to point at an already-downloaded copy.
_URL = "https://data.mendeley.com/public-files/datasets/sk9mpyt4tv/files/1136678c-1c14-4c25-9f77-b745f0792072/file_downloaded"
_NAME = "Data_EAR.xlsx"


def _raw():
    override = os.environ.get("GONZALEZ_EAR_RAW")
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

STEM = "gonzalez_jimarez_2026"
BLOCKS = {'ear': (['EAR1', 'EAR2', 'EAR3', 'EAR4', 'EAR5', 'EAR6', 'EAR7', 'EAR8', 'EAR9', 'EAR10'], {1, 2, 3, 4})}
COVS = {'Sexo': 'cov_sex', 'Edad': 'cov_age', 'Escolaridad': 'cov_education', 'Ocupación': 'cov_occupation', 'Pareja': 'cov_has_partner', 'Estadocivil': 'cov_marital_status', 'AcudealPsicologo': 'cov_seen_psychologist', 'Eventoimportante': 'cov_major_life_event', 'ConnotacióndeEvento': 'cov_event_valence', 'Lugarderesidencia': 'cov_residence', 'Ingresos': 'cov_income_band'}
IDCOL = None
SKIP = {'Autoestima2_recod': "a reverse-recoded self-esteem item. Only five of the scale's items are deposited and only in recoded form, with the original coding absent, so the block is deferred rather than shipped under a scale name it cannot be checked against", 'Autoestima5_recod': "a reverse-recoded self-esteem item. Only five of the scale's items are deposited and only in recoded form, with the original coding absent, so the block is deferred rather than shipped under a scale name it cannot be checked against", 'Autoestima6_recod': "a reverse-recoded self-esteem item. Only five of the scale's items are deposited and only in recoded form, with the original coding absent, so the block is deferred rather than shipped under a scale name it cannot be checked against", 'Autoestima8_recod': "a reverse-recoded self-esteem item. Only five of the scale's items are deposited and only in recoded form, with the original coding absent, so the block is deferred rather than shipped under a scale name it cannot be checked against", 'Autoestima9_recod': "a reverse-recoded self-esteem item. Only five of the scale's items are deposited and only in recoded form, with the original coding absent, so the block is deferred rather than shipped under a scale name it cannot be checked against", 'AutoestimaNegativa': 'derived subscale mean (fractional)', 'AutoestimaPositiva': 'derived subscale mean (fractional)', 'Autoestimageneral': 'derived total mean (fractional)'}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="Data EAR.xlsx")
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
