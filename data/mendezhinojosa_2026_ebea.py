#!/usr/bin/env python3
# Source: https://zenodo.org/records/19935602
# DOI: 10.23913/ride.v14i28.1767
#   Méndez Hinojosa, L. M., Castillo De León, M. A., & Cárdenas Rodríguez,
#   M. (2024). "Diseño y validación de una escala breve de estrategias de
#   aprendizaje." RIDE Revista Iberoamericana para la Investigación y el
#   Desarrollo Educativo, 14(28), e601. (CC BY 4.0)
# Data: Zenodo 19935602, "Excel EBEA.xlsx" (one sheet, 1,975 rows x 29
#       columns; undergraduates at a university in northern Mexico, mostly
#       UANL, online administration).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: shipped (mendezhinojosa_2026_ebea__items.csv). Both levels
#   checked: an .xlsx has no value labels; the 11 item column headers are the
#   full Spanish stems, numbered "1." .. "11.", and they match the paper's
#   Table 3 word for word. Option text from the paper's Instrumentos section
#   ("siempre, casi siempre, a veces, casi nunca y nunca", scored 5 to 1).
#   Spanish only: no English translation exists in the deposit or paper, so
#   the _translated fields are left empty (the administered-language
#   fallback in itemtext_standard.md).
#
# Tables:
#   mendezhinojosa_2026_ebea  ebea1-ebea11  Escala Breve de Estrategias de
#       Aprendizaje (EBEA), 11 Likert items, 5 = siempre .. 1 = nunca (paper:
#       "El recorrido de los ítems fue de 5 a 1"). Item code ebeaK is taken
#       from the header's own leading number "K." (asserted), so the code is
#       tied to its column by the header, not by position. Paper codes:
#       elaboration EE1-EE7 = items 1, 3, 4, 5, 6, 8, 10; organisation
#       EO1-EO4 = items 2, 7, 9, 11. The paper's final model drops EE2
#       (item 3) and EE5 (item 6); all 11 administered items ship.
#
# Cleaning:
#   - 19 rows are exact repeats of another row on all 25 respondent columns
#     (age through item 11, including city, programme and GPA) and sit at
#     consecutive subject numbers (e.g. 530-535 six times, 455-458 four
#     times): repeated submissions. The first occurrence is kept, so the
#     table has 1,956 ids, not the paper's 1,975.
#   - Sexo = "Todos los dias" (one row; an answer to a different question)
#     -> NA.
# Dropped: the three composites (Elaboración = items 1,3,4,5,6,8,10;
#   Organización = items 2,7,9; total = items 1-10; all asserted), the
#   numeric recode of Sexo (Género.1: 0 man, 1 woman, 2 other, asserted),
#   country of residence (all México bar two stray entries) and city of
#   residence (free text), and the subject number.
# id: row index of the de-duplicated file.
# Covariates: cov_age (4 blank), cov_sex (Hombre/Mujer/Prefiero no decirlo),
#   cov_gender (free-text gender identity as typed), cov_program (degree
#   programme and faculty), cov_semester (1-10; "NO APLIC" -> NA),
#   cov_study_mode (En línea/Híbrido/Presencial), cov_gpa (0-100 scale),
#   cov_scholarship, cov_employed, cov_extracurricular (1 = Si, 0 = No),
#   cov_work_hours (hours per week; "24h" -> 24, "28 hrs" -> 28, "." -> NA).

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/19935602/files/"
       "Excel%20EBEA.xlsx/content")

TABLE = "mendezhinojosa_2026_ebea"
ALLOWED = {1, 2, 3, 4, 5}
OPTIONS = {5: "Siempre", 4: "Casi siempre", 3: "A veces", 2: "Casi nunca",
           1: "Nunca"}
