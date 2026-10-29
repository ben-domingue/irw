"""
A 12-item mathematics-anxiety scale answered by 2,508 Ecuadorian high-school
students nested in 13 schools.

Source: Arciniegas-Romero, G. (2026). ANSIEDAD MATEMATICA Y FACTORES
        DEMOGRAFICOS [Dataset]. figshare. The deposit's own description: "This
        dataset originates from a cross-sectional quantitative study conducted
        with 2,508 high school students from 13 public urban institutions in
        Imbabura, Ecuador. The objective was to examine whether mathematics
        anxiety varies across gender, age, and ethnicity."
DOI: 10.6084/m9.figshare.31037029
Data: https://doi.org/10.6084/m9.figshare.31037029 (the file
        "ANSIEDAD, SEXO, ETNIA Y GENERO.sav")
License: CC BY 4.0 (verified on the figshare record, license.name "CC BY 4.0")
Item text: NOT shipped, and it is a rights hold rather than a gap. The `.sav`
        labels every one of the twelve items with its FULL Spanish stem ("No
        tengo ningun miedo a las matematicas.", "Cuando hago problemas de
        matematicas se me queda la mente en blanco y no soy capaz de pensar
        claramente.") and carries the Spanish anchors as value labels, so the
        wording is entirely in hand. But the wording is the Fennema-Sherman
        Mathematics Attitude Scales' -- the deposit's own description calls it
        "The Mathematics Attitude..." -- and
        `itemtext/instrument_rights_register.csv` already carries a `hold` for
        a Fennema-Sherman mathematics anxiety / self-perception item set. An
        existing hold is not re-litigated here, so nothing ships and no new
        register row is written; this deposit is recorded against that row
        instead, because it is now a second table waiting on the same answer.

**`cluster_id` is the school, and the school NAMES are deliberately not
shipped.** `Colegio` is a code 1-13 whose value labels name thirteen specific
public schools in one Ecuadorian province ("Teodoro Gomez", "Juan Pablo
Segundo", ...), in a sample aged 14-20. The names are a fine-grained locator for
minors and do not ship. The CODE does, as `cluster_id`, because 2,508 students
in 13 schools is real nesting that a user fitting a multilevel model needs and
an opaque 1-13 index carries no locating information by itself.

**The items interleave three subscales and the codes keep the deposit's own
numbering.** The file's column order is AC1, AC2, ARP1, AE1, AE2, AE3, AC3,
AC4, ARP2, ARP3, AE4, AC5 -- administration order, not subscale order -- and
the item codes preserve each item's own label rather than renumbering 1..12, so
`ac1`..`ac5` (5 items), `arp1`..`arp3` (3) and `ae1`..`ae4` (4) stay traceable
to the instrument's subscales. They ship as ONE table because they were
administered as one battery on one 1-5 agreement scale; a user who wants the
subscales separately can take them off the `item` prefix.

Dropped as derived: `TOTAL_AC`, `TOTAL_ARP`, `TOTAL_AE` and `TOTAL_ANSIEDAD`
are subscale and total scores; `ORDINAL_AC`, `ORDINAL_ARP`, `ORDINAL_AE`,
`ORDINAL_TOTAL_A` and `ORDN_TOTL_CALCULO` are low/medium/high bandings of those
scores; `Edad_ordinal` is a banding of `Age`, which ships properly as
`cov_age`.

`cov_calculus_score` is the deposit's `Calculo`, a mathematics achievement
score running 1-44. It is kept because it is the outcome the anxiety items are
there to predict, and it is a covariate rather than a response: it is one
number per student, not an item battery.

PII: none. Every column is numeric, there is no identifier (`id` is the row
index), and no name, date or free-text column; the school names live only in
the SPSS value labels and are not read into any shipped column. The screen
below prints its denominator.

Output: one table, 30,096 responses -- 2,508 students x 12 items, resp 1-5.
  * arciniegas_romero_2026_math_anxiety -- 12 items, resp 1-5, 13 clusters
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ANSIEDAD.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "arciniegas_romero_2026_math_anxiety"
PERMITTED = [1, 2, 3, 4, 5]

# The deposit's own column order, which is administration order.
ITEMS = ["AC1", "AC2", "ARP1", "AE1", "AE2", "AE3", "AC3", "AC4", "ARP2",
         "ARP3", "AE4", "AC5"]

COV_MAP = {
    "Age": "cov_age",
    "Sex": "cov_sex",
    "Ethnic": "cov_ethnicity",
    "Curso": "cov_year_group",
    "Cálculo": "cov_calculus_score",
}

DROP = {
    "TOTAL_AC": "subscale score",
    "TOTAL_ARP": "subscale score",
    "TOTAL_AE": "subscale score",
    "TOTAL_ANSIEDAD": "total anxiety score",
    "ORDINAL_AC": "low/medium/high banding of a subscale score",
    "ORDINAL_ARP": "low/medium/high banding of a subscale score",
    "ORDINAL_AE": "low/medium/high banding of a subscale score",
    "ORDINAL_TOTAL_A": "low/moderate/high banding of the total score",
    "ORDN_TOTL_CALCULO": "achievement banding of Cálculo, which ships as "
                         "cov_calculus_score",
    "Edad_ordinal": "age banding; Age ships as cov_age",
}


def pii_screen(df: pd.DataFrame, meta) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"
    schools = meta.variable_value_labels.get("Colegio") or {}
    print(f"  Colegio names {len(schools)} specific schools in its VALUE "
          f"labels (e.g. {sorted(schools.values())[:2]}); the names are not "
          "read into any shipped column, only the 1-13 code as cluster_id")
    assert len(schools) >= 10, schools


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df, meta)
    assert len(df) == 2508, len(df)

    # The stems ARE here. They do not ship, but the script states the fact
    # rather than letting a later reader assume the file is bare: this is a
    # rights hold on Fennema-Sherman wording, not a missing-wording gap.
    stems = {c: (meta.column_names_to_labels.get(c) or "").strip()
             for c in ITEMS}
    assert all(len(v) > 20 for v in stems.values()), stems
    print(f"variable labels present for all {len(df.columns)} columns, and for "
          f"the 12 items they are the FULL Spanish stems (e.g. "
          f"{stems['AC1']!r}) -- held, not absent: the Fennema-Sherman item "
          "set is registered `hold`")

    assert list(df.columns)[5:5 + len(ITEMS)] == ITEMS, \
        f"the item block is not where it was: {list(df.columns)[5:18]}"
    documented = sorted(int(k) for k in
                        (meta.variable_value_labels.get(ITEMS[0]) or {}))
    assert documented == PERMITTED, documented

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    df["cluster_id"] = df["Colegio"].astype(int)
    n_clusters = df["cluster_id"].nunique()
    sizes = df["cluster_id"].value_counts()
    print(f"cluster_id is the school: {n_clusters} clusters, "
          f"{sizes.min()}-{sizes.max()} students each")
    assert n_clusters == 13, n_clusters

    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(ITEMS) | set(DROP)
                 | {"id", "cluster_id", "Colegio"})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    codes = {c: c.lower() for c in ITEMS}
    assert len(set(codes.values())) == len(ITEMS), codes
    long = df[["id", "cluster_id"] + covs + ITEMS].rename(columns=codes)
    long = long.melt(id_vars=["id", "cluster_id"] + covs, var_name="item",
                     value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{before - len(long)} cell(s) outside {PERMITTED}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cluster_id"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} clusters={long['cluster_id'].nunique()} "
          f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
