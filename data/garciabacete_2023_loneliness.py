#!/usr/bin/env python3
# Source: https://zenodo.org/records/7393569
# DOI: none for this wave's data (Zenodo deposit; no related identifiers).
#   Garcia Bacete, F. J., Marande Perrin, G., Munoz Tinoco, M. V., & GREI
#   Group (2023). "Loneliness and Social Dissatisfaction Questionnaire /
#   Cuestionario de Soledad e Insatisfaccion Social // LONELINESS_Data_IC_T2-
#   Post." Zenodo. Instrument: Cassidy & Asher (1992), Spanish validation by
#   Garcia Bacete et al. (2014), as the deposit description states.
# Data: Zenodo 7393569, LONELINESS_Data_IC_T2-Post.sav (265 rows x 35
#       columns; second-grade primary pupils, Castellon (Spain) intervention
#       cohort, spring 2011-12, individually administered in Spanish). The
#       .dat is the same data. One wave of the GREI Longitudinal Project;
#       other waves and the SOCIOMET/victimization/teacher files are
#       separate Zenodo records, not used here.
# License: CC BY 4.0 (Zenodo record metadata, API; restated in the deposit's
#   identifying-metadata PDF).
#
# Item text: shipped (garciabacete_2023_loneliness__items.csv). The .sav has
#   no variable labels and no value labels (both levels empty); the deposit's
#   own descriptive-metadata PDFs (LONELINESS_Met-D_IC_T2-Post_Spa.pdf and
#   _Eng.pdf) give, per variable name, the Spanish wording as administered
#   (bracketed alternative phrasings included verbatim), the English
#   rendering, and the per-item value coding. Codes in this table are the
#   source variable names with the _T2post suffix removed.
#
# Table:
#   garciabacete_2023_loneliness  16 items, 1-3. The 16 loneliness items
#       Cassidy & Asher's single factor uses (the deposit's
#       LONE_Global_T2post is their mean, asserted): items 1, 3, 4, 6, 8, 9,
#       10, 12, 14, 16, 17, 18, 20, 21, 22, 24. Per the codebook the
#       positively worded items (1, 3, 4, 8, 10, 14, 16, 18, 22, 24) are
#       STORED reverse-coded (3 = No, 2 = Sometimes, 1 = Yes) and the others
#       1 = No .. 3 = Yes, so every item is keyed toward loneliness. The
#       option_text rows follow that per-item coding.
#
# Dropped:
#   - Loneliness2, 5, 7, 11, 13, 15, 19, 23: the questionnaire's hobby/
#     interest filler items (reading, TV, school, sports, maths, music,
#     drawing, video games), in none of the scale scores.
#   - LONE_* scale scores (six columns, 1-3 and 1-5 versions).
#   - ID: a structured study code (cohort/area/school/class/list number);
#     replaced by the row index. NClassList_T2post: class list number.
#   - Sample: constant 21 (Castellon intervention cohort).
#   - 52 children have no responses at all (absent at this wave): no rows.
# id: row index.
# Covariates: cov_sex (0 boy, 1 girl), cov_classroom (4-digit classroom code,
#   Classroom_T2post).

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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/7393569/files/"
       "LONELINESS_Data_IC_T2-Post.sav/content")
TABLE = "garciabacete_2023_loneliness"

