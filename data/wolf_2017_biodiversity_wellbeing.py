#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0170225
# DOI: 10.1371/journal.pone.0170225
# Supporting Information: https://doi.org/10.1371/journal.pone.0170225.s001 (Study 1),
#                          https://doi.org/10.1371/journal.pone.0170225.s002 (Study 2)
#
# Study 1 (N=140): PANAS positive affect (12i), Subjective Vitality Scale
# (6i), state anxiety (10i), rated after viewing high/low-biodiversity
# park photos.
# Study 2 (N=264): same 3 scales rated pre/post viewing a nature video, plus
# a video-liking scale (like, 6i) and a nature-connectedness scale
# (connect, 6i) rated once post-video. Pre and post use different-length
# item sets with mostly non-overlapping wording (e.g. posaff_pre1="proud"
# vs posaff_post1="interested") -- confirmed via SPSS variable labels these
# are not the same items re-asked, so pre/post are kept as separate tables
# rather than forced into a shared wave/item structure.
#
# Every item in every scale uses a uniform 5-point response format
# exported as either a bare numeric string ("2","3","4") or an endpoint
# label with the code in parentheses ("NOT AT ALL (1)", "EXTREMELY (5)",
# "STRONGLY AGREE (5)"), confirmed by enumerating the full value set
# across all item columns before writing the parser -- a single regex
# (trailing "(\d)", else the bare digit) recovers the 1-5 code everywhere.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URLS = {
    "s1": ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0170225.s001"),
    "s2": ("https://journals.plos.org/plosone/article/file"
           "?type=supplementary&id=10.1371/journal.pone.0170225.s002"),
}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def parse_resp(v) -> float:
    if v is None:
        return float("nan")
    s = str(v).strip()
    m = re.search(r"\((\d)\)\s*$", s)
    if m:
        return float(m.group(1))
    if s.isdigit():
        return float(s)
    return float("nan")


def fetch(key: str) -> pd.DataFrame:
    r = requests.get(SI_URLS[key], headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(parse_resp)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df1 = fetch("s1").rename(columns={"Study_ID": "id", "gender": "cov_sex",
                                       "age": "cov_age", "Biodiversity": "cov_biodiversity"})
    assert df1["id"].nunique() == len(df1)
    cov1 = ["cov_sex", "cov_age", "cov_biodiversity"]
    melt_scale(df1, cov1, [f"posaff{i}" for i in range(1, 13)], "wolf_2017_study1_posaff")
    melt_scale(df1, cov1, [f"vital{i}" for i in range(1, 7)], "wolf_2017_study1_vitality")
    melt_scale(df1, cov1, [f"anx{i}" for i in range(1, 11)], "wolf_2017_study1_anxiety")

    df2 = fetch("s2").rename(columns={"Study_ID": "id", "gender": "cov_sex", "age": "cov_age",
                                       "environment": "cov_environment", "information": "cov_information"})
    assert df2["id"].nunique() == len(df2)
    cov2 = ["cov_sex", "cov_age", "cov_environment", "cov_information"]
    melt_scale(df2, cov2, [f"posaff_pre{i}" for i in range(1, 9)], "wolf_2017_study2_posaff_pre")
    melt_scale(df2, cov2, [f"vital_pre{i}" for i in range(1, 4)], "wolf_2017_study2_vitality_pre")
    melt_scale(df2, cov2, [f"anx_pre{i}" for i in range(1, 7)], "wolf_2017_study2_anxiety_pre")
    melt_scale(df2, cov2, [f"posaff_post{i}" for i in range(1, 13)], "wolf_2017_study2_posaff_post")
    melt_scale(df2, cov2, [f"vital_post{i}" for i in range(1, 7)], "wolf_2017_study2_vitality_post")
    melt_scale(df2, cov2, [f"anx_post{i}" for i in range(1, 11)], "wolf_2017_study2_anxiety_post")
    melt_scale(df2, cov2, [f"like{i}" for i in range(1, 7)], "wolf_2017_study2_video_liking")
    melt_scale(df2, cov2, [f"connect{i}" for i in range(1, 7)], "wolf_2017_study2_nature_connect")


if __name__ == "__main__":
    convert()