ELAB, ORG = [1, 3, 4, 5, 6, 8, 10], [2, 7, 9]
YESNO = {"Si": 1, "No": 0}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=None)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    raw = load()
    assert raw.shape == (1976, 29), raw.shape
    header = [str(h).strip() for h in raw.iloc[0]]
    d = raw.iloc[1:].reset_index(drop=True)
    d.columns = range(29)

    # Positional layout, checked against the header text.
    expect = {0: "Número de sujeto", 1: "Edad", 2: "Sexo", 3: "Género",
              4: "Género", 5: "País de residencia",
              6: "Cuidad de residencia", 9: "Modalidad en la que está "
              "estudiando", 26: "Estrategias de Aprendizaje de Elaboración",
              27: "Estrategias de Aprendizaje de Organización",
              28: "ESTRATEGIAS DE APRENDIZAJE"}
    for k, v in expect.items():
        assert header[k] == v, (k, header[k])
    stems = {}
    for col in range(15, 26):
        m = re.match(r"^(\d+)\.\s+(.*)$", header[col])
        assert m, header[col]
        k = int(m.group(1))
        assert k == col - 14, (col, k)
        stems[col] = (f"ebea{k}", m.group(2).strip())
    item_cols = {col: code for col, (code, _) in stems.items()}

    # Composites: the deposit's own scoring.
    it = d[list(range(15, 26))].astype(float)
    it.columns = range(1, 12)
    assert (d[26] == it[ELAB].sum(axis=1)).all()
    assert (d[27] == it[ORG].sum(axis=1)).all()
    assert (d[28] == it[list(range(1, 11))].sum(axis=1)).all()
    assert it.notna().all().all()
    # Género.1 is a numeric recode of Sexo.
    rec = {"Hombre": 0, "Mujer": 1, "Prefiero no decirlo": 2,
           "Todos los dias": 2}
    assert (d[2].map(rec) == d[4]).all()
    assert (d[0].astype(int).values == range(1, len(d) + 1)).all()

    # Repeated submissions: identical on every respondent column.
    resp_cols = list(range(1, 26))
    dup = d.duplicated(subset=resp_cols, keep="first")
    assert dup.sum() == 19, dup.sum()
    d = d[~dup].reset_index(drop=True)

    out = pd.DataFrame({"id": d.index + 1})
    out["cov_age"] = pd.to_numeric(d[1]).astype("Int64")
    out["cov_sex"] = d[2].where(d[2] != "Todos los dias")
    out["cov_gender"] = d[3]
    out["cov_program"] = d[7]
    sem = d[8].astype(str).str.replace("°", "", regex=False)
    assert set(sem) <= {str(i) for i in range(1, 11)} | {"NO APLIC"}
    out["cov_semester"] = pd.to_numeric(sem.where(sem != "NO APLIC")) \
        .astype("Int64")
    out["cov_study_mode"] = d[9]
    out["cov_gpa"] = pd.to_numeric(d[10])
    for col, name in ((11, "cov_scholarship"), (12, "cov_employed"),
                      (14, "cov_extracurricular")):
        assert set(d[col]) <= set(YESNO), (col, set(d[col]))
        out[name] = d[col].map(YESNO).astype("Int64")
    hrs = d[13].replace({".": None, "24h": 24, "28 hrs": 28})
    out["cov_work_hours"] = pd.to_numeric(hrs)
    # Books: 0 subject no., 5 country, 6 city, 4 Sexo recode, 26-28
    # composites dropped; 1-3, 7-14 covariates; 15-25 items.
    used = {1, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14} | set(item_cols)
    dropped = {0, 4, 5, 6, 26, 27, 28}
    assert used | dropped == set(range(29)) and not used & dropped

    for col, code in item_cols.items():
        out[code] = pd.to_numeric(d[col])
    cov_cols = [c for c in out.columns if c.startswith("cov_")]
    long = out.melt(id_vars=["id"] + cov_cols,
                    value_vars=list(item_cols.values()),
                    var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for item, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (item, bad)
    pv = {i: ALLOWED for i in item_cols.values()}
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 1956
    assert long["item"].nunique() == 11
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    path = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(path, index=False)
    rep = irw_validate.validate_file(str(path), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")

    # Item text: administered Spanish stems from the column headers.
    text = []
    for col, (code, stem) in stems.items():
        for r in sorted(OPTIONS, reverse=True):
            text.append({
                "table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                "instrument": "Escala Breve de Estrategias de Aprendizaje "
                              "(EBEA)",
                "language": "Spanish", "instructions": "",
                "section_prompt": "", "item_text": stem,
                "item_text_translated": "", "correct_response": "",
                "option_text": OPTIONS[r], "option_text_translated": "",
                "resp": r})
    tx = pd.DataFrame(text)
    assert set(tx["item"]) == set(long["item"])
    assert set(tx["resp"]) == set(long["resp"])
    tx.to_csv(TEXT_DIR / f"{TABLE}__items.csv", index=False)
    print(f"{TABLE}__items.csv: rows={len(tx)}")


if __name__ == "__main__":
    convert()
