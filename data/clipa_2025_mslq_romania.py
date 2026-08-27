"""Motivation and learning strategies (81-item MSLQ) among Romanian higher-education students.

DOI: 10.17632/bj5vtsj7bj
Source: https://data.mendeley.com/datasets/bj5vtsj7bj
License: CC BY 4.0
Contributor (deposit record): Clipa, Cosma

225 students, 81 MSLQ items (VAR1-VAR81) on a 1-5 scale, shipped as one
table -- the deposit publishes its subscale structure only as computed
means, not as an item-to-subscale map.

Dropped: the 15 named subscale means (M1-M6 motivation, Ls1-Ls9
learning strategies), the two overall scale means, the EST/PRE/RES
model-output columns, and the *_numeric / *_dummy duplicates of
covariates that are also present in their original labelled form.
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

DOI = "10.17632/bj5vtsj7bj"
KEY = "bj5vtsj7bj"
FILENAME = 'Database_Motivation&LearningStrategies_COSMA.sav'
READ_KW = {}
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE_PREFIX = "clipa_2025_"
BLOCKS = {'mslq': 'VAR\\d+'}            # table suffix -> regex matching its item columns
COVS = {'Varsta': 'cov_age', 'An_studiu': 'cov_year_of_study', 'Program_frecventa': 'cov_program_attendance', 'Etnia': 'cov_ethnicity', 'Mediu_provenienta': 'cov_origin_environment', 'Media': 'cov_grade_band', 'Specializarea': 'cov_specialisation', 'Universitatea': 'cov_university', 'Facultatea': 'cov_faculty'}
DROP = ['Nr.Crt', 'Program.frecventa.numeric', 'Mediu_numeric', 'Media_numeric', 'Universitatea_Oradea_dummy', 'M1_Intrinsic.Goal.Orientation', 'M2_Extrinsic.Goal.Orientation', 'M3_Task.Value', 'M4_Control.of.Learning.Beliefs', 'M5_Self_Efficacy.for.Learning.and.Performance', 'M6_Test.Anxiety', 'Ls1_Rehearsal', 'Ls2_Elaboration', 'Ls3_Organization', 'Ls4_Critical.Thinking', 'Ls5_Metacognitive.Self_Regulation', 'Ls6_Time.and.Study.Environment.Management', 'Ls7_Effort.Regulation', 'Ls8_Peer.Learning', 'Ls9_Help.Seeking', 'Motivation_Scale', 'Learning_strategy_Scale', 'EST1_8', 'EST2_8', 'EST3_8', 'EST4_8', 'PRE_8', 'PRE_1', 'PRE_2', 'RES_1']
DROP_REASON = 'computed subscale/scale mean, model output, or a numeric duplicate of a labelled covariate'
SCALE = {'mslq': (1, 5)}              # table suffix -> (min, max), or None to infer
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
