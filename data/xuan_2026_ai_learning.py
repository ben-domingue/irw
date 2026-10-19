#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/QDK2ZO
# DOI: 10.7910/DVN/QDK2ZO
#   Xuan, Q. (2026). Data: Self-regulated learning pathways to university
#   students' intention to learn artificial intelligence: Do discipline and
#   gender matter? [Dataset]. Harvard Dataverse.
# Data: "rawdata_919.sav" (served as a .tab) -- 919 Chinese university
#   students, 115 items in 22 named blocks, every one on the same 1-6 scale,
#   with no missing cell anywhere in the file.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped, and extraction is solved -- every item's full
#   administered Chinese stem is in its SPSS variable label, and the label of
#   each block's FIRST item also carries the block's own name and number
#   ("8、AI工具的依赖度—1.当我无法访问AI时，我在外语学习中感到不安全。"). That
#   naming is where this script's table names come from, so the grouping is
#   the source's, not a guess from the prefixes. The eight metacognition
#   blocks are MAI subscales and the MAI's rights-register verdict is `hold`,
#   so the text waits on that ruling rather than on work.
#
# TWENTY-TWO tables, one per block, 919 respondents and 1-6 throughout.
# The block names are translations of the deposit's own label prefixes:
#   AIdep   11  AI工具的依赖度        dependence on AI tools
#   ready    4  使用AI工具的准备度    readiness to use AI tools
#   anxi     4  使用AI工具的焦虑度    anxiety about using AI tools
#   atti     4  使用AI工具的态度      attitude to using AI tools
#   IM       4  使用AI工具的内在动机  intrinsic motivation
#   related  4  自我感知关联度        perceived relatedness
#   supp     4  自我感知支持度        perceived (teacher) support
#   auto     4  自我感知自主性        perceived autonomy
#   comp     4  自我感知能力          perceived competence
#   ES       4  外界支持              external support
#   SC       4  辅助条件              facilitating conditions
#   SE       4  使用AI的自我效能      AI self-efficacy
#   effect   4  使用AI工具的效度      perceived usefulness
#   IAI      4  使用AI工具的意愿      intention to learn AI
#   DK       8  陈述性知识            declarative knowledge
#   PK       4  程序性知识            procedural knowledge
#   CK       5  条件性知识            conditional knowledge
#   plan     7  计划                  planning
#   IMS     10  信息管理策略          information management strategies
#   M        7  监控                  monitoring
#   RE       5  调节策略              regulation strategies
#   MSE      6  自我学习评价          self-evaluation
#
# id: the row index. The deposit carries no respondent id column.
# Covariates: cov_grade, cov_university_type, cov_major, cov_foreign_language
#   _level, cov_age_band, cov_gender, cov_prior_genai_use -- the deposit's own
#   codes, with no value labels documented, so nothing is relabelled. cov_age
#   _band is bands (1-4), not years, which is why it is not named cov_age.
import os
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
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "qdk2zo" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 14148148, "rawdata_919.sav"
SCALE = set(range(1, 7))
COVS = {"grade": "cov_grade", "stype": "cov_university_type",
        "major": "cov_major", "Elevel": "cov_foreign_language_level",
        "age": "cov_age_band", "gender": "cov_gender",
        "usage": "cov_prior_genai_use"}
# prefix -> (table suffix, item count, the Chinese block name in the label)
BLOCKS = [
    ("AIdep", "ai_dependence", 11, "AI工具的依赖度"),
    ("ready", "ai_readiness", 4, "使用AI工具的准备度"),
    ("anxi", "ai_anxiety", 4, "使用AI工具的焦虑度"),
    ("atti", "ai_attitude", 4, "使用AI工具的态度"),
    ("IM", "intrinsic_motivation", 4, "使用AI工具的内在动机"),
    ("related", "perceived_relatedness", 4, "自我感知关联度"),
    ("supp", "perceived_support", 4, "自我感知支持度"),
    ("auto", "perceived_autonomy", 4, "自我感知自主性"),
    ("comp", "perceived_competence", 4, "自我感知能力"),
    ("ES", "external_support", 4, "外界支持"),
    ("SC", "facilitating_conditions", 4, "辅助条件"),
    ("SE", "ai_self_efficacy", 4, "使用AI的自我效能"),
    ("effect", "perceived_usefulness", 4, "使用AI工具的效度"),
    ("IAI", "intention_to_learn_ai", 4, "使用AI工具的意愿"),
    ("DK", "declarative_knowledge", 8, "陈述性知识"),
    ("PK", "procedural_knowledge", 4, "程序性知识"),
    ("CK", "conditional_knowledge", 5, "条件性知识"),
    ("plan", "planning", 7, "计划"),
    ("IMS", "information_management", 10, "信息管理策略"),
    ("M", "monitoring", 7, "监控"),
    ("RE", "regulation_strategies", 5, "调节策略"),
    ("MSE", "self_evaluation", 6, "自我学习评价"),
]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 919, len(df)
    assert not df.isna().any().any(), "the file is complete; a blank is new"

    # Every block is named in its first item's label. Refuse a block whose
    # label no longer carries the name this script translated.
    plan = {}
    for prefix, suffix, n, zh in BLOCKS:
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        missing = [c for c in cols if c not in df.columns]
        assert not missing, (prefix, missing)
        assert zh in (labels.get(cols[0]) or ""), (cols[0], labels.get(cols[0]))
        for c in cols[1:]:
            assert len((labels.get(c) or "").strip()) > 4, (c, labels.get(c))
        plan[f"xuan_2026_{suffix}"] = cols

    item_cols = [c for cols in plan.values() for c in cols]
    assert len(item_cols) == len(set(item_cols)) == 115, len(item_cols)
    unaccounted = sorted(set(df.columns) - set(item_cols) - set(COVS))
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, cols in plan.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the administered 1-6 scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 919 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == 919 * 115, total
    print(f"22 tables, {total} responses")


if __name__ == "__main__":
    main()
