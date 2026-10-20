#!/usr/bin/env python3

# Source: https://zenodo.org/records/20817
# DOI: 10.5281/zenodo.20817
#   Rosas (2010). Niveles de inteligencia emocional en estudiantes de quinto
#   ano de secundaria de colegios mixtos y diferenciados del Callao
#   [Dataset]. Zenodo.
# Data: "2010_Rosas_Niveles_de_inteligencia_emocional_en_estudiantes_de_
#   quinto_ano_de_secundaria_de_colegios_mixtos_y_diferenciados_del_Callao
#   .sav" -- 160 fifth-year secondary students across 8 schools in Callao,
#   Peru, comparing mixed and single-sex, state and private schools.
# License: CC0 1.0 (the Zenodo record reports license id "cc-zero",
#   verified 2026-10-20).
#
# Item text: NOT shipped. Both label levels checked and both are empty for
#   the 60 items -- pyreadstat's column_names_to_labels is None for every
#   O1..O60 (labels exist only on the four covariates, e.g. SEXO -> "SEXO DE
#   LOS ESTUDIANTES"), and variable_value_labels is empty for the whole
#   file, so neither the stems nor the four anchors are present. Asserted
#   below, per label level, so the verdict is re-checked on every run rather
#   than trusted.
#   NOTE the file DOES carry value labels, but only on the four covariates
#   (SEXO -> MUJERES/VARONES, TIPOCOLEGIO -> DIFERENCIADO/MIXTO, GESTION ->
#   ESTATAL/PARROQUIAL, COLEGIO -> the eight school names). Not one of the 60
#   items has any. That distinction is the whole verdict here, so it is
#   asserted at both levels below rather than summarised -- a blanket "no
#   value labels in the file" would have been false, which is the
#   estevez_2021 (#1770) failure shape.
#   Where the text actually is: this is the 60-item BarOn Emotional Quotient
#   Inventory: Youth Version (BarOn ICE: NA), in its Spanish adaptation --
#   60 items on a 4-point scale, scored into exactly the six subscales this
#   file carries as composites (intrapersonal, interpersonal, stress
#   management, adaptability, general mood, positive impression). It is a
#   COMMERCIAL instrument (Multi-Health Systems), so its wording is
#   published but not freely reproducible, and the deposit's CC0 covers the
#   depositor's data rather than the instrument. It has NO row in
#   itemtext/instrument_rights_register.csv -- the register's four "baron"
#   matches are all Baron-COHEN instruments (AQ, EQ, RMET), a different
#   researcher entirely -- so nothing would have warned, and silence does
#   not ship. A register row for the BarOn EQ-i:YV / ICE: NA, verdict
#   included, is owed before any pass extracts this wording.
#
# ONE table: the 60 BarOn items, answered by every respondent.
#
# id: the file has NO identifier column, so `id` is the row index (1..160),
#   one row per respondent. The standard IRW treatment; the rows are already
#   de-identified and row order is the only link the deposit provides.
#
# resp: 1-4, integer. TWO isolated out-of-range cells are set to missing
#   rather than kept or rounded: O38 holds one 12.0 and O56 one 5.0, each a
#   single cell out of 160. On a 4-point scale a 12 is impossible and a 5 is
#   one past the top, and both are confined to one cell of one item while
#   every other value in all 9,600 cells is in 1-4 -- the signature of a
#   data-entry slip, not of a differently-scaled item. Nulling two cells
#   costs two observations; keeping them would put impossible values in the
#   corpus, and dropping the two items would cost 320. Everything else is
#   complete: zero missing cells in the raw 60 x 160 block.
#
# Dropped as composites, not responses: the six raw subscale sums (CINTRA,
#   CINTERP, CMANES, CADAPT, CANIMOG, CIMPOSITIVA), the general-scale sum
#   (CEGENERAL), their seven z-scores (zINTRAP..zCEGENERAL), the seven
#   standardised equivalents (CEINTRAP..CEIMPOSITIVA), CETOTAL, and the
#   banded diagnostic level NivelDiagnosticoCET. Also dropped: TT, which is
#   constant across all 160 rows and carries no information.
#
# Covariates: the deposit's four school/demographic variables, kept as the
#   source's own single-letter codes because the file supplies no value
#   labels to expand them and guessing would be worse than preserving them:
#   SEXO is M/V, TIPOCOLEGIO is D/M (diferenciado / mixto -- the study's own
#   comparison), GESTION is E/P (estatal / privado), and COLEGIO identifies
#   which of the 8 schools. COLEGIO is a school code, not a person
#   identifier.
#
# PII: none. The screen uses pd.api.types.is_string_dtype -- never
#   dtype == object, which returns zero on a pyreadstat frame -- and prints
#   the denominator, asserted non-zero; it finds 5 string columns, which are
#   SEXO, TIPOCOLEGIO, GESTION, COLEGIO and one further coded column. None
#   is a column whose job is to collect an identifier: there is no name,
#   email, date of birth, address, postal code, phone number or free-text
#   field anywhere in the file, and no student identifier of any kind (which
#   is why `id` has to be the row index). COLEGIO names a school, not a
#   respondent, and 160 students spread over 8 schools does not single
#   anyone out.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s5"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "zenodo" / "20817"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 20817
FNAME = ("2010_Rosas_Niveles_de_inteligencia_emocional_en_estudiantes_de_"
         "quinto_ano_de_secundaria_de_colegios_mixtos_y_diferenciados_del_"
         "Callao.sav")
