#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/P5G6RW
# DOI: 10.7910/DVN/P5G6RW (dataset; no paper DOI on the record)
#   Song, Yunping (2026). "The Influence of Family Quality of Life (FQoL) on the Parenting
#   Self-efficacy (PSE) of Parents of Pre-school Children: The Moderating Role of Parenting
#   Styles" [data set], Harvard Dataverse.
# Data: "1汇总数据-删除答案重复数据.sav" ("pooled data - duplicate answers removed", file
#       13378177): 1003 parents of Chinese pre-school children x 205 columns: demographics
#       (@1-@10), three item blocks (@11_1-25, @12_1-53, @13_1-40) and many derived scores.
#       Each item's variable label holds its Chinese wording (the first item of each block
#       also carries the block's instructions); no value labels on the items.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: variable labels hold every item's Chinese stem
#   (cheap: data_labels); value labels are absent, so the 1-5 anchors are not in the deposit,
#   and the English _translated columns would be IRW-generated -- left for a later pass.
#
# Tables (item code = header without the leading "@", e.g. 11_3 -> Q11_3; all 1-5):
#   song_2026_fqol                    Q11_1-25  family quality of life (subscales in the
#                                               file: family interaction, parenting,
#                                               emotional well-being, physical/material
#                                               well-being, disability-related support)
#   song_2026_parenting_self_efficacy Q12_1-53  parenting self-efficacy (acceptance, love
#                                               expression, safety, rules, companionship,
#                                               education, daily routine)
#   song_2026_parenting_style         Q13_1-40  parenting style (indulgent, democratic,
#                                               permissive, authoritarian, neglectful)
# Skipped: 序号 (kept as id), the total score, every subscale mean (FQ*, SE*, PS*), the
#   constant *_mean_1 columns, interaction terms, PRE_1/PGR_1 (regression output), 类型
#   (style classification), and the multi-select "who mainly cares for the child" dummies
#   (@2).
# Covariates (codes; the deposit has no value labels for them): cov_respondent_role (@1,
#   "you are the child's ...", 1/2), cov_parent_age_band (@3), cov_parent_education (@4),
#   cov_child_sex (@5, as recorded -- 8 distinct codes), cov_child_age_band (@6),
#   cov_n_children (@7), cov_child_living (@8), cov_residence (@9), cov_income_band (@10).

import re
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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "song_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/13378177?format=original"

TABLES = {"song_2026_fqol": ("11", 25), "song_2026_parenting_self_efficacy": ("12", 53),
          "song_2026_parenting_style": ("13", 40)}
COV_PREFIX = {"@1、": "cov_respondent_role", "@3、": "cov_parent_age_band",
              "@4、": "cov_parent_education", "@5、": "cov_child_sex", "@6、": "cov_child_age_band",
              "@7、": "cov_n_children", "@8、": "cov_child_living", "@9、": "cov_residence",
              "@10、": "cov_income_band"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(fetch())
    assert d.shape == (1003, 205), d.shape
    cols = {t: [f"@{b}_{i}" for i in range(1, k + 1)] for t, (b, k) in TABLES.items()}
    items = {c for v in cols.values() for c in v}
    assert items <= set(d.columns)
    covmap = {}
    for pre, new in COV_PREFIX.items():
        hit = [c for c in d.columns if c.startswith(pre)]
        assert len(hit) == 1, (pre, hit)
        covmap[hit[0]] = new
    rest = [c for c in d.columns if c not in items | set(covmap) | {"序号"}]
    print(f"  skip {len(rest)} columns: total, subscale means, constants, interactions, "
          "regression output, style class, caregiver dummies")
    assert d["序号"].is_unique
    d = d.rename(columns={"序号": "id", **covmap})
    d["id"] = d["id"].astype(int)
    covs = list(covmap.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in cols.items():
        cmap = {c: "Q" + c[1:] for c in its}
        t = d[["id"] + covs + its].rename(columns=cmap).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in cmap.values()}
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
