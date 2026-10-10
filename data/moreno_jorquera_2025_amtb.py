#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KOQP5C
# DOI: 10.5334/glo.113
#   Moreno-Jorquera, S., Guajardo-Gonzalez, J., & Saavedra-Concha, F. (2025).
#   "Motivation and Lexical Availability in Chilean Students Learning English as
#   L2", Glocality (CC BY 4.0).
# Data: Harvard Dataverse 10.7910/DVN/KOQP5C (Guajardo, Javiera; deposited
#       2025-12-17). AMTB+Dataset.xlsx (file 13255558): sheet "Likert completo",
#       136 English-pedagogy students (Universidad San Sebastian, Chile) x
#       "#" (p1..p136) + 43 AMTB items, each header the item's full Chilean-Spanish
#       stem prefixed by its number ("1. Me gustaria hablar muchos idiomas
#       perfectamente"), + 9 subscale means; nine further sheets repeat each
#       subscale's items with its mean. LA+Dataset.xlsx (13255557): "Informantes"
#       (CODIGO_INFORMANTE 1..136 + six background codes), "Variables" (the code
#       labels), and three lexical-availability word-list sheets.
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped for all nine tables (administered Chilean-Spanish stems from
#   the xlsx column headers; English from the article's Table 17 "AMTB Version
#   Presented to Students", the authors' own translation; 1-7 anchors from the
#   Methods: 1 strongly disagree, 4 neither agree nor disagree, 7 strongly agree,
#   2/3/5/6 unlabelled). Built by
#   automated_finding/itemtext_verification/make_itemtext_moreno_jorquera_2025.py.
#   Label levels checked: xlsx headers carry the stems; there are no value labels
#   (xlsx).
#
# Item codes: amtb_<n>, n = the leading number of the source header (reversible;
#   the header's own text is the item_text). Subscale membership is the article's
#   Table 3 and is asserted against the deposit's nine subscale sheets.
# Tables (1-7 agreement, all items positively worded per the article):
#   moreno_jorquera_2025_amtb_interest    1, 9, 27, 36          interest in foreign languages
#   moreno_jorquera_2025_amtb_intensity   6, 14, 24, 33, 40     motivational intensity
#   moreno_jorquera_2025_amtb_teacher     2, 10, 18, 28, 37, 43 English teacher evaluation
#   moreno_jorquera_2025_amtb_att_learn   3, 11, 19, 29, 38     attitudes toward learning English
#   moreno_jorquera_2025_amtb_att_people  16, 20, 23, 30        attitudes toward English speakers
#   moreno_jorquera_2025_amtb_integr      4, 12, 21, 31         integrative orientation
#   moreno_jorquera_2025_amtb_desire      5, 13, 22, 32, 39, 42 desire to learn English
#   moreno_jorquera_2025_amtb_course      8, 17, 26, 35, 41     English course evaluation
#   moreno_jorquera_2025_amtb_instrum     7, 15, 25, 34         instrumental orientation
# Skipped: the nine subscale-mean columns (composites); the LA word lists (free
#   recall of words, not item responses); NACIONALIDAD (all 1 = Chilean).
# Covariates from LA "Informantes", joined p<k> = CODIGO_INFORMANTE k. The join is
#   verified: the overall AMTB mean by semester reproduces the article's Table 20
#   (n 38/22/45/19/12; means 6.1/5.8/5.7/5.8/5.9; minima 4/4.5/2.2/4.5/5.4).
#   cov_sex (H male, M female, O other), cov_ses (BAJO/MEDIO/ALTO, the article's
#   three-level sociocultural index), cov_semester (1, 3, 5, 7, 9; the LA file
#   codes them 1-5), cov_english_level (basico/intermedio/avanzado), and
#   cov_level_source (propia apreciacion = self-assessed / test estandarizado).
# id: k from p<k>.

import os
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw" / "moreno_jorquera_2025"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"AMTB.xlsx": "https://dataverse.harvard.edu/api/access/datafile/13255558",
         "LA.xlsx": "https://dataverse.harvard.edu/api/access/datafile/13255557"}
