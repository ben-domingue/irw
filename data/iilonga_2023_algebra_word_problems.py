#!/usr/bin/env python3
# Source: https://researchdata.up.ac.za/articles/dataset/Algebraic_word_problem_solving_achievement_test_and_strategies/23634318
# DOI: 10.25403/UPresearchdata.23634318.v1 (dataset; no paper DOI on the record)
#   Iilonga, Hesekiel & Ogbonnaya, Ugorji (2023). "Algebraic word problem solving
#   achievement test and strategies" [data set]. University of Pretoria research
#   data repository (figshare).
# Data: "Algebraic word problem solving achievement test data.xlsx", sheet "Test
#       results": 351 Namibian secondary learners (ten schools A-J, learner codes
#       "1A".."34J") x six algebraic word problems Q1-Q6, each scored on four Polya
#       domains by a rubric "modified from Charles (1987) and Sumaryanta (2015)":
#       D1 understanding the problem, D2 devising a plan, D3 carrying out the plan,
#       D4 rechecking (looking back); plus per question N (no attempt flag), T
#       (= D1+D2+D3+D4) and Strategy (Krulik & Rudnick strategy code), and a Grand
#       Total. Row 1 is a legend (gender, home-language and field codes). The other
#       sheets ("Domains", "Overall Strategies", "Learners' biograph") are
#       aggregate tables.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: xlsx headers are codes only (Q1-Q6 x
#   D1-D4, no variable/value labels); the six problems are not in the deposit (the
#   interview docx has transcripts only), and the rubric's per-domain anchors are
#   not published there either.
#
# Shipped: iilonga_2023_algebra_word_problems -- 24 rubric scores, item = "Q<k>_D<j>",
#   item_family = "Q<k>" (the four domain scores of one problem are not locally
#   independent). Observed score ranges: D1, D2, D4 0-2; D3 0-4 (no rubric
#   document; ranges taken from the scores, consistent across all six problems).
#   One Q4_D4 = 3 dropped: the only 3 on any D4 item (2,105 D4 scores otherwise
#   0-2), i.e. an isolated entry error. "No attempt" rows are kept as scored by
#   the source (all four domains 0).
# Not shipped: per-question T and Grand Total (sums of the shipped scores), N (no-
#   attempt flag; already reflected in the zero scores), Strategy (nominal strategy
#   code, not a score).
# Covariates: cov_gender (M/F), cov_home_language (OS Oshiwambo, EN English, AF
#   Afrikaans, P Portuguese, DN Damara-Nama), cov_field (NS natural science, SS
#   social science, T technology, C commerce); cluster_id = school letter from the
#   learner code.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "iilonga_2023"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/41471124"
NAME = "iilonga_2023_algebra_word_problems"
DOMS = {"D1": range(0, 3), "D2": range(0, 3), "D3": range(0, 5), "D4": range(0, 3)}


def fetch() -> Path:
    p = RAW_DIR / "test_data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    raw = pd.read_excel(fetch(), sheet_name="Test results", header=None)
    assert raw.shape == (354, 47)
    hdr = raw.iloc[2].tolist()
    assert hdr[1:4] == ["Gender", "Home language", "Field of study"]
    cols = ["learner", "cov_gender", "cov_home_language", "cov_field"]
    for q in range(1, 7):
        assert raw.iloc[1, 4 + 7 * (q - 1)] == f"Q{q}"
        assert hdr[4 + 7 * (q - 1): 11 + 7 * q - 7] == ["D1", "D2", "D3", "D4", "N", "T", "Strategy"]
        cols += [f"Q{q}_{k}" for k in ["D1", "D2", "D3", "D4", "N", "T", "S"]]
    cols += ["GT"]
    d = raw.iloc[3:].copy()
    d.columns = cols
    d = d[d["learner"].notna()].reset_index(drop=True)
    assert len(d) == 351 and d["learner"].astype(str).str.strip().is_unique
    items = [f"Q{q}_{k}" for q in range(1, 7) for k in DOMS]
    sc = d[items].apply(pd.to_numeric)
    for q in range(1, 7):       # T is the sum of the four domain scores
        assert (sc[[f"Q{q}_{k}" for k in DOMS]].sum(axis=1) == d[f"Q{q}_T"].astype(int)).all()
    skipped = [c for c in cols if c not in items + cols[:4]]
    print(f"  [skip] {len(skipped)} columns: per-question T and GT (sums), N (no-attempt "
          f"flag), Strategy (nominal code): {skipped}")

    d.insert(0, "id", range(1, len(d) + 1))
    d["cluster_id"] = d["learner"].astype(str).str.strip().str.extract(r"^\d+([A-Z])$")[0]
    assert d["cluster_id"].notna().all()
    covs = ["cov_gender", "cov_home_language", "cov_field"]
    for c in covs:
        d[c] = d[c].astype(str).str.strip()
    t = d.melt(id_vars=["id", "cluster_id"] + covs, value_vars=items,
               var_name="item", value_name="resp")
    t["resp"] = pd.to_numeric(t["resp"])
    t["item_family"] = t["item"].str.split("_").str[0]
    dom = t["item"].str.split("_").str[1]
    ok = pd.Series([r in DOMS[k] for r, k in zip(t["resp"], dom)], index=t.index)
    print(f"  dropped {(~ok).sum()} out-of-range score(s): "
          f"{t.loc[~ok, ['id', 'item', 'resp']].values.tolist()}")
    assert (~ok).sum() == 1
    t = t[ok]
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "cluster_id"] + covs + ["item_family"]]
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(items) and not t.duplicated(["id", "item"]).any()
    pv = {i: set(DOMS[i.split("_")[1]]) for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
