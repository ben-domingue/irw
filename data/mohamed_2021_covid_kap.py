#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7856621
# DOI: 10.1186/s12889-021-10319-5
#   "Knowledge, attitude and practice of the Sudanese people towards COVID-19:
#   an online survey" (Mohamed, Elhassan, Mohamed, Mohammed, Edris, Mahgoop,
#   Sharif, Bashir, Abdelrahim, Idriss & Malik, 2021), BMC Public Health 21:274.
# Data: the article's only additional file, 12889_2021_10319_MOESM1_ESM.xlsx
#       (987 x 65, sheet "KAP COVID19 dataset"), fetched from the Europe PMC
#       supplementaryFiles zip. No codebook is deposited; columns were decoded
#       against the paper's Methods and Tables 1-2 (marginal counts).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data are
#          the article's own supplementary file.
#
# Item text: not shipped. No codebook or questionnaire is deposited (the paper
#   says the questionnaire is "attached in the supplementary appendix", but the
#   only additional file is this workbook). Table 2 of the paper prints the five
#   attitude statements and six practice statements, and their counts match the
#   columns exactly (e.g. att@mask 491 = "Wearing masks is important ..." 491),
#   so those two tables are recoverable from Table 2; the administration
#   language of the Google Form is not stated. Knowledge columns k1..k22 are
#   NOT recoverable item by item: Table 2 lists 19 knowledge options and the
#   file has 22 columns (see below).
#
# Sample: adult Sudanese (18+) answering a Google Form shared on Facebook and
# WhatsApp, 7-13 April 2020. No id column; id = row number.
#
# Tables:
#   (no knowledge table) k1..k22 are skipped -- ben-domingue, 2026-10-04. Each
#       column is one option of a select-all-that-apply question, already SCORED
#       by the authors (1 = credited; e.g. k1 "airborne" is credited when NOT
#       selected), and the 22 columns do not map one-to-one onto the 19 options
#       Table 2 lists, so no item can be identified. Their sum reproduces the
#       paper's mean knowledge score of 15.33 (asserted below as a sanity check).
#   mohamed_2021_covid_attitude   5 yes/no attitude items (1 = yes, 0 = no),
#       sum = attscore on every row (asserted).
#   mohamed_2021_covid_practice   6 practice items: own practice of social
#       distancing, hand washing, avoiding handshakes (binary as deposited --
#       the paper: "Yes frequently answer were considered as yes while yes
#       sometimes and no were considered as no", so these three are the
#       authors' collapse; the three-level originals are not in the file), and
#       the family's social distancing / hand washing / mask use on the raw
#       three-level coding (1 = yes frequently, 2 = yes sometimes, 3 = no;
#       1 is fixed by famsocial/famhandwash/fammasks == (raw == 1), asserted,
#       and by Table 2's counts 293/567/133). Direction therefore differs
#       between the two halves (own: 1 = practises; family: 1 = most practice).
#
# Duplicates: the paper says duplicates were excluded, but five pairs of rows
# are identical on all 65 columns (rows 40/42, 64/65, 247/733, 316/318,
# 736/742 in file order, mostly adjacent -- double submissions). The second of
# each pair is dropped (asserted: exactly 5), leaving 982 respondents.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
CACHE = REPO_ROOT / "automated_finding" / "runs" / "raw" / "mohamed_2021"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7856621/supplementaryFiles"
FNAME = "12889_2021_10319_MOESM1_ESM.xlsx"

