#!/usr/bin/env python3
# Dong, Conway, Bonnefon, Shariff & Rahwan (2026). Fears about artificial
# intelligence across 20 countries and six domains of application. American
# Psychologist 81(1), 53-67.
# DOI: 10.1037/amp0001454
# Source: https://osf.io/mb5nz/, "Preregistered Main Study/long-format data for
#   analysis.csv", https://osf.io/download/jh2w5/
#   sha256 3d42990fb27bacb41bbfa6edb9eb268926a5c127c2786bea521d0055b342a18b
#
# 10,000 respondents, 500 in each of 20 countries; every answer is a 0-100
# slider. The file has one row per id x occupation x trait (6 x 8), so an
# answer given once per occupation or once per trait is repeated on every row
# of its cell. Each table keeps one row per answer (#2906):
#   ai_fear_dong_2026_requirement  "a good [occupation] should be [trait]?",
#                                  item = occupation_trait, 48 items
#   ai_fear_dong_2026_ai           "AI, at its full potential, can be
#                                  [trait]?", item = trait, 8 items
#   ai_fear_dong_2026_own_fear     "are you afraid of AI being [occupation]?",
#                                  item = occupation, 6 items
#   ai_fear_dong_2026_other_fear   "most people in [country] are afraid of AI
#                                  being [occupation]?", item = occupation,
#                                  6 items
# `incentive` is a condition, not an answer, so it gets no table: in South
# Korea and the UK, half of each sample was offered bonus points for estimates
# of others' fear within 10 points of the country average. It is `treat` on
# other_fear (1 = offered, 0 = not), blank for the other 18 countries.
#
# Usage: python3 data/ai_fear_dong_2026.py [local copy of the csv]
#   (with no argument the file is downloaded)

import hashlib
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://osf.io/download/jh2w5/"
SHA256 = "3d42990fb27bacb41bbfa6edb9eb268926a5c127c2786bea521d0055b342a18b"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COVS = ["country", "age", "age_group", "gender", "education", "income",
        "social_class"]
# source column -> what each answer was given once per
TABLES = {"requirement": ["occupation", "trait"], "ai": ["trait"],
          "own.fear": ["occupation"], "other.fear": ["occupation"]}


def load(src):
    if src.startswith("https://"):
        r = requests.get(src, headers=UA, timeout=600)
        r.raise_for_status()
        raw = r.content
    else:
        raw = Path(src).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA256, f"{src} has changed"
    return pd.read_csv(io.BytesIO(raw))


def convert(src):
    df = load(src).rename(columns={c: f"cov_{c}" for c in COVS})
    covs = [f"cov_{c}" for c in COVS]
    assert (df.groupby("id")["incentive"].nunique(dropna=False) == 1).all()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for col, keys in TABLES.items():
        # one row per answer is only safe if the copies really are copies
        assert (df.groupby(["id"] + keys)[col].nunique() == 1).all(), col
        long = df.drop_duplicates(["id"] + keys).copy()
        long["item"] = long[keys].agg("_".join, axis=1)
        long["resp"] = long[col].astype("Int64")
        treat = []
        if col == "other.fear":
            long["treat"] = long["incentive"].astype("Int64")
            treat = ["treat"]
        long = long[["id", "item", "resp"] + treat + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        table = f"ai_fear_dong_2026_{col.replace('.', '_')}"
        report = irw_validate.validate_frame(long, label=table,
                                             profile="upload")
        assert report.conforms and not report.errors, \
            [(f.check, f.message) for f in report.errors]
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert(sys.argv[1] if len(sys.argv) > 1 else URL)
