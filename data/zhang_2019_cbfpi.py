#!/usr/bin/env python3
# Source: https://plos.figshare.com/articles/dataset/The_development_and_psychometric_evaluation_of_the_Chinese_Big_Five_Personality_Inventory-15/9737441
# DOI: 10.1371/journal.pone.0221621
#   Zhang, X., Wang, M.-C., He, L., Jie, L., & Deng, J. (2019). "The
#   development and psychometric evaluation of the Chinese Big Five
#   Personality Inventory-15." PLOS ONE, 14(8), e0221621. (Open access,
#   PMC6771307.)
# Data: the article's three supporting-information files on figshare:
#       S1 (pone.0221621.s001.xls, sheet "tengxun", 10,738 x 54): Sample 1,
#       adults who took the CBF-PI-B online in 2017;
#       S2 (pone.0221621.s002.xls, sheet "shenqi", 256 x 131): Sample 2,
#       Guangzhou University students;
#       S3 (.s003.docx): the 15 retained items in English and Chinese.
#       The paper's sample sizes (10,738 and 256) and Sample 1's 62.4% male
#       share are reproduced (asserted).
# License: CC BY 4.0 (figshare API).
#
# Item text: not shipped. Both label levels checked: .xls files, so there
#   are no variable or value labels; headers are positional (item1-item40,
#   CBF1-40, IPIP1-20, ...). S3.docx prints the 15 CBF-PI-15 items in
#   English and Chinese with their CBF-PI-B item numbers (paper_explicit for
#   15 of the 40 items, so it needs a verify script); the other 25 CBF-PI-B
#   items and the Mini-IPIP, BFI-10, BIS-Brief, PHQ-9 and GAD-7 stems are in
#   their published Chinese versions.
#
# Instruments and ranges (paper, "Measures"):
#   zhang_2019_cbfpi_b     CBF-PI-B, 40 items, 1-6 (disagree strongly ..
#                          agree strongly); both samples, cov_study. Items
#                          5, 8, 13, 15, 18, 32 and 36 are reverse-keyed,
#                          and the file stores them ALREADY REVERSED: the
#                          stored "E for CBF-PI-15" is the plain sum of
#                          items 5, 15 and 35 in every Sample 1 row
#                          (asserted). Item codes: Sample 1's itemK and
#                          Sample 2's CBFK are the same item K (the paper
#                          numbers the CBF-PI-B 1-40 in both); shipped as
#                          CBFK.
#   zhang_2019_mini_ipip   Mini-IPIP, 20 items, 1-5; Sample 2.
#   zhang_2019_bfi10       BFI-10, 10 items, 1-5; Sample 2.
#   zhang_2019_bis_brief   BIS-Brief, 8 items, 1-4 (rarely/never .. almost
#                          always/always); Sample 2.
#   zhang_2019_phq9        PHQ-9, 9 items, 1-4 (not at all .. nearly every
#                          day); Sample 2.
#   zhang_2019_gad7        GAD-7, 7 items, 1-4; Sample 2.
#   Whether the Mini-IPIP/BFI-10/BIS reverse-keyed items are stored raw or
#   reversed is not documented and not asserted.
#
# Cleaning:
#   - 999 is Sample 2's missing code (every block and covariate) -> NA.
#   - Out of the documented 1-4 range -> NA: BIS7 (one 5), GAD2 (one 5),
#     GAD7 (one 5).
#   - Sample 1 holds 10 exact repeated submissions: pairs of rows, mostly
#     with adjacent IDs, that agree on gender, age and all 40 items with
#     non-constant patterns. The later row of each pair is dropped
#     (asserted 10), so Sample 1 ships 10,728 people, not 10,738.
# Dropped columns:
#   - Sample 2 TriPM1-TriPM6: the paper never mentions the TriPM, and the
#     block is mislabelled: TriPM6 equals "Academic Performance" in every row
#     (asserted), and TriPM1-5 look like substance-use frequency codes. No
#     identity or range can be documented.
#   - Sample 2 Smoking, Drinking (codes undocumented) and "other
#     nationalities" (free-text ethnic group, e.g. Yao, Hui; no PII).
#   - Sample 1 "age group" (0-4, a derived banding of age).
#   - All composites: CBF-PI-B and CBF-PI-15 trait sums, Mini-IPIP and
#     BFI-10 trait sums, Total BIS/PHQ/GAD.
#   - ID / number: row counters.
# id: row index, Sample 1 first (1..10,728), then Sample 2.
# Covariates: cov_study (1 = Sample 1 online adults, 2 = Sample 2
#   students), cov_gender (1 male, 2 female; Sample 1's 62.4% male share
#   pins the coding), cov_age; Sample 2 also cov_han (1 Han, 2 other ethnic
#   group) and cov_academic_performance (self-rated vs classmates, 1 lower
#   .. 5 upper percentile per the paper; the one 6 -> NA).

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
S1_URL = "https://ndownloader.figshare.com/files/17438846"
S2_URL = "https://ndownloader.figshare.com/files/17438849"

