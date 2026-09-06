from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0205559
# DOI: 10.1371/journal.pone.0205559
# De Backer et al. (2018), "Do coaching style and game circumstances
# predict athletes' perceived justice of their coach? A longitudinal
# study in elite handball and volleyball teams". S2 File. CC BY 4.0.
# N=96 athletes, repeated across matches (wave = match_number, up to 11
# matches per athlete). Two tables: `decisionjustification` (4 items,
# 1-5) and `justice_appraisal` (12 items: distributive/procedural
# justice x group/personal referent, 3 items each, 1-5).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0205559.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DJ_ITEMS = [f"decisionjustification{i}" for i in range(1, 5)]
JA_ITEMS = ["distrgroup1", "procgroup1", "distrpers1", "procpers1", "distrpers2", "procgroup2",
            "distrgroup2", "procpers2", "distrpers3", "procpers3", "distrgroup3", "procgroup3"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", "match_number": "wave"})


# The response scale, from the paper: "Items were answered on a 5-point Likert
# scale ranging from 1 (strongly disagree) to 5 (strongly agree)." Both blocks
# are the same game-specific questionnaire, so both are 1-5.
#
# The deposit nonetheless carries 98 zeros -- 74 across the justice block, 24
# across decisionjustification -- and 0 is not a point on that scale (#1952).
# Three things about the .sav say they are re-encoded missing rather than a
# sixth category the paper failed to describe:
#
#   * all 16 item variables DECLARE 99 as their SPSS user-missing value, and
#     99 never occurs in the file;
#   * there is not one NaN cell in the whole file. A six-week per-match diary
#     that no athlete ever left a single item blank is not credible;
#   * the zeros sit singly inside otherwise-normal response vectors -- 19 of
#     the 21 rows carrying any zero in the justice block are only partly zero
#     -- which is a per-item skip, not a person who stopped responding.
#
# The earlier reading that 0 marks athletes who did not play (playing_match
# = 3, "niet spelen") is disproved: rows carrying a zero split 9/4/8 across
# playing_match, close to the 387/161/113 overall distribution.
#
# So 0 is dropped rather than shipped as a response. If it is ever established
# to mean something, the fix is to map it here rather than to restore it: the
# one thing that is certain is that it is not a point on a 1-5 scale.
RESP_MIN, RESP_MAX = 1, 5


def _ship(df, out_name, item_cols):
    long = df.melt(id_vars=["id", "wave"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    out_of_range = ~long["resp"].between(RESP_MIN, RESP_MAX)
    if out_of_range.any():
        gone = long.loc[out_of_range, "resp"].value_counts().sort_index()
        print(f"  {out_name}: dropped {int(out_of_range.sum())} response(s) outside "
              f"{RESP_MIN}-{RESP_MAX}: "
              + ", ".join(f"{v:.0f} x{n}" for v, n in gone.items()))
        long = long.loc[~out_of_range].reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _ship(df, "debacker_2018_decisionjustification", DJ_ITEMS)
    _ship(df, "debacker_2018_justice_appraisal", JA_ITEMS)


if __name__ == "__main__":
    convert()
