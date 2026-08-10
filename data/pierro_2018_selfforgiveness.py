#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0193357
# DOI: 10.1371/journal.pone.0193357
#
# Pierro, Pica, Giannini, Higgins, Kruglanski (2018). "Letting myself go
# forward past wrongs": How regulatory modes affect self-forgiveness.
# PLOS ONE.
#
# Four independently-recruited studies (S1-S4 File, SPSS .sav), each
# reporting several instruments. Per datastandard.md guidance for
# "same instrument in multiple studies", we ship one file per study rather
# than merging, since the paper does not explicitly confirm identical
# administration across all four samples (Study 2 in particular used a
# different experimental manipulation - "condition" - and only administered
# the self-forgiveness scale).
#
# Instruments confirmed present with raw item-level responses and
# consistent scale ranges across studies:
#   - Self-forgiveness (Sforgive/sforgive, 4 items, 1-4 scale) - Studies 1,2,3
#   - Locomotion Regulatory Mode Scale (loc, 12 items, 1-6 scale) - Studies 1,3,4
#   - Assessment Regulatory Mode Scale (ass, 12 items, 1-6 scale) - Studies 1,3,4
#   - Positive/Negative Affect (posaffect/negaffect, 10 items each, 1-5) - Study 3
#   - Temporal Focus (past/present/future, 4 items each, 1-7) - Study 4
#   - Heartland Forgiveness Scale (hfs, 6 items, 1-7) - Study 4
#
# Excluded: subscale total columns (locomotion, assessment, selfforgive,
# posaffect, negaffect, selfforgiveness, past, present, future - already
# computed aggregates); Study 3's "resp"/"serious"/"harmful" columns, whose
# out-of-Likert-range values (2-10) indicate they are already composite
# ratings rather than single raw items.

import io
import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

URLS = {
    1: "https://doi.org/10.1371/journal.pone.0193357.s001",
    2: "https://doi.org/10.1371/journal.pone.0193357.s002",
    3: "https://doi.org/10.1371/journal.pone.0193357.s003",
    4: "https://doi.org/10.1371/journal.pone.0193357.s004",
}


def fetch(study):
    r = requests.get(URLS[study], headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def make_cov(df, cols_map):
    out = pd.DataFrame({"id": df["subject"].astype(int)})
    for src, dst in cols_map.items():
        if src in df.columns:
            out[dst] = df[src]
    return out


def melt_scale(df, id_col, item_cols, cov_df, valid_min, valid_max):
    item_df = df[[id_col] + item_cols].copy()
    item_df = item_df.rename(columns={id_col: "id"})
    item_df["id"] = item_df["id"].astype(int)
    merged = item_df.merge(cov_df, on="id", how="left")
    cov_names = [c for c in cov_df.columns if c != "id"]
    long = merged.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                        var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]
    out_cols = ["id", "item", "resp"] + cov_names
    return long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long, fname):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    d1 = fetch(1)
    d2 = fetch(2)
    d3 = fetch(3)
    d4 = fetch(4)

    # ---- Study 1 ----
    cov1 = make_cov(d1, {"gender": "cov_gender", "age": "cov_age", "sample": "cov_sample"})
    sf1_items = ["sforgiveR1", "sforgive2", "sforgiveR3", "sforgive4"]
    loc1_items = [c for c in d1.columns if c.lower().startswith("loca")]
    ass1_items = [c for c in d1.columns if c.lower().startswith("ass") and c != "assessment"]
    write_scale(melt_scale(d1, "subject", sf1_items, cov1, 1, 4), "pierro_2018_selfforgive_s1.csv")
    write_scale(melt_scale(d1, "subject", loc1_items, cov1, 1, 6), "pierro_2018_locomotion_s1.csv")
    write_scale(melt_scale(d1, "subject", ass1_items, cov1, 1, 6), "pierro_2018_assessment_s1.csv")

    # ---- Study 2 ----
    cov2 = make_cov(d2, {"Gender": "cov_gender", "Age": "cov_age", "condition": "cov_condition"})
    sf2_items = ["SforgiveR1", "Sforgive2", "SforgiveR3", "Sforgive4"]
    write_scale(melt_scale(d2, "subject", sf2_items, cov2, 1, 4), "pierro_2018_selfforgive_s2.csv")

    # ---- Study 3 ----
    cov3 = make_cov(d3, {"gender": "cov_gender", "age": "cov_age"})
    sf3_items = ["sforgiver1", "sforgive2", "sforgiver3", "sforgive4"]
    loc3_items = [c for c in d3.columns if c.lower().startswith("loc") and not c.lower().startswith("locomotion")]
    ass3_items = [c for c in d3.columns if c.lower().startswith("ass") and c not in ("assessment",)]
    pos3_items = [c for c in d3.columns if c.lower().startswith("posaffect") and c != "posaffect"]
    neg3_items = [c for c in d3.columns if c.lower().startswith("negaffect") and c != "negaffect"]
    write_scale(melt_scale(d3, "subject", sf3_items, cov3, 1, 4), "pierro_2018_selfforgive_s3.csv")
    write_scale(melt_scale(d3, "subject", loc3_items, cov3, 1, 6), "pierro_2018_locomotion_s3.csv")
    write_scale(melt_scale(d3, "subject", ass3_items, cov3, 1, 6), "pierro_2018_assessment_s3.csv")
    write_scale(melt_scale(d3, "subject", pos3_items, cov3, 1, 5), "pierro_2018_posaffect_s3.csv")
    write_scale(melt_scale(d3, "subject", neg3_items, cov3, 1, 5), "pierro_2018_negaffect_s3.csv")

    # ---- Study 4 ----
    cov4 = make_cov(d4, {"gender": "cov_gender", "age": "cov_age"})
    loc4_items = [c for c in d4.columns if c.lower().startswith("loc") and not c.lower().startswith("locomotion")]
    ass4_items = [c for c in d4.columns if c.lower().startswith("ass") and c not in ("assessment",)]
    tf_past = [c for c in d4.columns if c.startswith("TFpast")]
    tf_present = [c for c in d4.columns if c.startswith("TFpresent")]
    tf_future = [c for c in d4.columns if c.startswith("TFfuture")]
    hfs_items = [c for c in d4.columns if c.lower().startswith("hfs")]
    write_scale(melt_scale(d4, "subject", loc4_items, cov4, 1, 6), "pierro_2018_locomotion_s4.csv")
    write_scale(melt_scale(d4, "subject", ass4_items, cov4, 1, 6), "pierro_2018_assessment_s4.csv")
    write_scale(melt_scale(d4, "subject", tf_past, cov4, 1, 7), "pierro_2018_tf_past_s4.csv")
    write_scale(melt_scale(d4, "subject", tf_present, cov4, 1, 7), "pierro_2018_tf_present_s4.csv")
    write_scale(melt_scale(d4, "subject", tf_future, cov4, 1, 7), "pierro_2018_tf_future_s4.csv")
    write_scale(melt_scale(d4, "subject", hfs_items, cov4, 1, 7), "pierro_2018_hfs_s4.csv")


if __name__ == "__main__":
    convert()
