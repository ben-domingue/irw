#!/usr/bin/env python3
# Source: https://zenodo.org/records/23512666
# DOI: 10.5281/zenodo.23512666 (dataset; the record names no published paper)
# Deposit: Gabardo-Martins, L. M. D. (2026). Dataset on Grit, Emotional Hope,
#   and Life Satisfaction Across the five Brazilian Regions [Data set].
#   Zenodo. (Zenodo lists one creator, "Larissa Maria, David Gabardo-Martins",
#   which reads as one person, Larissa Maria David Gabardo-Martins, typed into
#   the family/given fields the wrong way round; hence the gabardo_martins
#   prefix.)
# Data: BANCO_TOTAL_ESCALA_ESPERANCA.xlsx (one sheet, Planilha1; 791 rows x
#   103 columns)
#   sha256 83e1f03e3dc124d3a10e57466a86df3e9beb84a64425ba95b62d359a5512120c
# Codebook: none. The deposit is the one .xlsx and the record has no
#   description; columns are Portuguese construct prefixes plus an item number.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (worth_retrying: dup id-item).
# The duplicates were the triage's choice of id, not repeated measures: there
# is no id or wave column, no two rows are identical, and each row is one
# respondent. id = row index (1-791), the same in every table.
#
# FIVE output tables, one per scale prefix:
#   gabardo_martins_2026_grit                 GARRA1-8    8 items, 1-4
#   gabardo_martins_2026_emotional_hope       ESPEMO1-6   6 items, 1-8
#   gabardo_martins_2026_positive_function   FUNPOS1-10 10 items, 1-5
#   gabardo_martins_2026_flourishing          FLO1-8      8 items, 1-7
#   gabardo_martins_2026_life_satisfaction    SATV1-6     6 items, 1-7
# GARRA = grit (8 items, as the Grit-S), ESPEMO = esperanca emocional, FLO =
# florescimento (8 items, as Diener's Flourishing Scale), SATV = satisfacao com
# a vida, FUNPOS = funcionamento positivo -- that last instrument is not
# identified. All eight grit items intercorrelate positively (0.31-0.56), so
# any reverse-keyed items are already recoded in the file.
#
# resp: shipped as recorded. NO SCALE IS DOCUMENTED: the ranges above are
# observed, every point of each is used, nothing lies outside it. Anchors and
# direction are unconfirmed, so permitted_values is NOT passed to run_qc (it
# must come from documentation, never the data). Grit on 1-4 rather than the
# Grit-S's usual 1-5 is how the file reads; with 791 respondents x 8 items and
# no 5 anywhere it is a 4-point version, not a missing category. One cell is
# empty (ESPEMO4, one respondent) and is dropped.
#
# HELD, not shipped: ESPCOG_DES1-21 and ESPCOG_ACON1-21, a 21-stem cognitive
# hope measure rated twice per stem (DES = desejo, how much it is wished for;
# ACON = acontecer, how likely it is to happen), observed 0-5. The 0 is not
# confirmed as a scale point: on most items it is rare (DES 0-5 times of 791),
# but on DES10/DES20 it jumps to 73/98 and on several ACON items to 96-257,
# which is the shape of a "does not apply" code baked into the scale. Without a
# codebook that cannot be told apart from a real "not at all", so per
# datastandard "What to verify" item 4 these 42 columns wait for the source.
#
# Covariates: cov_gender, cov_age, cov_race (Cor), cov_marital_status,
#   cov_education (two spellings, "Pos"/"Pós graduacao", merged to "Pos"),
#   cov_employment (TRABALHA), cov_income (RENDA MENSAL, minimum-wage bands),
#   cov_region (the five IBGE macro-regions, derived from ESTADO -- coarser
#   than the source's state, never finer). All Portuguese strings as recorded.
# Not carried: ESTADO itself (the region is the study's own unit); faixa_idade
#   (filled for 168 rows only and redundant with age); the health,
#   religion, dependence, favela and assistance questions (not needed for these
#   scales; minimal set).
#
# PII: 22 text columns screened (is_string_dtype); no email address and no run
#   of 4+ digits in any of them; no name, date-of-birth, phone or ID column.
#   Four FREE-TEXT columns are DROPPED, in no form: PROFISSAO (occupation,
#   443 distinct), SATISFEITO COM O TRABALHO (a free-text job-satisfaction
#   answer, 522 distinct), QUAL DOENCA CRONICA (which chronic illness, 103
#   distinct) and QUAL PROB MENTAL (which mental-health problem, 149 distinct,
#   some answers a sentence long). These are the short clinical / self-report
#   free text of the 2026-10-21 Bottesi ruling: drop the column, ship the rest.
#
# Item text: not in hand. Headers are positional (GARRA1) and the deposit has
#   no questionnaire.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GABARDO_RAW", "BANCO_TOTAL_ESCALA_ESPERANCA.xlsx")

