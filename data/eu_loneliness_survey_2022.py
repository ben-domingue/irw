#!/usr/bin/env python3
# Source: EU Loneliness Survey (EU-LS), European Commission Joint Research Centre
#   Catalogue record: https://data.jrc.ec.europa.eu/dataset/82e60986-9987-4610-ab4a-84f0f5a9193b
#   DOI: 10.2905/jrc.v4vt8t8
#   Data files (CC BY 4.0, open) are hosted on the EC research-data repository:
#     EU27 sample  https://research-data.ec.europa.eu/records/bgjhy-y9v23
#     EU4 sample   https://research-data.ec.europa.eu/records/pt03a-3rq48
#   Questionnaires: records 4y0zp-dje28 (EU27) and bmnwr-gde76 (EU4).
#   Methodological report: https://publications.jrc.ec.europa.eu/repository/handle/JRC139563
#
# Fielded Nov-Dec 2022. Two cross-sectional samples, no overlap of persons:
#   eu27 - non-probability online panel, all 27 member states, 25,646 respondents aged 16+
#   eu4  - probability-based online panels in FR, IT, PL, SE, 4,029 respondents aged 16+
# Both files number persons 1..n independently, so ids are prefixed with the sample name.
# The sample is carried as cov_sample; survey weights as cov_w_country (both samples)
# and cov_w_eu27 (EU27 sample only, NaN for eu4).
#
# One file per scale (all codes taken from the shipped *_labels.csv):
#   euls_2022_djg            De Jong Gierveld 6-item loneliness scale, 1 Yes / 2 More or less / 3 No
#   euls_2022_ucla           UCLA 3-item loneliness scale, 1 Hardly ever or never / 2 Some of the time / 3 Often
#   euls_2022_social_support 4 items, 1 None of the time .. 5 All of the time
#   euls_2022_feelings       7 affect items (happy, angry, nervous, hopeless, restless, depressed,
#                            worthless), 1 Always .. 6 Never; EU4 sample lacks happy and angry
#   euls_2022_work           3 workplace loneliness items (employed respondents), 1 Always .. 5 Never
#   euls_2022_education      3 loneliness-in-education items (respondents in education), 1 Always .. 5 Never
#   euls_2022_civic          3 civic-attitude items, 1 Not at all .. 10 Perfectly
# Response direction is as administered (not harmonised across scales): on DJG, UCLA and the
# feelings items a HIGHER code means LESS of the named feeling for some items and MORE for others
# (DJG a-c are emotional-loneliness items worded negatively, d-f social items worded positively).
# Non-response codes dropped: 997 Not applicable, 998 Don't know, 999 Prefer not to say.
# Excluded: risk_a-c (an undocumented code 11 sits next to the 1-10 scale), the single-item
# loneliness_direct, the social-media, intervention, experiment and health modules, and
# date_birth_* / income / anthropometric columns.

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
CACHE = REPO_ROOT / "data" / "eu_loneliness_survey_2022_raw"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

API = "https://research-data.ec.europa.eu/api/records/{rec}/files/{name}/content"
SAMPLES = {
    "eu27": ("bgjhy-y9v23", "EU-Loneliness-Survey_Data_EU27_sample.zip", "id_pers"),
    "eu4":  ("pt03a-3rq48", "EU-Loneliness-Survey_Data_EU4_sample.zip", "id"),
}

NONRESP = {997, 998, 999}

SCALES = {
    "djg":            ([f"loneliness_djg_{k}" for k in "abcdef"], (1, 3)),
    "ucla":           ([f"loneliness_ucla_{k}" for k in "abc"], (1, 3)),
    "social_support": ([f"social_support_{k}" for k in "abcd"], (1, 5)),
    "feelings":       ([f"feelings_{k}" for k in ("happy", "angry", "nerv", "hopel",
                                                 "restl", "depr", "worthl")], (1, 6)),
    "work":           ([f"loneliness_work_{k}" for k in "abc"], (1, 5)),
    "education":      ([f"loneliness_education_{k}" for k in "abc"], (1, 5)),
    "civic":          ([f"civic_attitudes_{k}" for k in "abc"], (1, 10)),
}

