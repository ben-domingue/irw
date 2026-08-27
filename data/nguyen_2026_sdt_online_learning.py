"""Vietnamese students' basic psychological needs, mental health, academic
motivation and perceived academic performance in online learning.

DOI: 10.17632/n45sjtxmzy
Source: https://data.mendeley.com/datasets/n45sjtxmzy
License: CC BY 4.0
Contributor (deposit record): Nguyen

One .xlsx, 2,763 respondents x 38 Likert items, all on a 1-5 scale, in six
prefix-coded blocks:

    COM1-6   competence          }
    REL1-8   relatedness         }  Basic Psychological Needs Scale
    AUT1-7   autonomy            }  (three subscales, one instrument)
    MEH1-5   mental health
    ACM1-7   academic motivation
    ACP1-5   perceived academic performance

Each prefix ships as its own table. COM/REL/AUT are the three BPNS subscales;
IRW precedent (KEPAQ Functional/Emotional, KORQ Activity-Limitation/Symptoms,
STAI Y-1/Y-2 in the 2026-08-26 education batches) is to split subscales into
separate tables rather than pool them, and `run_qc`'s multi_scale check
objects to pooling them.

The four Vietnamese demographic columns are covariates, plus `Online`
(0/1, whether the respondent was in the online-learning condition).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/n45sjtxmzy"
KEY = "n45sjtxmzy"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

# block prefix -> (output table suffix, item count)
BLOCKS = {
    "competence": ["COM"],
    "relatedness": ["REL"],
    "autonomy": ["AUT"],
    "mental_health": ["MEH"],
    "academic_motivation": ["ACM"],
    "perceived_performance": ["ACP"],
}

COVS = {
    "Online": "cov_online_condition",
    "GIOI TINH": "cov_gender",
    "SINH VIEN NAM": "cov_year_of_study",
    "NGANH HOC": "cov_major",
    "THOI GIAN HOC TAP TRUC TUYEN": "cov_online_study_time",
}

SCALE_MIN, SCALE_MAX = 1, 5


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    files = r.json()["files"]
    cand = [f for f in files if f["filename"].lower().endswith(".xlsx")]
    assert len(cand) == 1, [f["filename"] for f in files]
    dl = cand[0]["content_details"]["download_url"]
    rr = requests.get(dl, headers=UA, timeout=120)
    rr.raise_for_status()
    return pd.read_excel(io.BytesIO(rr.content))


def build() -> None:
    df = fetch()
    df.columns = [str(c).strip() for c in df.columns]
    df["id"] = range(1, len(df) + 1)

    cov = df[["id"] + list(COVS)].rename(columns=COVS)

    used: set[str] = set(COVS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}

    for suffix, prefixes in BLOCKS.items():
        items = [c for c in df.columns
                 if any(c.startswith(p) and c[len(p):].isdigit() for p in prefixes)]
        assert items, suffix
        used.update(items)

        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"])
                .merge(cov, on="id"))
        long["resp"] = long["resp"].astype(int)

        bad = long.loc[~long["resp"].between(SCALE_MIN, SCALE_MAX), "resp"].unique()
        assert len(bad) == 0, f"{suffix}: off-scale resp values {bad}"

        long = long[["id", "item", "resp"] + [c for c in long.columns
                                              if c.startswith("cov_")]]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        assert not fails, f"{suffix} QC failed: {[(c.name, c.detail) for c in fails]}"
        for c in checks:
            if c.status == "warn":
                print(f"    NOTE [{suffix}] {c.name}: {c.detail}")

        name = f"nguyen_2026_sdt_{suffix}"
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        assert name not in written, f"duplicate table name {name}"
        written[name] = (long["id"].nunique(), long["item"].nunique(), len(long))
        print(f"  {name}: {written[name][0]} ids x {written[name][1]} items "
              f"= {written[name][2]} responses")

    # balance the books: every source column accounted for
    unused = [c for c in df.columns if c not in used and c != "id"]
    assert not unused, f"unaccounted source columns: {unused}"
    print(f"  total: {sum(v[2] for v in written.values())} responses "
          f"across {len(written)} tables")


if __name__ == "__main__":
    build()
