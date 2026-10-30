#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0308267
# DOI: 10.1371/journal.pone.0308267
# Paper: Li, J., & Lv, C. (2024). Exploring user acceptance of online virtual
#   reality exhibition technologies: a case study of Liangzhu Museum.
#   PLOS ONE 19(8): e0308267.
# Data: journal.pone.0308267.s001 (S1 Data, .xlsx), 313 rows x 28 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 313 respondents recruited via social media, 4 Jan - 10 Dec 2023, who had
# experienced the Liangzhu Museum online VR exhibition.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 27 items, 8,451 responses, zero missing cells.
#
# THE COLUMN HEADERS ARE THE ITEMS. Every data column is headed with its item
# code AND its full English wording ("INT1 The VR can respond quickly to my
# actions"), so the construct blocks, the item codes and the item text all come
# from the same string. Nothing is positional and nothing is inferred:
#   INT  5  Interactivity
#   IMM  3  Immersion
#   PRE  3  Presence
#   PU   4  Perceived usefulness
#   PEU  3  Perceived ease of use
#   PE   3  Perceived enjoyment
#   IU   3  Intention of use
#   TVAS 3  Tendency to visit the actual site
# These are exactly the eight constructs the article names, in its own order.
# Item text is shipped from the headers -- see li_2024_vr_exhibition_itemtext.py.
#
# THE SCALE DIRECTION IS NOT CONFIRMED BY THE ARTICLE, and that is stated
# rather than hidden. The paper says only "5-point scale" with "strongly
# disagree" and "strongly agree" as the endpoints; it never says which end is
# coded 1. resp therefore ships exactly as the deposit codes it, under the
# conventional reading that 1 is strongly disagree, and the description says
# the direction is unconfirmed. This is the same hazard that li_2024_deg_*
# turned up earlier in this batch, where the prose DID reveal a backwards
# scale -- here the prose reveals nothing either way, so the limitation is
# published with the table instead of being resolved by assumption. No item is
# reverse-worded (IMM3 "I am not easily distracted in the VR" and PEU3 "I don't
# find experiencing VR exhibitions difficult" are negations in their wording
# but point the same way as their constructs), so one direction applies to all
# 27 items.
#
# NO COVARIATES. The deposit is the serial number plus 27 item columns and
# nothing else. The article reports age and education distributions, but those
# columns are not in the file; their absence is the deposit's, not a drop.
#
# N IS 313, AND THE ARTICLE IS INCONSISTENT WITH ITSELF ABOUT THIS. It reports
# 347 questionnaires collected and 314 valid in one place and analyses "313
# samples (182 female, 131 male)" in another. The deposit holds 313 rows with
# `Serial No.` running 2..347 with gaps, which matches the 313 figure and the
# 347 collection. Recorded rather than reconciled.
#
# PII: screened over all 28 columns. Every one is numeric apart from nothing --
# the long header strings are column names, not values.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIVR_RAW", "journal.pone.0308267_S1_Data.xlsx")

N_ROWS = 313
LO, HI = 1, 5

CONSTRUCTS = {
    "INT": ("li_2024_vr_interactivity", 5, "Interactivity"),
    "IMM": ("li_2024_vr_immersion", 3, "Immersion"),
    "PRE": ("li_2024_vr_presence", 3, "Presence"),
    "PU": ("li_2024_vr_usefulness", 4, "Perceived usefulness"),
    "PEU": ("li_2024_vr_ease_of_use", 3, "Perceived ease of use"),
    "PE": ("li_2024_vr_enjoyment", 3, "Perceived enjoyment"),
    "IU": ("li_2024_vr_intention_to_use", 3, "Intention of use"),
    "TVAS": ("li_2024_vr_visit_actual_site", 3,
             "Tendency to visit the actual site"),
}
# "INT4I can control..." -- the code and the wording are not always separated
# by a space, so the split is on the digit boundary, not on whitespace
HEADER = re.compile(r"^(INT|IMM|PRE|PEU|PU|PE|IU|TVAS)(\d+)\s*(.*)$")


def parse_headers(df):
    """code -> (column, prefix, wording). Shared with the item-text build."""
    out = {}
    for c in df.columns:
        m = HEADER.match(str(c).strip())
        if m:
            code = m.group(1) + m.group(2)
            out[code] = (c, m.group(1), re.sub(r"\s+", " ", m.group(3)).strip())
    return out


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s) -- screen them: {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}; the long "
          f"headers are column names, not values")

    parsed = parse_headers(df)
    assert len(parsed) == 27, (len(parsed), "expected 27 item columns")
    for code, (col, prefix, text) in parsed.items():
        assert text, f"{code} has a code but no wording in its header: {col!r}"
    by_prefix = {}
    for code, (col, prefix, _) in parsed.items():
        by_prefix.setdefault(prefix, []).append((code, col))
    got = {k: len(v) for k, v in by_prefix.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"

    accounted = {"Serial No."} | {col for col, *_ in
                                  [(v[0],) for v in parsed.values()]}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    assert df["Serial No."].nunique() == len(df), "Serial No. is not unique"
    df = df.rename(columns={"Serial No.": "id"})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        pairs = sorted(by_prefix[prefix], key=lambda p: int(p[0][len(prefix):]))
        cols = [c for _, c in pairs]
        ren = {c: code for code, c in pairs}
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "a non-numeric response")
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].map(ren)
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"]]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 27 * N_ROWS, total
    print(f"8 tables, {total} responses (27 items x {N_ROWS} respondents)")


if __name__ == "__main__":
    convert()
