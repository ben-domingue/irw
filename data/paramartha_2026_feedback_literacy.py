#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/32969165
# DOI: 10.6084/m9.figshare.32969165.v1
#   Paramartha, A. A. G. Y. (2026). Raw data feedback literacy SEM [Dataset].
#   figshare.
# Data: "Data PLS3.xlsx" -- 272 respondents, 72 items on a 1-5 agreement
#   scale. The deposit's description: "These data were used to analyze the
#   structural relationship among growth mindset, academic self-concept, and
#   metacognitive awareness."
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. The .xlsx header is bare codes and the deposit ships
#   no codebook or questionnaire; its second file is a SmartPLS report, which
#   carries the measurement MODEL but no stems. So nothing in the deposit
#   states what any item asked.
#
# THE FOUR BLOCKS ARE NOT GUESSED FROM THE PREFIXES. The deposit's SmartPLS
#   report ("1. FL3 CB SEM Algorithm.xlsx", sheet "complete", outer loadings)
#   names the latent each retained indicator loads on, and that is what
#   separates them: FL takes SF/MS/UF/PF/MA items, MA takes the R*/K* items,
#   GM takes ASB/L2B items and ASC takes SC/SE items. The tables below extend
#   each latent to the whole prefix family it draws from, since the report
#   only lists the indicators that survived the author's model.
#   Note the collision: the latent named MA (metacognitive awareness) is NOT
#   the item prefix MA, which loads on feedback literacy.
#   The R*/K* block is a 19-item subset of a longer inventory numbered to 51
#   with regulation (R) and knowledge (K) items -- the shape of Schraw &
#   Dennison's (1994) 52-item Metacognitive Awareness Inventory -- but with no
#   stems in the deposit that is a description, not an identification.
#
# FOUR tables, 272 respondents, all 1-5:
#   paramartha_2026_feedback_literacy         24 items (SF, MS, UF, PF, MA)
#   paramartha_2026_metacognitive_awareness   19 items (R*, K*)
#   paramartha_2026_academic_self_concept     20 items (SC1-10, SE1-10)
#   paramartha_2026_language_mindsets          9 items (GLB, L2B, ASB)
#   Item numbering is gapped (SF1, SF3, SF4, SF5, SF7) because the deposit
#   ships the items retained after validation; the source's own codes are kept
#   rather than renumbered, so a gap is visible instead of hidden.
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the deposit ships no demographics.
# Dropped: one unnamed trailing column, which is the sum of all 72 items for
#   271 of 272 rows.
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
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "32969165" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 32969165, "Data PLS3.xlsx"
SCALE = set(range(1, 6))

FL = ["SF1", "SF3", "SF4", "SF5", "SF7", "MS1", "MS2", "MS4", "MS5",
      "UF2", "UF3", "UF4", "UF5", "UF6", "PF3", "PF4", "PF5", "PF6", "PF7",
      "MA1", "MA2", "MA3", "MA4", "MA5"]
MAI = ["R6", "R8", "K10", "K16", "K20", "K21", "R24", "K26", "K27", "K32",
       "K33", "K35", "R39", "R40", "R41", "R43", "R44", "R50", "R51"]
ASC = [f"SC{i}" for i in range(1, 11)] + [f"SE{i}" for i in range(1, 11)]
GM = ["GLB1", "GLB2", "GLB3", "L2B1", "L2B2", "L2B3", "ASB1", "ASB2", "ASB3"]
TOTAL_COL = "Unnamed: 72"

TABLES = {
    "paramartha_2026_feedback_literacy": FL,
    "paramartha_2026_metacognitive_awareness": MAI,
    "paramartha_2026_academic_self_concept": ASC,
    "paramartha_2026_language_mindsets": GM,
}


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
    items = [c for cols in TABLES.values() for c in cols]
    assert len(items) == len(set(items)) == 72, len(items)
    for c in items + [TOTAL_COL]:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in set(items + [TOTAL_COL])]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    share = float((df[items].sum(axis=1) == df[TOTAL_COL]).mean())
    assert share > 0.99, share
    print(f"dropped: {TOTAL_COL!r}, the sum of all 72 items for "
          f"{share:.1%} of rows")

    df.insert(0, "id", range(len(df)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in TABLES.items():
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
