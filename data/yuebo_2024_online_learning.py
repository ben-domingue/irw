from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0297515
# DOI: 10.1371/journal.pone.0297515
# Yuebo, Halili & Abdul Razak (2024), "Online learning success model for
# adults in open and distance education in Western China". S1 Data (.s001,
# CSV). CC BY 4.0. N=245 adult learners, all items 5-point Likert (1-5).
# Nine constructs from an ISS (information-system-success) + TPACK model:
# system quality (SQ), service quality (SEQ), information quality (IQ),
# continuous use (USE), user-perceived satisfaction (US), net benefit (NB),
# and TPACK's three sub-facets (TK, TCK, PCK) plus the overarching TPACK
# scale itself -> 10 distinct scales, shipped as 10 separate tables per
# datastandard.md's "multiple scales in one file" rule. The un-suffixed
# TK/TCK/PCK/TPACK columns are the paper's own aggregate mean-of-items
# columns for each subscale -- excluded as composites, not raw responses.

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0297515.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "yuebo_2024_sysquality":   ["SQ1", "SQ2", "SQ3", "SQ4"],
    "yuebo_2024_srvquality":   ["SEQ1", "SEQ2", "SEQ3", "SEQ4"],
    "yuebo_2024_infoquality":  ["IQ1", "IQ2", "IQ3", "IQ4"],
    "yuebo_2024_use":          ["USE1", "USE2", "USE3", "USE4", "USE5"],
    "yuebo_2024_satisfaction": ["US1", "US2", "US3", "US4"],
    "yuebo_2024_netbenefit":   [f"NB{i}" for i in range(1, 17)],
    "yuebo_2024_tk":           ["TK1", "TK2", "TK3", "TK4"],
    "yuebo_2024_tck":          ["TCK1", "TCK2", "TCK3", "TCK4"],
    "yuebo_2024_pck":          ["PCK1", "PCK2", "PCK3", "PCK4", "PCK5"],
    "yuebo_2024_tpack":        ["TPACK1", "TPACK2", "TPACK3", "TPACK4", "TPACK5"],
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"NU": "id"})
    assert df["id"].is_unique and df["id"].notna().all()

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