TABLE = "rosas_2010_emotional_intelligence"

ITEMS = [f"O{i}" for i in range(1, 61)]
COVS = {"SEXO": "cov_sex", "TIPOCOLEGIO": "cov_school_type",
        "GESTIÒN": "cov_school_management", "COLEGIO": "cov_school"}
# The file labels every covariate and no item; both halves are asserted.
SCALE = {1, 2, 3, 4}
N_RESP = 160
# Known data-entry slips, named explicitly so a change in the file is loud.
OUT_OF_RANGE = {"O38": 12.0, "O56": 5.0}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://zenodo.org/api/records/{RECORD}/files/{FNAME}/content"
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()))
    assert len(df) == N_RESP, len(df)
    missing = [c for c in [*ITEMS, *COVS] if c not in df.columns]
    assert not missing, missing

    # PII screen -- print the denominator so an empty selection is visible.
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] columns examined: {len(df.columns)} total, "
          f"{len(text_cols)} string-dtype")
    assert len(text_cols) > 0, "PII screen selected no columns"

    # Item-text verdict, re-checked per label level on every run.
    assert all(meta.column_names_to_labels.get(c) is None for c in ITEMS), \
        "an item gained a variable label (a stem); revisit the item-text verdict"
    labelled = set(meta.variable_value_labels)
    assert labelled == set(COVS), \
        f"value-label coverage changed: {labelled ^ set(COVS)}"
    print(f"[itemtext] stems: absent for all {len(ITEMS)} items; response "
          f"anchors: absent for all {len(ITEMS)} (the file's value labels "
          f"cover only the {len(COVS)} covariates). Not shipped; BarOn "
          f"ICE: NA is commercial and has no rights-register row.")

    assert df[ITEMS].isna().sum().sum() == 0, "unexpected missing in raw items"
    # Null the two isolated out-of-range cells (see header).
    for col, value in OUT_OF_RANGE.items():
        n = int((df[col] == value).sum())
        assert n == 1, f"expected exactly one {value} in {col}, found {n}"
        df.loc[df[col] == value, col] = pd.NA
    for c in ITEMS:
        extra = sorted(set(df[c].dropna().unique()) - {float(v) for v in SCALE})
        assert not extra, f"{c} still holds out-of-range values {extra}"

    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    for raw in COVS:
        labels = dict(meta.variable_value_labels[raw])
        present = set(df[raw].dropna().unique())
        orphan_codes = sorted(present - set(labels))
        orphan_labels = sorted(set(labels) - present)
        if orphan_codes:
            # The source's own label set has exactly one typo: COLEGIO is
            # coded 'GP' in the data and keyed 'GE' in the labels, for
            # "GENERAL PRADO". Repair it only when the pairing is forced --
            # one unmatched code and one unmatched key -- so this can never
            # silently guess among several.
            assert len(orphan_codes) == 1 and len(orphan_labels) == 1, (
                raw, orphan_codes, orphan_labels)
            labels[orphan_codes[0]] = labels.pop(orphan_labels[0])
            print(f"[labels] {raw}: code {orphan_codes[0]!r} is unlabelled "
                  f"and key {orphan_labels[0]!r} is unused; paired them as "
                  f"{labels[orphan_codes[0]]!r} (forced, 1-to-1)")
        df[raw] = df[raw].map(labels)
        assert df[raw].notna().all(), f"unmapped code in {raw}"
    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())

    t = (df[["id", *cov_cols, *ITEMS]]
         .melt(id_vars=["id", *cov_cols], value_vars=ITEMS,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    expected = N_RESP * len(ITEMS) - len(OUT_OF_RANGE)
    assert len(t) == expected, (len(t), expected)
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the 1-4 scale: {bad}"

    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert t["id"].nunique() == N_RESP
    assert t["item"].nunique() == len(ITEMS)

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
