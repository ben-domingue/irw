#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306629
# DOI: 10.1371/journal.pone.0306629
# Paper: Jin H, Peng Y (2024). The impact of team psychological safety on
#   employee innovative performance a study with communication behavior as a
#   mediator variable. PLOS ONE 19(10): e0306629.
# Data: S1 Data (XLSX), 580 rows x 21 columns, attached to the article itself.
#   No codebook; the headers name the construct and item number.
# License: CC BY 4.0 (the article's licence covers its SI file).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# triage flag good).
#
# 580 valid responses from employees of 40+ Chinese high-tech firms (paper,
# 3.1). "All items were measured using a 5-point Likert scale, where 5
# indicates 'very consistent' and 1 indicates 'very inconsistent'."
#
# FIVE output tables, one per construct, 3 items each (the paper's own
# measurement blocks; three items is the intake floor):
#   jin_2024_teamwork_understanding   Teamwork and Understanding 1-3
#   jin_2024_team_info_sharing        Team Information Sharing 1-3
#   jin_2024_effort_reward_balance    Balancing effort and reward 1, Balance of
#                                     effort and reward 2, Balancing effort and
#                                     reward 3 (the deposit's own spelling varies)
#   jin_2024_communication_effect     Communication effect 1, Communication
#                                     Effect 2, Communication Effect 3
#   jin_2024_innovation_performance   Employee Innovation Performance 1-3
# The first three are the paper's dimensions of team psychological safety;
# communication behaviour is the mediator, innovative performance the outcome.
#
# Item codes: the deposit's headers are "<construct name> <n>" with spaces and
#   inconsistent capitalisation. Each is mapped by an EXPLICIT header->code
#   dict (ITEMS below, keyed on the exact header text, not on position) to a
#   short code: tu1-3, tis1-3, ber1-3, ce1-3, eip1-3.
# DROPPED, not items: the five trailing construct columns (e.g. "Teamwork and
#   Understanding") -- each equals the mean of its three items in all 580 rows
#   (asserted).
# `id`: the deposit's "Reported by" column, 1-580, unique (asserted). No
#   covariates in the deposit (the demographics of Table 1 are not in S1).
#
# Imputation: none stated ("imput" absent from the article); no missing cells
#   and every item cell is an integer 1-5 (asserted).
#
# Item text: not shipped -- the deposit's headers name only the construct; the
#   paper says "all items in this study refer to relevant literature" and were
#   refined with executives, so wording would come from the paper's scale
#   table plus a per-source rights question (same adapted-from-the-literature
#   shape as tran_2026_*, left for a general ruling).
#
# PII: no string columns (all 21 columns numeric); asserted.

import os
import socket
import sys
import tempfile

import numpy as np
import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0306629.s001")
RAW = os.environ.get("JIN_RAW", "")

N_ROWS = 580
LO, HI = 1, 5
TABLES = {
    "jin_2024_teamwork_understanding": (
        {"Teamwork and Understanding 1": "tu1",
         "Teamwork and Understanding 2": "tu2",
         "Teamwork and Understanding 3": "tu3"},
        "Teamwork and Understanding"),
    "jin_2024_team_info_sharing": (
        {"Team Information Sharing 1": "tis1",
         "Team Information Sharing 2": "tis2",
         "Team Information Sharing 3": "tis3"},
        "Team information sharing"),
    "jin_2024_effort_reward_balance": (
        {"Balancing effort and reward 1": "ber1",
         "Balance of effort and reward 2": "ber2",
         "Balancing effort and reward 3": "ber3"},
        "Balancing effort and reward"),
    "jin_2024_communication_effect": (
        {"Communication effect 1": "ce1",
         "Communication Effect 2": "ce2",
         "Communication Effect 3": "ce3"},
        "Communication effectiveness"),
    "jin_2024_innovation_performance": (
        {"Employee Innovation Performance 1": "eip1",
         "Employee Innovation Performance 2": "eip2",
         "Employee Innovation Performance 3": "eip3"},
        "Employee Innovation Performance"),
}


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "jin_s1.xlsx")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_excel(fetch())
    assert df.shape == (N_ROWS, 21), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0 and strings == []
    assert df["Reported by"].is_unique
    assert int(df.isna().sum().sum()) == 0
    df = df.rename(columns={"Reported by": "id"})

    os.makedirs(OUT_DIR, exist_ok=True)
    used = {"id"}
    total = 0
    for name, (mapping, mean_col) in TABLES.items():
        assert len(name) <= 40, name
        cols = list(mapping)
        used |= set(cols) | {mean_col}
        assert df[cols].isin(range(LO, HI + 1)).all().all(), name
        # trailing construct column is the item mean -- a composite, dropped
        assert np.allclose(df[cols].mean(axis=1), df[mean_col]), mean_col
        sub = df[["id"] + cols].rename(columns=mapping)
        long = sub.melt(id_vars=["id"], var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values=list(range(LO, HI + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")

    assert used == set(df.columns), set(df.columns) ^ used
    assert total == 15 * N_ROWS, total
    print(f"5 tables, {total} responses; 5 mean columns dropped; all source "
          f"columns accounted for")


if __name__ == "__main__":
    convert()
