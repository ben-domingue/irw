#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Transcultural_adaptation_of_an_environmental_health_questionnaire_with_attitude_knowledge_and_skills_scales_for_Portuguese_nursing_students/27312150
# DOI: 10.3390/nursrep15010013
#   Alvarez-Garcia, C., Edra, B., Marques, G., Simoes, C., Simoes, C., &
#   Lopez-Franco, M. D. (2025). "Transcultural Adaptation of Environmental
#   Health Questionnaire with Attitude, Knowledge, and Skills Scales for
#   Portuguese Nursing Students." Nursing Reports, 15(1), 13. (Open access,
#   PMC11767602; preprint 10.20944/preprints202411.1691.v1.)
#   Dataset: Alvarez-Garcia, C., et al. (2024). figshare,
#   https://doi.org/10.6084/m9.figshare.27312150.v1
# Data: "Bases de datos_Figshare.xlsx", one sheet, 326 x 50: undergraduate
#       nursing students at one university in northern Portugal, 2023-2024.
#       The paper's 326 students, 272/53/1 by gender, 69/81/108/68 by year
#       and 58/48/220 by sustainability-session attendance are reproduced
#       (asserted).
# License: CC BY 4.0 (figshare API).
#
# Item text: not shipped. Both label levels checked: .xlsx, so no variable
#   or value labels; headers are positional ("Attitudes 1", "Knowledge 7").
#   Stems are in the published SANS_2 and the ChEHK-Q/ChEHS-Q (Alvarez-
#   Garcia et al. 2020, Health Educ J 79:826); the Portuguese wording is not
#   in the deposit.
#
# Instruments (paper section 2):
#   alvarezgarcia_2024_sans2  Sustainability Attitudes in Nursing Survey
#                             (SANS_2), 5 items, 1-7 Likert.
#   alvarezgarcia_2024_chehk  Children's Environmental Health Knowledge
#                             Questionnaire (ChEHK-Q), 26 items answered
#                             true / false / I don't know and scored as
#                             correct answers (maximum 26). Stored scored,
#                             0 = not correct, 1 = correct; "Knowledge
#                             Points" is their sum (asserted).
#   alvarezgarcia_2024_chehs  Children's Environmental Health Skills
#                             Questionnaire (ChEHS-Q), 12 items, 1-5 Likert.
#   Permitted values asserted per item. Item codes are the source headers
#   with the space replaced by an underscore (Attitudes_1 ...).
#
# Rows: each scale was left blank by some students, and 19 rows answer no
#   item at all (8 of them coincide on their demographics, which is the
#   file's 5 "duplicated" rows; asserted that no duplicated row holds a
#   response), so the tables carry 307 / 275 / 265 people. No fractional
#   cells.
# Dropped: the composites Attitudes Points, Knowledge Points, Skills Points
#   (sums of their items wherever all items are present, asserted).
# id: row index (no respondent id in the file).
# Covariates: cov_age, cov_gender (Female / Male / Transgender, as text;
#   "Transgenero" in the file), cov_year (1-4, year of the nursing degree),
#   cov_sessions (1 never attended a sustainability-and-nursing session,
#   2 attended, 3 attended more than three months ago; decoded from the
#   paper's 58/48/220 counts).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/50019543"

TABLES = {
    "alvarezgarcia_2024_sans2": ("Attitudes", 5, range(1, 8)),
    "alvarezgarcia_2024_chehk": ("Knowledge", 26, range(0, 2)),
    "alvarezgarcia_2024_chehs": ("Skills", 12, range(1, 6)),
}
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Year": "cov_year",
        "Sessions": "cov_sessions"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (326, 50), d.shape
    blocks = {p: [f"{p} {i}" for i in range(1, n + 1)]
              for p, n, _ in TABLES.values()}
    known = set(COVS) | {f"{p} Points" for p in blocks} | \
        {c for cols in blocks.values() for c in cols}
    assert set(d.columns) == known, set(d.columns) ^ known
    for p, cols in blocks.items():
        full = d[cols].notna().all(axis=1)
        assert (d.loc[full, cols].sum(axis=1) == d.loc[full, f"{p} Points"]
                ).all(), p
    assert d["Gender"].value_counts().to_dict() == {
        "Female": 272, "Male": 53, "Transgénero": 1}
    assert d["Year"].value_counts().to_dict() == {
        "3º": 108, "2º": 81, "1º": 69, "4º": 68}
    assert d["Sessions"].value_counts().to_dict() == {3: 220, 1: 58, 2: 48}
    all_items = [c for cols in blocks.values() for c in cols]
    dup = d.duplicated(keep=False)
    assert d.loc[dup, all_items].isna().all().all()
    assert d[all_items].isna().all(axis=1).sum() == 19

    d["Gender"] = d["Gender"].replace({"Transgénero": "Transgender"})
    d["Year"] = d["Year"].str.rstrip("º").astype(int)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (p, n, allowed) in TABLES.items():
        its = blocks[p]
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long["item"] = long["item"].str.replace(" ", "_")
        codes = [c.replace(" ", "_") for c in its]
        allowed = set(allowed)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in codes}
        long = long[["id", "item", "resp"] + cov_cols]
        long["cov_age"] = long["cov_age"].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == n > 1
        fails = [(c.name, c.detail)
                 for c in run_qc(long, permitted_values=pv)
                 if c.status == "fail"]
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
