#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0202277
# DOI: 10.1371/journal.pone.0202277
# S1 Data (SAV) -- survey of nurses/care workers in Japan (super-aging
# society study of burnout and religion). Two instruments in the same file:
#   - Frommelt Attitude Toward Care Of Dying Scale (abbreviated), 6 items,
#     columns Q10_1s-Q10_6s (labelled "TC scale" / attitude items in the
#     original Japanese column labels), 1-5 Likert.
#   - Japanese Burnout Index, 17 items, columns Q23_1s-Q23_17s (labelled
#     "burnout" in the original Japanese column labels), 1-5 Likert.
# Written as two separate scale files. Column labels in the source SAV are
# in Japanese; item numbering (1-6, 1-17) follows the original questionnaire
# order.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0202277.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_okamura_2018.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)
    return df


COV_MAP = {
    "age": "cov_age",
    "sex": "cov_sex",
    "Q16": "cov_religion",
    "inst": "cov_institution",
    "Q19": "cov_job_type",
    "expyrs": "cov_experience_years",
}


def build(df, item_cols, item_prefix, out_name):
    keep = ["ID"] + list(COV_MAP.keys()) + item_cols
    d = df[keep].copy()
    d = d.rename(columns={"ID": "id"})
    d = d.rename(columns=COV_MAP)
    cov_names = list(COV_MAP.values())

    item_map = {c: f"{item_prefix}{i+1}" for i, c in enumerate(item_cols)}
    d = d.rename(columns=item_map)
    item_names = list(item_map.values())

    d = d[pd.to_numeric(d["id"], errors="coerce").notna()].reset_index(drop=True)
    assert d["id"].nunique() == len(d), "id not unique"

    long = d.melt(id_vars=["id"] + cov_names, value_vars=item_names,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_names
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_dir_abs = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir_abs, exist_ok=True)
    out_path = os.path.join(out_dir_abs, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()

    attitude_cols = [f"Q10_{i}s" for i in range(1, 7)]
    build(df, attitude_cols, "attitude_", "okamura_2018_eol_attitude.csv")

    burnout_cols = [f"Q23_{i}s" for i in range(1, 18)]
    build(df, burnout_cols, "burnout_", "okamura_2018_burnout.csv")


if __name__ == "__main__":
    convert()
