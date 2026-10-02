#!/usr/bin/env python3
# Source: https://zenodo.org/records/7393759
# DOI: none for this wave's data (Zenodo deposit; no related identifiers).
#   Garcia Bacete, F. J., Marande Perrin, G., Munoz Tinoco, M. V., Jimenez
#   Lagares, I., & GREI Group (2023). "Self-perceived Victimization
#   Questionnaire / Cuestionario de Autopercepcion de Ser Victimizado //
#   VICTIMIZATION_Data_IC_T2-Post." Zenodo. Instrument: Garcia Bacete et al.
#   (2014), as the deposit description states.
# Data: Zenodo 7393759, VICTIMIZATION_Data_IC_T2-Post.sav (265 rows x 14
#       columns; second-grade primary pupils, Castellon (Spain) intervention
#       cohort, spring 2011-12, individually administered in Spanish). The
#       .dat is the same data. One wave of the GREI Longitudinal Project; the
#       same 265-child roster as garciabacete_2023_loneliness (a different
#       instrument, so a separate table). Other waves and the SOCIOMET
#       series are separate Zenodo records, not used here.
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: shipped (garciabacete_2023_victimization__items.csv). The .sav
#   has no variable labels and no value labels (both levels empty); the
#   deposit's own descriptive-metadata PDFs (VICTIMIZATION_Met-D_IC_T2-Post_
#   Spa.pdf and _Eng.pdf) give, per variable name, the Spanish wording as
#   administered, the English rendering and the value coding. Codes in this
#   table are the source variable names with the _T2post suffix removed.
#
# Table:
#   garciabacete_2023_victimization  SelfVictimiz1-8, 1-4 (1 = Never,
#       2 = Rarely/few times, 3 = Many times, 4 = Almost every day; the
#       Met-D codebook, every item). SELFVICTIMIZ_T2post is their mean
#       (asserted).
#
# Dropped:
#   - SELFVICTIMIZ_T2post (factor score).
#   - ID: a structured study code (cohort/area/school/class/list number);
#     replaced by the row index. NClassList_T2post: class list number.
#   - Sample: constant 21 (Castellon intervention cohort).
#   - 50 children have no responses at all (absent at this wave): no rows.
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
URL = ("https://zenodo.org/api/records/7393759/files/"
       "VICTIMIZATION_Data_IC_T2-Post.sav/content")
TABLE = "garciabacete_2023_victimization"

# (Spanish as administered, English) from the deposit's Met-D PDFs.
ITEMS = {
    1: ("Algunos niños de la clase te insultan, te ponen motes y te dicen "
        "cosas feas o desagradables",
        "Some classmates call you names or say mean things to you."),
    2: ("Algunos niños de la clase te pegan, te empujan o te dan patadas",
        "Some classmates hit you or kick you."),
    3: ("Algunos niños de la clase te tratan mal o te hacen llorar",
        "Some classmates mistreat you or make you cry."),
    4: ("Algunos niños de la clase te chinchan, hacen rabiar, enfadar",
        "Some classmates bother you, tease you or make you angry."),
    5: ("Algunos niños de la clase te dejan fuera de los juegos y no "
        "quieren estar contigo",
        "Some classmates leave you out of the games and don't want to be "
        "with you."),
    6: ("Algunos niños de la clase te obligan a hacer cosas que no quieres "
        "hacer",
        "Some classmates force you to do things you don't want to do."),
    7: ("Algunos niños de la clase se burlan y se ríen de ti",
        "Some classmates make fun of you and laugh at you."),
    8: ("Algunos niños de la clase intentan que los otros niños no sean "
        "amigos míos",
        "Some classmates try to keep other children from being my "
        "friends."),
}
OPTS = {1: ("Nunca", "Never"), 2: ("Pocas veces", "Rarely/few times"),
        3: ("Bastantes veces", "Many times"),
        4: ("Casi todos los días", "Almost every day")}
COMPOSITES = {"SELFVICTIMIZ_T2post"}
OTHER_DROPPED = {"ID", "NClassList_T2post", "Sample"}
COVS = {"Sex": "cov_sex", "Classroom_T2post": "cov_classroom"}


def col(k):
    return f"SelfVictimiz{k}_T2post"


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
    assert d.shape == (265, 14), d.shape

    # Balance the books.
    items = {col(k) for k in ITEMS}
    known = items | COMPOSITES | OTHER_DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert not any(meta.column_names_to_labels.values())
    assert not meta.variable_value_labels

    diff = (d[sorted(items)].mean(axis=1) - d["SELFVICTIMIZ_T2post"]).abs()
    assert (diff.dropna() < 1e-9).all() and diff.notna().sum() == 215
    assert (d["Sample"] == 21).all() and d["ID"].is_unique
    assert not d.drop(columns="ID").dropna(subset=sorted(items)) \
        .duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d = d.rename(columns={col(k): f"SelfVictimiz{k}" for k in ITEMS})
    its = [f"SelfVictimiz{k}" for k in ITEMS]
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = set(OPTS)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 215 and long["item"].nunique() == 8
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

    # Item text from the deposit codebook.
    text = []
    for k, (es, en) in ITEMS.items():
        for resp, (o_es, o_en) in OPTS.items():
            text.append({
                "table": TABLE, "section_id": f"{TABLE}_1",
                "item": f"SelfVictimiz{k}",
                "instrument": "Self-perceived Victimization Questionnaire "
                              "(Garcia Bacete et al. 2014)",
                "language": "Spanish", "instructions": "",
                "section_prompt": "", "item_text": es,
                "item_text_translated": en, "correct_response": "",
                "option_text": o_es, "option_text_translated": o_en,
                "resp": resp})
    tx = pd.DataFrame(text)
    assert set(tx["item"]) == set(long["item"])
    assert set(tx["resp"]) == set(long["resp"])
    tx.to_csv(TEXT_DIR / f"{TABLE}__items.csv", index=False)
    print(f"{TABLE}__items.csv: rows={len(tx)}")


if __name__ == "__main__":
    convert()
