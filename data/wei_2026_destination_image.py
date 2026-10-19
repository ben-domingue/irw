#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T53TAK
# DOI: 10.7910/DVN/T53TAK
#   Wei, W. (2026). Mapping the Cognitive-Affective-Spatial Dynamics of
#   Destination Image [Dataset]. Harvard Dataverse.
# Data: "data.xls" -- 500 self-drive tourists in Shandong, China, answering a
#   Chinese-language questionnaire whose COLUMN HEADERS ARE THE ITEM STEMS.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped here, but it needs no further work: every stem is the
#   column header, in the administered Chinese, and the anchors are printed
#   inside the first one (1=非常不同意 ... 5=非常同意). The items are the
#   study's own, so there is no rights question either. The mapping is below,
#   so the item codes this script assigns stay addressable.
#
# The two files are the same data: `data.xls` and `问卷数据.xls` have equal
#   values and equal columns (different MD5s only because they were saved
#   twice). `data.xls` is read; nothing is shipped twice.
#
# ONE table: the 16-item agreement block, 1-5, complete for all 500
#   respondents. Items are numbered by questionnaire order:
#   item01  山东省高速公路网络覆盖完善，方便跨区域游览
#   item02  国/省道景观优美，驾驶体验愉悦
#   item03  景区停车场充足且标识清晰
#   item04  交通拥堵问题影响行程体验
#   item05  沿海公路（如青岛滨海大道）景观层次丰富，风景优美
#   item06  内陆文化景观（如泰山、三孔）与自然环境融合度高
#   item07  沿途村镇风貌具有地域特色
#   item08  夜间行车景观照明效果良好
#   item09  加油站/充电站布局合理，满足需求
#   item10  住宿条件（如酒店、民宿）非常舒适。
#   item11  旅游咨询服务点（如驿站）信息实用
#   item12  应急救援服务响应及时
#   item13  自驾过程让我感受到探索未知的兴奋
#   item14  餐饮服务（如鲁菜、海鲜胶东海鲜、淄博烧烤）非常有特色带来惊喜
#   item15  与当地居民的互动增强文化认同感
#   item16  山东旅游让我感到非常放松
#   item04 is negatively worded ("congestion spoiled the trip") and ships as
#   administered; nothing in this pipeline reverse-keys an item.
#   item11 and item12 were answered 2-5 only -- no respondent chose 1. That is
#   the observed range, not a different scale: the block's anchors are stated
#   once, in item01's header, for all sixteen.
#
# NOT SHIPPED, and why:
#   The four multiple-response blocks -- trip motivations (6 boxes), information
#   sources used (5), regions visited (5) and which service to improve first
#   (6). Each is a select-all-that-apply question stored as 0/1 boxes, so the
#   "items" of one block are the options of one question, not a scale.
#   The free-text keyword question (请用关键词描述...), which is empty for all
#   500 rows.
#
# id: the row index. The file carries no respondent id column.
# Covariates: cov_gender, cov_age_band, cov_origin, cov_occupation,
#   cov_main_vehicle, cov_daily_driving_hours, cov_image_information_channel,
#   cov_overall_impression, cov_would_recommend -- the single-choice questions,
#   as the deposit's own codes, which it does not label. The last two are
#   single global ratings (1-5 impression, 1/2 recommend) and belong on the
#   person, not in the 16-item table.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "t53tak" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 14135954, "data.xls"
ITEM_SLICE = slice(18, 34)          # the agreement block, in file order
COV_POS = {42: "cov_gender", 43: "cov_age_band", 44: "cov_origin",
           45: "cov_occupation", 0: "cov_main_vehicle",
           17: "cov_daily_driving_hours",
           34: "cov_image_information_channel", 35: "cov_overall_impression",
           46: "cov_would_recommend"}
SCALE = set(range(1, 6))
ANCHORS = "1=非常不同意"             # printed in the first item's header
TABLE = "wei_2026_destination_image"


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
    df = pd.read_excel(fetch())
    assert df.shape == (500, 48), df.shape
    headers = list(df.columns)
    item_cols = headers[ITEM_SLICE]
    assert len(item_cols) == 16, len(item_cols)
    # The block is identified by its printed anchors, not by position alone.
    assert ANCHORS in item_cols[0], item_cols[0]
    for c in item_cols:
        vals = set(df[c].dropna().unique())
        assert vals <= SCALE and len(vals) >= 4, (c, sorted(vals))
        assert df[c].notna().all(), c

    renames = {c: f"item{i:02d}" for i, c in enumerate(item_cols, 1)}
    covs = {headers[i]: name for i, name in COV_POS.items()}
    # Every column is accounted for: items, covariates, the four 0/1 blocks
    # and the empty free-text question.
    boxes = [c for i, c in enumerate(headers)
             if i not in COV_POS and c not in item_cols
             and set(df[c].dropna().unique()) <= {0, 1}
             and df[c].notna().all()]
    empty = [c for c in headers if df[c].notna().sum() == 0]
    assert len(boxes) == 22 and len(empty) == 1, (len(boxes), len(empty))
    assert set(headers) == set(item_cols) | set(covs) | set(boxes) | set(empty)
    print(f"not shipped: {len(boxes)} multiple-response boxes across four "
          f"select-all questions, and 1 empty free-text column")

    df = df.rename(columns={**renames, **covs})
    df["id"] = range(1, len(df) + 1)
    items = list(renames.values())
    cov_cols = list(covs.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    t = (df[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    assert set(t["resp"]) <= SCALE
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 500 and t["item"].nunique() == 16
    assert len(t) == 500 * 16

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
