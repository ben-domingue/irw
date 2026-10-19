#!/usr/bin/env python3

# Source: https://zenodo.org/records/21494885
# DOI: 10.5281/zenodo.21494885 (dataset; the record names no published paper)
#   Oner, B. (2026). Enjoyment and Boredom in Physical Education: The Mediating Role
#   of Motivation in the Relationship Between Basic Psychological Need Satisfaction
#   and Affective Outcomes [Dataset]. Zenodo.
# Data: "bpns.sav": 617 schoolchildren (ages 10-14). Four instruments at the item
#       level on two response formats, so four tables.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. Both label levels checked: VALUE labels are present on the
#   items and give the anchors, but the VARIABLE labels are empty throughout, so the
#   deposit carries anchors without stems -- the option-only shape ruled out in
#   irw#1770. Two of these instruments would be blocked anyway even with stems in
#   hand: the c*/r*/a* block is a basic-psychological-need-satisfaction measure, and
#   the CSDT library (BPNS/BPNSFS) is a register block of full scope. Which BPNS this
#   is cannot be settled from the file, because resolving the CSDT-BPNS vs BNSSS
#   collision requires the item CONTENT, and there is none here -- so the question is
#   moot for item text and recorded rather than guessed.
#
# Four tables (the deposit's own code prefixes):
#   oner_2026_pe_enjoyment   4 items, enj1-4, 1-5.
#   oner_2026_pe_boredom     4 items, bor1-4, 1-5.
#   oner_2026_pe_motivation  9 items, 1-5: im1-3 intrinsic, em1-3 extrinsic,
#                            am1-3 amotivation -- one instrument, three subscales.
#   oner_2026_basic_needs   12 items, 1-7: c1-4 competence, r1-4 relatedness,
#                            a1-4 autonomy -- one instrument, three subscales.
# Not shipped: enj_n, bor_n, intr_n, extr_n, amot_n, c_n, r_n, a_n, bpn_n -- subscale
#   and scale means computed by the depositor (all fractional).
# Covariates: cov_age, cov_gender, cov_grade.
# id: the deposit carries no respondent identifier, so id is the row index (1-617).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_21494885"
ENJ = [f"enj{i}" for i in range(1, 5)]
BOR = [f"bor{i}" for i in range(1, 5)]
MOT = [f"{p}{i}" for i in range(1, 4) for p in ("im", "em", "am")]
NEEDS = [f"{p}{i}" for i in range(1, 5) for p in ("c", "r", "a")]
MEANS = ["enj_n", "bor_n", "intr_n", "extr_n", "amot_n", "c_n", "r_n", "a_n", "bpn_n"]
COVS = {"AGE": "cov_age", "GENDER": "cov_gender", "GRADE": "cov_grade"}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(21494885, "bpns.sav", RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 617, len(d)
    assert not any((meta.column_names_to_labels or {}).get(c) for c in d.columns), \
        "variable labels appeared; the item-text verdict in the header needs redoing"
    books(list(d.columns), {
        "shipped": ENJ + BOR + MOT + NEEDS,
        "covariate": list(COVS),
        "subscale or scale mean computed by the depositor": MEANS,
    })
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    covs = list(COVS.values())
    v5, v7 = range(1, 6), range(1, 8)
    emit({
        "oner_2026_pe_enjoyment": (long(d, ENJ, covs, valid=v5), pv_for(ENJ, v5)),
        "oner_2026_pe_boredom": (long(d, BOR, covs, valid=v5), pv_for(BOR, v5)),
        "oner_2026_pe_motivation": (long(d, MOT, covs, valid=v5), pv_for(MOT, v5)),
        "oner_2026_basic_needs": (long(d, NEEDS, covs, valid=v7), pv_for(NEEDS, v7)),
    })


if __name__ == "__main__":
    main()
