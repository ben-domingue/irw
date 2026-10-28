#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MP3HQU
# DOI: 10.7910/DVN/MP3HQU
# Paper: Costa, M. (2020). How partisanship and sexism influence voters'
#        reactions to #MeToo scandals. Research & Politics, 7(3).
# Data: metoo_data.csv, downloaded with format=original (the .tab conversion
#       is lossy; see automated_finding/.claude/skills SKILL.md)
# License: CC0 1.0 (stated on the Harvard Dataverse deposit page)
# Item text: shipped for the punishment battery only (readme.pdf in the deposit
#   gives every stem verbatim and the 1-5 anchors). The four sexism items are
#   the HOSTILE SEXISM subscale of the Ambivalent Sexism Inventory
#   (Glick & Fiske, 1996) -- stems searched verbatim -- and no public rights
#   grant was found for it, so that table's item text is HELD, not shipped.
#   The wording is in readme.pdf of this deposit if a grant is ever recorded.
#
# Two output tables:
#   costa_2020_sexism     -- ASI hostile sexism, 4 items, pre/post (wave 1/2)
#   costa_2020_punishment -- 5 study-authored punishment items, post only,
#                            asked of the two scandal arms (N=1870)
#
# Design columns: treat = 1 for the two scandal arms (jokes, assault), 0 for
# the control arm; cov_story_type keeps which of the two scandal stories was
# shown. cov_senator_party is the randomised party of the senator in the
# vignette -- a second manipulated factor, carried as a covariate because
# `treat` can only hold one.
#
# Not shipped: pre_/post_favorability and pre_/post_vote (0-10 single-item
# senator evaluations). Two items that are not a scale, so they are left out
# rather than shipped as a degenerate two-item table.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("COSTA_RAW", "metoo_data.csv")

# readme.pdf: "on 5 point scale (1=Disagree strongly; 5=Agree strongly)"
LIKERT = {
    "Disagree strongly": 1,
    "Disagree somewhat": 2,
    "Neither disagree nor agree": 3,
    "Agree somewhat": 4,
    "Agree strongly": 5,
}

COVS = {
    "senator_party": "cov_senator_party",
    "pid7": "cov_pid7",
    "gender": "cov_gender",
    "age": "cov_age",
    "newsinterest": "cov_newsinterest",
}

STORY = {1: "jokes", 2: "assault", 3: "control"}


def convert():
    df = pd.read_csv(RAW)
    assert df["id"].nunique() == len(df), "id is not unique"

    df = df.rename(columns=COVS)
    df["cov_story_type"] = df["condition"].map(STORY)
    assert df["cov_story_type"].notna().all(), "unmapped condition code"
    df["treat"] = (df["condition"] != 3).astype(int)

    cov_cols = sorted(COVS.values()) + ["cov_story_type"]
    keep = ["id", "treat"] + cov_cols

    # ---- sexism: same 4 ASI hostile items pre (wave 1) and post (wave 2)
    frames = []
    for wave, prefix in ((1, "pre_sexism_"), (2, "post_sexism_")):
        cols = [c for c in df.columns if c.startswith(prefix)]
        assert len(cols) == 4, cols
        part = df[keep + cols].melt(id_vars=keep, value_vars=cols,
                                    var_name="item", value_name="resp")
        part["item"] = part["item"].str.replace(prefix, "sexism_", regex=False)
        part["wave"] = wave
        frames.append(part)
    sexism = pd.concat(frames, ignore_index=True)

    # ---- punishment: 5 study-authored items, asked post-treatment only
    pcols = [c for c in df.columns if c.startswith("punishment_")]
    assert len(pcols) == 5, pcols
    punish = df[keep + pcols].melt(id_vars=keep, value_vars=pcols,
                                   var_name="item", value_name="resp")

    # every source column is either shipped, a design/cov column, or named here
    shipped = set(COVS) | {"id", "condition"}
    shipped |= {c for c in df.columns if "sexism_" in c or "punishment_" in c}
    left_out = [c for c in pd.read_csv(RAW, nrows=0).columns if c not in shipped]
    assert left_out == ["pre_favorability", "pre_vote",
                        "post_favorability", "post_vote"], left_out
    print("deliberately not shipped (two non-scale 0-10 outcomes):", left_out)

    os.makedirs(OUT_DIR, exist_ok=True)
    written = set()
    for name, long in (("costa_2020_sexism", sexism),
                       ("costa_2020_punishment", punish)):
        long["resp"] = long["resp"].map(LIKERT)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        order = ["id", "item", "resp"]
        if "wave" in long.columns:
            order.append("wave")
        order += ["treat"] + cov_cols
        long = long[order]
        assert name not in written, f"duplicate output name {name}"
        written.add(name)
        path = os.path.join(OUT_DIR, name + ".csv")
        long.to_csv(path, index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
