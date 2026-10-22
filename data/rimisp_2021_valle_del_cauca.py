"""
Two item blocks from Rimisp's 2021 quality-of-life and subjective-wellbeing
survey of 300 rural and peri-urban residents of three municipalities in Valle
del Cauca, Colombia (Florida, Pradera, Tuluá), fielded November-December 2021
for the "Territorios en Diálogo" programme: satisfaction with five household
utilities, and how often care and reproductive work is recognised or paid by
three different actors.

Source: Rimisp - Centro Latinoamericano para el Desarrollo Rural. Encuesta de
        medición de calidad de vida y bienestar subjetivo de Valle del Cauca -
        Colombia. Harvard Dataverse.
DOI: 10.7910/DVN/ZXQBC7
Data: https://doi.org/10.7910/DVN/ZXQBC7 --
        Base_TED_Colombia_Valle_del_Cauca.csv (300 x 325, ';'-delimited,
        latin-1, decimal commas) with "Libro de códigos de Encuesta
        bienestar_Valle del Cauca_Colombia.pdf" as the deposit's own codebook
License: CC0 1.0 (verified on the Harvard Dataverse record, latestVersion
        .license.name = "CC0 1.0")
Item text: NOT shipped, deferred rather than unavailable. The deposit's
        codebook PDF gives every item's full Spanish wording and all its
        option labels against the column name -- both blocks are fully
        recoverable from it. The administration was Spanish, so shipping it
        means an English gloss in the `_translated` fields, which is
        IRW-generated content and owes an itemtext_issues.qmd line; that is
        the same translation pass already owed by saputra_2025_fomo_consumer
        and andreu_sanchez_2023_*, and it is queued with them in
        automated_finding/TODO.md rather than done piecemeal here. instrument:
        both blocks are Rimisp's own programme survey questions, not a
        published scale (the care-work block's stem was searched verbatim and
        matches nothing published); rights: study-authored, and the deposit is
        CC0.

This deposit read as `download_failed` with "Error tokenizing data. C error:
Expected 4 fields in line 7" in the 2026-10-21 sweep. The file is both
latin-1 AND ';'-delimited, and the reader could survive only one of those at
a time -- see the fix in irw_triage_updated._read_delimited.

PII: no names, emails, dates of birth, phone numbers or platform account IDs.
Geographic columns ARE dropped and are not carried forward in any form:
`MUNICIPIO` (three named municipalities of roughly 50-200k inhabitants) and
`PDET` (names the territory, and its second value spells out "NO_PDET_TULUÁ",
so it leaks the municipality). A municipality of that size beside age, sex and
ethnic self-identification in the same row is the county-level surface the
2026-10-20 geographic-code ruling is about. `QA3A_ZONA` (municipal seat vs
rural) is kept -- it is a two-category rural/urban indicator, not a place.

`id` is the row index. `RESP_ID` is documented in the codebook as "Número de
encuesta, 1 - 300" but actually holds nine-digit platform submission numbers
(130085960, ...), so the documentation and the column disagree; the row index
is used instead and the mismatch is recorded here rather than resolved.

The satisfaction block has a SIXTH response option that is not a scale point:
"6. No tiene servicio" ("does not have the service"). The deposit supplies its
own numeric recode with those cases set missing (`QB1B_na`), and this script
re-derives the 1-5 mapping from the text columns itself and asserts it agrees
with the depositor's recode on every cell -- so the sentinel is dropped, not
read as a sixth, most-satisfied category.

Output: two tables, one per block -- different stems, different scales.
  rimisp_2021_household_services  5 items, 1-5, 299 ids,  999 responses
  rimisp_2021_care_work           3 items, 1-5, 300 ids,  900 responses
Skipped: QE5A/QE5B, two items on a 4-point "how common is this in your
community" scale, below the 3-item floor.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("Base_TED_Colombia_Valle_del_Cauca.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

SERVICES = [f"QB1B_{i}" for i in range(1, 6)]
SERVICES_RECODE = [f"QB1B_{i}a" for i in range(1, 6)]
CARE = [f"QD2_{i}" for i in range(1, 4)]

# Verbatim from the data file, which is latin-1 Spanish. The sixth option is a
# not-applicable sentinel and maps to missing, not to a scale point.
SATISFACTION = {
    "Muy insatisfecho(a)": 1,
    "Algo insatisfecho(a)": 2,
    "Ni satisfecho(a) ni insatisfecho(a)": 3,
    "Algo satisfecho(a)": 4,
    "Muy satisfecho(a)": 5,
    "No tiene el servico": None,     # sic: the data spells it without the 'i'
}
# "Nuca" is the data file's own misspelling of "Nunca"; mapped as it is
# spelled there rather than corrected, so the mapping stays checkable.
FREQUENCY = {"Nuca": 1, "Casi nunca": 2, "Algunas veces": 3,
             "Casi siempre": 4, "Siempre": 5}

COV_MAP = {"QA3A_ZONA": "cov_zone",
           "JOVENES_ADULTOS": "cov_age_group",
           "QA8_EDAD": "cov_age",
           "SEXO": "cov_sex",
           "QC1_GENERO": "cov_gender_identity",
           "QC3_GRUPO_ETNICO": "cov_ethnic_group",
           "QC4_CAMPESINO": "cov_self_identifies_campesino",
           "PERTENENCIA_ETNICA": "cov_belongs_to_ethnic_group",
           "PROYECTO": "cov_project"}

DROPPED_GEO = {
    "MUNICIPIO": "municipality (3 named municipalities) -- geographic code, "
                 "DROPPED under the 2026-10-20 ruling, not carried forward "
                 "in any form",
    "PDET": "names the development territory and spells out the municipality "
            "in one of its two values -- geographic code, DROPPED",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}")
    assert len(text_cols) > 0, "screen selected no columns"
    # Every text column in this file is a closed category from the codebook;
    # the survey carries no free-text box at all. The only columns with many
    # distinct values are the two geographic ones, dropped below, and FECHA.
    wide = {c: df[c].nunique() for c in text_cols if df[c].nunique() > 12}
    print(f"  text columns with more than 12 distinct values: {wide}")
    assert set(wide) <= {"FECHA", "MUNICIPIO", "PDET"}, wide


def main() -> None:
    df = pd.read_csv(SRC, sep=";", decimal=",", encoding="latin-1")
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 300, len(df)

    print(f"  RESP_ID is documented as 'Número de encuesta, 1 - 300' but "
          f"holds {df['RESP_ID'].nunique()} nine-digit submission numbers "
          f"(e.g. {df['RESP_ID'].iloc[0]}); using the row index as id")

    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src].values
    covs = list(COV_MAP.values())

    # Re-derive the satisfaction recode and check it against the depositor's.
    derived = {}
    for i, col in enumerate(SERVICES, start=1):
        bad = set(df[col].dropna().unique()) - set(SATISFACTION)
        assert not bad, (col, bad)
        mapped = df[col].map(SATISFACTION)
        theirs = df[f"QB1B_{i}a"]
        both = mapped.notna() & theirs.notna()
        assert (mapped[both] == theirs[both]).all(), f"{col}: recode disagrees"
        assert (mapped.isna() == theirs.isna()).all(), \
            f"{col}: the two recodes disagree about which cells are missing"
        derived[col] = mapped
    print(f"  satisfaction recode re-derived from the text columns and "
          f"identical to the depositor's QB1B_na on every cell; "
          f"'No tiene el servico' -> missing "
          f"({int(df[SERVICES].isin(['No tiene el servico']).sum().sum())} "
          "cells)")

    for col in CARE:
        bad = set(df[col].dropna().unique()) - set(FREQUENCY)
        assert not bad, (col, bad)
        derived[col] = df[col].map(FREQUENCY)

    skipped = dict(DROPPED_GEO)
    skipped["DEPARTAMENTO"] = ("constant (Valle del Cauca) -- no information, "
                               "and it is geography")
    skipped["RESP_ID"] = ("nine-digit survey submission number; the row index "
                          "is used as id instead")
    skipped["FECHA"] = "interview date; single-wave survey, no analytic use"
    skipped["DESAGREGAR"] = ("sampling flag for the programme's own "
                             "disaggregation, not a respondent attribute")
    skipped.update({c: f"depositor's own numeric recode of {c[:-1]}, "
                       "re-derived and verified above rather than shipped"
                    for c in SERVICES_RECODE})
    skipped["QE5A"] = ("one of two items on a 4-point 'how common is this in "
                       "your community' scale -- below the 3-item floor")
    skipped["QE5B"] = skipped["QE5A"]
    used = {"RESP_ID"} | set(COV_MAP) | set(SERVICES) | set(CARE)
    rest = [c for c in df.columns if c not in used | set(skipped)]
    # Everything else in this 325-column household survey is a single
    # question's multi-select checklist, a count of hours/minutes, an income
    # figure, a derived index, or a single-answer pick -- none of it an item
    # battery of three or more probes sharing one response scale.
    print(f"  skipped {len(rest)} further columns: the remainder of a "
          "325-column household survey -- multi-select checklists for one "
          "question each, hour/minute durations, income figures, derived "
          "indices and single-answer picks; no other block of 3+ probes "
          "shares one response scale")
    for c, why in sorted(skipped.items()):
        print(f"  skipped column {c}: {why}")

    blocks = [("household_services", SERVICES), ("care_work", CARE)]
    for name, cols in blocks:
        wide = pd.concat([out, pd.DataFrame({c: derived[c] for c in cols})],
                         axis=1)
        long = wide.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        long = long.dropna(subset=["resp"]).copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        table = f"rimisp_2021_{name}"
        assert long["id"].nunique() >= 100, (table, long["id"].nunique())
        assert long["item"].nunique() >= 3, table
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
