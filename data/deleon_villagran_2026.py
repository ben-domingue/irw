#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/p622ddkyxf/2
# DOI: 10.17632/p622ddkyxf.2
# Data: Encuesta TMMS24.sav
# License: CC BY 4.0 (verified on the deposit record)
# Reference: Deleon Villagran, M. (2026). Data - The Trait Meta-Mood Scale-24 (TMMS-24) and Academic performance. Mendeley Data.
#
#  respondents. 1 table(s) ship:
#   deleon_villagran_2026_tmms24                            24 items, 1-5
#
# The Trait Meta-Mood Scale-24, Spanish (Fernandez-Berrocal adaptation),
#   24 items 1-5. NO register row for the TMMS -- logged as a
#   register-row request.
# `caso` is a case number, unique over all 491 rows, so it is the id.
#
# PII: none. All three screen surfaces were checked -- column name, values, and
#   the SPSS/Stata variable label where the file has one.
#
# Item text: not shipped. Every item carries its full Spanish stem in the variable label, so this is extraction-solved -- but the administration is Spanish with no author-supplied English, so the English would be IRW-generated and owes a translation_source and an issues-page callout. Where the text is: the .sav variable labels, Item4_01..Item4_24.
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
# harvest.py does). Set DELEON_RAW to point at an already-downloaded copy.
_URL = "https://data.mendeley.com/public-files/datasets/p622ddkyxf/files/1cb56a91-108c-4a24-b4bf-6683b91c1997/file_downloaded"
_NAME = "Encuesta_TMMS24.sav"


def _raw():
    override = os.environ.get("DELEON_RAW")
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

STEM = "deleon_villagran_2026"
BLOCKS = {'tmms24': (['Item4_01', 'Item4_02', 'Item4_03', 'Item4_04', 'Item4_05', 'Item4_06', 'Item4_07', 'Item4_08', 'Item4_09', 'Item4_10', 'Item4_11', 'Item4_12', 'Item4_13', 'Item4_14', 'Item4_15', 'Item4_16', 'Item4_17', 'Item4_18', 'Item4_19', 'Item4_20', 'Item4_21', 'Item4_22', 'Item4_23', 'Item4_24'], {1, 2, 3, 4, 5})}
COVS = {'Sexo': 'cov_sex', 'Edad': 'cov_age', 'CRegional': 'cov_campus', 'Facultad': 'cov_faculty', 'Carrera': 'cov_programme', 'Nivel_Academico': 'cov_academic_year', 'Apoyo_económico': 'cov_family_support', 'Situacion_Laboral': 'cov_employment'}
IDCOL = 'caso'
SKIP = {'Calificacion_real': 'self-reported grade average, a continuous outcome rather than an item', 'Nota_real': 'banding of Calificacion_real', 'Calificacion_ideal': 'self-reported ideal grade, an outcome', 'Nota_ideal': 'banding of Calificacion_ideal', 'Abrumado': 'a single standalone item, not a scale', 'Postergar_tareas': 'a single standalone item, not a scale', 'AtE_Suma': 'TMMS-24 subscale sum', 'ClE_Suma': 'TMMS-24 subscale sum', 'RdlE_Suma': 'TMMS-24 subscale sum', 'AtE_Niveles': 'banding of a subscale sum', 'ClE_Niveles': 'banding of a subscale sum', 'RdlE_Niveles': 'banding of a subscale sum', 'AteNivel': 'banding of a subscale sum', 'ClENivel': 'banding of a subscale sum', 'RdlENivel': 'banding of a subscale sum', 'Calificación_Real_': 'banding of a grade', 'Calificación_Ideal_': 'banding of a grade'}


def convert():
    df = load_table(open(_raw(), "rb").read(), filename="Encuesta TMMS24.sav")
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
