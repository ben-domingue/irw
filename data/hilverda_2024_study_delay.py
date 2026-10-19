#!/usr/bin/env python3

# Source: https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/8HOMVS
# DOI: 10.34894/8HOMVS
#   Hilverda, F., Vollmann, M., & Scheepers, R. A. (2024). Study delay during
#   emergency remote teaching among students at Dutch universities: The role
#   of education satisfaction and academic wellbeing [Dataset]. DataverseNL.
# Data: "study_delay_during_ERT_dataset_N=680.sav" -- 680 students at Dutch
#   universities, measured at three points during the 2020-21 remote-teaching
#   year (t1 September 2020, t2 January 2021, t3 May 2021).
# License: CC BY 4.0 (verified on the DataverseNL record, 2026-10-19).
# Item text: NOT shipped. The deposit's codebook PDF names each column
#   ("t1 academic burnout (exhaustion) item 1") but carries no stem and no
#   response anchors, so the wording is in the published scales, not here.
#   Both the label level and the codebook were checked.
#
# TWO tables, each three waves of the same items for the same 680 students --
#   which is what `wave` is for:
#   hilverda_2024_burnout      5 items x 3 waves, 0-6
#   hilverda_2024_engagement   3 items x 3 waves, 0-6
#   Items are named bo1-bo5 and eng1-eng3: the wave is in the `wave` column,
#   not in the item name, so the same item links across waves.
#
# The scale ships as the 0-6 the deposit records. The codebook gives the
#   response format only as "Scale"; 0-6 is what is in the data for all eight
#   items at all three waves, and no value outside it occurs.
#
# NOT SHIPPED: the deposit's own block means (t1_bo, t1_eng, ... and the
#   t123_* grand means), the ERT percentage columns and their recodes, and
#   t*_sat_e (education satisfaction, one global 0-10 item per wave -- a
#   single item is not a table, and a wave-varying value is not a covariate).
#   t3_delay, the study's outcome, is a single administrative 0/1 flag.
#
# id: the deposit's own `id` (1-680, unique), kept so the waves link.
# Covariates: cov_age, cov_university, cov_study_year, cov_phase,
#   cov_study_field, cov_gender, cov_migration_background,
#   cov_first_generation, cov_living_situation -- all time-invariant, as the
#   deposit's own codes. cov_gender is its three-category version, not the
#   binary recode.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "8homvs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 500940, "study_delay_during_ERT_dataset_N=680.sav"
WAVES = (1, 2, 3)
SCALE = set(range(0, 7))
COVS = {"t1_age": "cov_age", "t1_uni": "cov_university",
        "t1_year": "cov_study_year", "t1_phase": "cov_phase",
        "t1_field": "cov_study_field", "t1_gen": "cov_gender",
        "t1_migr": "cov_migration_background",
        "t1_1stgen": "cov_first_generation",
        "t1_living": "cov_living_situation"}
TABLES = {"hilverda_2024_burnout": ("bo", 5),
          "hilverda_2024_engagement": ("eng", 3)}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.nl/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 680, len(df)
    assert df["id"].is_unique

    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (prefix, n) in TABLES.items():
        frames = []
        for w in WAVES:
            cols = [f"t{w}_{prefix}{i}" for i in range(1, n + 1)]
            missing = [c for c in cols if c not in df.columns]
            assert not missing, (name, w, missing)
            for c in cols:   # the label names the construct and the wave
                lab = (labels.get(c) or "").lower()
                assert lab.startswith(f"t{w} academic"), (c, lab)
            part = (df[["id", *cov_cols, *cols]]
                    .melt(id_vars=["id", *cov_cols], value_vars=cols,
                          var_name="item", value_name="resp")
                    .dropna(subset=["resp"]))
            part["item"] = part["item"].str.replace(f"t{w}_", "", regex=False)
            part["wave"] = w
            frames.append(part)
        t = pd.concat(frames, ignore_index=True)
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the recorded 0-6 scale: {bad}"
        t = t[["id", "item", "resp", "wave", *cov_cols]]
        assert not t.duplicated(["id", "item", "wave"]).any(), name
        assert t["item"].nunique() == n and set(t["wave"]) == set(WAVES)
        assert t["id"].nunique() == 680
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} waves={t['wave'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
