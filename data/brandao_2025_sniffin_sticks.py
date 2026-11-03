#!/usr/bin/env python3
# Source: https://zenodo.org/records/15384922
# DOI: 10.5281/zenodo.15384922 (data); paper 10.7717/peerj.19733
# Deposit: de Paula Brandão PR, Pereira DA, de Carvalho Bispo DD, von Glehn F,
#   Silveira-Moriyama L, Titze-de-Almeida SS, et al. (2025). Sniffin' Sticks
#   smell identification test: exploring measurement properties in an adult
#   Brazilian healthcare professionals sample [dataset]. Zenodo. Paper: same
#   title, PeerJ 2025, 10.7717/peerj.19733.
# Data: peerj-104137-raw_data_sniffing_data.csv, semicolon-delimited, 144
#   Brazilian healthcare professionals, one row each.
# License: CC BY 4.0 (verified on the Zenodo record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3; Step 2b
# recoverable_format: the file is semicolon-delimited), worked from
# leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# ONE output table:
#   brandao_2025_sniffin_sticks  Sniffin' Sticks odour identification test,
#     Brazilian Portuguese adaptation. One item per target odour, item code =
#     the odour named in the deposit's header (leather .. fish); resp 1 =
#     correctly identified, 0 = not ("individual item responses in binary
#     form", per the record). The record describes the 16-item test (SS-16);
#     the deposit has 15 odour columns -- orange, item 1 of the standard SS-16,
#     is absent -- and is shipped as deposited.
# No covariates: the file has none. `id` is the deposit's own row number.
#
# Item text: not shipped (the target odours are the item codes; the four
#   printed choices per pen are not in the deposit).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("BRANDAO_RAW", "peerj-104137-raw_data_sniffing_data.csv")
ODOURS = ["leather", "cinnamon", "peppermint", "banana", "lemon", "liquorice", "turpentine", "garlic", "coffee",
          "apple", "cloves", "pineapple", "rose", "anise", "fish"]


def convert():
    df = pd.read_csv(RAW, sep=";")
    df = df.rename(columns={df.columns[0]: "row"})
    assert df.shape == (144, 16), df.shape
    assert list(df.columns[1:]) == ODOURS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    assert df["row"].is_unique
    df["id"] = df["row"]
    long = df[["id"] + ODOURS].melt(id_vars=["id"], var_name="item", value_name="resp").dropna(subset=["resp"])
    assert set(long["resp"]) <= {0, 1}
    long["resp"] = long["resp"].astype(int)
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1] for c in ODOURS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "brandao_2025_sniffin_sticks.csv"), index=False)
    print(f"brandao_2025_sniffin_sticks: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