TABLES = {
    "gabardo_martins_2026_grit": ("GARRA", 8, (1, 4)),
    "gabardo_martins_2026_emotional_hope": ("ESPEMO", 6, (1, 8)),
    "gabardo_martins_2026_positive_function": ("FUNPOS", 10, (1, 5)),
    "gabardo_martins_2026_flourishing": ("FLO", 8, (1, 7)),
    "gabardo_martins_2026_life_satisfaction": ("SATV", 6, (1, 7)),
}
HELD = [f"ESPCOG_{k}{i}" for i in range(1, 22) for k in ("DES", "ACON")]
COVS = {"GENERO": "cov_gender", "Idade": "cov_age", "Cor": "cov_race",
        "ESTAD_CIVIL": "cov_marital_status", "ESCOLARIDADE": "cov_education",
        "TRABALHA": "cov_employment", "RENDA MENSAL": "cov_income"}
FREE_TEXT_DROPPED = ["PROFISSAO", "SATISFEITO COM O TRABALHO",
                     "QUAL DOENCA CRONICA", "QUAL PROB MENTAL"]
NOT_CARRIED = ["ESTADO", "faixa_idade", "DEPENDE DE ALGUEM FINANC",
               "DOENCA CRONICA", "PROBLEMA MENTAL", "AUXILIO  TRATAMENTO",
               "DEFICIENCIA", "QUAL DEFICIENCIA",
               "SERVICO DE ASSISTENCIA SAUDE", "RELIGIAO",
               "IMPORTANCIA CRENCA RELIGIOSA", "MORA EM FAVELAS"]
REGION = {
    "Norte": ["Acre", "Amapa", "Amazonas", "Para", "Rondônia", "Roraima",
              "Tocantins"],
    "Nordeste": ["Alagoas", "Bahia", "Ceara", "Maranhao", "Paraíba",
                 "Pernambuco", "Piauí", "Rio Grande do Norte", "Sergipe"],
    "Centro-Oeste": ["Distrito Federal", "Goias", "Mato Grosso",
                     "Mato Grosso do Sul"],
    "Sudeste": ["Minas Gerais", "Rio de Janeiro", "Sao Paulo",
                "Espirito Santo"],
    "Sul": ["Parana", "Rio Grande do Sul", "Santa Catarina"],
}
STATE_TO_REGION = {s: r for r, states in REGION.items() for s in states}


def convert():
    df = pd.read_excel(RAW, sheet_name="Planilha1")
    assert df.shape == (791, 103), df.shape

    items = {t: [f"{p}{i}" for i in range(1, n + 1)]
             for t, (p, n, _) in TABLES.items()}
    accounted = ({c for cols in items.values() for c in cols} | set(HELD)
                 | set(COVS) | set(FREE_TEXT_DROPPED) | set(NOT_CARRIED))
    assert set(df.columns) == accounted, set(df.columns) ^ accounted

    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(text_cols)} text columns examined")
    assert len(text_cols) == 22
    for c in text_cols:
        s = df[c].dropna().astype(str)
        assert not s.str.contains(r"[\w.+-]+@[\w-]+\.\w+").any(), c
        assert not s.str.contains(r"\d{4,}").any(), c

    df.insert(0, "id", range(1, len(df) + 1))
    df["cov_region"] = df["ESTADO"].map(STATE_TO_REGION)
    assert df["cov_region"].notna().all(), \
        set(df.loc[df["cov_region"].isna(), "ESTADO"])
    df = df.rename(columns=COVS)
    df["cov_education"] = df["cov_education"].str.replace("Pós", "Pos",
                                                          regex=False)
    covs = list(COVS.values()) + ["cov_region"]

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (_, _, (lo, hi)) in TABLES.items():
        cols = items[table]
        long = df.melt(id_vars=["id"] + covs, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert set(long["resp"]) == set(range(lo, hi + 1)), table
        assert long["id"].nunique() >= 100

        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
