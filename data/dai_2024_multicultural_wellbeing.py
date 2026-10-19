#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/x8zvbjv6p2/1
# DOI: 10.17632/x8zvbjv6p2.1
#   Dai, X. (2024). Multicultural experience and subjective well-being among
#   young Chinese [Dataset]. Mendeley Data.
# Data: the deposit's single "data.sav" -- 1,387 young Chinese adults in five
#   provinces, complete on every item.
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped. The acculturation-index items carry their domain in
#   the SPSS label ("Acculturation index: Family values"), which names the
#   facet but is not the administered stem; the other three blocks have no
#   label at all. The wording is in the published scales.
#
# FOUR tables, 1,387 respondents, no missing cell anywhere:
#   dai_2024_acculturation_index  8 items, 0/1  (which culture the respondent
#                                 identifies with on each of eight domains:
#                                 political ideology, family values,
#                                 communication styles, spoken language,
#                                 worldview, concept of morality, personal
#                                 aspirations, sense of humour)
#   dai_2024_cultural_difference  3 items, 1-5
#   dai_2024_wellbeing            5 items, 1-5
#   dai_2024_self_esteem          5 items, 1-5
#
# THE ADMINISTERED COLUMNS ARE THE ONES WITH THE `R` SUFFIX, and that is the
#   opposite of what the name suggests. The deposit keeps both: `Differ3R` and
#   `SEsteem2R`/`SEsteem4R` sit inside their blocks, and plain `Differ3`,
#   `SEsteem2`, `SEsteem4` appear later in the file as the SCORED copies --
#   proved arithmetically here, each equals 6 minus its `R` twin for all 1,387
#   rows. The block members ship, in the administered direction; nothing is
#   reverse-keyed, per the data standard.
#
# NOT SHIPPED: the scored copies above, the block composites (`Differ`,
#   `SEsteem`, `AI`, `MExp`) and their z-scores (`ZDiffer`, `ZSEsteem`), and
#   `Residence`, which is free-text province-city in Chinese (its numeric
#   recode ships as cov_province). `AI` is the sum of the eight index items
#   for all 1,387 rows, which is this file's arithmetic check.
#
# id: the row index. The deposit carries no respondent id column.
# Covariates: cov_age, cov_gender, cov_education, cov_province,
#   cov_multicultural_experience -- the deposit's own codes. Two columns hold
#   the multicultural-experience count (`MultiCulturalEx` and `MExp`) and they
#   differ by one, so only `MExp`, the one the deposit's own analysis names,
#   ships; the discrepancy is recorded here rather than resolved.
import os
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
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "x8zvbjv6p2" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET, VERSION, FNAME = "x8zvbjv6p2", 1, "data.sav"
AI = [f"AI_{i}" for i in range(1, 9)]
DIFFER = ["Differ1", "Differ2", "Differ3R"]
SWB = [f"SWB{i}" for i in range(1, 6)]
ESTEEM = ["SEsteem1", "SEsteem2R", "SEsteem3", "SEsteem4R", "SEsteem5"]
SCORED_COPIES = {"Differ3": "Differ3R", "SEsteem2": "SEsteem2R",
                 "SEsteem4": "SEsteem4R"}
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Edu_L": "cov_education",
        "MExp": "cov_multicultural_experience"}
PROVINCE_COL = "Residence_coding北京1上海2廣東3陝西4四川5"
TABLES = {"dai_2024_acculturation_index": (AI, {0, 1}),
          "dai_2024_cultural_difference": (DIFFER, set(range(1, 6))),
          "dai_2024_wellbeing": (SWB, set(range(1, 6))),
          "dai_2024_self_esteem": (ESTEEM, set(range(1, 6)))}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get("https://data.mendeley.com/public-api/datasets/"
                         f"{DATASET}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"]
               if f["filename"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 1387, len(df)
    items = AI + DIFFER + SWB + ESTEEM
    assert not df[items].isna().any().any(), "unexpected missing in a block"
    for c in AI:                      # the label names the domain
        assert (labels.get(c) or "").startswith("Acculturation index:"), c

    # Which copy is administered: the scored one is 6 minus its R twin.
    for scored, administered in SCORED_COPIES.items():
        assert (df[scored] == 6 - df[administered]).all(), (scored, administered)
    print(f"scored copies not shipped (each = 6 - its R twin): "
          f"{sorted(SCORED_COPIES)}")
    assert (df[AI].sum(axis=1) == df["AI"]).all(), \
        "AI is not the sum of the eight index items"
    print("AI equals the sum of the 8 index items for all 1,387 respondents")
    assert not (df["MultiCulturalEx"] == df["MExp"]).all(), \
        "the two experience columns now agree; re-read the header note"

    df = df.rename(columns={**COVS, PROVINCE_COL: "cov_province"})
    df["id"] = range(1, len(df) + 1)
    cov_cols = [*COVS.values(), "cov_province"]
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols, scale) in TABLES.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 1387 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:140]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
