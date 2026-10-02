#!/usr/bin/env python3
# Source: https://zenodo.org/records/10105133
# DOI: none confirmed (Zenodo deposit; no related identifiers). A later
#   paper by an overlapping team -- Sutrisno, C., Suyato, S., Mulyono, B., &
#   Nurhayati, I. (2025), "Analysis of students perceptions of democracy
#   quality and civic behavior among UNY students", Jurnal Pendidikan PKN
#   6(1), 10.26418/jppkn.v6i1.92523 -- may analyse these data, but its page
#   is bot-walled and the link is unconfirmed, so it is not cited as the
#   source.
#   Suyato, Hidayah, Y., & Setiawan, E. P. (2023). "Citizenship Behavior
#   Questionnaire (CBQ)." Zenodo.
# Data: Zenodo 10105133, "Citizenship Behavior Questionnaire (Raw Data)
#       (1).xlsx" (340 rows x 41 columns; students of Universitas Negeri
#       Yogyakarta, Indonesia).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: shipped for suyato_2023_cbq (suyato_2023_cbq__items.csv) from
#   the deposit's "Citizenship Behavior Questionnaire (Codebook).xlsx",
#   which gives, per variable name, the English stem and the value coding
#   (1 = absolutely no .. 4 = absolutely yes). The xlsx data file has no
#   label levels of its own (plain headers). The deposit's questionnaire
#   .docx is in English and the description says "this document was given
#   to University students in Indonesia", so the English is taken as the
#   administered wording. Not shipped for suyato_2023_democracy: the
#   codebook's D labels (-1 = a little worse .. 2 = much better) are a
#   recoded direction that does not match the questionnaire's five printed
#   options ("Is much lower than before" .. "Is much higher than before").
#
# Tables (item codes are the source column names):
#   suyato_2023_cbq  K1-K20, Citizenship Behavior Questionnaire (part 2 of
#       the questionnaire), 1-4 per the codebook.
#   suyato_2023_democracy  D1-D19, perceived change in the quality of
#       democracy in Indonesia (part 3). Permitted set {-1, 0, 1, 2} per the
#       codebook (-1 = a little worse, 0 = no difference, 1 = a little
#       better, 2 = much better). The printed questionnaire offers five
#       options; the codebook documents four codes and no "much worse", so
#       how the fifth option was coded is undocumented.
#
# Dropped: nothing besides the two covariates below; there is no id column
#   and no composite.
# id: row index.
# Covariates: cov_faculty (text, trailing spaces stripped), cov_gender
#   (0 male, 1 female).

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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/10105133/files/"
DATA_URL = BASE + ("Citizenship%20Behavior%20Questionnaire%20(Raw%20Data)"
                   "%20(1).xlsx/content")
BOOK_URL = BASE + ("Citizenship%20Behavior%20Questionnaire%20(Codebook)"
                   ".xlsx/content")

TABLES = {
    "suyato_2023_cbq": ([f"K{i}" for i in range(1, 21)], {1, 2, 3, 4}),
    "suyato_2023_democracy": ([f"D{i}" for i in range(1, 20)],
                              {-1, 0, 1, 2}),
}
K_CODING = ("1 = absolutely no; 2 = mostly No; 3 = mostly yes; "
            "4 = absolutely yes")
D_CODING = ("-1 = a little worse; 0 = no difference; 1 = a little better; "
            "2 = much better")
COVS = {"FACULTY": "cov_faculty", "GENDER": "cov_gender"}


def get(url):
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return io.BytesIO(r.content)


def parse_coding(s):
    out = {}
    for part in s.split(";"):
        k, _, v = part.partition("=")
        out[int(k.strip())] = v.strip()
    return out


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d = pd.read_excel(get(DATA_URL))
    book = pd.read_excel(get(BOOK_URL), header=None,
                         names=["var", "label", "coding"])
    assert d.shape == (340, 41), d.shape
    book = book.set_index("var")

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert set(book.index) == known
    for c in TABLES["suyato_2023_cbq"][0]:
        assert book.loc[c, "coding"] == K_CODING, c
    for c in TABLES["suyato_2023_democracy"][0]:
        assert book.loc[c, "coding"].strip() == D_CODING, c
    assert not d.duplicated().any()
    assert not d[sorted(items)].isna().any().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["FACULTY"] = d["FACULTY"].str.strip()
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long["cov_gender"] = long["cov_gender"].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() == 340
        assert long["item"].nunique() == len(its)
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

        if table == "suyato_2023_cbq":
            opts = parse_coding(K_CODING)
            text = []
            for it in its:
                for resp, opt in opts.items():
                    text.append({
                        "table": table, "section_id": f"{table}_1",
                        "item": it,
                        "instrument": "Citizenship Behavior Questionnaire "
                                      "(CBQ)",
                        "instructions": "", "section_prompt": "",
                        "item_text": book.loc[it, "label"].strip(),
                        "correct_response": "", "option_text": opt,
                        "resp": resp})
            tx = pd.DataFrame(text)
            assert set(tx["item"]) == set(long["item"])
            assert set(tx["resp"]) == allowed
            tx.to_csv(TEXT_DIR / f"{table}__items.csv", index=False)
            print(f"{table}__items.csv: rows={len(tx)}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
