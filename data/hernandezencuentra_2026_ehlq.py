#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/31150441
# DOI: 10.6084/m9.figshare.31150441
#   Hernández Encuentra, E., Bas Sarmiento, P., Fernández Gutiérrez, M., &
#   González Caballero, J. L. (2026). Digital health literacy among the
#   Spanish population [Dataset]. figshare.
# Data: "Data_ESP _todas_Variables.xlsx", sheet "Datos" -- 400 respondents to
#   an online panel survey of the Spanish population, administered in Spanish,
#   in two fielding waves (300 + 100).
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped, though the deposit carries it in full. The
#   "variables" sheet gives the complete Spanish stem for all 35 eHLQ items
#   and all 10 eHEALS items, and the "etiquetas" sheet the value labels, so
#   extraction is solved. Held because both instruments are published
#   third-party scales with no row in
#   itemtext/instrument_rights_register.csv -- the eHealth Literacy
#   Questionnaire (eHLQ, Kayser et al. 2018; 35 items in 7 domains, which is
#   exactly this file's P5A-P5D block and its Domain1-7 composites) and eHEALS
#   (Norman & Skinner 2006). Under the 2026-10-15 silence rule that is a hold.
#   Shipping it would also need an IRW English translation, which owes a
#   translation_source and an issues-page callout.
#
# THE eHEALS BLOCK SHIPS THE DEPOSIT'S OWN RECODE, NOT THE RAW COLUMNS. P08_1
#   to P08_10 are stored 0-4 and the P08_*_R copies 1-5; the recode is exactly
#   +1 for 400 of 400 rows on every one of the ten items, and the deposit's
#   eHEALS composite equals the sum of P08_3_R..P08_10_R for 400 of 400 rows.
#   So 1-5 is the administered scale, the eight scored items are P08_3-P08_10,
#   and the item codes keep the source's numbering.
#   P08_1 and P08_2 are the two preliminary eHEALS questions (the internet is
#   useful / important for my health). They are not part of the 8-item scale
#   and are not a table on their own, so they are dropped with this reason.
#
# TWO tables, 400 respondents:
#   hernandezencuentra_2026_ehlq      35 items, 1-4 (P5A_1..P5D_35)
#   hernandezencuentra_2026_eheals     8 items, 1-5 (P08_3..P08_10)
# id: the 0-based row index. The deposit's respid is an online-panel
#   participant id; under the 2026-09-20 narrowing it is replaced by the row
#   index, never a hash.
# Covariates: cov_gender, cov_age, cov_age_band, cov_province,
#   cov_municipality_size, cov_region, cov_tech_consumer,
#   cov_self_rated_health, cov_education, cov_education_completed,
#   cov_employment, cov_ses, cov_sample_wave, cov_completion_time_s.
#   The last is the survey's own "duration" (0D-00:06:32) in seconds -- a
#   whole-survey completion time, so a named covariate and never `rt`, which
#   is per-item only.
# Dropped: the 7 eHLQ domain means, Total_F1-7, the eHEALS composite, the raw
#   0-4 P08 columns, the recoded socioeconomic/technology copies
#   (ISO_full, ISO_short, ISO_kg_R, tecnol_R), the merge bookkeeping
#   (_merge, _NMiss) and one unnamed trailing column of 12 stray values.
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "31150441" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME, SHEET = 31150441, "Data_ESP _todas_Variables.xlsx", "Datos"

EHLQ = ([f"P5A_{i}" for i in range(1, 11)]
        + [f"P5B_{i}" for i in range(11, 21)]
        + [f"P5C_{i}" for i in range(21, 29)]
        + [f"P5D_{i}" for i in range(29, 36)])
EHEALS = [f"P08_{i}_R" for i in range(3, 11)]
COVS = {
    "P01.Género": "cov_gender",
    "P02. Edad": "cov_age",
    "RANGOSEDAD": "cov_age_band",
    "PROVINCIA": "cov_province",
    "P03. Rango número habitantes.": "cov_municipality_size",
    "CCAA": "cov_region",
    "P6 autocategorización uso tecnologia": "cov_tech_consumer",
    "P7 salud percibida": "cov_self_rated_health",
    "P9": "cov_education",
    "S01A": "cov_education_completed",
    "S02A": "cov_employment",
    "ISO_kg": "cov_ses",
    "onada": "cov_sample_wave",
}
DROPPED = (["respid", "eHEALS", "ISO_full", "ISO_short", "ISO_kg_R",
            "tecnol_R", "_merge", "_NMiss", "Unnamed: 91",
            "P08_1_R", "P08_2_R"]
           + [f"P08_{i}" for i in range(1, 11)]
           + [f"Domain{i}meanscore" for i in range(1, 8)]
           + [f"Total_F{i}" for i in range(1, 8)]
           )


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def dur_seconds(s: str):
    m = re.fullmatch(r"(\d+)D-(\d{2}):(\d{2}):(\d{2})", str(s).strip())
    if not m:
        return pd.NA
    d, h, mi, sec = (int(x) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + sec


def main():
    df = pd.read_excel(fetch(), sheet_name=SHEET)

    # The recode the eHEALS block ships under, proved rather than assumed.
    for i in range(1, 11):
        assert (df[f"P08_{i}_R"] == df[f"P08_{i}"] + 1).all(), i
    assert (df[EHEALS].sum(axis=1) == df["eHEALS"]).all(), \
        "the deposit's eHEALS composite is not the sum of P08_3_R..P08_10_R"

    known = set(EHLQ) | set(EHEALS) | set(COVS) | set(DROPPED) | {"duration"}
    for c in known:
        assert c in df.columns, f"expected source column {c} is absent"
    unaccounted = [c for c in df.columns if c not in known]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, derived or administrative ({len(DROPPED)} columns): "
          f"{DROPPED}")

    df = df.rename(columns=COVS)
    df["cov_completion_time_s"] = df["duration"].map(dur_seconds).astype("Int64")
    cov_cols = [*COVS.values(), "cov_completion_time_s"]
    for cov in COVS.values():
        v = pd.to_numeric(df[cov])
        df[cov] = v.astype("Int64") if (v.dropna() % 1 == 0).all() else v
    df.insert(0, "id", range(len(df)))

    tables = {
        "hernandezencuentra_2026_ehlq": (EHLQ, set(range(1, 5)), None),
        "hernandezencuentra_2026_eheals": (
            EHEALS, set(range(1, 6)), lambda c: c.replace("_R", "")),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, (cols, scale, recode) in tables.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp")
             .dropna(subset=["resp"]))
        if recode:
            t["item"] = t["item"].map(recode)
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the documented scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
