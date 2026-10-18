#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/zdfpy5wtmy
# DOI: 10.17632/zdfpy5wtmy
#   Yang, Meng (2026). "Dataset for a study on AI-assisted oral training,
#   appreciative education, and foreign language speaking anxiety."
#   Mendeley Data.
# Data: Foreign Language Speaking Anxiety Questionnaire (FLSAQ).sav
#       (1,044 rows x 20 columns) and Appreciative Education (AE)
#       Questionnaire Data.sav (209 rows x 34 columns). Chinese EFL learners.
# License: CC BY 4.0 (Mendeley public API, data_licence.short_name).
#
# Item text: SHIPPED for the FLSAQ, and this deposit is the cheap case the
#   gate is written for. Both label levels were checked. Each variable label
#   carries the English stem AND the administered Chinese in one cell, each
#   self-numbered 1-18 matching Q1-Q18 -- so the code-to-text tie is the
#   source's own numbering, not positional. The English is the AUTHORS',
#   not IRW-generated, so no translation_source and no issues-page callout
#   are owed. Value labels exist for all 18 items but are literally
#   {1:'1', ..., 5:'5'} -- unlabeled anchors, so option_text stays blank at
#   every point rather than being padded with the number (audit_batch.R
#   warns on padding, and the deposit's codebook gives no anchors either).
#   Two source typos are transcribed as they stand, not silently corrected:
#   Q7 "I feel n1ervous", Q9 "I don't feel conffdent".
#
#   RIGHTS NOTE: irw-validate warns that Q14's item_text_translated matches
#   the register's Perceived Stress Scale row. That is a FALSE POSITIVE on
#   the substring "nervous and": FLSAQ Q14 is "I get nervous and confused
#   when I am speaking in English classes", the PSS-10 item is "In the last
#   month, how often have you felt nervous and stressed?". Different
#   instrument, different referent, different timeframe. Read, not inferred.
#   The register's own rule 1 is that a hit is a lead, never a verdict.
#
#   NOT shipped for the AE questionnaire: its item codes are Chinese column
#   names and no author English exists for the items (the deposit codebook
#   glosses only the demographics), so the English would be IRW-generated
#   and would owe a translation_source plus a public callout per table. That
#   belongs in the deferred translation round in TODO, not here.
#
# Tables:
#   yang_2026_flsaq   Q1-Q18, 1-5. The Foreign Language Speaking Anxiety
#       Questionnaire, 18 items, administered in Chinese. (The FLSAQ is the
#       study's own speaking-anxiety instrument built on Horwitz et al.'s
#       FLCAS; the deposit prints all 18 stems itself.)
#   yang_2026_appreciative_education  19 AE items, 1-5, codes are the
#       source's own Chinese column names.
#
# Dropped, with reasons printed:
#   FLSAQ: index (row number, replaced by it as id -- it is 1..1044 unique);
#     totalseconds -> cov_completion_time_s. It is a WHOLE-SURVEY duration,
#     not a per-item latency, so it is a named covariate and never `rt`.
#   AE: five subscale means (情感基础, 课堂运用, 学生反馈, 外部环境) and
#     'A4您对赏识教育很了解', which holds fractional values (1.25, 1.5, ...)
#     and is a mean, not an item; 'AE的态度' is entirely empty;
#     '你认为哪些原因可能会造成赏识教育在所有学科' is a pick-a-reason
#     nominal question (1-4, unordered) and fails resp's ordinal requirement.
#   The deposit's third file, pre/post IELTS speaking and anxiety scores,
#     has n=13 -- below the N>=100 floor, and is scores not items.
# id: FLSAQ the source `index`; AE the source `序号`.
# Covariates: FLSAQ cov_completion_time_s. AE cov_gender, cov_education,
#   cov_years_teaching, cov_school_runs_ae.

import io
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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/zdfpy5wtmy"
F_FLSAQ = "Foreign Language Speaking Anxiety Questionnaire (FLSAQ).sav"
F_AE = "Appreciative Education (AE) Questionnaire Data.sav"

QS = [f"Q{i}" for i in range(1, 19)]
ALLOWED = {1, 2, 3, 4, 5}

AE_ITEMS = [
    "赏识教育鼓励下，你的学习成绩进步了", "您对赏识教育了解程度",
    "A1您认为赏识教育运用到该课堂教育中重要吗", "A3教师在课堂中运用赏识教育的频率多吗",
    "A2你时常和同事一起讨论赏识教育",
    "B3你认为学校的老师对学生十分的关爱", "B1你认为老师能够平等看待所有的学生",
    "B4你本身就对这门课非常的热爱", "B5你与多数师生的关系都十分和谐",
    "B2你非常喜欢这个专业",
    "C3频繁使用正向语言来赞扬", "C2鼓励积极参与活动", "C4学困生更需要",
    "C1私下表扬更好",
    "D4意识到教师在使用赏识教育的方法", "D3因被肯定而喜欢这门学科",
    "D1对于个人成绩积极影响", "D2涉及学科考试成绩会有明显的进步",
    "E4您所在学校非常提倡赏识教育", "E3学校经常举办与赏识教育相关的讲座或培训",
    "E1学校有在通过政策或手段来促进应用", "E2学校是否鼓励学生积极参与学习社团活动",
]
AE_COVS = {"性别": "cov_gender", "学历": "cov_education",
           "学龄": "cov_years_teaching",
           "你们学校经常开展有关赏识教育的教学设计": "cov_school_runs_ae"}
