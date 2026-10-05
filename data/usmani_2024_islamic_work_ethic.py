#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/6xt3b959nv/1
# DOI: 10.1016/j.heliyon.2024.e37032
#   "Perceptions of politics and knowledge sharing: Moderating role of Islamic
#   work ethic in the Islamic banking industry of Pakistan" (Usmani, 2024),
#   Heliyon 10(18):e37032. PMC11422587.
# Data: Mendeley Data doi:10.17632/6xt3b959nv.1 "ISLAMIC WORK ETHICS DATA SET
#       (125 respondents)", POSTDOCDATA.sav (125 x 44, SPSS). The article's own
#       SI (mmc1.doc) is the questionnaire, not data.
# License: CC BY 4.0 on the Mendeley Data deposit (data_licence short_name
#          "CC BY 4.0"), which governs the data. The article itself is
#          CC BY-NC 4.0 (Europe PMC core record).
#
# Item text: shipped (SPSS variable labels carry every item stem verbatim;
#   value labels carry the 5 anchors 1 = Strongly Disagree ... 5 = Strongly
#   Agree on every item). Both label levels checked; both cross-checked against
#   the questionnaire in the article's SI mmc1.doc, administered in English.
#   Built by automated_finding/itemtext_verification/make_itemtext_usmani_2024.py.
#
# Sample: 125 employees of seven Islamic / window-Islamic banks in Karachi,
# Pakistan (convenience sample, paper/hard-copy and online questionnaire).
# No id column in the file: the row index (1..125) is the id.
#
# Tables (all items 1-5, 5-point Likert, Strongly Disagree ... Strongly Agree):
#   usmani_2024_iwe   Islamic Work Ethic, short version (Ali 1992), IWE1-17
#   usmani_2024_ks    Knowledge Sharing (van den Hooff & de Ridder), KS1-10
#   usmani_2024_pops  Perceptions of Organizational Politics Scale (Kacmar &
#                     Ferris 1991), 12 items in three subscales: general
#                     political behaviour PPGP1-6, go along to get ahead
#                     PPGAL1-4, pay and promotion PPPP1-2. The paper scores it
#                     as one 12-item scale, so it ships as one table.
#
# Duplicates: two pairs of rows are identical on all 39 items (ids 36/37 are
# identical on every column; ids 23/27 differ only in EXPERIENCE). Exact
# agreement on 39 five-point items is not chance; read as double entry of a
# hard-copy questionnaire. The second row of each pair is dropped, so N = 123.
#
# Covariates: GENDER and BANKNAME counts match the paper's Table 2 exactly.
#   EXPERIENCE is skipped: the file's value labels have five levels (and skip
#   "2 to 3 years") while the questionnaire has six and the data use codes 1-6;
#   code 6 (48 people) is unlabelled and the paper's Table 2 counts for the
#   middle bands do not match the codes under either reading.
#   EDUCATION code 4 (one person) is unlabelled -> NA.
#
# No imputation (every item cell is an integer), no missing item cells. The
# questionnaire asked for name/contact/email, but none of it is in the
# deposited file (44 columns: 39 items + 5 coded demographics).

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "usmani_2024" / "POSTDOCDATA.sav"
URL = ("https://data.mendeley.com/public-files/datasets/6xt3b959nv/files/"
       "ae60b205-3109-4deb-9021-dd89a6bf54d9/file_downloaded")


def load():
    if not RAW.exists():
        r = requests.get(URL, timeout=120)
        r.raise_for_status()
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_bytes(r.content)
    return pyreadstat.read_sav(str(RAW))


def main() -> None:
    d, meta = load()
    assert d.shape == (125, 44), d.shape

    tables = {
        "usmani_2024_iwe": [f"IWE{i}" for i in range(1, 18)],
        "usmani_2024_ks": [f"KS{i}" for i in range(1, 11)],
        "usmani_2024_pops": [f"PPGP{i}" for i in range(1, 7)]
                            + [f"PPGAL{i}" for i in range(1, 5)]
                            + [f"PPPP{i}" for i in range(1, 3)],
    }
    item_cols = [c for items in tables.values() for c in items]
    assert len(item_cols) == len(set(item_cols)) == 39
    assert d[item_cols].notna().all().all()
    assert (d[item_cols] % 1 == 0).all().all()

    d.insert(0, "id", range(1, len(d) + 1))
    # paper Table 2 (all 125): 90 male / 35 female; banks 26/9/52/10/8/9/11
    assert d["GENDER"].value_counts().to_dict() == {1: 90, 2: 35}
    assert d["BANKNAME"].value_counts().sort_index().tolist() == [26, 9, 52, 10, 8, 9, 11]

    # double-entered rows (see header)
    dup = d.duplicated(subset=item_cols, keep="first")
    assert dup.sum() == 2, dup.sum()
    assert sorted(d.loc[dup, "id"]) == [27, 37]
    print(f"  [drop] ids {sorted(d.loc[dup, 'id'])}: exact duplicates on all 39 items")
    d = d.loc[~dup].copy()

    d["cov_gender"] = d["GENDER"].map({1: "male", 2: "female"})
    d["cov_age_group"] = d["AGE"].map({1: "under 21", 2: "21-30", 3: "31-40",
                                       4: "41-50", 5: "over 50"})
    d["cov_education"] = d["EDUCATION"].map({1: "undergraduate", 2: "graduate",
                                             3: "doctorate"})
    d["cov_bank"] = d["BANKNAME"].map({
        1: "Habib Metropolitan Bank", 2: "Dubai Islamic Bank",
        3: "Meezan Islamic Bank", 4: "MCB Islamic Bank", 5: "Faysal Bank",
        6: "Al Baraka Bank", 7: "BankIslami"})
    for c in ["cov_gender", "cov_age_group", "cov_bank"]:
        assert d[c].notna().all(), c
    assert d["cov_education"].isna().sum() == 1
    cov_cols = ["cov_gender", "cov_age_group", "cov_education", "cov_bank"]

    skipped = {
        "EXPERIENCE": "value labels inconsistent with the questionnaire and the "
                      "paper (code 6, n=48, unlabelled); see header",
    }
    accounted = {"id", "GENDER", "AGE", "EDUCATION", "BANKNAME"} | set(item_cols) | set(skipped)
    orig = set(d.columns) - set(cov_cols)
    assert orig == accounted, orig ^ accounted
    for c, why in skipped.items():
        print(f"  [skip] {c}: {why}")

    assert len(tables) == len(set(tables))
    for name, items in tables.items():
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: {1, 2, 3, 4, 5} for i in items}
        for i, s in pv.items():
            assert set(t.loc[t["item"] == i, "resp"]) <= s, (name, i)
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
