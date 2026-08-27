"""Students' learning experience, engagement and achievement in blended-learning courses, Vietnamese engineering universities.

DOI: 10.17632/tdsspksw83
Source: https://data.mendeley.com/datasets/tdsspksw83
License: CC BY 4.0
Contributor (deposit record): hoai, Le, Pham

580 raw survey responses, five-point Likert throughout. Constructs per the
deposit description: teaching presence (TP), social presence (SP), cognitive
presence (CP), instructional design quality (IDQ), learning experience (LE),
student engagement (SE), academic achievement (AA).
CONSENT and SQ are screening constants (single value for every respondent)
and are dropped.

QC exemption: `resp_scale_mixed` fires on 8 of the 30 items because nobody
ever chose the bottom category on them (observed 2-5 rather than 1-5). Every
item maxes at 5, the deposit describes a single five-point instrument, and
SP4 -- the item that breaks the tie inside its own block -- has exactly one
respondent at 1. That is floor non-use on a left-skewed scale, not two
response scales, so the check is waived by name below rather than splitting
a real subscale.
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

DOI = "10.17632/tdsspksw83"
KEY = "tdsspksw83"
FILENAME = 'Blended learning_data set.xlsx'
UA = {"User-Agent": "irw-batch/1.0 (research)"}

TABLE_PREFIX = "hoai_2026_"
BLOCKS = {'teaching_presence': ['TP'], 'social_presence': ['SP'], 'cognitive_presence': ['CP'], 'instructional_design_quality': ['IDQ'], 'learning_experience': ['LE'], 'student_engagement': ['SE'], 'academic_achievement': ['AA']}
COVS = {'GENDER': 'cov_gender', 'AGE': 'cov_age_band', 'YEAR': 'cov_year_of_study', 'MAJOR': 'cov_major', 'PROGRAM': 'cov_program', 'UNIVERSITY_TYPE': 'cov_university_type'}
DROP = ['CONSENT', 'SQ']          # composites / constants, with reasons in DROP_REASON
DROP_REASON = 'screening constant, single value for every respondent'
SCALE = (1, 5)
QC_WAIVERS = {
    "resp_scale_mixed": "uniform five-point instrument; 8/30 items simply "
                        "never drew the bottom category (floor non-use)",
}
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
        waived = [c for c in fails if c.name in QC_WAIVERS]
        for c in waived:
            print(f"    WAIVED [{suffix}] {c.name}: {QC_WAIVERS[c.name]}")
        fails = [c for c in fails if c.name not in QC_WAIVERS]
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