# (Spanish as administered, English) from the deposit's Met-D PDFs.
# True = positively worded, stored 3 = No .. 1 = Yes.
ITEMS = {
    1: ("En el colegio, ¿te resulta fácil hacer nuevos amigos o amigas?",
        "It's easy for me to make new friends at school", True),
    3: ("En el colegio, ¿tienes otros niños o niñas con los que hablar? "
        "[ hablas con otros niños de tus cosas?]",
        "At school I have kids to talk to", True),
    4: ("En clase, ¿se te da bien trabajar con otros niños o niñas?",
        "I am good at working with other children", True),
    6: ("En el colegio, ¿te resulta difícil hacer amigos o amigas?",
        "It's hard for me to make friends at school", False),
    8: ("En el colegio, ¿tienes muchos amigos o amigas?",
        "I have lots of friends at school", True),
    9: ("¿Te sientes solo, sola, en el colegio?",
        "I feel alone at school", False),
    10: ("¿Puedes encontrar un amigo o una amiga cuando lo necesitas?",
         "I can find a friend when I need one", True),
    12: ("En el colegio, ¿te resulta difícil gustar a otros niños? "
         "[ ¿te cuesta caer bien a otros niños?; ¿te cuesta caer simpático "
         "a otros niños?]",
         "It's hard to get other kids at school to like me", False),
    14: ("En el colegio, ¿tienes niños o niñas con los que jugar?",
         "I have kids to play with at school", True),
    16: ("En el colegio, ¿te llevas bien con otros niños o niñas? "
         "[ ¿te las apañas bien con otros niños?; ¿te las arreglas con "
         "otros niños?]",
         "At school I get along with other kids", True),
    17: ("En clase, ¿sientes que te dejan fuera en algunas cosas? "
         "[ ¿sientes que no te hacen caso...?; ¿sientes que te dan de "
         "lado …?)]",
         "I feel left out of things at school", False),
    18: ("En el colegio, ¿hay niños o niñas a los que puedes acudir cuando "
         "necesitas ayuda?",
         "At school I can go to other kids when I need help", True),
    20: ("¿Es difícil para ti llevarte bien con los compañeros en el "
         "colegio?",
         "I don't get along with other children at school", False),
    21: ("En el colegio, ¿Te encuentras solo? [¿estás solo, sola?]",
         "I'm lonely at school", False),
    22: ("¿Les gustas (tú) a los niños y niñas de tu clase? [¿Caes bien a "
         "los niños y niñas de tu clase?]",
         "I am well-liked by kids in my class", True),
    24: ("¿Tienes amigos o amigas en el colegio?",
         "I have friends at school", True),
}
FILLERS = [2, 5, 7, 11, 13, 15, 19, 23]
OPTS = {"No": ("No", "No, it is not true of me"),
        "Sometimes": ("A veces", "Sometimes true of me"),
        "Yes": ("Sí", "Yes, it is always true of me")}
COMPOSITES = {f"LONE_{s}_T2post" for s in
              ("SocDif", "Dissatisf", "Global", "SocDif_1to5",
               "Dissatisf_1to5", "Global_1to5")}
OTHER_DROPPED = {"ID", "NClassList_T2post", "Sample"}
COVS = {"Sex": "cov_sex", "Classroom_T2post": "cov_classroom"}


def col(k):
    return f"Loneliness{k}_T2post"


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
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (265, 35), d.shape

    # Balance the books.
    items = {col(k) for k in ITEMS}
    fillers = {col(k) for k in FILLERS}
    known = items | fillers | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not meta.column_names_to_labels.get(col(1))
    assert not meta.variable_value_labels

    # The deposit's scores reproduce from the stored codes, which confirms
    # the item set and that the positive items are stored reverse-coded.
    def mean_of(ks):
        return d[[col(k) for k in ks]].mean(axis=1)
    for ks, c in ((list(ITEMS), "LONE_Global_T2post"),
                  ([6, 9, 12, 17, 20, 21], "LONE_SocDif_T2post"),
                  ([3, 8, 10, 14, 16, 18, 22, 24], "LONE_Dissatisf_T2post")):
        diff = (mean_of(ks) - d[c]).abs()
        assert (diff.dropna() < 1e-9).all() and diff.notna().sum() == 213, c
    assert (d["Sample"] == 21).all() and d["ID"].is_unique

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d = d.rename(columns={col(k): f"Loneliness{k}" for k in ITEMS})
    its = [f"Loneliness{k}" for k in ITEMS]
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = {1, 2, 3}
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 213 and long["item"].nunique() == 16
    pv = {i: allowed for i in its}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")

    # Item text from the deposit codebook, per-item coding.
    text = []
    for k, (es, en, positive) in ITEMS.items():
        order = ["Yes", "Sometimes", "No"] if positive else \
            ["No", "Sometimes", "Yes"]
        for resp, key in enumerate(order, 1):
            text.append({
                "table": TABLE, "section_id": f"{TABLE}_1",
                "item": f"Loneliness{k}",
                "instrument": "Loneliness and Social Dissatisfaction "
                              "Questionnaire (Cassidy & Asher 1992), Spanish "
                              "version (Garcia Bacete et al. 2014)",
                "language": "Spanish", "instructions": "",
                "section_prompt": "", "item_text": es,
                "item_text_translated": en, "correct_response": "",
                "option_text": OPTS[key][0],
                "option_text_translated": OPTS[key][1], "resp": resp})
    tx = pd.DataFrame(text)
    assert set(tx["item"]) == set(long["item"])
    assert set(tx["resp"]) == set(long["resp"])
    tx.to_csv(TEXT_DIR / f"{TABLE}__items.csv", index=False)
    print(f"{TABLE}__items.csv: rows={len(tx)}")


if __name__ == "__main__":
    convert()
