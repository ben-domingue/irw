#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0293298
# DOI: 10.1371/journal.pone.0293298
# S1 Data (CSV) -- online survey of breast cancer survivors on sexual
# functioning coping strategies. The paper's SI is mostly qualitative
# (open-ended coping-method text) and demographics, but questions 16-36 are
# a Female Sexual Function Index (FSFI)-style battery: 21 closed-ended
# Likert/frequency items on desire, arousal, lubrication, orgasm,
# satisfaction, and pain, each with its own text-labelled response scale
# (exported as category strings, not numeric codes). This script extracts
# only that item battery -- not the qualitative/demographic columns -- and
# recodes each item's category labels to an ordinal 0-5 scale via
# keyword-based rank functions (0 reserved for "no sexual activity" /
# "did not attempt intercourse" / "no partner(s)" sentinel responses,
# which FSFI scoring treats as the bottom of the scale, not missing data).

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0293298.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SENTINEL_RE = re.compile(
    r"no sexual activity|did not attempt intercourse|no partner\(s\)",
    re.IGNORECASE,
)


def rank_level(s):  # very low/low/moderate/high/very high
    s = s.lower()
    if "very low" in s or "very low or none" in s:
        return 1
    if "moderate" in s:
        return 3
    if "very high" in s:
        return 5
    if "high" in s:
        return 4
    if "low" in s:
        return 2
    return None


def rank_freq(s):  # almost never .. almost always
    s = s.lower()
    if "almost never" in s or "almost never or never" in s:
        return 1
    if "a few times" in s:
        return 2
    if "sometimes" in s:
        return 3
    if "most times" in s:
        return 4
    if "almost always" in s:
        return 5
    return None


def rank_confidence(s):
    s = s.lower()
    if "very low" in s:
        return 1
    if "low confidence" in s:
        return 2
    if "moderate" in s:
        return 3
    if "high confidence" in s:
        return 4
    if "very high" in s:
        return 5
    return None


def rank_difficulty(s):  # higher = easier = better function
    s = s.lower()
    if "extremely difficult" in s or "impossible" in s:
        return 1
    if "very difficult" in s:
        return 2
    if "slightly difficult" in s:
        return 4
    if "difficult" in s:
        return 3
    if "not difficult" in s:
        return 5
    return None


def rank_satisfaction(s):
    s = s.lower()
    if "very dissatisfied" in s:
        return 1
    if "moderately dissatisfied" in s:
        return 2
    if "equally satisfied and dissatisfied" in s:
        return 3
    if "moderately satisfied" in s:
        return 4
    if "very satisfied" in s:
        return 5
    return None


def rank_count_freq_5(s):  # not at all .. almost every day (item 18)
    s = s.lower()
    order = ["not at all", "once a week", "a few times this month", "once",
             "two to three times per week", "almost every day"]
    # explicit disambiguation: "once" alone vs "once a week"
    if s.strip() == "not at all":
        return 0
    if s.strip() == "once":
        return 1
    if "a few times this month" in s:
        return 2
    if "once a week" in s:
        return 3
    if "two to three times per week" in s:
        return 4
    if "almost every day" in s:
        return 5
    return None


def rank_count_freq_6(s):  # item 19, adds "more than once per day"
    r = rank_count_freq_5(s)
    if r is not None:
        return r
    if "more than once per day" in s.lower():
        return 6
    return None


def code_item(series, rank_fn):
    out = []
    for v in series:
        if pd.isna(v):
            out.append(None)
        elif SENTINEL_RE.search(str(v)):
            out.append(0)
        else:
            out.append(rank_fn(str(v)))
    return out


# (source column substring, rank function)
ITEM_SPEC = [
    ("16.", rank_level),
    ("17.", rank_freq),
    ("18.", rank_count_freq_5),
    ("19.", rank_count_freq_6),
    ("20.", rank_freq),
    ("21.", rank_level),
    ("22.", rank_confidence),
    ("23.", rank_freq),
    ("24.", rank_freq),
    ("25.", rank_difficulty),
    ("26.", rank_freq),
    ("27.", rank_difficulty),
    ("28.", rank_freq),
    ("29.", rank_difficulty),
    ("30.", rank_satisfaction),
    ("31.", rank_satisfaction),
    ("32.", rank_satisfaction),
    ("33.", rank_satisfaction),
    ("34.", rank_freq),
    ("35.", rank_freq),
    ("36.", rank_level),
]


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    import io
    return io.BytesIO(r.content)


def convert():
    df = pd.read_csv(fetch())
    df = df.rename(columns={"Record ID": "id"})

    frames = []
    for prefix, rank_fn in ITEM_SPEC:
        col = next((c for c in df.columns if c.strip().startswith(prefix)), None)
        if col is None:
            continue
        item_name = f"fsfi_{prefix.rstrip('.')}"
        resp = code_item(df[col], rank_fn)
        frames.append(pd.DataFrame({"id": df["id"], "item": item_name, "resp": resp}))

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    assert df["id"].nunique() == len(df), "id not unique"

    out_cols = ["id", "item", "resp"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_dir_abs = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir_abs, exist_ok=True)
    out_name = "vonhippel_2023_fsfi.csv"
    out_path = os.path.join(out_dir_abs, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
