"""Covariance family (irw_cov, source = "cov"): Liang (2026) digital innovation and event participants' intentions MASEM.

Source: Mendeley Data kphvbbfcxg v1 (https://doi.org/10.17632/kphvbbfcxg.1),
"How Does Digital Innovation Affect Event Participants' Behavioural Intentions?
A Meta-Analysis of the Mediating Role of Emotional Attachment - Data collection"
(creator 梁锦涛 / Liang Jintao, 2026). Licence: CC BY 4.0 (Mendeley public API
data_licence "CC BY 4.0"; DataCite rightsList cc-by-4.0; checked 2026-11-18).

Data collection.xlsx is read with openpyxl (values only; nothing in it is run):
- sheet "中介" (mediation): one row per study and construct pair (序号 row number,
  作者+出版年 author-year, 变量关系 pair, 相关系数 r, 样本量 N, then one column per
  construct PEOU, PU, PE, EA, BI holding that study's reliabilities on its first
  row). The author-year cell is filled only on a study's first row; following rows
  with a blank author-year belong to the same study. The three summary rows at the
  bottom (信度 etc.: mean reliabilities) have no pair and are skipped. This is the
  only source of correlations.
- the moderator sheets "国家文化调节" (country, 国家, and its 个人主义 individualism
  score), "节事类型调节" (event type, 节事类型), "参与模式调节" (participation mode,
  参与类型) and "数字创新类型调节" (digital innovation, 数字创新类型): one EA-BI row per
  sample with author-year and N. Used only for the record fields, matched to a
  sample by author-year (ignoring a digit the deposit appends to tell samples of one
  article apart, e.g. "Timothy Hyungsoo Jung1-2017") and N; a field is filled only
  when the match is unique.
The sheet "中介相关系数矩阵" is the pooled matrix (model output) and is not used; the
per-pair sheets (EA-BI etc.) are not used either (their values for some studies
differ from "中介"; see notes).

Constructs: PEOU, PU, PE, EA, BI. The deposit never defines the abbreviations; the
dataset title names emotional attachment (EA) and behavioural intentions (BI). PE is
kept as deposited, undefined.

Samples: a study's rows normally share one N. Two articles ("Timothy Hyungsoo
Jung-2017", N 145 and 119; "Tussyadiah, Iis-2017", N 724 and 202) put two samples
under one label: each pair appears once per N, and the moderator sheets list the two
samples separately ("...Jung1-2017" N 119, "Tussyadiah, Iis1-2017" N 202). Such a
study is split by N, and each sample takes the deposit's own label from the
moderator sheets. A label used for two separate studies ("Ayman Harb-2025", rows 21
and 70) is told apart the same way ("Ayman Harb1-2025", N 293). A study with more
than one N but no repeated pair, or a label that cannot be resolved, is held.

A construct with no correlation in a sample was not measured there and is dropped.
A pair between two measured constructs that "中介" does not give is written as a row
with an empty value (blank cells allowed, Ben, 2026-11-18). A sample with |r| >= 1 or
fewer than two constructs is held. Reliabilities on a sample's first row become
`rel` rows for the constructs in its matrix (type not stated in the deposit); for
"Timothy Hyungsoo Jung-2017" they sit on the N 145 row and are given to that sample
only. Values are written in shortest round-trip form, i.e. as stored.

Modification (2026-11-17, revised 2026-11-18): pivoted from pairwise rows to the long
lower-triangle layout in data/covariance/README.md, one group per sample. Values
unchanged.

Usage: python3 data/covariance/mendeley_liang2026_eventdigital.py <out dir>
(IRW_LIANG_XLSX=<saved Data collection.xlsx> reads a saved copy instead of Mendeley)
"""
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import openpyxl

URL = ("https://data.mendeley.com/public-files/datasets/kphvbbfcxg/files/"
       "57212af7-c5a2-416b-9c46-921ee5f6b280/file_downloaded")
