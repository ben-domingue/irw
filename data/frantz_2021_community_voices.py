#!/usr/bin/env python3
# Source: https://zenodo.org/records/5171463
# DOI: 10.5061/dryad.np5hqbzs4 (data, mirrored on Zenodo 5171463); paper: Frantz, Petersen & Lucaites
#   (2021), "Novel approach to delivering pro-environmental messages significantly shifts norms and
#   motivation, but children are not more effective spokespeople than adults".
# Data: Study1_Data.sav (875 US adults, MTurk), Study2_Data.sav (511), Study3_Data.sav (426; Oberlin +
#       MTurk), all after a "Community Voices" slide-show manipulation. Shared blocks: Concern_1-14
#       (environmental concern, 1-5), Commit_k (commitment to pro-environmental actions, 1-5; Study 1
#       has 10 items coded 1/3/6/7/8 for the five anchors -> recoded 1-5; Study 2's 13 items carry
#       only 1/2/4/5 with mismatched value labels and are NOT shipped; Study 3 has 13 items 1-5),
#       Norms_1-19 (efficacy/responsibility/optimism/youth and adult norms, 1-5; Studies 2-3 omit
#       items 11 and 17), CNS_1-5 (Connectedness to Nature, 1-5), Empathy_1-3 (Studies 2-3, 1-5) and,
#       Study 1 only, mood1_1-9 / Mood2_1-9 (nine mood adjectives on a 0-100 slider before and after
#       the slide show). The *_r reversed copies, means and Timing/Con columns are not shipped.
#       Messaging_survey_items_operational_definitions_reliabilities.docx documents the items.
# License: CC0 1.0 (Zenodo / Dryad).
#
# Item text: shipped for concern, commitment, norms, cns and empathy (.sav variable labels = stems,
#   value labels = anchors; Study 1's five-point labels read Disagree / Agree where Studies 2-3 read
#   Slightly Disagree / Slightly Agree -- the Study 1 wording is shipped, the difference is noted).
#   Built by automated_finding/itemtext_verification/make_itemtext_frantz_2021.py. mood: not shipped
#   (0-100 slider, one-word adjective labels).
#
# Tables (cov_study 1/2/3; ids offset 0 / 1000 / 2000): frantz_2021_env_concern (14),
#   frantz_2021_env_commitment (13; Studies 1 and 3), frantz_2021_env_norms (19), frantz_2021_cns (5),
#   frantz_2021_empathy (3; Studies 2-3), frantz_2021_mood (Study 1, 9 x wave 1-2, 0-100).
# Covariates: cov_study, cov_condition (study-specific label), cov_gender (1 male, 2 female, 3 other),
#   cov_age, cov_education (1-8), cov_political_affiliation (1 Dem, 2 Ind, 3 Rep, 4 other),
#   cov_political_orientation (1 liberal - 7 conservative).
# id: row index within study + offset.
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


def mendeley_fetch(dataset: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://data.mendeley.com/public-api/datasets/{dataset}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"] if f["filename"] == fname][0]
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

import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "zn_5171463"
FILES = {1: "Study1_Data.sav", 2: "Study2_Data.sav", 3: "Study3_Data.sav"}
CONCERN = [f"Concern_{i}" for i in range(1, 15)]
COMMIT = [f"Commit_{i}" for i in range(1, 14)]
NORMS = [f"Norms_{i}" for i in range(1, 20)]
CNS = [f"CNS_{i}" for i in range(1, 6)]
EMP = [f"Empathy_{i}" for i in range(1, 4)]
MOOD = [f"mood_{i}" for i in range(1, 10)]
COVS = ["cov_study", "cov_condition", "cov_gender", "cov_age", "cov_education",
        "cov_political_affiliation", "cov_political_orientation"]
S1_COMMIT = {1: 1, 3: 2, 6: 3, 7: 4, 8: 5}


def read(study: int):
    return pyreadstat.read_sav(str(zenodo_fetch(5171463, FILES[study], RAW_DIR)))


def labels(study: int = 1):
    _, meta = pyreadstat.read_sav(str(zenodo_fetch(5171463, FILES[study], RAW_DIR)), metadataonly=True)
    return meta.column_names_to_labels, meta.variable_value_labels


def prep(study: int) -> pd.DataFrame:
    d, meta = read(study)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1 + (study - 1) * 1000
    d["cov_study"] = study
    if study == 1:
        d["cov_condition"] = d["condition"].map(meta.variable_value_labels["condition"])
        for c in [f"Commit_{i}" for i in range(1, 11)]:
            assert set(d[c].dropna().unique()) <= set(S1_COMMIT), c
            d[c] = d[c].map(S1_COMMIT)
    elif study == 2:
        d["cov_condition"] = d["Condition"].map(meta.variable_value_labels["Condition"])
        d = d.drop(columns=COMMIT)  # 1/2/4/5 coding with mismatched labels: not shipped
    else:
        d["cov_condition"] = d["Source"].map(meta.variable_value_labels["Source"]).fillna("") + "/" + \
            d["Locality"].map(meta.variable_value_labels["Locality"]).fillna("")
    d["cov_gender"] = d["Gender"].astype("Int64")
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_education"] = d["Education"].astype("Int64")
    d["cov_political_affiliation"] = d["Political"].astype("Int64")
    d["cov_political_orientation"] = d["PoliScale"].astype("Int64")
    return d


def main() -> None:
    ds = {s: prep(s) for s in (1, 2, 3)}
    assert [len(ds[s]) for s in (1, 2, 3)] == [875, 511, 426]

    def stack(items, studies, valid):
        parts = []
        for s in studies:
            cols = [c for c in items if c in ds[s].columns]
            parts.append(long(ds[s], cols, COVS, valid=valid))
        return pd.concat(parts, ignore_index=True)

    concern = stack(CONCERN, (1, 2, 3), range(1, 6))
    commit = stack(COMMIT, (1, 3), range(1, 6))
    norms = stack(NORMS, (1, 2, 3), range(1, 6))
    cns = stack(CNS, (1, 2, 3), range(1, 6))
    emp = stack(EMP, (2, 3), range(1, 6))
    d1 = ds[1]
    parts = []
    for w, pre in [(1, "mood1_"), (2, "Mood2_")]:
        cols = [f"{pre}{i}" for i in range(1, 10)]
        dd = d1[["id", *COVS, *cols]].copy()
        dd["wave"] = w
        t = dd.melt(id_vars=["id", "wave", *COVS], value_vars=cols, var_name="item", value_name="resp").dropna(subset=["resp"])
        t["item"] = t["item"].map({c: f"mood_{i}" for i, c in enumerate(cols, 1)})
        parts.append(t)
    mood = pd.concat(parts, ignore_index=True)[["id", "item", "resp", "wave", *COVS]]
    assert mood["resp"].between(0, 100).all()
    mood = mood.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    emit({"frantz_2021_env_concern": (concern, pv_for(CONCERN, range(1, 6))),
          "frantz_2021_env_commitment": (commit, pv_for(COMMIT, range(1, 6))),
          "frantz_2021_env_norms": (norms, pv_for(NORMS, range(1, 6))),
          "frantz_2021_cns": (cns, pv_for(CNS, range(1, 6))),
          "frantz_2021_empathy": (emp, pv_for(EMP, range(1, 6))),
          "frantz_2021_mood": (mood, None)})


if __name__ == "__main__":
    main()
