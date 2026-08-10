from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0327981
# DOI: 10.1371/journal.pone.0327981
# Abou Hashish, Alsayed & Abdel Razek (2025), "Embracing AI in academia: A
# mixed methods study of nursing students' and educators' perspectives on
# using ChatGPT". S2 File (raw data, .xlsx). CC BY 4.0. This file covers
# the nursing-student sub-sample only (N=240; the separate N=40 educator
# sub-sample described in the paper is not in this file). 40-item
# researcher-developed questionnaire (10 items each across Knowledge,
# Perceptions, Attitudes, Concerns domains), 5-point Likert (1=strongly
# disagree .. 5=strongly agree). Response cells are stored as text labels
# with the numeric code in parentheses, e.g. "Agree (4)" / "Strongly
# Disagree (1)" (with inconsistent spacing across rows) -- extracted via
# regex on the parenthesized digit. Shipped as one table (all 40 items are
# sub-domains of a single self-developed survey administered together, not
# independently-published distinct instruments).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0327981.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    likert_cols = []
    for c in df.columns:
        extracted = df[c].astype(str).str.extract(r"\((\d)\)")[0]
        if extracted.notna().mean() > 0.8:
            likert_cols.append(c)
    assert len(likert_cols) == 40, f"expected 40 Likert items, found {len(likert_cols)}"

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns={
        "AGE": "cov_age",
        "\xa0 Year of Study:\n  ": "cov_year_of_study",
    })

    item_names = [f"item_{i:02d}" for i in range(1, 41)]
    rename_map = dict(zip(likert_cols, item_names))
    df = df.rename(columns=rename_map)

    for new_name in item_names:
        df[new_name] = df[new_name].astype(str).str.extract(r"\((\d)\)")[0]

    # Raw cells carry a stray bullet+tab prefix from the source checkbox
    # form (e.g. "•\tFourth Year") and inconsistent capitalization
    # ("Fourth year" vs "Fourth Year"); normalize both away.
    df["cov_year_of_study"] = (
        df["cov_year_of_study"].astype(str)
        .str.replace(r"^[•\t\s]+", "", regex=True)
        .str.strip()
        .str.title()
    )

    cov_cols = ["cov_age", "cov_year_of_study"]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_names,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "abouhashish_2025_chatgpt_attitudes"
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
