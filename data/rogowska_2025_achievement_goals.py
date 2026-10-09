#!/usr/bin/env python3
# Source: https://doi.org/10.17632/86pvx7pkx4.1
# DOI: 10.17632/86pvx7pkx4.1 (dataset; the record names no paper)
#   Rogowska, Aleksandra; Gabriel, Marta (2025). Achievement goals and performance anxiety
#   in musicians and athletes [Data set]. Mendeley Data, V1.
# Data: DataBase.xlsx, sheet "Data": 210 adults (107 musicians, 103 athletes;
#       an online survey; the record does not name the country) x ID, Gender, Age, Group, AGQ1-AGQ18 (Achievement Goal
#       Questionnaire for Sport, 3x2 model), six AGQ subscale sums, CSAI1-CSAI14
#       (Competitive State Anxiety Inventory-2 Revised) and three CSAI subscale scores.
#       Sheet "Description" names each column ("Achievement Goal Questionnaire, item 01").
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped. The Description sheet labels items only by instrument and
#   number; no wording or anchors are in the deposit.
#
# Subscale membership is recovered from the deposit's own composites and asserted below:
#   each AGQ subscale column equals the sum of three items, and each CSAI score is a
#   fixed multiple of an item sum (self-confidence = sum of 4 items; somatic and
#   cognitive = 2 x the sum of 5 items, the CSAI-2R x10/items rescaling).
# Tables (as stored; item = the deposit's column name):
#   rogowska_2025_agq_task_app    AGQ1, AGQ7, AGQ14   task-approach      } 1-7
#   rogowska_2025_agq_task_av     AGQ6, AGQ9, AGQ13   task-avoidance     }
#   rogowska_2025_agq_self_app    AGQ12, AGQ17, AGQ18 self-approach      }
#   rogowska_2025_agq_self_av     AGQ4, AGQ8, AGQ15   self-avoidance     }
#   rogowska_2025_agq_other_app   AGQ5, AGQ10, AGQ16  other-approach     }
#   rogowska_2025_agq_other_av    AGQ2, AGQ3, AGQ11   other-avoidance    }
#   rogowska_2025_csai_somatic    CSAI1, 4, 6, 9, 12  somatic anxiety    } 1-4
#   rogowska_2025_csai_cognitive  CSAI2, 5, 8, 11, 14 cognitive anxiety  }
#   rogowska_2025_csai_confidence CSAI3, 7, 10, 13    self-confidence    }
#   (The CSAI-2R has 17 items; the deposit has 14.)
# Skipped: the six AGQ sums and three CSAI scores.
# Covariates: cov_gender (Women / Men), cov_age, cov_group (Musician / Athlete).
# id: the deposit's ID (unique, 1-210).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.17632_86pvx7pkx4"
P = "rogowska_2025_"
AGQ = {"agq_task_app": ("AGQ TAP", [1, 7, 14]), "agq_task_av": ("AGQ TAV", [6, 9, 13]),
       "agq_self_app": ("AGQ SAP", [12, 17, 18]), "agq_self_av": ("AGQ SAV", [4, 8, 15]),
       "agq_other_app": ("AGQ OAP", [5, 10, 16]), "agq_other_av": ("AGQ OAV", [2, 3, 11])}
CSAI = {"csai_somatic": ("CSAI som", [1, 4, 6, 9, 12], 2),
        "csai_cognitive": ("CSAI cog", [2, 5, 8, 11, 14], 2),
        "csai_confidence": ("CSAI self", [3, 7, 10, 13], 1)}
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Group": "cov_group"}


def fetch() -> Path:
    p = RAW_DIR / "DataBase.xlsx"
    if not p.exists():
        j = requests.get("https://data.mendeley.com/public-api/datasets/86pvx7pkx4/files"
                         "?folder_id=root&version=1", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j if f["filename"] == "DataBase.xlsx"][0]
        download(url, p)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), "Data")
    d.columns = [c.strip() for c in d.columns]
    assert d.shape == (210, 45) and d["ID"].is_unique
    tables = {}
    for suf, (comp, nums) in AGQ.items():
        its = [f"AGQ{n}" for n in nums]
        assert (d[its].sum(axis=1) == d[comp]).all(), suf
        tables[suf] = (its, range(1, 8))
    for suf, (comp, nums, k) in CSAI.items():
        its = [f"CSAI{n}" for n in nums]
        assert (k * d[its].sum(axis=1) == d[comp]).all(), suf
        tables[suf] = (its, range(1, 5))
    used = {c for its, _ in tables.values() for c in its}
    comps = [v[0] for v in AGQ.values()] + [v[0] for v in CSAI.values()]
    assert used | set(comps) | set(COVS) | {"ID"} == set(d.columns)
    d["id"] = d["ID"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {P + suf: (long(d, its, covs, valid=valid), {i: set(valid) for i in its})
           for suf, (its, valid) in tables.items()}
    emit(out)


if __name__ == "__main__":
    main()
