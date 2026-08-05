#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201258
# DOI: 10.1371/journal.pone.0201258
#
# Cooper KM, Hendrix T, Stephens MD, et al. (2018) To be funny or not to be
# funny: Gender differences in student perceptions of instructor humor in
# college science courses. PLoS ONE.
#
# S3 File (XLSX, N=1637) contains anonymized survey data. Respondents were
# shown a checklist of 34 topics and asked to mark each one they found
# funny (funny.*) and, separately, each one they found offensive
# (offensive.*) -- both binary 0/1 item batteries. Two genuine item-level
# scales:
#   - offensive.*: 34 binary items ("did you find this topic offensive?")
#   - funny.*: 34 binary items ("did you find this topic funny?")
# Excluded: single lead-in Likert item ("appreciate when instructors use
# humor..."), free-text explanation/reasoning columns, and the
# funny.belonging/funny.relatability/funny.attention/unfunny.* qualitative
# follow-up columns (all free text, not item responses).

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0201258.s005"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[["anonymous.ID"] + item_cols].copy()
    d = d.rename(columns={"anonymous.ID": "id"})
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S3 File (XLSX)...")
    raw = fetch_raw()

    off_cols = [c for c in raw.columns if c.startswith("offensive.")]
    funny_cols = [c for c in raw.columns
                  if c.startswith("funny.")
                  and c not in ("funny.belonging", "funny.relatability", "funny.attention")]

    offensive = build_long(raw, off_cols)
    funny = build_long(raw, funny_cols)

    write_scale(offensive, "cooper_2018_offensive_topics.csv")
    write_scale(funny, "cooper_2018_funny_topics.csv")


if __name__ == "__main__":
    convert()
