"""Academic stress, motivation and learner autonomy among Vietnamese lower-secondary students.

DOI: 10.17632/whsbpyxy6w
Source: https://data.mendeley.com/datasets/whsbpyxy6w
License: CC BY 4.0
Contributor (deposit record): Nguyen

1,489 Hanoi lower-secondary students, all items five-point Likert.
Seven constructs, per the deposit description: academic pressure/stress
(AP), academic motivation (AM), family factors (F), school autonomy support
(S), student voice (V), student choice (C), student ownership (O).
The seven bare composite columns (AP, S, AM, F, V, C, O) are subscale means
and are dropped.
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

DOI = "10.17632/whsbpyxy6w"
KEY = "whsbpyxy6w"
FILENAME = 'Dataset on The impact of academic stress and academic motivation on learner autonomy among Vietnamese low.xlsx'
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE_PREFIX = "nguyen_2026_autonomy_"
BLOCKS = {'academic_pressure': ['AP'], 'academic_motivation': ['AM'], 'family_factors': ['F'], 'school_autonomy_support': ['S'], 'student_voice': ['V'], 'student_choice': ['C'], 'student_ownership': ['O']}
COVS = {'GioiTinh': 'cov_gender', 'KhoiLop': 'cov_grade', 'LoaiHinh': 'cov_school_type', 'HocLuc': 'cov_academic_performance'}
DROP = ['AP', 'S', 'AM', 'F', 'V', 'C', 'O']          # composites / constants, with reasons in DROP_REASON
DROP_REASON = 'subscale composite mean, not a raw item'
SCALE = (1, 5)
DROP_NON_INTEGER = False


def fetch() -> pd.DataFrame:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    files = r.json()["files"]
    match = [f for f in files if f["filename"] == FILENAME]
    assert len(match) == 1, [f["filename"] for f in files]
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=120)
    rr.raise_for_status()
    buf = io.BytesIO(rr.content)
    if FILENAME.lower().endswith(".sav"):
        import pyreadstat
        return pyreadstat.read_sav(_spill(rr.content, ".sav"))[0]
    if FILENAME.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(buf)
    return pd.read_csv(buf)


def _spill(content: bytes, suffix: str) -> str:
    import tempfile
    fh = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    fh.write(content)
    fh.close()
    return fh.name


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
    for suffix, prefixes in BLOCKS.items():
        items = [c for c in df.columns
                 if any(c.startswith(p) and c[len(p):].isdigit() for p in prefixes)
                 and c not in DROP]
        assert items, suffix
        used.update(items)

        long = (df[["id"] + items]
                .melt(id_vars="id", var_name="item", value_name="resp")
                .dropna(subset=["resp"])
                .merge(cov, on="id"))

        if DROP_NON_INTEGER:
            nonint = long["resp"] % 1 != 0
            if nonint.any():
                print(f"    [{suffix}] dropped {int(nonint.sum())} non-integer "
                      f"(person-mean imputed) cells")
                long = long[~nonint]
        long["resp"] = long["resp"].astype(int)

        bad = long.loc[~long["resp"].between(*SCALE), "resp"].unique()
        assert len(bad) == 0, f"{suffix}: off-scale resp {bad}"

        long = long[["id", "item", "resp"]
                    + [c for c in long.columns if c.startswith("cov_")]]

        checks = run_qc(long)
        fails = [c for c in checks if c.status == "fail"]
        assert not fails, f"{suffix} QC failed: {[(c.name, c.detail) for c in fails]}"
        for c in checks:
            if c.status == "warn":
                print(f"    NOTE [{suffix}] {c.name}: {c.detail}")

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
