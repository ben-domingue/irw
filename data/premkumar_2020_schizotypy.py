#!/usr/bin/env python3

# Source: https://zenodo.org/records/3956134
# DOI: 10.5281/zenodo.3956134 (dataset)
#   Premkumar, Preethi; Kuipers, Elizabeth; Kumari, Veena (2020). The path from schizotypy
#   to depression and aggression and the role of family stress [Dataset]. Zenodo.
#   Paper: Premkumar, P., Kuipers, E., & Kumari, V. (2020). European Psychiatry.
# Data: "Schizotypy, depression, aggression and perceived EE - data sharing.sav": 104
#       participants, four published instruments deposited at the item level.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for all four tables (English, from the SPSS variable labels, which
#   carry the full stem for all 192 items). Checked both label levels: the variable labels
#   hold the stems; the file carries no value labels, so the response-option wording comes
#   from each instrument's published anchors as the paper names them, and is recorded as
#   canonical_instrument in the provenance for the anchors while the stems are
#   study_materials.
#
# Four tables, one per instrument, each with its own response width:
#   premkumar_2020_lee      38 items, 1-4 -- Level of Expressed Emotion.
#   premkumar_2020_olife   104 items, 0/1 -- Oxford-Liverpool Inventory of Feelings and
#                          Experiences.
#   premkumar_2020_bpaq     29 items, 1-7 -- Buss-Perry Aggression Questionnaire.
#   premkumar_2020_dass21   21 items, 0-3 -- Depression Anxiety Stress Scales-21.
# Not shipped: every *_R / *R column (the depositor's reverse-scored copy of an item
#   already shipped in its raw direction), the subscale and total scores, the behavioural
#   task Arousal/Relevance medians, and PCS.
# Covariates: cov_age, cov_gender, cov_marital_status, cov_ethnicity. Age_birthyear is
#   dropped as redundant with age_current -- one age measure is enough and the year adds
#   nothing the age does not.
# id: row index of the file. "participant_order" is not unique -- values 14 and 16 each
#   appear twice over 104 rows -- so it cannot serve as the person key.
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_3956134"
FNAME = "Schizotypy, depression, aggression and perceived EE - data sharing.sav"
LEE = [f"LEE{i:02d}" for i in range(1, 39)]
OLIFE = [f"OLIFE{i:03d}" for i in range(1, 105)]
BPAQ = [f"Buss{i:02d}" for i in range(1, 30)]
DASS = [f"DASS{i:02d}" for i in range(1, 22)]
COVS = {"age_current": "cov_age", "Gender": "cov_gender",
        "Maritalstatus": "cov_marital_status", "Ethnicity": "cov_ethnicity"}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(3956134, FNAME, RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 104, len(d)
    src = list(d.columns)
    rev = [c for c in src if c.endswith(("_R", "R")) and c.startswith(
        ("LEE", "OLIFE", "Buss")) and c not in LEE + OLIFE + BPAQ]
    totals = ["OLIFE_UE", "OLIFE_CD", "OLIFE_AN", "OLIFE_IN", "OLIFE_TOT",
              "BP_Phys_Agg", "BP_Verb_Agg", "BP_Anger", "BPHostility",
              "DASS_depression", "DASS_anxiety", "DASS_stress",
              "LEE_LES", "LEE_Intrusiveness", "LEE_Irritability", "LEE_Criticism"]
    task = [c for c in src if c.startswith(("Arousal_", "Relevance_"))]
    books(src, {
        "shipped": LEE + OLIFE + BPAQ + DASS,
        "covariate": list(COVS),
        "non-unique participant_order, superseded by the row index": ["participant_order"],
        "redundant with cov_age": ["Age_birthyear"],
        "depositor's reverse-scored copy of an item already shipped raw": rev,
        "subscale or total score": totals + ["PCS"],
        "behavioural task rating medians, not item responses": task,
        "sample-membership flags": ["behav_data", "both_parts"],
    })
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["id"] = range(1, len(d) + 1)
    emit({
        "premkumar_2020_lee": (long(d, LEE, covs, valid=range(1, 5)),
                               pv_for(LEE, range(1, 5))),
        "premkumar_2020_olife": (long(d, OLIFE, covs, valid=range(0, 2)),
                                 pv_for(OLIFE, range(0, 2))),
        "premkumar_2020_bpaq": (long(d, BPAQ, covs, valid=range(1, 8)),
                                pv_for(BPAQ, range(1, 8))),
        "premkumar_2020_dass21": (long(d, DASS, covs, valid=range(0, 4)),
                                  pv_for(DASS, range(0, 4))),
    })


if __name__ == "__main__":
    main()
