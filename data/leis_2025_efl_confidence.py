#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZCKGGC
# DOI: 10.7910/DVN/ZCKGGC (dataset; the record names no paper -- the file name points to
#   RELC Journal -- and none was found; not the same data as leis_2025_english_motivation,
#   which is DVN/25QUO9, 379 Indian high-school students)
#   Leis, Adrian (2025). Confidence and Motivation in University EFL Classrooms.
#   Harvard Dataverse.
# Data: "RELC_intrinsic and confidence.xlsx" (format=original): one sheet laid out for
#       reading -- row 1 holds the question text (bilingual English/Japanese for the
#       background questions, Japanese only for the motivation items), followed by 177
#       Japanese university students, a blank row and two summary rows (Av, SD). Columns:
#       gender, age, nationality, a stay-abroad question, major (free text), four
#       self-ratings of English skill (speaking, listening, reading, writing), then four
#       motivation blocks of three items, each block followed by Av./SD and an average
#       column: Intrinsic (alpha .923), Identified (.839), Introjected (.884), Extrinsic
#       (.874). Responses run 0-5.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The header row carries every Japanese motivation stem and the
#   bilingual self-rating questions (cheap at the header level; xlsx, no value labels),
#   but the 0-5 anchors are not in the deposit and the English for the motivation items
#   would be IRW's.
#
# Item codes: <block>_<k>, k = position within the block (1-3), the block from the
#   header above it (Intrinsic, Identified, Introjected, Extrinsic); self-rating items
#   speaking/listening/reading/writing. The stems are printed by the script.
# Tables (0-5 as stored):
#   leis_2025_efl_intrinsic    intrinsic_1-3    } the four regulation types of the
#   leis_2025_efl_identified   identified_1-3   } self-determination continuum, three
#   leis_2025_efl_introjected  introjected_1-3  } items each ("I study English because
#   leis_2025_efl_extrinsic    extrinsic_1-3    } ...")
#   leis_2025_efl_skill_rating speaking, listening, reading, writing ("How good do you
#                              think your English <skill> is?")
# Skipped: the stay-abroad question (blank for all but one), major (free text),
#   nationality (all Japanese), the average columns and the Av./SD rows.
# Covariates: cov_gender (as written), cov_age.
# id: row index of the respondent rows.

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_zckggc"
FNAME = "RELC_intrinsic and confidence.xlsx"
P = "leis_2025_efl_"
BLOCKS = {"Intrinsic": 10, "Identified": 16, "Introjected": 22, "Extrinsic": 28}
SKILLS = {5: "speaking", 6: "listening", 7: "reading", 8: "writing"}


def main() -> None:
    raw = pd.read_excel(dv_fetch("10.7910/DVN/ZCKGGC", FNAME, RAW_DIR), header=None)
    assert raw.shape == (182, 33)
    head = raw.iloc[1]
    body = raw.iloc[2:].copy()
    body = body[body[2] == "Japanese"]  # drops the blank and Av/SD rows
    assert len(body) == 177 and body[0].isin(["Female", "Male", float("nan")]).all()
    assert body[0].isna().sum() == 2  # two respondents left gender blank
    d = pd.DataFrame({"id": range(1, len(body) + 1), "cov_gender": body[0].values,
                      "cov_age": body[1].astype(int).values})
    tables = {}
    for blk, c0 in BLOCKS.items():
        assert str(raw.iloc[0, c0]).startswith(blk)
        assert str(raw.iloc[1, c0 + 4]).startswith(blk + " Average")
        its = []
        for k in range(3):
            code = f"{blk.lower()}_{k + 1}"
            d[code] = pd.to_numeric(body[c0 + k]).values
            print(f"  {code}: {head[c0 + k]}")
            its.append(code)
        tables[blk.lower()] = its
        avg = pd.to_numeric(body[c0 + 4]).values
        assert (abs(d[its].mean(axis=1).values - avg) < 1e-9).all(), blk
    for c, skill in SKILLS.items():
        assert skill in str(head[c]).lower()
        d[skill] = pd.to_numeric(body[c]).values
    tables["skill_rating"] = list(SKILLS.values())
    covs = ["cov_gender", "cov_age"]
    out = {P + suf: (long(d, its, covs, valid=range(0, 6)), {i: set(range(6)) for i in its})
           for suf, its in tables.items()}
    emit(out)


if __name__ == "__main__":
    main()
