#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254074
# DOI: 10.1371/journal.pone.0254074
# S1 File (XLSX, sheet "Nurses Data") -- COVID-19 mental well-being study of
# 171 nurses in Kenya. Responses were exported as text category labels
# rather than numeric codes; each block below is re-coded to the standard
# 0-based (or 1-based, for ISI) integer scale of its instrument. Five
# instruments in the file, each written as its own scale file:
#   PHQ-9 (9 items, 0-3), GAD-7 (7 items, 0-3), ISI (7 items, item-specific
#   anchors, re-coded 0-4), IES-R (22 items, 0-4), SPFI (16 items across
#   3 subscales, re-coded 0/1-6 per the source True/False-style anchors
#   used here -> collapsed to a common 0-4 numeric code per anchor set).
# The row above the header (row index 0 in the raw sheet) carries the
# instrument name as a banner; the real column headers are on row index 1.

import os
import io

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0254074.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FREQ_MAP = {  # PHQ-9 / GAD-7 style
    "Not at all": 0,
    "Several days": 1,
    "More than half the days": 2,
    "Nearly every day": 3,
}

# ISI: each item has its own anchor wording; observed categories per item
# (see automated review) mapped onto a common 0-4 ordinal severity code.
ISI_MAPS = {
    30: {"Mild": 1, "Moderate": 2, "Severe": 3, "Very Severe": 4},
    31: {"Mild": 1, "Moderate": 2, "Severe": 3},
    32: {"Mild": 1, "Moderate": 2, "Severe": 3, "Very Severe": 4},
    33: {"Very Satisfied": 0, "Satisfied": 1, "Moderately Satisfied": 2,
         "Dissatisfied": 3, "Very Dissatisfied": 4},
    34: {"Not at all Noticable": 0, "Alittle": 1, "Somewhat": 2, "Much": 3},
    35: {"Not Worried at all": 0, "Alittle": 1, "Somewhat": 2, "Much": 3,
         "Very Much Worried": 4},
    36: {"Not at all Interfering": 0, "Alittle": 1, "Somewhat": 2,
         "Much": 3, "Very Much Interfering": 4},
}

IESR_MAP = {
    "Not at all": 0, "A little bit": 1, "Moderately": 2,
    "Quite a bit": 3, "Extremely": 4,
}

# SPFI mixes two anchor families across its 16 items (professional
# fulfillment items a-f use a "True" agreement scale; exhaustion /
# disengagement items use a frequency scale). Map each family separately.
# Raw category text confirmed directly from the source file: the "True"
# family has exactly 5 categories (no "Very Little" -- that belongs only
# to the freq family), and the freq family's second-lowest category is
# literally "Very Little", not "A little bit" -- an earlier version of
# this map used "A little bit", which never matched anything in the raw
# data, silently dropping every genuine "Very Little" response as NaN
# (that's why resp=1 never appeared in the shipped output).
SPFI_TRUE_MAP = {
    "Not at all True": 0, "Somewhat True": 1,
    "Moderately True": 2, "Very True": 3, "Completely True": 4,
}
SPFI_FREQ_MAP = {
    "Not at all": 0, "Very Little": 1, "Moderately": 2, "A lot": 3,
    "Extremely": 4,
}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return io.BytesIO(r.content)


def load_raw():
    buf = fetch()
    raw = pd.read_excel(buf, sheet_name="Nurses Data", header=None)
    data = raw.iloc[2:].reset_index(drop=True)
    return data


def build(data, col_idx, value_maps, item_prefix, out_name, cov):
    """col_idx: list of column indices (0-based) for this scale.
    value_maps: single dict (applied to all cols) or dict {col_idx: dict}.
    """
    n = len(data)
    ids = pd.Series(range(1, n + 1), name="id")

    frames = []
    for i, c in enumerate(col_idx):
        vmap = value_maps[c] if isinstance(value_maps, dict) and c in value_maps else value_maps
        resp = data[c].map(vmap)
        frames.append(pd.DataFrame({
            "id": ids,
            "item": f"{item_prefix}{i+1}",
            "resp": resp,
        }))
    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = pd.to_numeric(long["resp"])

    for cname, cidx in cov.items():
        m = dict(zip(ids, data[cidx]))
        long[cname] = long["id"].map(m)

    out_cols = ["id", "item", "resp"] + list(cov.keys())
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_dir_abs = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir_abs, exist_ok=True)
    out_path = os.path.join(out_dir_abs, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    data = load_raw()
    cov = {"cov_age_cat": 1, "cov_gender": 2}

    build(data, list(range(13, 22)), FREQ_MAP, "phq9_",
          "ali_2021_phq9.csv", cov)
    build(data, list(range(22, 29)), FREQ_MAP, "gad7_",
          "ali_2021_gad7.csv", cov)
    build(data, list(range(30, 37)), ISI_MAPS, "isi_",
          "ali_2021_isi.csv", cov)
    build(data, list(range(37, 59)), IESR_MAP, "iesr_",
          "ali_2021_iesr.csv", cov)

    # SPFI: cols 59-64 (professional fulfillment, "true" anchors),
    # 65-68 (work exhaustion, freq anchors), 69-74 (interpersonal
    # disengagement, freq anchors)
    spfi_maps = {}
    for c in range(59, 65):
        spfi_maps[c] = SPFI_TRUE_MAP
    for c in range(65, 75):
        spfi_maps[c] = SPFI_FREQ_MAP
    build(data, list(range(59, 75)), spfi_maps, "spfi_",
          "ali_2021_spfi.csv", cov)


if __name__ == "__main__":
    convert()
