#!/usr/bin/env python3

# Source: https://zenodo.org/records/20110159
# DOI: 10.5281/zenodo.20110159 (dataset; the record names no published paper)
#   Hung (2026). Parental Emotional Warmth and Subjective Happiness Among University
#   Students: A Sequential Mediation Model of Adaptive Perfectionism and the Two
#   Dimensions of Grit [Dataset]. Zenodo.
# Data: "Paternal.sav" (523) and "Maternal.sav" (553). These are NOT two samples: 512
#       of the ids appear in BOTH files, so they are two views of one study -- the
#       father-report and mother-report versions of the warmth block, with the other
#       instruments repeated verbatim in each file. The files are therefore MERGED on
#       the deposit's own id, and each repeated block is taken ONCE. Stacking them
#       instead would have shipped 512 respondents twice.
# License: CC BY 4.0 (Zenodo record).
#
# One block is NOT shipped because the deposit contradicts itself about it. For the 512
# ids present in both files, Order*, POE*, COI*, SH*, gender, Age and NOC are
# byte-identical between the two -- but HS5/HS8/HS10/HS15 DISAGREE on 323, 360, 417 and
# 379 of those 512 respondents respectively. The same item code therefore carries two
# different responses for the same person and nothing in the deposit says which is
# correct, so the HS block is dropped rather than shipped on a coin flip. Its wording
# ("My best just never seems to be good enough for me") is an adaptive-perfectionism
# discrepancy item, not the happiness scale the code suggests, which is a second reason
# to leave it for a human.
#
# Item text: NOT shipped, though English stems are present for every item at the
#   variable-label level (checked; value labels carry the anchors). The three shipped
#   instruments are all named third-party measures: POE/COI is the Grit scale (register
#   verdict BLOCK on both the 12-item and Grit-S rows), Order* is the Order subscale of
#   the Almost Perfect Scale-Revised and SH1-3 the Subjective Happiness Scale, neither
#   of which carries a quotable grant -- so the 2026-10-15 silence ruling holds them.
#   The warmth items ("My parents praised me") are an EMBU-style parental-rearing
#   measure, also unidentifiable to a grantor. Extraction is solved for all of them.
#
# Four tables:
#   hung_2026_parental_warmth  14 items, 1-6: Fwarmth1-7 (father) and Mwarmth1-7
#     (mother) -- the same seven questions about two targets, so fourteen items.
#   hung_2026_perfectionism_order  4 items, 1-7 (Order1, Order2, Order4, Order6).
#   hung_2026_grit_parental       12 items, 1-7: POE1/4/6/9/10/12 and the six
#     reverse-worded COI*R. The R suffix is the deposit's own and marks the wording
#     direction, not a recode -- every column holds the raw 1-7 response.
#   hung_2026_subjective_happiness 3 items, 1-7 (SH1-SH3).
# Not shipped: FwarmthMean, MwarmthMean, APMean, POEmean/POEMean, COIMeanR, SHMean1 --
#   depositor means -- and SDRsum, a social-desirability sum score.
# Covariates: cov_gender, cov_age, cov_n_children_in_family (NOC),
#   cov_father_education (FEL) and cov_mother_education (MEL), each taken from the file
#   that carries it.
# id: the deposit's own serial number, which is unique within and consistent across the
#   two files (that is what let them be merged).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_20110159"
SERIAL = "\u5e8f\u865f"          # the deposit's id column, Chinese for "serial no."
FW = [f"Fwarmth{i}" for i in range(1, 8)]
MW = [f"Mwarmth{i}" for i in range(1, 8)]
ORDER = ["Order1", "Order2", "Order4", "Order6"]
HS = ["HS5", "HS8", "HS10", "HS15"]
GRIT = [f"POE{i}" for i in (1, 4, 6, 9, 10, 12)] + \
       [f"COI{i}R" for i in (2, 3, 5, 7, 8, 11)]
