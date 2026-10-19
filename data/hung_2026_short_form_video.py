#!/usr/bin/env python3

# Source: https://zenodo.org/records/19784064
# DOI: 10.5281/zenodo.19784064 (dataset; the record names no published paper)
#   Hung (2026). The Relationship Between Self-Control and Problematic Short-Form Video
#   Use: The Mediating Roles of Boredom Proneness and Trait-State Fear of Missing Out
#   [Dataset]. Zenodo.
# Data: "wave4(582).sav": 582 Chinese students. The file name says wave 4, but only one
#       wave is deposited, so there is no wave column to ship -- a single occasion.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. Both label levels checked and English stems are present for
#   every item, so extraction is solved -- but every instrument here is a named
#   third-party measure with no quotable grant, which the 2026-10-15 silence ruling
#   holds: the FoMO scale (TFoMO/SFoMO), a Brief Self-Control-style scale (IS/ES/Im/Re)
#   and a problematic-use scale whose own stem names social media (PSVU, "How often
#   during the last year have you spent a lot of time thinking about social media...").
#
# Five tables, all 1-7, one per instrument:
#   hung_2026_fomo            7 items: TFoMO1-4 trait, SFoMO6/7/9 state.
#   hung_2026_self_control    5 items: IS1R/2R/3/5R/6R (inhibitory self-control; the R
#                             suffix is the deposit's own wording-direction marker).
#   hung_2026_sensation_seek  3 items: ES10-12.
#   hung_2026_impulsivity     3 items: Im1R/2R/5R.
#   hung_2026_restraint       3 items: Re7-9.
#   hung_2026_problematic_video 6 items: PSVU1-6.
# Not shipped: TFoMOmean, SFoMOmean, FoMOmean, ISmean, ESmean, BPmean, Immean, Remean,
#   SCmean, PSVUmean -- depositor means.
# Covariates: cov_age, cov_gender, cov_grade (the deposit spells it "grace").
# id: the deposit's "number" (582 distinct over 582 rows).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_19784064"
FNAME = "wave4\uff08582\uff09.sav"
FOMO = ["TFoMO1", "TFoMO2", "TFoMO3", "TFoMO4", "SFoMO6", "SFoMO7", "SFoMO9"]
IS = ["IS1R", "IS2R", "IS3", "IS5R", "IS6R"]
ES = ["ES10", "ES11", "ES12"]
IM = ["Im1R", "Im2R", "Im5R"]
RE = ["Re7", "Re8", "Re9"]
PSVU = [f"PSVU{i}" for i in range(1, 7)]
COVS = {"age": "cov_age", "gender": "cov_gender", "grace": "cov_grade"}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(19784064, FNAME, RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 582, len(d)
    means = [c for c in d.columns if str(c).endswith("mean")]
    assert len(means) == 10, means
    books(list(d.columns), {
        "shipped": FOMO + IS + ES + IM + RE + PSVU,
        "covariate": list(COVS),
        "respondent id": ["number"],
        "mean computed by the depositor": means,
    })
    d = d.rename(columns={"number": "id", **COVS})
    assert d["id"].nunique() == len(d)
    covs = list(COVS.values())
    v = range(1, 8)
    emit({
        "hung_2026_fomo": (long(d, FOMO, covs, valid=v), pv_for(FOMO, v)),
        "hung_2026_self_control": (long(d, IS, covs, valid=v), pv_for(IS, v)),
        "hung_2026_sensation_seek": (long(d, ES, covs, valid=v), pv_for(ES, v)),
        "hung_2026_impulsivity": (long(d, IM, covs, valid=v), pv_for(IM, v)),
        "hung_2026_restraint": (long(d, RE, covs, valid=v), pv_for(RE, v)),
        "hung_2026_problematic_video": (long(d, PSVU, covs, valid=v), pv_for(PSVU, v)),
    })


if __name__ == "__main__":
    main()
