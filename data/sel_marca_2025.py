"""sel_marca_2025_{estudantes,familiares,professores}

Rebuild from the six OSF source exports (osf.io/hcaqv, private; access granted
by the depositor Luis Anunciacao, 2026-09-11). Fixes ben-domingue/irw#1849.

Source structure
----------------
Each export is wide, one column per (wave, item) named <WAVE>_Q<q>_P<p>, where
the wave prefix -- not the file -- carries the occasion:

    A9   "1o Semestre"  fieldwork 2024-04-06 .. 2024-08-30   -> wave 1
    A12  "Etapa 2"      fieldwork 2024-10-16 .. 2024-12-13   -> wave 2

(dates from the `Aplicacoes` sheet of the pesquisa_questoes_4_* dictionaries.)

The two exports per group are NOT two cohorts. The Dec-2024 export holds both
A9 and A12 columns; the Jan-2025 export is an A12-only re-export taken later,
with more A12 answers but fewer people. Every person in the later export is
already in the earlier one. So A12 is the UNION of the two, with the later
export winning the handful of cells where they disagree; taking either file
alone loses real data. The old `cov_cohort` column encoded the source file and
is dropped -- it was never a cohort.

Teacher rows are per class: `professores` has one row per (teacher, class).
Q8/Q23/Q26 genuinely differ between a teacher's classes; Q12/Q14 are about the
teacher and repeat identically across them (confirmed empirically, and by the
`Aplicacao Unica` flag in the professores A12 dictionary: Sim for Q14, Nao for
Q8/Q23/Q26). `id` is therefore teacher x class, which keeps the class-level
items addressable at the cost of copying the teacher-level answers across that
teacher's classes.

Name: the fieldwork ran entirely in 2024, so `_2025` is a misnomer. Kept for
now to avoid a rename/re-upload; tracked separately.

Respondent names and e-mail addresses in the source are never read.
"""

import os
import re
import pandas as pd

WAVE_ORDER = {"A9": 1, "A12": 2}

POTENTIAL_COVS = [
    "Estado", "Municipio", "Município", "Escola", "Programa",
    "Ano escolar", "Perfil", "Parentesco", "Turma",
]

# Never ingested.
PII = [
    "Nome do Estudante", "Nome do Responsavel", "Nome do Responsável",
    "Nome do Professor", "E-mail", "E-mail Responsavel", "E-mail Responsável",
]

RESP_RANGE = {
    "estudantes": (1, 5),
    "familiares": (0, 5),
    "professores": (0, 10),
}

ITEM_RE = re.compile(r"^(A9|A12)_(Q\d+_P\d+)$")


def _clean_cov(name):
    return "cov_" + (
        name.lower()
        .replace(" ", "_")
        .replace("í", "i")
        .replace("ú", "u")
    )


def _unit_id(df, survey_group):
    """Analysis unit: teacher x class for professores, respondent elsewhere."""
    uid = df["IDUsuario"].astype(str).str.strip()
    if survey_group != "professores":
        return uid
    turma = df["IDTurma"].astype(str).str.strip()
    return uid + "_" + turma


def _melt(df, survey_group):
    df = df.drop(columns=[c for c in PII if c in df.columns], errors="ignore")
    df = df.loc[:, ~df.columns.duplicated()]

    out = pd.DataFrame({"unit": _unit_id(df, survey_group)})
    for c in df.columns:
        if c in POTENTIAL_COVS:
            out[_clean_cov(c)] = df[c]

    item_cols = [c for c in df.columns if ITEM_RE.match(str(c))]
    if not item_cols:
        raise ValueError("no item columns found")

    wide = pd.concat([out, df[item_cols]], axis=1)
    long = wide.melt(
        id_vars=list(out.columns),
        value_vars=item_cols,
        var_name="raw_item",
        value_name="resp",
    ).dropna(subset=["resp"])

    parts = long["raw_item"].str.extract(ITEM_RE)
    long["wave"] = parts[0].map(WAVE_ORDER).astype("Int64")
    long["item"] = parts[1]
    long = long.drop(columns=["raw_item"])

    lo, hi = RESP_RANGE[survey_group]
    long["resp"] = pd.to_numeric(
        long["resp"].astype(str).str.strip(), errors="coerce"
    )
    long.loc[(long["resp"] < lo) | (long["resp"] > hi), "resp"] = pd.NA
    long = long.dropna(subset=["resp"])
    if (long["resp"] % 1 == 0).all():
        long["resp"] = long["resp"].astype("Int64")
    return long


def convert_to_irw(file_paths, outdir="raw_data"):
    groups = {}
    for path in file_paths:
        base = os.path.basename(path)
        group = next(
            (g for g in RESP_RANGE if g in base), None
        )
        if group is None:
            raise ValueError("cannot infer survey group from %s" % base)
        # Later export (A12-only re-export) wins on conflicting cells.
        rank = 1 if "173808" in base else 0
        df = pd.read_csv(path, sep=";", encoding="latin1", low_memory=False)
        long = _melt(df, group)
        long["_rank"] = rank
        groups.setdefault(group, []).append(long)

    written = {}
    for group, frames in groups.items():
        df = pd.concat(frames, ignore_index=True)
        # Union across exports; later export wins a disagreement.
        df = (
            df.sort_values("_rank")
            .drop_duplicates(subset=["unit", "item", "wave"], keep="last")
            .drop(columns=["_rank"])
        )
        df = df.rename(columns={"unit": "id"})
        cov_cols = sorted(c for c in df.columns if c.startswith("cov_"))
        df = df[["id", "item", "resp", "wave"] + cov_cols]
        df = df.sort_values(["id", "wave", "item"], ignore_index=True)

        out = os.path.join(outdir, "sel_marca_2025_%s.csv" % group)
        df.to_csv(out, index=False)
        written[group] = (out, df)
    return written


if __name__ == "__main__":
    files_to_process = [
        "raw_data/pesquisa_4_estudantes_1733083208226.csv",
        "raw_data/pesquisa_4_familiares_1733083353172.csv",
        "raw_data/pesquisa_4_professores_1733083488620.csv",
        "raw_data/pesquisa_4_estudantes_1738086324819.csv",
        "raw_data/pesquisa_4_familiares_1738086444228.csv",
        "raw_data/pesquisa_4_professores_1738086513968.csv",
    ]
    for group, (path, df) in convert_to_irw(files_to_process).items():
        print("%-12s %8d rows  %6d ids  %4d items  waves=%s -> %s"
              % (group, len(df), df["id"].nunique(), df["item"].nunique(),
                 sorted(df["wave"].unique()), path))