SH = ["SH1", "SH2", "SH3"]
SHARED = ORDER + GRIT + SH


def main() -> None:
    import pyreadstat
    pat, _ = pyreadstat.read_sav(zenodo_fetch(20110159, "Paternal.sav", RAW_DIR),
                                 apply_value_formats=False)
    mat, _ = pyreadstat.read_sav(zenodo_fetch(20110159, "Maternal.sav", RAW_DIR),
                                 apply_value_formats=False)
    assert (len(pat), len(mat)) == (523, 553), (len(pat), len(mat))
    for d in (pat, mat):
        assert d[SERIAL].nunique() == len(d)
    pmeans = ["FwarmthMean", "APMean", "POEmean", "COIMeanR", "SHMean1", "SDRsum"]
    mmeans = ["MwarmthMean", "APMean", "POEMean", "COIMeanR", "SHMean1", "SDRsum"]
    books(list(pat.columns), {
        "shipped": FW + SHARED, "covariate": ["gender", "Age", "NOC", "FEL"],
        "respondent id": [SERIAL],
        "dropped: the two files disagree on this block": HS,
        "mean or sum computed by the depositor": pmeans,
    })
    books(list(mat.columns), {
        "shipped": MW + SHARED, "covariate": ["gender", "Age", "NOC", "MEL"],
        "respondent id": [SERIAL],
        "dropped: the two files disagree on this block": HS,
        "mean or sum computed by the depositor": mmeans,
    })

    # The deposit contradicts itself on HS; prove that here rather than only in prose.
    pi = pat.set_index(SERIAL)
    mi = mat.set_index(SERIAL)
    common = sorted(set(pi.index) & set(mi.index))
    assert len(common) == 512, len(common)
    for c in SHARED:
        x, y = pi.loc[common, c], mi.loc[common, c]
        bad = int(((x != y) & ~(x.isna() & y.isna())).sum())
        assert bad == 0, (c, bad)
    for c in HS:
        x, y = pi.loc[common, c], mi.loc[common, c]
        bad = int(((x != y) & ~(x.isna() & y.isna())).sum())
        assert bad > 0, c
        print(f"    [dropped] {c}: the two files disagree for {bad} of "
              f"{len(common)} shared respondents")

    # Merge: shared blocks once (from Paternal, proven identical), warmth from each.
    base = pi[SHARED + ["gender", "Age", "NOC", "FEL"]].copy()
    extra = mi.loc[[i for i in mi.index if i not in pi.index],
                   SHARED + ["gender", "Age", "NOC"]].copy()
    extra["FEL"] = pd.NA
    d = pd.concat([base, extra])
    d["MEL"] = mi["MEL"].reindex(d.index)
    for c in FW:
        d[c] = pi[c].reindex(d.index)
    for c in MW:
        d[c] = mi[c].reindex(d.index)
    d = d.reset_index().rename(columns={
        SERIAL: "id", "gender": "cov_gender", "Age": "cov_age",
        "NOC": "cov_n_children_in_family", "FEL": "cov_father_education",
        "MEL": "cov_mother_education"})
    assert d["id"].nunique() == len(d) == 564, (d["id"].nunique(), len(d))
    covs = ["cov_gender", "cov_age", "cov_n_children_in_family",
            "cov_father_education", "cov_mother_education"]
    v6, v7 = range(1, 7), range(1, 8)
    emit({
        "hung_2026_parental_warmth": (long(d, FW + MW, covs, valid=v6),
                                      pv_for(FW + MW, v6)),
        "hung_2026_perfectionism_order": (long(d, ORDER, covs, valid=v7),
                                          pv_for(ORDER, v7)),
        "hung_2026_grit_parental": (long(d, GRIT, covs, valid=v7), pv_for(GRIT, v7)),
        "hung_2026_subjective_happiness": (long(d, SH, covs, valid=v7), pv_for(SH, v7)),
    })


if __name__ == "__main__":
    main()