SHA256 = "334324015d9563b88964f69d64024a62126408bd200c32dfa79c22f1ff73f3ce"   # Data collection.xlsx, v1
TABLE = "liang_2026_eventdigital5"
ORDER = ["PEOU", "PU", "PE", "EA", "BI"]
COUNTRY = {"中国": "CN", "美国": "US", "韩国": "KR", "英国": "GB", "中国台湾": "TW",
           "西班牙": "ES", "马来西亚": "MY", "马拉西亚": "MY", "泰国": "TH", "加拿大": "CA",
           "意大利": "IT", "爱尔兰": "IE", "挪威": "NO", "德国": "DE", "斯洛伐克": "SK",
           "印度": "IN", "卡塔尔": "QA", "约旦": "JO", "土耳其": "TR", "葡萄牙": "PT",
           "西班牙、葡萄牙": "ES;PT", "中国香港": "HK", "尼日利亚": "NG"}
EVENT = {"文化节庆": "cultural festival", "体育赛事": "sports event"}
MODE = {"线下": "offline", "线上": "online"}
DIGITAL = {"体验类数字创新": "experience-oriented", "传播类数字创新": "dissemination-oriented"}
# sheet -> (column -> moderator name, translation or None)
MODSHEETS = {"国家文化调节": {4: ("country", COUNTRY), 5: ("individualism", None)},
             "节事类型调节": {5: ("event_type", EVENT)},
             "参与模式调节": {4: ("participation_mode", MODE)},
             "数字创新类型调节": {4: ("digital_innovation", {"社交媒体": "SM"}), 5: ("digital_innovation_type", DIGITAL)}}


def get(url):
    """The workbook (IRW_LIANG_XLSX=<path> reads a saved copy instead; Mendeley
    sometimes answers with a JSON error page, which is retried)."""
    if os.environ.get("IRW_LIANG_XLSX"):
        return Path(os.environ["IRW_LIANG_XLSX"]).read_bytes()
    for _ in range(5):
        req = urllib.request.Request(url, headers={"User-Agent": "irw-cov-build"})
        with urllib.request.urlopen(req, timeout=300) as r:
            b = r.read()
        if b[:2] == b"PK":
            return b
        time.sleep(10)
    raise SystemExit("Mendeley did not return the workbook")


def base(label):
    """Author-year without a sample digit before the year: 'X Jung1-2017' -> 'X Jung-2017'."""
    return re.sub(r"\d+-(\d{4})$", r"-\1", label.strip())


