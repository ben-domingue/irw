#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Anonymized_dataset_for_In_the_Spotlight_Exploring_Celebrity_Worship_Body_Image_and_Self-Esteem_among_Indian_Professional_College_Students_/30929354
# DOI: 10.6084/m9.figshare.30929354.v1
# Data: "Research Data.xlsx", sheet "Master Data" (the real header is the SECOND row; the
#   first row only spans the YABIS_A groups). Sheet "Code Book" documents the covariates.
# License: CC BY 4.0 (verified on the figshare record: license "CC BY 4.0")
# Reference: Vezhodulu, S., Velayudhan, B., & Yesodharan, R. (2025). Anonymized dataset
#   for: In the Spotlight: Exploring Celebrity Worship, Body Image and Self-Esteem among
#   Indian Professional College Students. figshare.
# Item codes: the source headers are "CWS#1", "YABIS_B#1", "RSES#1"; '#' is replaced by '_'
#   and nothing else changes, so the mapping is reversible one-for-one. The YABIS_A block
#   has no per-item header at all -- the first spreadsheet row labels five groups
#   (YABIS_A#1..#5) and the second labels their columns "actual"/"ideal"/"Total score"/
#   "Absolute value" -- so its actual/ideal columns are taken POSITIONALLY from that two-row
#   header (groups 1-3 carry 4 columns, groups 4-5 carry 3) and ship as YABIS_A_1_actual /
#   YABIS_A_1_ideal and so on.
# Item text: not shipped. Label levels checked: the .xlsx has no variable or value labels
#   (not an SPSS file); the deposit's "Code Book" sheet was read in full and codes the eight
#   demographic covariates only (age band, gender, family type, residence, course, year,
#   screen time, health issues) -- it carries no item wording. The stems live in the
#   published Celebrity Attitude/Worship Scale, the YABIS and Rosenberg's Self-Esteem Scale,
#   third-party instruments the deposit's CC BY does not reach.
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s2"))
CACHE = Path(os.environ.get("IRW_CACHE", "/tmp/irw_cache_s2"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch(url: str, name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not p.exists():
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=600) as r, open(p, "wb") as f:
            f.write(r.read())
    return p


def screen_pii(d: pd.DataFrame) -> None:
    """Print every string column and its sample values; assert the denominator is non-zero."""
    txt = [c for c in d.columns if pd.api.types.is_string_dtype(d[c])]
    print(f"  [pii] string columns examined: {len(txt)} of {d.shape[1]}")
    assert len(txt) > 0 or d.select_dtypes("object").empty, "PII screen selected no columns"
    for c in txt:
        vals = d[c].dropna().astype(str).unique()[:8]
        print(f"  [pii] {c!r}: {list(vals)}")


def emit(tables: dict) -> None:
    """name -> (long frame, permitted_values or None). QC, upload-profile validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names), f"duplicate output names: {names}"
    assert max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    """Melt `items` to long, drop missing, keep only codes in `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items,
               var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
    t = t.dropna(subset=["resp"])
    if valid is not None:
        keep = t["resp"].isin(valid)
        if not keep.all():
            print(f"    dropped {int((~keep).sum())} resp outside {sorted(valid)[:1]}.."
                  f"{sorted(valid)[-1:]}")
        t = t[keep]
    order = (["id", "item", "resp"]
             + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
             + [c for c in ("cluster_id", "block_id") if c in t.columns]
             + covs)
    return t[order].reset_index(drop=True)


def pvals(items, valid, rename: dict | None = None) -> dict:
    """permitted_values keyed by the shipped item code."""
    vs = sorted(float(v) for v in valid)
    return {(rename or {}).get(c, c): list(vs) for c in items}

URL = "https://ndownloader.figshare.com/files/60549590"

COVS = {
    "Age": "cov_age_band", "Gender": "cov_gender", "Types of Family": "cov_family_type",
    "Residence": "cov_residence", "Professional Course": "cov_course",
    "Sem/Year": "cov_year_of_study", "Screen time": "cov_screen_time",
    "Health issues": "cov_health_issues",
}
# YABIS_A actual/ideal column positions in the header=1 frame (see the header note above).
YA_ACTUAL = [51, 55, 59, 63, 66]
YA_IDEAL = [52, 56, 60, 64, 67]
MULTISELECT = ["Facebook", "Twitter", "Instagram", "Spotify", "YouTube", "WhatsApp",
               "Reddit", "Snapchat", "Netflix", "Creative inspiration", "Entertainment",
               "Idolize & stan", "Obsessed", "Educational"]
REELS = ["Follow reels", "Make reels", "Co-create reels with celebrities"]


def convert() -> None:
    p = fetch(URL, "figshare_30929354_Research_Data.xlsx")
    d = pd.read_excel(p, sheet_name="Master Data", header=1)
    screen_pii(d)
    src = list(d.columns)

    # Rename the positional YABIS_A columns before anything else touches names.
    ya_rename = {}
    for k, (ai, ii) in enumerate(zip(YA_ACTUAL, YA_IDEAL), start=1):
        ya_rename[src[ai]] = f"YABIS_A_{k}_actual"
        ya_rename[src[ii]] = f"YABIS_A_{k}_ideal"
    assert len(set(ya_rename.values())) == 10
    d.columns = [ya_rename.get(c, c) for c in d.columns]

    d = d.rename(columns={"Participants": "id"})
    assert d["id"].nunique() == len(d), "Participants is not one row per respondent"
    print(f"  respondents={d['id'].nunique()}")

    d = d.rename(columns=COVS)
    covs = sorted(COVS.values())

    cws = [f"CWS#{i}" for i in range(1, 25)]
    yb = [f"YABIS_B#{i}" for i in range(1, 25)]
    rses = [f"RSES#{i}" for i in range(1, 11)]
    ya = list(ya_rename.values())
    hashless = {c: c.replace("#", "_") for c in cws + yb + rses}

    tables = {}
    for name, items, valid in (
            # 1-5 Likert; a single 13 in the CWS block is a keying slip and is dropped.
            ("vezhodulu_2025_celebrity_worship", cws, range(1, 6)),
            ("vezhodulu_2025_yabis_a", ya, range(1, 7)),
            ("vezhodulu_2025_yabis_b", yb, range(1, 6)),
            ("vezhodulu_2025_rses", rses, range(1, 5))):
        assert all(c in d.columns for c in items), name
        tables[name] = (long(d, items, covs, valid=set(float(v) for v in valid),
                             rename=hashless),
                        pvals(items, valid, rename=hashless))

    used = set(cws) | set(yb) | set(rses) | set(ya_rename)
    for c in src:
        if c == "Participants" or c in COVS or c in used:
            continue
        if c in MULTISELECT:
            print(f"  [skip] {c}: multi-select usage/motive checkbox, not an ordered "
                  f"response scale")
        elif c in REELS:
            print(f"  [skip] {c}: coded 1/2 in the data while the deposit's Code Book "
                  f"documents Yes=1/No=0; the coding cannot be resolved from the deposit")
        elif "Total" in c or "Absolute" in c:
            print(f"  [skip] {c}: scale/subscale total or actual-ideal discrepancy "
                  f"(composite)")
        else:
            raise AssertionError(f"unaccounted source column: {c}")

    emit(tables)


if __name__ == "__main__":
    convert()
