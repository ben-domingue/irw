#!/usr/bin/env python3
# Source: https://zenodo.org/records/22014024
# DOI: 10.5281/zenodo.22014024
# Data: "Data set_Mansplaining and Flow Experience in Alpine Outdoor Winter
#   Sports.sav" (SPSS; variable AND value labels populated for all 58 columns)
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Fecker, D., & Bosio, B. (2026). Mansplaining and Flow Experience
#   in Alpine Outdoor Winter Sports.
#
# 888 winter-sports participants. Two instruments share the file; only one
# ships.
#
#   v_43..v_48  mansplaining experience, 6 items, 1-5 frequency  -> SHIPPED
#   v_25..v_42  flow experience, 18 items, 1-5 agreement         -> REFUSED
#
# WHY THE FLOW BLOCK IS REFUSED. Its 18 items are Jackson & Eklund flow-scale
# items, verbatim and recognisable from the stems: "… my abilities match the
# challenge of the situation", "… I make the correct movements without
# thinking about trying to do so", "… I have total concentration", "… I am not
# concerned with what others may be thinking of me", "… the way time passes
# seems to be different from normal", "… the experience leaves me feeling
# great" -- two items for each of the nine canonical flow dimensions. The
# rights register BLOCKS the Jackson & Eklund scale (its row names the
# Brazilian-Portuguese DFS-2), and Ben ruled on 2026-09-29 (irw#2401) that a
# block row covers the instrument in EVERY language, so the English
# administration is covered too. That row's matcher is empty on both columns,
# so an automated rights check would have passed this block; it was caught by
# reading the stems against itemtext/register_gaps_2026-10-18.csv, which gains
# a row for the English DFS-2/FSS-2.
#
# The mansplaining block is study-authored (Fecker & Bosio's own items, no
# published instrument behind them) and has no register row, so it ships.
#
# `FLOW` and `MANS` are the two block means (fractional) and are dropped.
# `v_4..v_14` is a multi-select "which winter sports do you do" checklist, one
# column per sport; `Skill_*` and `C1_*` are dummy expansions of `v_19` and
# `v_18`. None is an ordinal item, so they are not melted.
#
# PII: none. The value-level email screen is clean and there is no free-text
# column other than `v_14` ("Other winter sports:"), which names sports.
#
# Item text: SHIPPED. The administration is English -- every one of the 58
# variable labels is English, there is no German anywhere in the file despite
# the Austrian authorship, which is the same basis batch C used for
# hung_2026c. Variable labels carry the full stem for each of the six items
# and value labels carry all five anchors ("never" / "once or twice" /
# "sometimes" / "often" / "many times"), so both the stems and the options are
# the source's own. mapping_basis=data_labels: the .sav ties each code to its
# text directly, and the item codes are the source's own `v_43..v_48` rather
# than anything this script assigns.

import os

import pandas as pd
import pyreadstat

HERE = os.path.dirname(os.path.abspath(__file__))

# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set FECKER_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/22014024/files/Data%20set_Mansplaining%20and%20Flow%20Experience%20in%20Alpine%20Outdoor%20Winter%20Sports.sav/content")
_NAME = "zenodo_22014024__mansplaining.sav"


def _raw():
    override = os.environ.get("FECKER_RAW")
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

OUT_DIR = os.path.join(HERE, "..", "automated_finding", "irw_output")
TEXT_DIR = os.path.join(HERE, "..", "automated_finding", "itemtext_output")

MANS = [f"v_{i}" for i in range(43, 49)]
FLOW = [f"v_{i}" for i in range(25, 43)]
TABLE = "fecker_2026_mansplaining"

COVS = {"GENDER": "cov_gender", "SPORTM": "cov_main_sport",
        "v_18": "cov_activity_frequency", "v_19": "cov_skill_level",
        "v_21": "cov_professional_training", "v_23": "cov_activity_is_job",
        "v_50": "cov_gender_of_explainer"}


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    labs = meta.column_names_to_labels or {}
    vlabs = meta.variable_value_labels or {}
    print(f"raw: {df.shape}")

    print(f"REFUSING {FLOW[0]}..{FLOW[-1]} (18 items): Jackson & Eklund flow "
          f"scale, which the rights register blocks in every language")

    assert df["lfdn"].nunique() == len(df), "lfdn is not unique"
    df = df.rename(columns={"lfdn": "id"})

    cov_src = {k: v for k, v in COVS.items() if k in df.columns}
    accounted = set(["id"]) | set(cov_src) | set(MANS) | set(FLOW)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c in ("FLOW", "MANS"):
            skipped[c] = "block mean (fractional), derived"
        elif c.startswith("Skill_"):
            skipped[c] = "dummy expansion of v_19, carried as cov_skill_level"
        elif c.startswith("C"):
            skipped[c] = "dummy expansion of v_18/v_21/v_23, already carried"
        elif c in [f"v_{i}" for i in range(4, 17)]:
            skipped[c] = "multi-select 'which winter sports' checklist option"
        elif c == "v_18_inv":
            skipped[c] = "reversed copy of v_18"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:18} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    long = df[["id"] + MANS].melt(id_vars="id", var_name="item",
                                  value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(float)

    for c in MANS:
        permitted = set(float(k) for k in (vlabs.get(c) or {}))
        assert permitted == {1.0, 2.0, 3.0, 4.0, 5.0}, f"{c}: {permitted}"
        bad = set(long.loc[long["item"] == c, "resp"].unique()) - permitted
        assert not bad, f"{c}: {sorted(bad)} outside its value labels"
    print("  every item within its documented 1-5 anchor set")

    long = long.merge(df[["id"] + list(cov_src)].rename(columns=cov_src),
                      on="id", how="left")
    assert long["item"].nunique() == 6 and long["id"].nunique() >= 100
    long = long[["id", "item", "resp"] + list(cov_src.values())]
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    write_item_text(long, labs, vlabs)


def write_item_text(long, labs, vlabs):
    """One row per item x response option, from the .sav's own two label
    levels. `item` and `resp` are taken from the response table that was just
    written, so the two sets match by construction."""
    rows = []
    for item in sorted(long["item"].unique(), key=lambda s: int(s.split("_")[1])):
        stem = " ".join(str(labs.get(item, "")).split())
        assert stem, f"{item}: no variable label to use as a stem"
        for code, text in sorted((vlabs.get(item) or {}).items(),
                                 key=lambda kv: float(kv[0])):
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_1",
                "item": item,
                # Study-authored items, so there is no named instrument.
                "instrument": "",
                "language": "en",
                "instructions": "",
                "section_prompt": "",
                "item_text": stem,
                # Not a knowledge test; no key exists.
                "correct_response": "",
                "option_text": " ".join(str(text).split()),
                "resp": float(code),
                "instructions_translated": "",
                "section_prompt_translated": "",
                # The administration is English, so there is nothing to
                # translate -- the *_translated half stays empty by design,
                # not for want of the text.
                "item_text_translated": "",
                "option_text_translated": "",
            })
    it = pd.DataFrame(rows)
    assert set(it["item"]) == set(long["item"]), "item sets differ"
    assert set(it["resp"]) >= set(long["resp"]), "an observed resp has no option"
    os.makedirs(TEXT_DIR, exist_ok=True)
    it.to_csv(os.path.join(TEXT_DIR, f"{TABLE}__items.csv"), index=False)
    print(f"{TABLE}__items: rows={len(it)} items={it['item'].nunique()} "
          f"options={it['resp'].nunique()}")


if __name__ == "__main__":
    convert()