AE_DROP = {"序号", "情感基础", "课堂运用", "学生反馈", "外部环境", "AE的态度",
           "A4您对赏识教育很了解",
           "你认为哪些原因可能会造成赏识教育在所有学科"}

# The first CJK character starts the administered Chinese; everything before
# it, minus the leading "<n>." the source writes, is the authors' English.
CJK = re.compile(r"[一-鿿]")


def split_label(lab):
    m = CJK.search(lab)
    assert m, lab
    eng = lab[:m.start()].strip()
    zho = lab[m.start():].strip()
    eng = re.sub(r"^\d+\s*\.?\s*", "", eng).strip()
    assert eng and zho, (eng, zho)
    return eng, zho


def fetch(name):
    meta = requests.get(API, headers=UA, timeout=60).json()
    lic = (meta.get("data_licence") or {}).get("short_name")
    assert lic == "CC BY 4.0", lic
    url = next(f["content_details"]["download_url"] for f in meta["files"]
               if f["filename"] == name)
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    p = OUT_DIR.parent / "runs" / f"_yang_{abs(hash(name))}.sav"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(r.content)
    df, m = pyreadstat.read_sav(str(p), apply_value_formats=False)
    p.unlink()
    return df, m


def ship(table, long, allowed, cov_cols):
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() > 1
    pv = {i: allowed for i in long["item"].unique()}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
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
    return long


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    names = []

    # ---- FLSAQ -----------------------------------------------------------
    d, m = fetch(F_FLSAQ)
    assert d.shape == (1044, 20), d.shape
    known = set(QS) | {"index", "totalseconds"}
    assert set(d.columns) == known, set(d.columns) ^ known
    print("dropped 0 column(s); index -> id, totalseconds -> "
          "cov_completion_time_s (whole-survey duration, never rt)")
    assert d["index"].is_unique
    d = d.rename(columns={"index": "id",
                          "totalseconds": "cov_completion_time_s"})
    long = d.melt(id_vars=["id", "cov_completion_time_s"], value_vars=QS,
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    bad = set(long["resp"]) - ALLOWED
    assert not bad, bad
    ship("yang_2026_flsaq", long, ALLOWED, ["cov_completion_time_s"])
    names.append("yang_2026_flsaq")

    # ---- FLSAQ item text -------------------------------------------------
    rows = []
    for q in QS:
        eng, zho = split_label(m.column_names_to_labels[q])
        for r in sorted(ALLOWED):
            rows.append({
                "table": "yang_2026_flsaq", "section_id": "yang_2026_flsaq_1",
                "item": q,
                "instrument": "Foreign Language Speaking Anxiety "
                              "Questionnaire (FLSAQ)",
                "language": "Chinese", "instructions": "",
                "section_prompt": "", "item_text": zho,
                "correct_response": "", "option_text": "", "resp": r,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": eng, "option_text_translated": "",
            })
    it = pd.DataFrame(rows)
    assert set(it["item"]) == set(QS)
    assert it.groupby("item").size().eq(len(ALLOWED)).all()
    tp = TEXT_DIR / "yang_2026_flsaq__items.csv"
    it.to_csv(tp, index=False)
    print(f"{tp.name}: {len(it)} rows, {it['item'].nunique()} items x "
          f"{len(ALLOWED)} options")

    # ---- Appreciative Education -----------------------------------------
    d2, m2 = fetch(F_AE)
    assert d2.shape == (209, 34), d2.shape
    known2 = set(AE_ITEMS) | set(AE_COVS) | AE_DROP
    assert set(d2.columns) == known2, set(d2.columns) ^ known2
    print(f"dropped {len(AE_DROP) - 1} AE column(s): 4 subscale means, "
          f"'A4...' (fractional -> a mean, not an item), 'AE的态度' (empty), "
          f"and the pick-a-reason nominal question")
    assert d2["序号"].is_unique
    d2 = d2.rename(columns={"序号": "id", **AE_COVS})
    cov2 = list(AE_COVS.values())
    long2 = d2.melt(id_vars=["id"] + cov2, value_vars=AE_ITEMS,
                    var_name="item", value_name="resp").dropna(subset=["resp"])
    long2["resp"] = long2["resp"].astype(int)
    bad = set(long2["resp"]) - ALLOWED
    assert not bad, bad
    ship("yang_2026_appreciative_education", long2, ALLOWED, cov2)
    names.append("yang_2026_appreciative_education")

    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