# categorical covariates: carry the shipped label text; "Prefer not to say"/"Don't know" -> NaN
COV_LABELLED = {
    "country": "cov_country",
    "gender": "cov_gender",
    "education": "cov_education",
    "relationship": "cov_relationship",
    "work_status": "cov_work_status",
    "health_general": "cov_health_general",
    "municipality_type": "cov_municipality_type",
}
COV_NUMERIC = {"age": "cov_age", "w_country": "cov_w_country", "w_eu27": "cov_w_eu27"}
# EU27 labels are truncated at 80 characters; replace the two long ones. work_status codes
# 1-8 are identical in both samples; education is NOT (EU4 codes it on ISCED 0-8 and ships
# its own short labels, which are kept as is)
LABEL_FIX = {
    "education": {1: "Not completed primary", 2: "Completed primary", 3: "Completed secondary",
                  4: "Post-secondary vocational or bachelor", 5: "Master or doctoral"},
    "work_status": {1: "In paid work", 2: "In education", 3: "Unemployed, looking for a job",
                    4: "Unemployed, not looking", 5: "Permanently sick or disabled", 6: "Retired",
                    7: "Doing housework or caring", 8: "Other"},
}
NONRESP_LABELS = ("Prefer not", "Don’t know", "Don't know")
COV_COLS = ["cov_sample"] + list(COV_LABELLED.values()) + list(COV_NUMERIC.values())


def fetch(sample: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rec, name, _ = SAMPLES[sample]
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / name
    if not local.exists():
        r = requests.get(API.format(rec=rec, name=name), headers=UA, timeout=300)
        r.raise_for_status()
        local.write_bytes(r.content)
    z = zipfile.ZipFile(local)
    vals = next(n for n in z.namelist() if n.endswith("_values.csv"))
    labs = next(n for n in z.namelist() if n.endswith("_labels.csv"))
    return (pd.read_csv(io.BytesIO(z.read(vals)), low_memory=False),
            pd.read_csv(io.BytesIO(z.read(labs)), low_memory=False))


def load_sample(sample: str) -> pd.DataFrame:
    vals, labs = fetch(sample)
    idcol = SAMPLES[sample][2]
    assert vals[idcol].nunique() == len(vals)
    out = pd.DataFrame({"id": sample + "_" + vals[idcol].astype(str)})
    out["cov_sample"] = sample
    for src, dst in COV_LABELLED.items():
        lab = labs[src].astype("string")
        if src in LABEL_FIX and (sample == "eu27" or src == "work_status"):
            lab = vals[src].map(LABEL_FIX[src]).astype("string")
        lab = lab.mask(vals[src].isin(NONRESP) | lab.str.startswith(NONRESP_LABELS, na=False))
        out[dst] = lab
    for src, dst in COV_NUMERIC.items():
        col = pd.to_numeric(vals[src], errors="coerce") if src in vals else pd.Series(float("nan"), index=vals.index)
        out[dst] = col.mask(col.isin(NONRESP))
    for items, _ in SCALES.values():
        for it in items:
            out[it] = pd.to_numeric(vals[it], errors="coerce") if it in vals else float("nan")
    return out


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wide = pd.concat([load_sample("eu27"), load_sample("eu4")], ignore_index=True)
    assert wide["id"].nunique() == len(wide)
    for scale, (items, (lo, hi)) in SCALES.items():
        long = wide.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                         var_name="item", value_name="resp")
        long = long[long["resp"].between(lo, hi)].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + COV_COLS].reset_index(drop=True)
        fn = f"euls_2022_{scale}.csv"
        pv = {it: set(range(lo, hi + 1)) for it in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (fn, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:160]}")
        long.to_csv(OUT_DIR / fn, index=False)
        per_item = long.groupby("item")["resp"].agg(["min", "max", "count"])
        print(f"{fn}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()} rows={len(long)}")
        print(per_item.to_string())


if __name__ == "__main__":
    convert()
