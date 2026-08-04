#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256283
# DOI: 10.1371/journal.pone.0256283
# Supporting Information: journal.pone.0256283_S2_File.xlsx
#   ("Data survey PIED" -- the raw response spreadsheet; S1_File is the
#   survey instrument PDF, S1_Fig a diagram, all fetched via the article's
#   .s001-.s004 supplementary-file URLs to identify the right one)
#
# Teachers (public schools, Extremadura, Spain, N=251) rating ICT
# integration on three instruments, all administered together in one
# response sheet with the same underlying 6-point response format. Per
# datastandard.md's "one scale per file" rule, split into three tables:
#
#   sqd            -- SQD-Scale, 24 items, 6-pt "Strongly disagree(1) ...
#                      Fully agree(6)" -- support for ICT integration.
#   tictip         -- Scale for teachers' ICT integration proficiency, 6-pt
#                      "Never(1) ... Always(6)". Paper text reports 27 items
#                      across 6 subscales (2+5+2+10+3+5=27), but the raw
#                      sheet has 28 TICTIP0x columns (all in-range 1-6, no
#                      structural anomaly, no duplicate column) -- shipping
#                      all 28 as administered rather than guessing which one
#                      the paper's factor analysis dropped.
#   learning_design -- 22 "Learning Design Support" items, same 6-pt Never..
#                      Always scale, in three dimensions: SPA (spaces used
#                      for teaching-learning with ICT, 8 items), RES
#                      (learning outcomes expected from ICT use, 8 items),
#                      PRA (type of teaching practice performed with ICT, 6
#                      items). Not reported with separate per-dimension
#                      reliabilities in the paper (unlike SQD's six named
#                      subscales), so kept as one file with an item_family
#                      column marking SPA/RES/PRA membership.
#
# No covariate columns (age/gender/etc.) are present in the raw sheet
# despite being described in the Methods -- only item responses and ID.
# No imputation/missing-data language found in the article text.

import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0256283.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def _write(long, out_name):
    out_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def _melt(df, item_cols, out_name, extra_cols=None):
    id_vars = ["id"] + (extra_cols or [])
    long = df.melt(id_vars=id_vars, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)].reset_index(drop=True)
    out_cols = ["id", "item", "resp"] + (extra_cols or [])
    long = long[out_cols]
    _write(long, out_name)


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Data")
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df), "id not unique"

    sqd_cols = [c for c in df.columns if c.startswith("SQD")]
    tictip_cols = [c for c in df.columns if c.startswith("TICTIP")]
    spa_cols = [c for c in df.columns if c.startswith("SPA")]
    res_cols = [c for c in df.columns if c.startswith("RES")]
    pra_cols = [c for c in df.columns if c.startswith("PRA")]

    assert len(sqd_cols) == 24, len(sqd_cols)
    assert len(tictip_cols) == 28, len(tictip_cols)
    assert len(spa_cols) == 8 and len(res_cols) == 8 and len(pra_cols) == 6

    _melt(df, sqd_cols, "valverdeberrocoso_2021_sqd")
    _melt(df, tictip_cols, "valverdeberrocoso_2021_tictip")

    ld_cols = spa_cols + res_cols + pra_cols
    fam_map = {c: "spa" for c in spa_cols}
    fam_map.update({c: "res" for c in res_cols})
    fam_map.update({c: "pra" for c in pra_cols})
    long = df.melt(id_vars=["id"], value_vars=ld_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)].reset_index(drop=True)
    long["item_family"] = long["item"].map(fam_map)
    long = long[["id", "item", "resp", "item_family"]]
    _write(long, "valverdeberrocoso_2021_learning_design")


if __name__ == "__main__":
    convert()
