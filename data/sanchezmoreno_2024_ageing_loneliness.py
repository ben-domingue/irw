#!/usr/bin/env python3

# Source: https://zenodo.org/records/14200089
# DOI: 10.5281/zenodo.14200089 (dataset)
#   Sanchez-Moreno, E. (2024). Dataset corresponding to the project "Aging,
#   loneliness, and well-being in Spain" [Dataset]. Zenodo.
# Data: "Data_PID2020-115993RB-I00.sav": 887 older adults in Spain. The deposit also
#       ships the same data as a .csv; the .sav is read because it is the copy that
#       carries the labels, and the .csv's Soledad columns disagree with it on range.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped, though the Spanish stems ARE in hand -- both label levels are
#   populated (variable labels give every stem, value labels give the anchors), so this
#   is a rights hold and not a gap, and either table ships immediately on a ruling.
#   - The 6 Soledad items are recognisably the De Jong Gierveld Loneliness Scale, a
#     NAMED third-party instrument, and the 2026-10-15 ruling is that silence on a
#     named third-party instrument no longer ships.
#   - The 42 social-support items could not be tied to a named instrument at all: the
#     deposit names none, and a 6-questions x 7-relationship-targets battery of this
#     shape matches several published schedules. Since it cannot be established as
#     author-developed, it is held on the same conservative reading rather than
#     shipped on an assumption.
#
# Two tables, because the two instruments have different response scales:
#   sanchezmoreno_2024_social_support  42 items, 1-5. The SAME six questions asked
#     about seven relationship targets, which is what the codes encode: B1 partner,
#     B2 sons, B3 daughters, B4 grandchildren, B5 siblings, B6 neighbours, B7 friends;
#     the suffix .4-.9 is the question within each target. Structural missingness is
#     expected and large (only 384 of 887 answer the partner block at all), because a
#     target block is only asked of respondents who have that relationship.
#   sanchezmoreno_2024_loneliness       6 items, 1-3.
# resp 9 ("No sabe / No contesta") is the deposit's missing code on every item of both
# instruments and is dropped.
#
# Not shipped: VAR00001 and VAR00002, section-header columns labelled "LONELINESS" and
#   "SOCIAL SUPPORT" that hold no data at all (0 non-null of 887).
# Covariates: cov_sex, cov_age, cov_living_arrangement, cov_children,
#   cov_education, cov_health_activity_limitation (the deposit's GALI).
# id: the deposit carries no respondent identifier, so id is the row index (1-887).
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
    """Every source column is either shipped or skipped for a printed reason."""
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_14200089"
TARGETS = {1: "partner", 2: "sons", 3: "daughters", 4: "grandchildren",
           5: "siblings", 6: "neighbours", 7: "friends"}
SUPPORT = [f"B{b}.{i}" for b in range(1, 8) for i in range(4, 10)]
LONELY = [f"Soledad{i}" for i in range(1, 7)]
HEADERS = ["VAR00001", "VAR00002"]
COVS = {"Sex": "cov_sex", "Age": "cov_age", "Living": "cov_living_arrangement",
        "Children": "cov_children", "Education": "cov_education",
        "GALI": "cov_health_activity_limitation"}
MISSING_CODE = 9


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(
        zenodo_fetch(14200089, "Data_PID2020-115993RB-I00.sav", RAW_DIR),
        apply_value_formats=False)
    assert len(d) == 887, len(d)
    for c in HEADERS:
        assert d[c].notna().sum() == 0, (c, d[c].notna().sum())
    books(list(d.columns), {
        "shipped": SUPPORT + LONELY,
        "covariate": list(COVS),
        "section header, no data": HEADERS,
    })
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    for c in SUPPORT + LONELY:
        d[c] = d[c].replace(MISSING_CODE, pd.NA)
    covs = list(COVS.values())
    v5, v3 = range(1, 6), range(1, 4)
    emit({
        "sanchezmoreno_2024_social_support":
            (long(d, SUPPORT, covs, valid=v5), pv_for(SUPPORT, v5)),
        "sanchezmoreno_2024_loneliness":
            (long(d, LONELY, covs, valid=v3), pv_for(LONELY, v3)),
    })


if __name__ == "__main__":
    main()
