#!/usr/bin/env python3
# Source: https://zenodo.org/records/10254868
# DOI: 10.5281/zenodo.10254868
# Data: "base de datos general.sav" (SPSS; variable labels carry the full
#   Spanish stem for every item, value labels absent)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Vila López, N., Küster-Boluda, I., & Ugalde-Sánchez, C. (2023).
#   BRAND ATTACHMENT DATA BASE.
#
# 1,922 respondents rating a brand on seven blocks, all on the same 1-8
# scale. One table per block, following the one-file-per-scale convention:
#
#   AP1..AP10   brand-personality adjectives, set A  -> _personality_a
#   PE1..PE15   brand-personality adjectives, set B  -> _personality_b
#   CA1..CA5    brand awareness                      -> _awareness
#   CM1..CM6    brand credibility                    -> _credibility
#   LM1..LM3    brand loyalty                        -> _loyalty
#   RP1..RP3    perceived risk                       -> _perceived_risk
#   IC1..IC3    purchase intention                   -> _purchase_intention
#
# AP and PE are both adjective batteries ("ap1 Cariñoso", "pe1 Con los pies en
# la tierra") and may be two matrices of one brand-personality instrument, but
# the deposit codes them as two blocks and nothing in it says they are one, so
# they are kept separate rather than merged on a guess.
#
# `id` IS THE ROW INDEX, AND THE REASON MATTERS. The `ID` column has 1,893
# distinct values over 1,922 rows: 29 ids appear twice. Those are **id
# collisions, not repeated respondents** -- for every one of the 29 pairs the
# two rows differ on the items (each duplicated id shows exactly 2 distinct
# answers per item, and 0 of the 29 pairs has an identical response vector).
# Treating `ID` as the person would merge two different people under one id
# and manufacture within-person disagreement. The row index is used instead,
# which keeps all 1,922 respondents distinct. `ID` is not carried: it has no
# meaning outside this file and keeping it would invite the same mistake.
#
# THREE DATA-ENTRY ERRORS, FILTERED PER ITEM-RESPONSE. On a 1-8 scale the file
# holds `AP10 = 53` (one row), `PE9 = 43` (one row) and `RP2 = 9` (one row).
# Each is a single cell, isolated to one item, with every other response in
# that item and that row in range -- the signature of a keying slip, not of a
# wider scale. The three item-responses are dropped; the respondents keep
# their other answers.
#
# `PC1..PC5` are fractional and are the block means; dropped.
#
# PII: none. The value-level email screen is clean, the variable-label screen
# is clean, and the only free text is `P` (the brand name shown).
#
# Item text: NOT shipped. BOTH label levels were checked: variable labels
# carry the administered Spanish stem for all 45 items, and value labels are
# EMPTY for every one of them -- so the deposit holds the questions but not
# one response anchor, and the 1-8 scale's endpoints are unknown. Shipping
# stems with invented anchors is not an option, and option_text cannot be left
# wholly absent. Where the text is: this .sav's variable labels for the stems;
# the anchors need the paper's method section.

import os
import re

import pandas as pd
import pyreadstat


# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set VILALOPEZ_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/10254868/files/base%20de%20datos%20general.sav/content")
_NAME = "zenodo_10254868__base_de_datos_general.sav"


def _raw():
    override = os.environ.get("VILALOPEZ_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent":
                           "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(dest, "wb") as fh:
            fh.write(r.read())
    return dest

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

BLOCKS = {"personality_a": ("AP", 10), "personality_b": ("PE", 15),
          "awareness": ("CA", 5), "credibility": ("CM", 6),
          "loyalty": ("LM", 3), "perceived_risk": ("RP", 3),
          "purchase_intention": ("IC", 3)}
SCALE = set(float(v) for v in range(1, 9))

COVS = {"atri": "cov_attribute_condition", "CIUDAD": "cov_city",
        "EDAD": "cov_age", "GENERO": "cov_gender", "NSE": "cov_ses"}


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    labs = meta.column_names_to_labels or {}
    vlabs = meta.variable_value_labels or {}
    print(f"raw: {df.shape}")

    dup_ids = df["ID"].duplicated(keep=False)
    item_cols = [c for c in df.columns
                 if re.match(r"^(AP|PE|LM|CA|CM|RP|IC)\d+$", c)]
    pairs = df[dup_ids].groupby("ID")[item_cols]
    identical = sum(1 for _, g in pairs if g.drop_duplicates().shape[0] == 1)
    print(f"ID has {df['ID'].nunique()} distinct values over {len(df)} rows; "
          f"{dup_ids.sum()} rows share an id. Identical response vectors "
          f"among those groups: {identical} -- so they are id COLLISIONS, not "
          f"repeated respondents. Using the row index as `id`.")
    assert identical == 0, "some duplicated ids now look like real repeats"

    df = df.reset_index(drop=True)
    df["row_id"] = df.index + 1

    # Both label levels, stated rather than concluded.
    n_stem = sum(1 for c in item_cols if (labs.get(c) or "").strip())
    n_anchor = sum(1 for c in item_cols if vlabs.get(c))
    print(f"label levels: {n_stem}/{len(item_cols)} items have a variable "
          f"label (stem), {n_anchor}/{len(item_cols)} have value labels "
          f"(anchors) -> stems present, anchors absent, no item text shipped")

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    accounted = set(["ID", "row_id"]) | set(cov_src) | set(item_cols)
    skipped = {}
    for c in df.columns:
        if c in ("row_id",) or c in cov_src or c in item_cols:
            continue
        if c == "ID":
            skipped[c] = "collides across respondents; row index used instead"
        elif re.match(r"^PC\d+$", c):
            skipped[c] = "block mean (fractional), derived"
        elif c in ("CA5R",):
            skipped[c] = "reverse-coded copy of CA5"
        elif c in ("P",):
            skipped[c] = "free-text brand name shown to the respondent"
        elif re.match(r"^(P1|DC\d|DIG)", c):
            skipped[c] = "single background question, not part of an instrument"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:10} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written, total = set(), 0
    for name, (prefix, n) in BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        assert all(c in df.columns for c in cols), f"{name}: missing columns"
        long = (df[["row_id"] + cols].melt(id_vars="row_id", var_name="item",
                                           value_name="resp")
                .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(float)

        off = long[~long["resp"].isin(SCALE)]
        if len(off):
            for _, r in off.iterrows():
                print(f"    drop {r['item']}={r['resp']:g} (one cell, outside "
                      f"the 1-8 scale -- keying slip)")
            assert len(off) <= 2, f"{name}: {len(off)} off-scale cells, too " \
                                  f"many to call keying slips"
            long = long[long["resp"].isin(SCALE)]

        long = long.merge(df[["row_id"] + list(cov_src)].rename(columns=cov_src),
                          on="row_id", how="left").rename(columns={"row_id": "id"})
        assert long["item"].nunique() > 1, f"{name}: single item"
        assert long["id"].nunique() >= 100, f"{name}: N={long['id'].nunique()}"
        long = long[["id", "item", "resp"] + list(cov_src.values())]

        out_name = f"vila_lopez_2023_{name}"
        assert out_name not in written, f"duplicate output name {out_name}"
        written.add(out_name)
        long.to_csv(os.path.join(OUT_DIR, f"{out_name}.csv"), index=False)
        total += len(long)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")
    print(f"total responses: {total}")


if __name__ == "__main__":
    convert()
