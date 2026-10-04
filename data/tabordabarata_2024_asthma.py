#!/usr/bin/env python3
# Source: https://zenodo.org/records/11155084
# DOI: 10.1371/journal.pone.0333760
#   Dos Santos, Costa, Pereira, Pedro & Taborda-Barata (2025). "Development
#   and validation of an asthma self-knowledge questionnaire." PLOS One
#   20(10): e0333760. (PMC12578227)
#   Deposit: Taborda-Barata, L. (2024). Zenodo, 10.5281/zenodo.11155084.
# Data: Zenodo 11155084, DB-Asma.sav (149 rows x 162 columns; Portuguese
#       adults with and without asthma, face-to-face survey at hospital
#       consultations). The paper reports n = 235 (104 asthmatic, 131 not);
#       the deposit holds 149 of them.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text:
#   asthma_knowledge -- not shipped. Both label levels checked: no variable
#     labels on Q1-Q21; value labels carry only the five agreement anchors.
#     The English wording of all 21 statements is in the paper's Table 1
#     ("Examples of questions"), keyed Q1-Q21 -- a paper_explicit lead.
#   hls_eu_q47, bsi -- not shipped. Both label levels are populated: the
#     full Portuguese stems are the variable labels (AF1-AF47, A1-A53) and
#     the anchors are the value labels. The deposit has no English, so the
#     required item_text_translated would be an IRW machine translation;
#     left for an itemtext pass (English originals: HLS-EU-Q47, BSI).
#
# Tables (item codes are the source column names):
#   tabordabarata_2024_asthma_knowledge  Q1-Q21  Bronchial Asthma
#       Self-Knowledge Questionnaire (the paper's new instrument). Paper: a
#       5-point Likert scale, 1 = Discordo Totalmente .. 5 = Concordo
#       Totalmente (also the file's value labels). No reverse-scored items
#       (paper). Domains: general aspects Q1-6, pathophysiological/clinical
#       Q7-12, therapeutic Q13-18, non-pharmacological therapeutic Q19-21;
#       AG/AFC/AT/ATNF/GLOBAL equal those sums (asserted).
#   tabordabarata_2024_hls_eu_q47  AF1-AF47  European Health Literacy Survey
#       (HLS-EU-Q47, Portuguese), the paper's convergent-validity measure.
#       Value labels: 1 Muito Dificil, 2 Dificil, 3 Facil, 4 Muito Facil,
#       5 Nao sei ("don't know"). "Don't know" is not a point on the
#       difficulty scale, so 5 would be set to NA; it never occurs (asserted).
#   tabordabarata_2024_bsi  A1-A53  Brief Symptom Inventory (Portuguese,
#       53 items; not named in the paper, identified by its 53 variable-label
#       stems and the BSI_* dimension scores in the file). Value labels:
#       0 Nunca .. 4 Muitissimas Vezes.
#
# Dropped: AG, AFC, AT, ATNF, GLOBAL and their *_media means;
#   Literacia_MEDIA, Literacia_TOTAL; the nine BSI_* dimension means;
#   Numerador (row counter 1..149); Grupo_etario and Tempo_asma_2 (binned
#   copies of Idade and TempodeAsma).
# id: row index. The file's Codigo ("01-AB-001": site, group, sequence) is a
#   study code, replaced by the row index.
# Covariates: cov_age, cov_gender (1 female, 2 male), cov_education (1 no
#   schooling .. 7 university), cov_occupation (1 unemployed, 2 employed,
#   3 retired, 4 student), cov_residence (1 urban, 2 town, 3 village,
#   4 farm), cov_asthma (1 yes, 2 no), cov_asthma_years, cov_family_asthma
#   and cov_contact_asthma (1 yes, 2 no), cov_act (Asthma Control Test:
#   0 controlled, 1 not controlled, 2 not applicable), cov_gina (severity
#   1 mild intermittent .. 4 severe persistent, 5 not applicable),
#   cov_asthma_medication (1 yes, 2 no, 3 n/a), cov_other_medication (1 yes,
#   2 no), cov_mmse (0 no cognitive deficit, 1 deficit, 2 n/a), cov_gds
#   (0 normal, 1 mildly, 2 severely depressed, 3 n/a), cov_cesd (0 not
#   depressed, 1 depressed, 2 n/a).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/records/11155084/files/DB-Asma.sav?download=1"

Q = [f"Q{i}" for i in range(1, 22)]
AF = [f"AF{i}" for i in range(1, 48)]
A = [f"A{i}" for i in range(1, 54)]
TABLES = {
    "tabordabarata_2024_asthma_knowledge": (Q, range(1, 6)),
    "tabordabarata_2024_hls_eu_q47": (AF, range(1, 5)),
    "tabordabarata_2024_bsi": (A, range(0, 5)),
}
DOMAINS = {"AG": Q[0:6], "AFC": Q[6:12], "AT": Q[12:18], "ATNF": Q[18:21],
           "GLOBAL": Q}
COMPOSITES = (set(DOMAINS) | {f"{k}_média" for k in DOMAINS}
              | {"Literacia_MÉDIA", "Literacia_TOTAL", "BSI_somatizacao",
                 "BSI_obss_compul", "BSI_SENS_INTERP", "BSI_Depressão",
                 "BSI_HOSTILIDADE", "BSI_ANS_FÓB", "BSI_IDEA_PARAN",
                 "BSI_Psicoticismo", "BSI_IGS"})
OTHER_DROPPED = {"Numerador", "Código", "Grupo_etário", "Tempo_asma_2"}
COVS = {"Idade": "cov_age", "Género": "cov_gender",
        "HabLit": "cov_education", "Ocupação": "cov_occupation",
        "Residência": "cov_residence", "Asma": "cov_asthma",
        "TempodeAsma": "cov_asthma_years",
        "Familiar_Asma": "cov_family_asthma",
        "Contacto_Asma": "cov_contact_asthma", "ACT": "cov_act",
        "GINA": "cov_gina", "Medicação": "cov_asthma_medication",
        "OutraMedicação": "cov_other_medication", "MMSE": "cov_mmse",
        "GDS": "cov_gds", "CES_D": "cov_cesd"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (149, 162), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["Código"].is_unique

    # Documented response sets (value labels; the Q set is also the paper's).
    vl = meta.variable_value_labels
    for c in Q:
        assert sorted(vl[c]) == [1, 2, 3, 4, 5], c
    for c in AF:
        assert sorted(vl[c]) == [1, 2, 3, 4, 5] and \
            vl[c][5.0] == "Não sei", c
    for c in A:
        assert sorted(vl[c]) == [0, 1, 2, 3, 4], c
    assert not d[AF].eq(5).any().any()      # no "don't know" answers
    for its, _ in TABLES.values():
        x = d[its]
        assert ((x % 1 == 0) | x.isna()).all().all()   # no imputation
    for k, its in DOMAINS.items():
        ok = d[its].notna().all(axis=1)
        assert (d.loc[ok, k] == d.loc[ok, its].sum(axis=1)).all(), k

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        pv = {i: set(allowed) for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
