#!/usr/bin/env python3
# Source: https://zenodo.org/records/21776225
# DOI: none found. The deposit is "Dataset associated with the paper 'The
#   role of listening in digital empathy: a Portuguese adaptation of the
#   Basic Empathy Scale and of the Online Empathy Questionnaire'"; it lists
#   no related identifier, and Crossref and Europe PMC title searches found
#   no such paper as of 2026-10-02.
#   Neiva Santos, I., Reis, A. I., & Azevedo, J. (2026). Zenodo,
#   10.5281/zenodo.21776225.
# Data: Zenodo 21776225, "Survey data__1st year_2022_23.sav" (105 rows x 95
#       columns; Portuguese first-year university students, 2022-23, two
#       administrations F1 and F2).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: the full Portuguese
#   stems are the variable labels of every item; the anchors are value
#   labels on the positively keyed BES/OEQ items and the communication
#   items, absent on the eight reverse-keyed BES items. The deposit has no
#   English, so the required item_text_translated would be an IRW machine
#   translation; left for an itemtext pass.
#
# Tables (item codes are the source column names without the F1_/F2_ wave
#   prefix; F2_ComVideochamada is spelled "ComVideochamada" with an accent at
#   F2 and is unified to the F1 spelling):
#   neivasantos_2026_bes   EEBA_2..EEBA_20 (19 items)  Basic Empathy Scale,
#       Portuguese adaptation ("Escala de Empatia Basica Adaptada"). Value
#       labels: 1 Discordo totalmente .. 5 Concordo totalmente. The eight
#       negatively worded items (4, 5, 6, 7, 13, 14, 18, 19) carry no value
#       labels and are stored ALREADY reverse-keyed: F1/F2_EEBA_Total equal
#       the plain sum of the stored values, not of 6 - x (asserted). No
#       EEBA_1 is in the deposit.
#   neivasantos_2026_oeq   EEOA_1..EEOA_8  Online Empathy Questionnaire,
#       Portuguese adaptation. Same 1-5 agreement labels; the totals equal
#       the plain sums (asserted).
#   neivasantos_2026_comm_channels  ComPessoal, ComTelefonica,
#       ComMensescrita, ComMensgravada, ComVideochamada  "Generally, I talk
#       with my closest friends in person / by phone / by written messages /
#       by recorded messages / by video call". Value labels: 1 Nunca ..
#       5 Sempre.
#   The response range 1-5 is taken from the value labels (for the BES
#   reverse-keyed items, from the labelled items of the same scale); no
#   paper was found to confirm it.
# wave: 1 = F1, 2 = F2, the deposit's two administrations of the same
#   battery. What separates them is not documented (no paper); the
#   cov_session / cov_narrative flags suggest an intervention in between.
#
# Cleaning: 12 respondents have no F1 answers and 13 no F2 answers; no
#   fractional or out-of-label values.
# Dropped: every *_Total, *_Afetiva, *_Cognitiva score, the Media_* means
#   and the Dif_* differences; Grupo_etario and Grupo_nacionalidade (binned
#   copies of Idade and Nacionalidade).
# id: row index (the file has no respondent id).
# Covariates: cov_age, cov_gender (1 female, 2 male, 3 non-binary),
#   cov_nationality (1 Portuguese, 2 Brazilian, 3 other), cov_session
#   (took part in the classroom session: 1 yes, 2 no), cov_narrative
#   (produced an audio narrative: 1 yes, 2 no).

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
URL = ("https://zenodo.org/records/21776225/files/"
       "Survey%20data__1st%20year_2022_23.sav?download=1")

BES = [f"EEBA_{i}" for i in range(2, 21)]
OEQ = [f"EEOA_{i}" for i in range(1, 9)]
COMM = ["ComPessoal", "ComTelefónica", "ComMensescrita", "ComMensgravada",
        "ComVideochamada"]
TABLES = {"neivasantos_2026_bes": BES, "neivasantos_2026_oeq": OEQ,
          "neivasantos_2026_comm_channels": COMM}
REVERSED = [f"EEBA_{i}" for i in (4, 5, 6, 7, 13, 14, 18, 19)]
TOTALS = {("F1", "BES"): "F1_EEBA_Total", ("F1", "OEQ"): "F1_EEO_Total",
          ("F2", "BES"): "F2_EEBA_Total", ("F2", "OEQ"): "F2_EEOA_Total"}
COVS = {"Idade": "cov_age", "Género": "cov_gender",
        "Nacionalidade": "cov_nationality",
        "Participante_sessão": "cov_session",
        "Participante_narrativa": "cov_narrative"}
OTHER_DROPPED = {"Grupo_etário", "Grupo_nacionalidade"}


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
    assert d.shape == (105, 95), d.shape
    d = d.rename(columns={"F2_ComVídeochamada": "F2_ComVideochamada"})

    # Balance the books: items, covariates, and score columns.
    items = [f"{w}_{c}" for w in ("F1", "F2")
             for its in TABLES.values() for c in its]
    scores = {c for c in d.columns
              if any(k in c for k in ("Total", "Afetiva", "Cognitiva",
                                      "Media_", "Dif_"))}
    known = set(items) | scores | set(COVS) | OTHER_DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    assert len(scores) == 24

    vl = dict(meta.variable_value_labels)
    vl["F2_ComVideochamada"] = vl.pop("F2_ComVídeochamada")
    for w in ("F1", "F2"):
        for c in BES + OEQ:
            labs = vl.get(f"{w}_{c}")
            if c in REVERSED:
                assert not labs, c
            else:
                assert sorted(labs) == [1, 2, 3, 4, 5] and \
                    labs[5.0] == "Concordo totalmente", c
        for c in COMM:
            labs = vl.get(f"{w}_{c}")
            assert sorted(labs) == [1, 2, 3, 4, 5] and \
                labs[1.0] == "Nunca", c
        for (ww, scale), tot in TOTALS.items():
            if ww != w:
                continue
            cols = [f"{w}_{c}" for c in (BES if scale == "BES" else OEQ)]
            ok = d[cols].notna().all(axis=1) & d[tot].notna()
            assert ok.sum() >= 90
            assert (d.loc[ok, tot] == d.loc[ok, cols].sum(axis=1)).all(), tot
    x = d[items]
    assert ((x % 1 == 0) | x.isna()).all().all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        parts = []
        for k, w in enumerate(("F1", "F2"), start=1):
            sub = d[["id"] + cov_cols + [f"{w}_{c}" for c in its]].rename(
                columns={f"{w}_{c}": c for c in its})
            sub = sub.melt(id_vars=["id"] + cov_cols, value_vars=its,
                           var_name="item", value_name="resp")
            sub["wave"] = k
            parts.append(sub)
        long = pd.concat(parts, ignore_index=True)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        allowed = set(range(1, 6))
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp", "wave"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item", "wave"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        pv = {i: allowed for i in its}
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
