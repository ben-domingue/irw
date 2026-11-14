#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/7yh3n7n824/1
# DOI: 10.17632/7yh3n7n824.1 (data)
#   Keskin O (2026). Antalya Soundscape Anonymized Survey Dataset [Data set]. Mendeley Data, V1.
# License: CC BY 4.0 (Mendeley Data)
# Data: Antalya_Soundscape_Anonymized_dataset.csv, 492 in-situ responses at seven coastal stops in
#   Antalya, Turkiye (daytime and evening); ISO 12913-2 perceived affective quality ratings and the
#   perceived dominance of seven sound sources, all 1-5 (observed; the record describes the ISO
#   framework). One row = one respondent; id = row order.
# Tables (item = the deposit's column name):
#   keskin_2026_antalya_paq           -- PAQ_Pleasant, _Calm, _Uneventful, _Monotonous, _Annoying,
#                                        _Chaotic, _Vibrant, _Eventful
#   keskin_2026_antalya_sound_sources -- Sound_Traffic, _Human, _Nature, _Water, _Music,
#                                        _Construction, _Animal_Bird
# Covariates: cov_stop (Stop_ID), cov_time_period.
# Not shipped: Overall_Pleasantness / Overall_Eventfulness (the ISO projections, derived) and
#   Overall_Satisfaction (single item).
# Item text: not shipped -- attribute names only; the questionnaire is described in the deposit's
#   Readme, not reproduced item by item.
import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/7yh3n7n824/files/"
       "316400b0-92f4-44e1-9333-ffe5364f8b0d/file_downloaded")
TABLES = {"keskin_2026_antalya_paq": ["PAQ_Pleasant", "PAQ_Calm", "PAQ_Uneventful", "PAQ_Monotonous", "PAQ_Annoying",
                                      "PAQ_Chaotic", "PAQ_Vibrant", "PAQ_Eventful"],
          "keskin_2026_antalya_sound_sources": ["Sound_Traffic", "Sound_Human", "Sound_Nature", "Sound_Water",
                                                "Sound_Music", "Sound_Construction", "Sound_Animal_Bird"]}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':
        c = requests.get(json.loads(c)["url"], timeout=120).content
    d = pd.read_csv(io.BytesIO(c))
    assert len(d) == 492
    d["id"] = range(1, len(d) + 1)
    d["cov_stop"] = d["Stop_ID"]
    d["cov_time_period"] = d["Time_Period"]
    covs = ["cov_stop", "cov_time_period"]
    for name, items in TABLES.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin([1, 2, 3, 4, 5]).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
