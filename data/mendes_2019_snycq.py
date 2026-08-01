#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/VMJ6NV
# DOI: 10.7910/DVN/VMJ6NV
# License: CC0 1.0 (dataset-level "additional/modified terms and conditions"
# clause in Dataverse's termsOfUse field is boilerplate text with nothing
# appended after it -- no actual restriction is stated).

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://dataverse.harvard.edu/api/access/datafile/3322520"  # SNYCQ.tsv
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DIMENSIONS = ["positive", "negative", "future", "past", "myself", "people",
              "surrpundings", "vigilance", "images", "words", "intrusive"]

# "specific" and "vague" are the same single bipolar item (specificity of
# thought content) -- different administration blocks in the source file
# label it with different poles. Canonicalized to "specific_vague" here.
ITEM_PATTERN = re.compile(
    r"^SNYCQ_(?P<wave>.+)_(?P<dim>" + "|".join(DIMENSIONS) + r"|specific|vague)$")

# Chronological order of administration is inferred from the file's own
# naming (pre precedes post; run-01 precedes run-02) and documented, not
# verified against the source paper's task-order description -- the
# relative order of the two post-scan tasks (ETS/CPTS) and of the AP/PA
# phase-encoding runs is a best-effort assumption.
WAVE_ORDER = {
    "pre-ses-02": 1,
    "post-ses-02-run-01-acq-AP": 2,
    "post-ses-02-run-01-acq-PA": 3,
    "post-ses-02-run-02-acq-AP": 4,
    "post-ses-02-run-02-acq-PA": 5,
    "post-ses-02-task-ETS": 6,
    "post-ses-02-task-CPTS": 7,
}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    raw_path = os.path.join(OUT_DIR, "_mendes_2019_raw.tsv")
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_csv(raw_path, sep="\t")
    os.remove(raw_path)

    # The source file has a stray duplicate "participant_id" column
    # (mostly empty); drop it and keep the real one.
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.rename(columns={"participant_id": "id"})
    assert df["id"].nunique() == len(df)

    value_cols = [c for c in df.columns if c.startswith("SNYCQ_")]
    records = []
    for c in value_cols:
        m = ITEM_PATTERN.match(c)
        assert m, f"unrecognized column: {c!r}"
        wave_label, dim = m.group("wave"), m.group("dim")
        item = "specific_vague" if dim in ("specific", "vague") else dim
        wave = WAVE_ORDER[wave_label]
        sub = df[["id", c]].rename(columns={c: "resp"})
        sub["item"] = item
        sub["wave"] = wave
        records.append(sub)

    long = pd.concat(records, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # A single isolated value (103.947) out of 14289 exceeds the 0-100 VAS
    # bound -- a data-entry error, not a real scale point.
    long = long[(long["resp"] >= 0) & (long["resp"] <= 100)].reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"]
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    out_name = "mendes_2019_snycq"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.1f}-{long['resp'].max():.1f}")


if __name__ == "__main__":
    convert()
