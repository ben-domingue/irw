"""Climate Anxiety and Psychological Resilience scales, Turkish samples.

Source: Atik, Servet (2026), Zenodo 10.5281/zenodo.18601426, CC BY 4.0.
Two files, `EFA.sav` (606 respondents) and `CFA.sav` (323), each carrying the
same 24 items on a 1-5 scale plus four demographic columns.

Two instruments, so two tables:

  atik_2026_climate_anxiety      CI1-CI12
  atik_2026_psych_resilience     GI1-GI12

Each pools both samples into one table with `cov_sample`, per the
same-instrument rule: identical item set, identical response format, two
administrations of one study. Ids are offset so the CFA sample's ids continue
past the EFA sample's maximum rather than colliding with it.

The two files name the same items differently -- `EFA.sav` uses the Turkish
initials `CIK`/`GIK` while `CFA.sav` uses `CI`/`GI`. The item *positions* are
identical (12 and 12, same order, same 1-5 scale), so the EFA names are mapped
onto the CFA names. Without that the pooled table would carry 48 item codes
for a 24-item pair of instruments.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 18601426
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {"atik_2026_climate_anxiety": "CI",
          "atik_2026_psych_resilience": "GI"}
COVARIATES = {
    "DD1.Cinsiyetiniz": "cov_gender",
    "DD2düzeyiniz": "cov_education",
    "DD3.Günlükİnternetkullanımsüreniz": "cov_daily_internet_use",
    "DD4.Güniçerisindeçoğunluklakullandığınızsosyalmedyaarac": "cov_main_social_media",
}


def fetch_raw(out_dir=None):
    """Return {stem: path} for the two .sav files."""
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    paths = {}
    for f in rec["files"]:
        if not f["key"].lower().endswith(".sav"):
            continue
        local = os.path.join(out_dir or "/tmp", f["key"])
        if not os.path.exists(local):
            r = requests.get(f["links"]["self"], timeout=600)
            r.raise_for_status()
            with open(local, "wb") as fh:
                fh.write(r.content)
        paths[os.path.splitext(f["key"])[0].upper()] = local
    return paths


def read_sav(p):
    try:
        return pyreadstat.read_sav(p, apply_value_formats=False)[0]
    except Exception:
        return pyreadstat.read_sav(p, apply_value_formats=False,
                                   encoding="latin1")[0]


def canonical(col):
    """EFA's Turkish item names -> the CFA names used as the canonical codes."""
    m = re.match(r"^(CİK|GİK|CI|GI)(\d+)$", str(col))
    if not m:
        return None
    prefix = {"CİK": "CI", "GİK": "GI"}.get(m.group(1), m.group(1))
    return f"{prefix}{m.group(2)}"


def main(paths=None):
    paths = paths or fetch_raw()
    frames = []
    id_offset = 0
    for sample in ("EFA", "CFA"):
        df = read_sav(paths[sample])
        rename = {c: canonical(c) for c in df.columns if canonical(c)}
        assert len(rename) == 24, f"{sample}: expected 24 items, got {len(rename)}"
        df = df.rename(columns={**rename, **COVARIATES})
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1 + id_offset
        id_offset = int(df["id"].max())
        df["cov_sample"] = sample
        frames.append(df)

    covs = list(COVARIATES.values()) + ["cov_sample"]
    os.makedirs(OUT_DIR, exist_ok=True)
    for table, prefix in SCALES.items():
        parts = []
        for df in frames:
            cols = [c for c in df.columns if re.match(rf"^{prefix}\d+$", str(c))]
            assert len(cols) == 12, f"{table}: expected 12 items, found {len(cols)}"
            parts.append(df.melt(id_vars=["id"] + covs, value_vars=cols,
                                 var_name="item", value_name="resp"))
        long = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == 12, table
        assert long["resp"].between(1, 5).all(), f"{table}: expected 1-5"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
