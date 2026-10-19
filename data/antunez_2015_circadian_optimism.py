#!/usr/bin/env python3
# Source: https://zenodo.org/records/18681901
# DOI: 10.5281/zenodo.18681901
# Data: Dataset.sav (SPSS; variable and value labels present)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Antúnez Vílchez, J. M., Adan, A., & Navarro, J. F. (2015).
#   Circadian typology is related to resilience and optimism in healthy adults.
#
# 1,937 healthy Spanish adults, three instruments on three different scales --
# which is the `resp_scale_mixed` flag the triage raised.
#
#   RMEQ1..RMEQ5   reduced Morningness-Eveningness Questionnaire  -> _rmeq
#   LOT1..LOT10    Life Orientation Test-Revised, 1-5             -> _lotr
#   CDR1..CDR10    Connor-Davidson Resilience Scale-10            -> NOT SHIPPED
#
# RIGHTS, and this is the reason two of the three blocks move and one does not:
#
#   * **CDR1..CDR10 is the CD-RISC-10 and the register BLOCKS it**
#     ("Connor-Davidson Resilience Scale (CD-RISC-25 / CD-RISC-10)"). The
#     block is dropped whole. Note that the register's matcher for that row is
#     `^C[0-9]{1,2}$|cd[-_]?risc`, which does NOT match `CDR1` -- the first
#     alternative wants C followed only by digits, the second wants the word
#     "risc". So an automated rights check would have passed this block. It was
#     caught by reading the stems against
#     itemtext/register_gaps_2026-10-18.csv, and that file gains a row for it.
#   * **LOT-R is verdict `ship_with_note`**, so the LOT block ships and owes a
#     public issues-page note (recorded in itemtext_provenance.csv).
#   * **The RMEQ has no register row at all.** Nothing blocks it, but a miss is
#     not an all-clear, so it is logged in register_gaps_2026-10-18.csv as an
#     uncovered published instrument (Adan & Almirall's reduction of Horne &
#     Östberg).
#
# PER-ITEM SCALES, NOT ONE SHARED SET. The five RMEQ items have deliberately
# different response sets -- RMEQ1/3/4 run 1-5, RMEQ2 runs 1-4, and RMEQ5 is
# scored 0/2/4/6 -- because that is how the MEQ is built. Asserting a single
# permitted set across the block would fail on correct data, so each item is
# checked against **its own value labels from the .sav**, which is the
# source's own documented codebook. Observed-range differences inside this
# block are instrument design, not a defect.
#
# CDRISC / LOTR / RMEQ_TOT are the three scored totals and are dropped.
#
# Item text: NOT shipped. BOTH label levels were checked. Variable labels are
# EMPTY for every item (only `Marcatemporal` and `EST_TRAB` carry one); value
# labels ARE populated for all 25 items, so the deposit holds the response
# anchors but not one question stem. Shipping option_text without stems is
# exactly what irw#1770 forbids. Where the text is: the published RMEQ and
# LOT-R themselves, both canonical.

import os

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402


# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set ANTUNEZ_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/18681901/files/Dataset.sav/content")
_NAME = "zenodo_18681901__Dataset.sav"


def _raw():
    override = os.environ.get("ANTUNEZ_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent":
                           "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(dest, "wb") as fh:
            fh.write(r.read())
    return dest

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RMEQ = [f"RMEQ{i}" for i in range(1, 6)]
LOTR = [f"LOT{i}" for i in range(1, 11)]
CDRISC10 = [f"CDR{i}" for i in range(1, 11)]

COVS = {"Edad": "cov_age", "Sexo": "cov_sex", "TC": "cov_circadian_typology",
        "Estado_civil": "cov_marital_status", "Estudios": "cov_education",
        "Laboral": "cov_employment", "Turno_nocturno": "cov_night_shift",
        "Dep_semana": "cov_exercise_days", "Dep_horas": "cov_exercise_hours"}

BLOCKS = {"rmeq": RMEQ, "lotr": LOTR}


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    print(f"raw: {df.shape}")
    vlabs = meta.variable_value_labels or {}

    assert df["Codigo_user"].nunique() == len(df), "Codigo_user is not unique"
    df = df.rename(columns={"Codigo_user": "id"})

    print(f"dropping {CDRISC10[0]}..{CDRISC10[-1]}: the CD-RISC-10, which the "
          f"rights register BLOCKS. The register's matcher "
          f"'^C[0-9]{{1,2}}$|cd[-_]?risc' does not match these codes.")

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    covs = df[["id"] + list(cov_src)].rename(columns=cov_src)

    accounted = set(["id"]) | set(cov_src) | set(RMEQ) | set(LOTR) | set(CDRISC10)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c in ("CDRISC", "LOTR", "RMEQ_TOT"):
            skipped[c] = "scored total of a block, derived"
        elif c.startswith(("edad_rec", "Edad_recod", "Laboral_recod")):
            skipped[c] = "categorised recode of a covariate already carried"
        elif c in ("Prob_medico", "Prob_psico"):
            skipped[c] = "free-text medical/psychological problem description"
        elif c == "Marcatemporal":
            skipped[c] = "survey submission timestamp"
        elif c == "EST_TRAB":
            skipped[c] = "recode of Laboral already carried"
        elif c in ("Tabaco", "Café", "Te", "Red_bull", "Hachís", "Cocaína",
                   "Anfetaminas", "Éxtasis", "Alucinógenos", "Alcohol"):
            skipped[c] = ("substance-frequency item; each has its own "
                          "response set and they are not one instrument")
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:16} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written = set()
    for name, cols in BLOCKS.items():
        long = df[["id"] + cols].melt(id_vars="id", var_name="item",
                                      value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(float)

        # Each item against ITS OWN documented value-label keys.
        for c in cols:
            permitted = set(float(k) for k in (vlabs.get(c) or {}))
            obs = set(long.loc[long["item"] == c, "resp"].unique())
            assert permitted, f"{c}: no value labels to validate against"
            bad = obs - permitted
            assert not bad, f"{c}: {sorted(bad)} outside its value labels " \
                            f"{sorted(permitted)}"
        print(f"  {name}: every item within its own value-label set "
              f"({', '.join(f'{c}:{len(vlabs[c])}' for c in cols[:5])}...)")

        long = long.merge(covs, on="id", how="left")
        assert long["item"].nunique() > 1, f"{name}: single item"
        assert long["id"].nunique() >= 100, f"{name}: N={long['id'].nunique()}"
        long = long[["id", "item", "resp"] + list(cov_src.values())]

        out_name = f"antunez_2015_{name}"
        assert out_name not in written, f"duplicate output name {out_name}"
        written.add(out_name)
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, f"{out_name}.csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
