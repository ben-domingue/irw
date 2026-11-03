#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229695
# DOI: 10.1371/journal.pone.0229695
# Paper: Ramirez-Maestre C, Esteve R, Serrano-Ibanez ER, et al. (2020).
#   Psychometric characteristics and factorial structures of the Defensive
#   Pessimism Questionnaire--Spanish Version (DPQ-SV). PLOS ONE 15(4): e0229695.
# Data: Mendeley Data 10.17632/zvj6cz68sc.1, file DATA.sav, 545 psychology
#   undergraduates at the University of Malaga, 2017/18.
# License: CC BY 4.0, verified on the DEPOSIT (data.mendeley.com public API,
#   data_licence "CC BY 4.0"); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# Five output tables, the deposit's own item codes throughout:
#   ramirez_maestre_2020_dpq          PESIMI1..12, Defensive Pessimism
#       Questionnaire (Spanish translation), 1 not at all true of me .. 7 very
#       true of me. One out-of-range cell (PESIMI5 = 33) dropped.
#   ramirez_maestre_2020_lotr         LOT1..LOT10 minus the four filler items
#       (2, 5, 6, 8): the six scored LOT-R items, 0 strongly disagree .. 4
#       strongly agree, as administered (the pessimism items 3, 7, 9 are NOT
#       reversed; LOT3R/LOT7R/LOT9R are partial recodes and are dropped).
#   ramirez_maestre_2020_panas        PANAS1..20 (Sandin et al. Spanish
#       version), 1 never .. 5 always. Five cells coded 0 (outside 1-5)
#       dropped.
#   ramirez_maestre_2020_stai_trait   STAI1..20, trait subscale of the Spanish
#       STAI, 0-3. One out-of-range cell (STAI20 = 6) dropped.
#   ramirez_maestre_2020_flourishing  FLO1..8, labelled FLOURISHING in the
#       .sav: eight items on 1-7, the shape of Diener et al.'s Flourishing
#       Scale (8 items, 1 strongly disagree .. 7 strongly agree). Not described
#       in the paper; identified from the variable label and the format.
# Covariates: sex (value labels), age.
# Dropped: SUJETO (a per-centre counter: 451 values over 545 rows; `id` is the
#   row index), CURSO (centre), the 3 EXITO items (expectations of success,
#   1-9, described nowhere), and every composite (PLENI, OPTITOT, OPTI, PESI,
#   PANAPOSI, PANANEG, STAITOT, PESIDEF, REFLEX, NEGAEXP, EXITO).
#
# Item text: NOT SHIPPED. Only the first item of each block carries a variable
#   label, and it is the block name ("PESIMISMO DEFENSIVO"); no value labels
#   (both levels checked). The Spanish wording is not in the deposit.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("RAMIREZ_RAW", "DATA.sav")


def emit(name, df, items, cov_cols, permitted):
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    long = long[long["resp"].notna()]
    bad = ~long["resp"].isin(permitted)
    if bad.any():
        print(f"  {name}: dropping {int(bad.sum())} out-of-range cell(s): "
              f"{long.loc[bad, ['item', 'resp']].value_counts().to_dict()}")
    long = long[~bad]
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    return name, int(bad.sum())


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (545, 91)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    df["id"] = range(1, len(df) + 1)
    df["cov_sex"] = df["SEXO"].map({1.0: "male", 2.0: "female"})
    df["cov_age"] = df["EDAD"]
    cov_cols = ["cov_sex", "cov_age"]
    blocks = {
        "ramirez_maestre_2020_dpq": ([f"PESIMI{i}" for i in range(1, 13)], list(range(1, 8))),
        "ramirez_maestre_2020_lotr": ([f"LOT{i}" for i in (1, 3, 4, 7, 9, 10)], [0, 1, 2, 3, 4]),
        "ramirez_maestre_2020_panas": ([f"PANAS{i}" for i in range(1, 21)], [1, 2, 3, 4, 5]),
        "ramirez_maestre_2020_stai_trait": ([f"STAI{i}" for i in range(1, 21)], [0, 1, 2, 3]),
        "ramirez_maestre_2020_flourishing": ([f"FLO{i}" for i in range(1, 9)], list(range(1, 8))),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = [emit(n, df, it, cov_cols, perm) for n, (it, perm) in blocks.items()]
    names = [o[0] for o in out]
    assert len(set(names)) == len(names)
    assert dict(out) == {"ramirez_maestre_2020_dpq": 1, "ramirez_maestre_2020_lotr": 0,
                         "ramirez_maestre_2020_panas": 5, "ramirez_maestre_2020_stai_trait": 1,
                         "ramirez_maestre_2020_flourishing": 0}
    shipped = {c for it, _ in blocks.values() for c in it}
    dropped = (["SUJETO", "CURSO", "LOT2", "LOT5", "LOT6", "LOT8", "LOT3R", "LOT7R", "LOT9R", "EXITO1", "EXITO2",
                "EXITO3", "PLENI", "OPTITOT", "OPTI", "PESI", "PANAPOSI", "PANANEG", "STAITOT", "PESIDEF", "REFLEX",
                "NEGAEXP", "EXITO"])
    assert set(meta.column_names) == shipped | {"SEXO", "EDAD"} | set(dropped)
    assert meta.variable_value_labels["SEXO"] == {1.0: "HOMBRE", 2.0: "MUJER"}
    print("dropped:", dropped)


if __name__ == "__main__":
    convert()