def mod_rows(wb):
    """[(label, N, {moderator: value})] from the moderator sheets."""
    out = []
    for sheet, cols in MODSHEETS.items():
        for r in list(wb[sheet].iter_rows(values_only=True))[1:]:
            if not r[0]:
                continue
            d = {}
            for c, (name, tr) in cols.items():
                v = r[c]
                if v is None or str(v).strip() == "":
                    continue
                v = str(v).strip()
                d[name] = tr.get(v, v) if tr else v
                if tr is COUNTRY and v not in COUNTRY:
                    raise SystemExit(f"unknown country {v}")
            out.append((str(r[0]).strip(), int(r[3]), d))
    return out


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    raw = get(URL)
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise SystemExit("Data collection.xlsx differs from the copy this script was checked against")
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    rows = list(wb["中介"].iter_rows(values_only=True))
    if rows[0] != ("序号", "作者+出版年", "变量关系", "相关系数", "样本量", *ORDER):
        raise SystemExit(f"unexpected header {rows[0]}")
    mrows = mod_rows(wb)
    blocks, cur = [], None
    for r in rows[1:]:
        if r[2] is None:
            continue
        if r[1]:
            cur = {"label": str(r[1]).strip(), "row": r[0], "rows": []}
            blocks.append(cur)
        cur["rows"].append(r)
    count = {}
    for b in blocks:
        count[b["label"]] = count.get(b["label"], 0) + 1

    def own_label(label, n):
        hits = sorted({m[0] for m in mrows if base(m[0]) == base(label) and m[1] == n})
        return hits[0] if len(hits) == 1 else None

    samples, held = [], []
    for b in blocks:
        ns = sorted({int(r[4]) for r in b["rows"]}, key=[int(r[4]) for r in b["rows"]].index)
        keys = [frozenset(str(r[2]).strip().split("-")) for r in b["rows"]]
        repeated = len(set(keys)) < len(keys)
        if len(ns) > 1 and not repeated:
            held.append({"group": b["label"], "n": ns, "why": "several N in one study, no repeated pair"})
            continue
        for n in ns:
            rs = [r for r in b["rows"] if int(r[4]) == n]
            if len(ns) > 1 or count[b["label"]] > 1:
                lab = own_label(b["label"], n)
                if lab is None or lab in [s["group"] for s in samples]:
                    lab = f"{b['label']} (row {rs[0][0]})" if len(ns) == 1 else None
                if lab is None:
                    held.append({"group": b["label"], "n": n, "why": "two samples under one label, no label for this N"})
                    continue
            else:
                lab = b["label"]
            samples.append({"group": lab, "deposit_label": b["label"], "n": n, "rows": rs,
                            "first_row": rs[0][0], "rel_row": rs[0]})

    long, records = [], []
    for s in samples:
        r_of = {}
        for r in s["rows"]:
            a, c = str(r[2]).strip().split("-")
            if a == c or a not in ORDER or c not in ORDER or frozenset((a, c)) in r_of:
                raise SystemExit(f"{s['group']}: bad or repeated pair {a}-{c}")
            if not isinstance(r[3], (int, float)) or isinstance(r[3], bool):
                raise SystemExit(f"{s['group']}: r {r[3]!r}")
            r_of[frozenset((a, c))] = r[3]
        v = [x for x in ORDER if any(x in p for p in r_of)]
        if len(v) < 2 or any(abs(x) >= 1 for x in r_of.values()):
            held.append({"group": s["group"], "n": s["n"], "why": "|r| >= 1 or fewer than two constructs"})
            continue
        if s["group"] in [rec["group"] for rec in records]:
            raise SystemExit(f"duplicate group {s['group']}")
        blank = []
        for a, i in enumerate(v):
            for j in v[:a + 1]:
                if i == j:
                    val = "1"
                elif frozenset((i, j)) in r_of:
                    val = repr(float(r_of[frozenset((i, j))]))
                else:
                    val = ""
                    blank.append(f"{j}-{i}")
                long.append({"stat": "cor", "var1": i, "var2": j, "value": val, "n": s["n"], "group": s["group"]})
        rel, rel_dropped = {}, []
        rr = s["rel_row"]
        if rr is not None:
            for k, x in zip(ORDER, rr[5:10]):
                if x is None:
                    continue
                if not isinstance(x, (int, float)) or not 0 < x <= 1:
                    raise SystemExit(f"{s['group']}: reliability {x!r}")
                if k in v:
                    rel[k] = repr(float(x))
                else:
                    rel_dropped.append(k)
        for k in v:
            if k in rel:
                long.append({"stat": "rel", "var1": k, "var2": "", "value": rel[k], "n": s["n"], "group": s["group"]})
        mods = {}
        for m in mrows:
            if base(m[0]) == base(s["group"].split(" (row")[0]) and m[1] == s["n"]:
                for k, x in m[2].items():
                    mods.setdefault(k, set()).add(x)
        y = re.search(r"-(\d{4})$", s["deposit_label"])
        records.append({"group": s["group"], "deposit_label": s["deposit_label"], "first_row": s["first_row"],
                        "n_obs": s["n"], "vars": v, "blank": blank, "rel": sorted(rel),
                        "rel_not_in_matrix": rel_dropped, "year": y.group(1) if y else "",
                        "mods": {k: next(iter(x)) for k, x in sorted(mods.items()) if len(x) == 1},
                        "mods_conflict": sorted(k for k, x in mods.items() if len(x) > 1)})
    with open(out / f"{TABLE}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["stat", "var1", "var2", "value", "n", "group"])
        w.writeheader()
        w.writerows(long)
    with open(out / f"{TABLE}_records.json", "w") as f:
        json.dump({"table": TABLE, "records": records, "held": held}, f, indent=1, ensure_ascii=False)
    print(f"wrote {TABLE}.csv: {len(records)} samples built, {len(held)} held")
    for h in held:
        print("held:", h)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 mendeley_liang2026_eventdigital.py <out dir>")
    main(sys.argv[1])
