#!/usr/bin/env python3

# Source: https://zenodo.org/records/18639119
# DOI: 10.5281/zenodo.18639119 (dataset; the record names no published paper)
#   Hu, Hui-Ling (2026). Shu wei you min gong zuo xing fu gan [Digital nomad work
#   wellbeing] [Dataset]. Zenodo.
# Data: "Cao Qi 1020.xlsx" (the deposit spells the filename in Chinese), single sheet:
#       539 respondents. Two response widths are deposited at the item level.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The workbook carries bare codes with no header row of stems, no
#   SPSS labels and no codebook, and the record links no paper, so the wording is not
#   reachable from the deposit. The survey was administered in Chinese.
#
# Two tables:
#   hu_2026_digital_nomad_wellbeing  58 items, 1-7. Thirteen labelled blocks of one
#     agreement-scale questionnaire, kept in one file (the reading ruled for the small
#     PLS-SEM blocks of jo_2023 / diredja_2025, irw#2940): TE (6), PD (4), SD (5),
#     PR (10), JD (5), LOC (6), TSOL (3), TSIV (3), TSC (1), TSCX (2), BC (4), SWB (5),
#     OSI (4). The block names are the deposit's own and are not expanded here, because
#     nothing in the deposit says what they stand for.
#   hu_2026_psqi  12 items, 0-3 -- the Pittsburgh Sleep Quality Index items the deposit
#     carries raw: B1-B9 (PSQI question 5a-5i) and PSQID7, PSQID8, PSQIE9 (questions 7-9).
# Not shipped:
#   PSQIB, PSQID, PSQIA2, PSQIA4, PSQIA4A2, PSQI, SQ -- PSQI component and total scores
#     (three of them fractional, which is what gives them away).
#   PSQIC -- a 0-3 column whose code matches neither the B1-B9 nor the PSQID7/8/E9
#     pattern, so whether it is a raw item or a component cannot be told from the deposit.
#     Excluded rather than guessed at.
# resp cleaning: B1 carries a single 7 among 538 values in 0-3. The out-of-range value is
#   isolated to one item and one respondent, which is the signature of a data-entry slip
#   rather than a wider coding scheme, so that one cell is blanked.
# Covariates: cov_gender, cov_education, cov_age_band, cov_work_hours_band (all banded
#   codes as deposited), cov_completion_time_s (the deposit's restime -- a whole-survey
#   duration, so a named covariate and never `rt`, which is per-item only).
# id: row index of the sheet.
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


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
    return p


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
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
    """Melt `items` to long, drop missing, check integer codes inside `valid`, order columns.
    `rename` maps a source column to the `item` code it ships under (default: the column name)."""
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_18639119"
FNAME = "\u66f9\u6dc71020.xlsx"
SEVEN = {"TE": 6, "PD": 4, "SD": 5, "PR": 10, "JD": 5, "LOC": 6,
         "TSOL": 3, "TSIV": 3, "BC": 4, "SWB": 5, "OSI": 4}
PSQI = [f"B{i}" for i in range(1, 10)] + ["PSQID7", "PSQID8", "PSQIE9"]
COVS = {"gender": "cov_gender", "edu": "cov_education", "age": "cov_age_band",
        "workhour": "cov_work_hours_band", "restime": "cov_completion_time_s"}


def main() -> None:
    d = pd.read_excel(zenodo_fetch(18639119, FNAME, RAW_DIR))
    assert len(d) == 539, len(d)
    src = list(d.columns)
    seven = [f"{p}{i}" for p, n in SEVEN.items() for i in range(1, n + 1)]
    seven += ["TSC1", "TSCX2", "TSCX3"]
    assert len(seven) == 58 and all(c in src for c in seven), len(seven)
    books(src, {
        "shipped": seven + PSQI,
        "covariate": list(COVS),
        "PSQI component or total score":
            ["PSQIB", "PSQID", "PSQIA2", "PSQIA4", "PSQIA4A2", "PSQI", "SQ"],
        "unresolvable PSQI code -- raw item or component cannot be told apart": ["PSQIC"],
    })
    n_bad = int((~d["B1"].isin(range(0, 4))).sum())
    assert n_bad == 1, n_bad
    print(f"    [B1] blanked {n_bad} out-of-range value(s): "
          f"{sorted(d.loc[~d['B1'].isin(range(0, 4)), 'B1'].unique())}")
    d.loc[~d["B1"].isin(range(0, 4)), "B1"] = None
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["id"] = range(1, len(d) + 1)
    emit({
        "hu_2026_digital_nomad_wellbeing":
            (long(d, seven, covs, valid=range(1, 8)), pv_for(seven, range(1, 8))),
        "hu_2026_psqi":
            (long(d, PSQI, covs, valid=range(0, 4)), pv_for(PSQI, range(0, 4))),
    })


if __name__ == "__main__":
    main()
