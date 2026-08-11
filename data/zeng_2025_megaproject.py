#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0334291
# DOI: 10.1371/journal.pone.0334291
# S1 File (raw survey data): https://doi.org/10.1371/journal.pone.0334291.s001
#   (resolves to https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0334291.s001&type=supplementary)
#
# Paper: Zeng Z, Shen Y, Yang J, Hengsadeekul T (2025). "The impact of
# international megaproject social responsibility on satisfaction with the
# environmental compensation mechanism: The role of stakeholder
# participation." PLOS ONE.
#
# Three separate 5-point Likert scales are administered in one survey and
# saved to three separate IRW output files per datastandard.md's
# "one file per scale" rule:
#   - MSR  (megaproject social responsibility, items 2.1-2.39, 39 items)
#   - SEAP (stakeholder environmental activities participation, 3.1-3.11, 11 items)
#   - ECM  (satisfaction with environmental compensation mechanism, 4.1-4.15, 15 items)

import os
import re
import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0334291.s001&type=supplementary"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "1.1 您的性别?\n Your gender is?": "cov_gender",
    "1.2 您是否有宗教信仰？ \nWhat's your religion": "cov_religion",
    "1.3 您在大型项目行业工作了多少年?\nHow many years have you worked in the megaproject industry?": "cov_years_experience",
    "1.4 您的最高学历是?\nPlease specify your highest education? \n": "cov_education",
    "1.5 您对社会责任熟悉吗? \nAre you familiar with social responsibility?\n": "cov_ssr_familiarity",
    "1.7 您在参与大型工程项目当中属于以下哪个角色？\nFor megaprojects, which of the following groups do you belong to?": "cov_role",
}


def fetch_raw():
    local = os.path.join(BASE, "pone0334291_s001.xlsx")
    if not os.path.exists(local):
        r = requests.get(URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(local, "wb") as f:
            f.write(r.content)
    return local


def convert():
    raw = fetch_raw()
    df = pd.read_excel(raw)
    df = df.rename(columns={"序号": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique"

    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    # Item columns carry the full bilingual question text, and the first
    # item of each section has the section banner text prepended before its
    # own "N.M" number (e.g. "2. Evaluation of social responsibility ...
    # —2.1 During the project launch period ..."). A pattern anchored
    # at the start of the string misses that first item per section, so
    # search the whole string for the first "N.M" occurrence instead and
    # bucket by the leading digit (section number).
    section_map = {2: "zeng_2025_megaproject_msr",
                   3: "zeng_2025_megaproject_seap",
                   4: "zeng_2025_megaproject_ecm"}
    section_items = {2: [], 3: [], 4: []}
    for c in df.columns:
        if c in ("id",) or c in cov_cols:
            continue
        m = re.search(r"(\d+)\.(\d+)", str(c))
        if not m:
            continue
        sec = int(m.group(1))
        if sec in section_items:
            section_items[sec].append((c, f"item_{m.group(1)}_{m.group(2)}"))

    for sec, out_name in section_map.items():
        pairs = section_items[sec]
        if not pairs:
            print(f"  no columns matched for {out_name}")
            continue
        item_cols = [c for c, _ in pairs]
        rename_map = dict(pairs)
        sub = df[["id"] + cov_cols + item_cols].rename(columns=rename_map)
        new_item_cols = list(rename_map.values())

        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=new_item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # valid scale is 1-5; filter any sentinel outside that range
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
