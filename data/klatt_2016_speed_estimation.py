#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0159455
# DOI: 10.1371/journal.pone.0159455
# Supporting Information: https://doi.org/10.1371/journal.pone.0159455.s001
#
# "Putting Up a Big Front" -- speed estimation task. Participants verbally
# estimated the speed (km/h) of 8 different cars approaching at 3 target
# speeds (45/50/55 km/h) from 2 road positions (trottoir=sidewalk,
# insel=traffic island), i.e. 48 trials/items per participant. Each item
# name encodes its own true target speed (e.g. "@44898_nis_45_trottoir"
# was driven at 45 km/h), so `resp` is the signed estimation error
# (participant's verbal estimate minus the true target speed), not the raw
# estimate -- this ties the response to what the study actually measures
# (over/under-estimation of an approaching car's speed) while keeping the
# same ordinal direction-within-item property a raw estimate would have
# (higher resp = greater perceived-vs-actual overestimation). The separate
# road-crossing behavior columns in the same file (los_/ank_/
# DauerUeberqueren_* and their Mw_ means) are per-condition aggregates over
# repeated trials, not raw single-observation responses, and are not
# shipped here (see datastandard.md's "Verifying a continuous-looking
# column is actually a raw response").

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0159455.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = Path("/tmp/0159455_s001.sav")
    tmp.write_bytes(r.content)
    df, _meta = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    return df


def convert():
    df = fetch_data()
    df = df.rename(columns={"Vp": "id"})
    assert df["id"].nunique() == len(df)

    item_cols = [c for c in df.columns if c.startswith("@")]

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # each item name is "@<car_id>_<car_code>_<true_speed>_<position>"
    true_speed = long["item"].str.extract(r"_(\d+)_(?:trottoir|insel)$")[0]
    true_speed = pd.to_numeric(true_speed, errors="coerce")
    assert true_speed.notna().all(), "could not parse true speed from every item name"
    long["resp"] = long["resp"] - true_speed

    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "klatt_2016_speed_estimation.csv", index=False)
    print(f"klatt_2016_speed_estimation.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
