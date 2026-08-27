"""Psychometric dataset for the development of a teacher executive-function instrument.

DOI: 10.17632/6y7sbzjbny
Source: https://data.mendeley.com/datasets/6y7sbzjbny
License: CC BY 4.0
Contributor (deposit record): lestari, Jatnika, Agustiani

785 Indonesian pre-service teachers, 80 items scored 0-3 in three
blocks: cognitive flexibility (CF, 24), inhibitory control (IC, 40)
and working memory (WM, 16). Each ships as its own table.

The 'Nama' column was checked for PII and holds anonymised participant
codes ('S 001', 'S 002', ...), not real names; it is dropped anyway in
favour of a sequential id. The remaining Indonesian columns are
background covariates.
"""
from __future__ import annotations

import io
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/6y7sbzjbny"
KEY = "6y7sbzjbny"
FILENAME = 'Raw Data, Construct Reliability (CR), and Average Variance Extracted (AVE).xlsx'
READ_KW = {}
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE_PREFIX = "lestari_2026_"
BLOCKS = {'cognitive_flexibility': 'CF\\d+', 'inhibitory_control': 'IC\\d+', 'working_memory': 'WM\\d+'}            # table suffix -> regex matching its item columns
COVS = {'Asal Perguruan Tinggi': 'cov_institution', 'Jenis Kelamin': 'cov_gender', 'Program Studi': 'cov_study_program', 'Semester': 'cov_semester', 'Pengalaman Mengajar (dapat dipilih lebih dari 1)': 'cov_teaching_experience', 'Durasi Pengalaman mengajar': 'cov_teaching_experience_duration', 'Apakah pernah mengikuti microteaching?': 'cov_microteaching', 'IPK saat ini': 'cov_gpa', 'Seberapa sering anda mengamati guru mengajar atau terlibat langsung di kelas nyata?': 'cov_classroom_observation_frequency'}
DROP = ['Nama']
DROP_REASON = 'anonymised participant code, replaced by a sequential id'
SCALE = {'cognitive_flexibility': (0, 3), 'inhibitory_control': (0, 3), 'working_memory': (0, 3)}              # table suffix -> (min, max), or None to infer
QC_WAIVERS = {}


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    files = r.json()["files"]
    match = [f for f in files if f["filename"] == FILENAME]
    assert len(match) == 1, [f["filename"] for f in files]
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    low = FILENAME.lower()
    if low.endswith(".sav"):
        import pyreadstat
        fh = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
        fh.write(rr.content); fh.close()
        return pyreadstat.read_sav(fh.name)[0]
    if low.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(rr.content), **READ_KW)
    return pd.read_csv(io.BytesIO(rr.content), **READ_KW)


def build() -> None:
    df = fetch()
    df.columns = [str(c).strip() for c in df.columns]
    df["id"] = range(1, len(df) + 1)
    cov = df[["id"] + list(COVS)].rename(columns=COVS)

    used = set(COVS) | set(DROP)
    for c in DROP:
        print(f"    dropped '{c}': {DROP_REASON}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for suffix, pattern in BLOCKS.items():
        items = [c for c in df.columns
                 if re.fullmatch(pattern, c) and c not in DROP and c not in COVS]
        assert items, f"{suffix}: pattern {pattern!r} matched nothing"
        used.update(items)

        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"])
                .merge(cov, on="id"))

        nonint = long["resp"] % 1 != 0
        if nonint.any():
            print(f"    [{suffix}] dropped {int(nonint.sum())} non-integer cells")
            long = long[~nonint]
        long["resp"] = long["resp"].astype(int)

        lo, hi = SCALE[suffix]
        oor = ~long["resp"].between(lo, hi)
        if oor.any():
            vals = sorted(long.loc[oor, "resp"].unique())
            per = long.loc[oor].groupby("item").size().to_dict()
            print(f"    [{suffix}] dropped {int(oor.sum())} out-of-range cells "
                  f"{vals} (data-entry errors, isolated to {per})")
            long = long[~oor]

        long = long[["id", "item", "resp"]
                    + [c for c in long.columns if c.startswith("cov_")]]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        for c in [c for c in fails if c.name in QC_WAIVERS]:
            print(f"    WAIVED [{suffix}] {c.name}: {QC_WAIVERS[c.name]}")
        fails = [c for c in fails if c.name not in QC_WAIVERS]
        assert not fails, f"{suffix} QC failed: {[(c.name, c.detail) for c in fails]}"
        for c in checks:
            if c.status == "warn":
                print(f"    NOTE [{suffix}] {c.name}: {c.detail}")

        assert long["id"].nunique() >= 100, f"{suffix}: N={long['id'].nunique()} < 100"
        assert long["item"].nunique() > 1, f"{suffix}: single-item scale"

        name = f"{TABLE_PREFIX}{suffix}"
        assert name not in written, f"duplicate table name {name}"
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written[name] = (long["id"].nunique(), long["item"].nunique(), len(long))
        print(f"  {name}: {written[name][0]} ids x {written[name][1]} items "
              f"= {written[name][2]} responses")

    unused = [c for c in df.columns if c not in used and c != "id"]
    assert not unused, f"unaccounted source columns: {unused}"
    print(f"  total: {sum(v[2] for v in written.values())} responses "
          f"across {len(written)} tables")


if __name__ == "__main__":
    build()