KNOW = [f"k{i}" for i in range(1, 23)]
ATT = ["att@handwash", "att@mask", "att@iso", "att@distanc", "att@danger"]
PRAC_OWN = ["practice@socialdistance", "practice@handwashing", "practice@handshaking"]
PRAC_FAM = ["Fam@practice@social", "fam@practice@handwash", "fam@practice@facemask"]
COV = {
    "agegroups": "cov_age_group",        # 1 = under 30 (576), 2 = 30+ (411)
    "AREAOFRESIDENCE": "cov_residence",  # 1 Khartoum (708), 2 outside Sudan (111), 3 other states (168)
    "gender": "cov_gender",              # 1 male (549), 2 female (438)
    "Education": "cov_education",        # 1 university+ (940), 2 basic (47)
    "awarness": "cov_awareness",         # 1 aware of the pandemic (901), 2/3 no or not sure
}
SKIP = {
    "k4": "constant 0 on all 987 rows (no information)",
    "knwscore": "knowledge sum score (composite)",
    "attscore": "attitude sum score (composite)",
    "practicescore": "practice sum score (composite)",
    "pracctscore": "practice sum score incl. family (composite)",
    "pracres": "dichotomised practice score (composite)",
    "KnowS": "dichotomised knowledge score (composite)",
    "AttitS": "dichotomised attitude score (composite)",
    "pracsresult": "dichotomised practice score (composite)",
    "famsocial": "binary recode of Fam@practice@social (== 1)",
    "famhandwash": "binary recode of fam@practice@handwash (== 1)",
    "fammasks": "binary recode of fam@practice@facemask (== 1)",
    "neigh@practice@social": "neighbours' practice, 1-4 coding undocumented",
    "Neigh@practice@masks": "neighbours' practice, 1-4 coding undocumented",
    "clarity": "question not described in the paper",
    "badattitude": "question not described in the paper",
    "socialgatherings": "question not described in the paper",
    "bakeries": "question not described in the paper",
    "shopps": "question not described in the paper",
    "transportation": "question not described in the paper",
    "effect": "question not described in the paper",
}
SKIP.update({k: "scored select-all option; mapping to the paper's 19 options "
                "undocumented (skipped, ben-domingue 2026-10-04)"
             for k in KNOW if k != "k4"})
SKIP.update({f"s{i}": "source-of-information checklist (s2, s3 not identifiable "
                       "in Table 1); not an instrument" for i in range(1, 8)})


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / FNAME
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FNAME))
    return pd.read_excel(p)


def main():
    d = fetch()
    assert d.shape == (987, 65), d.shape
    assert (d["k4"] == 0).all()
    # the paper's mean knowledge score (15.33) is the mean of the k-column sum
    # (15.329), not of the deposited knwscore (15.299)
    assert abs(d[KNOW].sum(axis=1).mean() - 15.33) < 0.005
    assert (d[ATT].sum(axis=1) == d["attscore"]).all()
    for raw, b in zip(PRAC_FAM, ["famsocial", "famhandwash", "fammasks"]):
        assert ((d[raw] == 1).astype(int) == d[b]).all(), raw
    assert [int((d[c] == 1).sum()) for c in PRAC_OWN] == [601, 684, 266]

    tables = {
        "mohamed_2021_covid_attitude": (ATT, {k: {0, 1} for k in ATT}),
        "mohamed_2021_covid_practice": (PRAC_OWN + PRAC_FAM,
                                        {**{k: {0, 1} for k in PRAC_OWN},
                                         **{k: {1, 2, 3} for k in PRAC_FAM}}),
    }
    assert len(tables) == len(set(tables))
    used = [c for items, _ in tables.values() for c in items]
    assert len(used) == len(set(used))
    accounted = set(used) | set(COV) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")

    dup = d.duplicated(keep="first")
    assert int(dup.sum()) == 5, int(dup.sum())
    d = d[~dup].reset_index(drop=True)
    print("  dropped 5 exact-duplicate rows (double submissions)")
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COV)
    cov_cols = list(COV.values())

    for name, (items, pv) in tables.items():
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t["item"] = t["item"].str.replace("@", "_").str.lower()
        pvn = {k.replace("@", "_").lower(): v for k, v in pv.items()}
        for i, s in pvn.items():
            assert set(t.loc[t["item"] == i, "resp"]) <= s, (name, i)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t, permitted_values=pvn)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pvn})
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
