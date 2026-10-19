#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/32994878
# DOI: 10.6084/m9.figshare.32994878.v1
#   Li, H. (2026). The Effects of AI Self-Efficacy and AI Anxiety on Writing
#   Self-Regulated Learning [Dataset]. figshare.
# Data: "The Effects of AI Self-Efficacy and AI Anxiety on Writing
#   Self-Regulated Learning.xlsx" -- 204 respondents, six item blocks on a
#   1-5 agreement scale, administered in Chinese.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. The only label level a .xlsx has is the header row,
#   and it carries bare codes for 48 of the 50 columns; the two exceptions are
#   the validity items described below, whose Chinese stems ARE in the header.
#   No codebook or questionnaire file is in the deposit, so the wording of
#   every shipped item is only in the author's paper.
#
# TWO VALIDITY COLUMNS ARE NOT ITEMS and are dropped with their reasons:
#   - MST5 is an instructed-response attention check -- its header reads
#     "to prove you are reading carefully, choose option 2 here", and 200 of
#     204 respondents chose 2.
#   - FH5 ("I never want to get a high score in writing tasks") is the only
#     other column whose header carries its own stem, is reverse-worded, and
#     was answered 1-3 only. It reads as a companion validity item rather than
#     an FH scale item, so it is excluded rather than shipped as one.
#   The deposit's 总分 column is the raw sum of all 50 columns, both checks
#   included, so it does not settle which columns are scale items and no
#   composite is shipped.
#
# CONSTRUCT NAMING. Only two blocks can be identified from the deposit: AIAX
#   is AI anxiety and AISE AI self-efficacy, which is the deposit's title. The
#   other four (MST, EC, PL, FH) are the deposit's own block codes for what
#   the title calls writing self-regulated learning; nothing in the deposit
#   says which subscale each is, and they are NOT guessed at here -- the four
#   tables carry the source's code. A later pass with the paper in hand can
#   rename them.
#
# SIX tables, 204 respondents, all 1-5:
#   li_2026_ai_anxiety        AIAX1-8  (8 items)
#   li_2026_ai_self_efficacy  AISE1-8  (8 items)
#   li_2026_mst               MST1-9 less MST5  (8 items)
#   li_2026_ec                EC1-8    (8 items)
#   li_2026_pl                PL1-8    (8 items)
#   li_2026_fh                FH1-9 less FH5    (8 items)
# id: the deposit's own 序号 serial (1-204), kept so the six tables link.
# Covariates: none -- the deposit ships no demographics.
import os
import re
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
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "32994878" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 32994878
FNAME = ("The Effects of AI Self-Efficacy and AI Anxiety on Writing "
         "Self-Regulated Learning.xlsx")
SCALE = set(range(1, 6))

BLOCKS = {
    "li_2026_ai_anxiety": ("AIAX", 8, ()),
    "li_2026_ai_self_efficacy": ("AISE", 8, ()),
    "li_2026_mst": ("MST", 9, (5,)),
    "li_2026_ec": ("EC", 8, ()),
    "li_2026_pl": ("PL", 8, ()),
    "li_2026_fh": ("FH", 9, (5,)),
}
EXCLUDED = ["MST5", "FH5"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch())
    # Headers carry stray question numbers ("7、AIAX1") and, on the two
    # validity columns, the whole stem. Reduce each to its own item code.
    codes = {}
    for c in df.columns:
        m = re.search(r"((?:AIAX|AISE|MST|EC|PL|FH)\d+)", str(c))
        if m:
            assert m.group(1) not in codes.values(), m.group(1)
            codes[c] = m.group(1)
    df = df.rename(columns=codes)

    blocks = {name: [f"{pre}{i}" for i in range(1, n + 1)
                     if i not in skip]
              for name, (pre, n, skip) in BLOCKS.items()}
    items = [c for cols in blocks.values() for c in cols]
    for c in items + EXCLUDED + ["序号", "总分"]:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns
                   if c not in set(items + EXCLUDED + ["序号", "总分"])]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"excluded, validity checks rather than items: {EXCLUDED}")
    print("dropped, the deposit's raw total over all 50 columns: 总分")

    df = df.rename(columns={"序号": "id"})
    df["id"] = pd.to_numeric(df["id"]).astype(int)
    assert df["id"].is_unique

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in blocks.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the documented 1-5 scale: {bad}"
        t = t[["id", "item", "resp"]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