P = "moreno_jorquera_2025_amtb_"
# (table suffix, Table 3 item numbers, deposit subscale sheet prefix)
TABLES = {
    "interest": ([1, 9, 27, 36], "1. "),
    "intensity": ([6, 14, 24, 33, 40], "2. "),
    "teacher": ([2, 10, 18, 28, 37, 43], "3. "),
    "att_learn": ([3, 11, 19, 29, 38], "4. "),
    "att_people": ([16, 20, 23, 30], "5. "),
    "integr": ([4, 12, 21, 31], "6. "),
    "desire": ([5, 13, 22, 32, 39, 42], "7. "),
    "course": ([8, 17, 26, 35, 41], "8. "),
    "instrum": ([7, 15, 25, 34], "9. "),
}
SEX = {1: "H", 2: "M", 3: "O"}
SES = {1: "BAJO", 2: "MEDIO", 3: "ALTO"}
SEMESTER = {1: 1, 2: 3, 3: 5, 4: 7, 5: 9}
LEVEL = {1: "BASICO", 2: "INTERMEDIO", 3: "AVANZADO"}
SOURCE = {1: "PROPIA APRECIACION", 2: "TEST ESTANDARIZADO"}
TABLE20 = {1: (38, 6.1, 4.0), 3: (22, 5.8, 4.5), 5: (45, 5.7, 2.2), 7: (19, 5.8, 4.5),
           9: (12, 5.9, 5.4)}


def fetch() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, url in FILES.items():
        p = RAW_DIR / name
        if not p.exists():
            r = requests.get(url, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
        out[name] = p
    return out


def main() -> None:
    paths = fetch()
    x = pd.ExcelFile(paths["AMTB.xlsx"])
    d = pd.read_excel(x, "Likert completo")
    assert d.shape == (136, 53) and d["#"].is_unique
    itemcols = list(d.columns[1:44])
    num = {c: int(re.match(r"\s*(\d+)\.", c).group(1)) for c in itemcols}
    assert sorted(num.values()) == list(range(1, 44))
    means = list(d.columns[44:53])
    assert all(re.match(r"\d\. [A-Z]", m) for m in means), means
    for m in means:
        print(f"  [skip] {m}: subscale mean")
    # Table 3 membership == the deposit's own subscale sheets
    assert sorted(n for its, _ in TABLES.values() for n in its) == list(range(1, 44))
    sheets = x.sheet_names[1:]
    for suf, (its, pre) in TABLES.items():
        sh = [s for s in sheets if s.startswith(pre)]
        assert len(sh) == 1, (suf, sh)
        cols = [c for c in pd.read_excel(x, sh[0]).columns[1:] if not str(c).startswith("Unnamed")]
        assert sorted(int(re.match(r"\s*(\d+)\.", c).group(1)) for c in cols) == sorted(its), suf
    vals = d[itemcols]
    assert vals.isin(range(1, 8)).all().all() and vals.notna().all().all()

    assert d["#"].str.fullmatch(r"p\d+").all()
    d["id"] = d["#"].str[1:].astype(int)
    inf = pd.read_excel(paths["LA.xlsx"], "Informantes")
    assert inf.shape == (136, 7) and inf["CODIGO_INFORMANTE"].is_unique
    assert (inf["NACIONALIDAD"] == 1).all()
    print("  [skip] NACIONALIDAD: constant (all Chilean)")
    cov = pd.DataFrame({
        "id": inf["CODIGO_INFORMANTE"].astype(int),
        "cov_sex": inf["SEXO"].map(SEX),
        "cov_ses": inf["NIVEL_SOCIOCULTURAL"].map(SES),
        "cov_semester": inf["AÑO DE ENSEÑANZA"].map(SEMESTER),
        "cov_english_level": inf["NIVEL_INGLÉS"].map(LEVEL),
        "cov_level_source": inf["OBTENCIÓN_NIVEL"].map(SOURCE),
    })
    assert cov.notna().all().all()
    d = d.merge(cov, on="id", how="left", validate="one_to_one")
    assert d["cov_sex"].notna().all()
    # verify the join against the article's Table 20
    d["_mot"] = d[itemcols].mean(axis=1)
    g = d.groupby("cov_semester")["_mot"].agg(["count", "mean", "min"])
    for sem, (n, mu, lo) in TABLE20.items():
        assert g.loc[sem, "count"] == n and round(g.loc[sem, "mean"], 1) == mu \
            and round(g.loc[sem, "min"], 1) == lo, (sem, g.loc[sem].tolist())
    d = d.rename(columns={c: f"amtb_{n}" for c, n in num.items()})
    covs = [c for c in cov.columns if c != "id"]

    names = [P + s for s in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for suf, (its, _) in TABLES.items():
        name = P + suf
        icodes = [f"amtb_{n}" for n in its]
        t = d.melt(id_vars=["id"] + covs, value_vars=icodes, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(icodes) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 8)) for i in icodes}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