CBF = [f"CBF{i}" for i in range(1, 41)]
S2_TABLES = {
    "zhang_2019_mini_ipip": ([f"IPIP{i}" for i in range(1, 21)], range(1, 6)),
    "zhang_2019_bfi10": ([f"BFI{i}" for i in range(1, 11)], range(1, 6)),
    "zhang_2019_bis_brief": ([f"BIS{i}" for i in range(1, 9)], range(1, 5)),
    "zhang_2019_phq9": ([f"PHQ{i}" for i in range(1, 10)], range(1, 5)),
    "zhang_2019_gad7": ([f"GAD{i}" for i in range(1, 8)], range(1, 5)),
}
S1_COMPOSITES = {f"{t} for CBF-PI-B" for t in "ONACE"} | \
    {f"{t} for CBF-PI-15" for t in "NCAOE"}
S2_COMPOSITES = (
    {f"{t} for Mini IPIP" for t in "NCAOE"}
    | {f"{t} for BFI-10" for t in "NCAOE"}
    | {"Total BIS", "Total PHQ", "Total GAD"}
    | {f"{t} for CBF-PI-B" for t in "NCAOE"}
    | {"N for CBF-PI-15", "C CBF-PI-15", "A CBF-PI-15", "O CBF-PI-15",
       "E CBF-PI-15"})
TRIPM = [f"TriPM{i}" for i in range(1, 7)]
S2_DROPPED = {"Smoking", "Drinking", "other nationalities"}
OUT_OF_RANGE = {"BIS7": 1, "GAD2": 1, "GAD7": 1}


def load(url):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def write(table, long, items, allowed, cov_cols):
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = set(allowed)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (table, it, bad)
    pv = {i: allowed for i in items}
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(items) > 1
    fails = [(c.name, c.detail) for c in run_qc(long, permitted_values=pv)
             if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{table}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")
    return table


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Sample 1 ----
    s1 = load(S1_URL)
    assert s1.shape == (10738, 54), s1.shape
    s1_items = [f"item{i}" for i in range(1, 41)]
    known = {"ID", "gender", "age", "age group"} | set(s1_items) | \
        S1_COMPOSITES
    assert set(s1.columns) == known, set(s1.columns) ^ known
    assert (s1[s1_items].isin(range(1, 7))).all().all()
    assert round((s1["gender"] == 1).mean(), 3) == 0.624
    # reverse-keyed items are stored reversed: E-15 = 5 + 15 + 35 as stored
    assert (s1[["item5", "item15", "item35"]].sum(axis=1)
            == s1["E for CBF-PI-15"]).all()
    dup = s1.duplicated(["gender", "age"] + s1_items, keep="first")
    assert dup.sum() == 10, dup.sum()
    s1 = s1[~dup].reset_index(drop=True)
    s1 = s1.rename(columns={f"item{i}": f"CBF{i}" for i in range(1, 41)})
    s1 = s1.rename(columns={"gender": "cov_gender", "age": "cov_age"})
    s1.insert(0, "cov_study", 1)
    s1.insert(0, "id", s1.index + 1)

    # ---- Sample 2 ----
    s2 = load(S2_URL)
    assert s2.shape == (256, 131), s2.shape
    s2_items = CBF + [i for its, _ in S2_TABLES.values() for i in its]
    known = ({"number", "gender", "age", "nationality", "Academic Performance"}
             | set(s2_items) | set(TRIPM) | S2_DROPPED | S2_COMPOSITES)
    assert set(s2.columns) == known, set(s2.columns) ^ known
    assert (s2["TriPM6"] == s2["Academic Performance"]).all()
    assert not s2.drop(columns="number").duplicated().any()
    s2 = s2.replace(999, np.nan)
    s2["age"] = pd.to_numeric(s2["age"].replace("999", np.nan))
    for c, n in OUT_OF_RANGE.items():
        hi = s2[c] > 4
        assert hi.sum() == n, (c, hi.sum())
        s2.loc[hi, c] = np.nan
    s2.loc[s2["Academic Performance"] == 6, "Academic Performance"] = np.nan
    s2 = s2.rename(columns={"gender": "cov_gender", "age": "cov_age",
                            "nationality": "cov_han",
                            "Academic Performance":
                                "cov_academic_performance"}).copy()
    s2.insert(0, "cov_study", 2)
    s2.insert(0, "id", len(s1) + s2.index + 1)

    names = []
    # CBF-PI-B, both samples
    covs = ["cov_study", "cov_gender", "cov_age"]
    both = pd.concat([s1[["id"] + covs + CBF], s2[["id"] + covs + CBF]],
                     ignore_index=True)
    long = both.melt(id_vars=["id"] + covs, value_vars=CBF, var_name="item",
                     value_name="resp")
    names.append(write("zhang_2019_cbfpi_b", long, CBF, range(1, 7), covs))

    covs2 = ["cov_gender", "cov_age", "cov_han", "cov_academic_performance"]
    for table, (its, allowed) in S2_TABLES.items():
        long = s2.melt(id_vars=["id"] + covs2, value_vars=its,
                       var_name="item", value_name="resp")
        names.append(write(table, long, its, allowed, covs2))
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
