#!/usr/bin/env python3

# Source: https://zenodo.org/records/22035722
# DOI: 10.5281/zenodo.22035722 (dataset; the record names no published paper)
#   Hartmann, P. (2026). Survey data on artificial intelligence use, awareness of AI's
#   environmental impact, climate anxiety and pro-climate behavioural intentions
#   [Dataset]. Zenodo.
# Data: "26 IJCS AI climate.sav": 845 US respondents, five instruments at the item
#       level. The SPSS variable labels carry the full stem of every item and the
#       value labels carry every scale anchor.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for FOUR of the five tables (English, from the SPSS variable
#   labels; both label levels checked -- variable labels give the stems, value labels
#   give the anchors). NOT shipped for hartmann_2026_climate_anxiety: those nine items
#   are the Climate Change Anxiety Scale (Clayton & Karazsia 2020), a named
#   third-party instrument with no quotable rights clause, and the 2026-10-15 ruling
#   is that silence on a named third-party instrument no longer ships. The other four
#   scales are authored by the depositor for this study (AI-use frequency counts, AI
#   environmental-impact beliefs, climate commitment, pro-climate behavioural
#   intentions), so the CC BY deposit is the originator's own grant.
#
# Five tables, one per instrument, because each has its own response scale:
#   hartmann_2026_ai_use_intensity      4 items, 1-7 frequency bands.
#   hartmann_2026_ai_env_awareness      8 items, 1-5 agreement.
#   hartmann_2026_climate_anxiety       9 items, 1-5 frequency.
#   hartmann_2026_climate_commitment    4 items, 1-5 agreement.
#   hartmann_2026_pro_climate_intention 5 items, 1-5 likelihood.
# Covariates: cov_gender, cov_age, cov_region, cov_education, cov_income.
# id: the deposit's "ID" (845 distinct over 845 rows).
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
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
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


def books(all_cols, used: dict) -> None:
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_22035722"
USE = [f"AIUseIntensity{i}" for i in range(1, 5)]
AWARE = [f"AIEnvironmentalImpactAwareness{i}" for i in range(1, 9)]
ANX = [f"ClimateAnxiety{i}" for i in range(1, 10)]
COMMIT = [f"ClimateCommitment{i}" for i in range(1, 5)]
INTENT = [f"ProClimateIntention{i}" for i in range(1, 6)]
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Region": "cov_region",
        "Education": "cov_education", "Income": "cov_income"}
# The item codes shipped are the deposit's own column names, shortened only where the
# source name is unwieldy; the mapping is explicit so nothing is positional.
RENAME_AWARE = {c: f"AIEnvAware{i}" for i, c in enumerate(AWARE, 1)}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(22035722, "26 IJCS AI climate.sav", RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 845, len(d)
    src = list(d.columns)
    books(src, {
        "shipped": USE + AWARE + ANX + COMMIT + INTENT,
        "covariate": list(COVS),
        "respondent id": ["ID"],
    })
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    assert d["id"].nunique() == len(d), d["id"].nunique()
    v7, v5 = range(1, 8), range(1, 6)
    emit({
        "hartmann_2026_ai_use_intensity":
            (long(d, USE, covs, valid=v7), pv_for(USE, v7)),
        "hartmann_2026_ai_env_awareness":
            (long(d, AWARE, covs, valid=v5, rename=RENAME_AWARE),
             pv_for(RENAME_AWARE.values(), v5)),
        "hartmann_2026_climate_anxiety":
            (long(d, ANX, covs, valid=v5), pv_for(ANX, v5)),
        "hartmann_2026_climate_commitment":
            (long(d, COMMIT, covs, valid=v5), pv_for(COMMIT, v5)),
        "hartmann_2026_pro_climate_intention":
            (long(d, INTENT, covs, valid=v5), pv_for(INTENT, v5)),
    })


if __name__ == "__main__":
    main()
