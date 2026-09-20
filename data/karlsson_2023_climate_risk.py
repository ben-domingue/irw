#!/usr/bin/env python3
"""Climate-change risk perception, pre and post a mental-imagery manipulation.

Source: https://www.nature.com/articles/s41598-023-37195-w
DOI: 10.1038/s41598-023-37195-w
Data: https://osf.io/k6vp9/ (Survey/Data/Mental_Imagery_Emotion_Environmental
      _Risk_October+20,+2022_20.sav)
License: CC BY 4.0 (Crossref)

1,001 US respondents rated the same six climate-risk items twice -- once
before and once after a mental-imagery manipulation -- so this ships as one
table with `wave` (1 = pre, 2 = post) and `treat`.

`resp` is a 0-100 slider, kept as a float. These are continuous per-item
ratings, not composites: the deposit's own averages live in separate
`Pre_RiskAverage`/`Post_RiskAverage` columns, which are excluded.

THE POST BLOCK IS MISNAMED IN THE DEPOSIT. The codebook lists
Post_Risk_DV_1..6, but the file has Post_Risk_DV_1, _2, _3, _5, _6 and
`MPost_Risk_DV_4` -- a stray M on the fourth column. It is item 4: its
variable label is "How big of a risk is climate change for you?", which is
Pre_Risk_DV_4's label word for word. Renamed on load so the pre and post
waves carry the same six item codes; without that the table would silently
ship five paired items and one orphan.

`treat` is 0 for the control arm (instinctive mental imagery) and 1 for the
two active arms, with `cov_condition` keeping which arm (1 control,
2 enhanced imagery, 3 prevented imagery) since the standard's `treat` is
binary and this design has three cells. One respondent has no condition
recorded; their `treat` and `cov_condition` are blank rather than guessed.

Item text: not shipped. The full stems are in the SPSS variable labels, but
`resp` is a continuous 0-100 slider, so there is no item x response-option
grid to write -- the itemtext schema's unit is the option row. The wording is
recorded here and in the dictionary Notes instead.

Not shipped from this deposit: the 80-trial mental rotation block. Only 87 of
1,001 respondents have any of it (914 NaN per column), which is below the
100-id floor. The 48 interleaved valence/arousal/vividness ratings belong to
the manipulation itself rather than to an instrument, and are left alone.
"""
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
TABLE = "karlsson_2023_climate_risk"
DATA_URL = ("https://osf.io/download/rqs83/"
            "?view_only=5aa191c0ad0041b8aed85df0ae9f25f0")
UA = {"User-Agent": "irw-batch/1.0 (research)"}
SAV = Path("/tmp/irw_karlsson_2023.sav")

# The stray M is the deposit's, not ours -- see the docstring.
POST_FIXES = {"MPost_Risk_DV_4": "Post_Risk_DV_4"}
ITEMS = [f"Risk_DV_{i}" for i in range(1, 7)]
WAVES = {"Pre": 1, "Post": 2}
SLIDER_MIN, SLIDER_MAX = 0.0, 100.0
CONTROL_ARM = 1.0


def load() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    SAV.write_bytes(r.content)
    df, meta = pyreadstat.read_sav(str(SAV))
    SAV.unlink()
    df = df.rename(columns=POST_FIXES)
    # The rename is only safe if the two labels really are the same item.
    pre_lab = meta.column_names_to_labels.get("Pre_Risk_DV_4", "")
    post_lab = meta.column_names_to_labels.get("MPost_Risk_DV_4", "")
    assert pre_lab and pre_lab == post_lab, (
        "MPost_Risk_DV_4 no longer matches Pre_Risk_DV_4's label; re-check "
        "the deposit before trusting the rename")
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def convert() -> None:
    raw = load()

    cov = raw[["id", "Gender", "Age", "Condition"]].rename(
        columns={"Gender": "cov_gender", "Age": "cov_age",
                 "Condition": "cov_condition"})
    cov["treat"] = (cov["cov_condition"] != CONTROL_ARM).astype("Int64")
    cov.loc[cov["cov_condition"].isna(), "treat"] = pd.NA

    frames = []
    for prefix, wave in WAVES.items():
        cols = [f"{prefix}_{it}" for it in ITEMS]
        missing = [c for c in cols if c not in raw.columns]
        assert not missing, f"wave {wave}: missing columns {missing}"
        block = raw[["id"] + cols].rename(columns=dict(zip(cols, ITEMS)))
        long = block.melt(id_vars="id", var_name="item", value_name="resp")
        long["wave"] = wave
        frames.append(long)

    long = pd.concat(frames, ignore_index=True).merge(cov, on="id")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    cov_cols = ["cov_gender", "cov_age", "cov_condition"]
    long = long[["id", "item", "resp", "wave", "treat"] + cov_cols]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert long["resp"].between(SLIDER_MIN, SLIDER_MAX).all(), "resp off the slider"
    assert not long.duplicated(["id", "item", "wave"]).any(), "duplicate id/item/wave"
    assert long["id"].nunique() >= 100, "below the 100-id floor"
    assert long["item"].nunique() == 6, "item count changed"
    assert long["wave"].nunique() == 2, "lost a wave"
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
