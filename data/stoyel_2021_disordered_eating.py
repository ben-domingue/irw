#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257577
# DOI: 10.1371/journal.pone.0257577
# SI: S1 Data (10.1371/journal.pone.0257577.s001), XLSX
#
# Prospective (3-wave) study of disordered-eating risk factors in
# athletes. The source file is wide, one row per subject, with item
# columns named "<PREFIX><item#>.<wave>: <item text>" (e.g. "DT3.2: I
# feel extremely guilty after overeating" = Drive-for-Thinness item 3,
# wave 2). ~20 subscale prefixes cover EDI subscales (Drive for
# Thinness, Body Dissatisfaction, Bulimia, Maturity Fears, Interoceptive
# Awareness, Ineffectiveness, Perfectionism, Interpersonal Distrust),
# PANAS (positive/negative affect), sociocultural-influence measures
# (modeling behavior, sociocultural info/pressure, TV/athlete
# internalization, social media), and EDE-Q subscales (restraint,
# eating/shape/weight concern, binge/purge). Each prefix becomes its own
# output table with a `wave` column (1/2/3). "MEAN SCALE SCORE" columns
# (per-subscale aggregate) are excluded. No person-id column in the
# source (title says "NO ID"); row index used as id. SLEEP/DIET/PERIOD
# blocks mix heterogeneous question types (hours, clock times, yes/no)
# rather than one coherent Likert construct and are not shipped.

import os
import io
import re
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0257577.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# prefix -> (output construct name, valid_min, valid_max)
SCALES = {
    "DT":    ("drive_thinness", 0, 3),
    "BD":    ("body_dissat", 0, 3),
    "BUL":   ("bulimia", 0, 3),
    "MATFR": ("maturity_fears", 0, 3),
    "IPAW":  ("interocept_awareness", 0, 3),
    "INEFF": ("ineffectiveness", 0, 3),
    "PERF":  ("perfectionism", 0, 3),
    "IPDT":  ("interpersonal_distrust", 0, 3),
    "POSAF": ("pos_affect", 1, 5),
    "NEGAF": ("neg_affect", 1, 5),
    "MBEH":  ("social_modeling", 1, 5),
    "SCINF": ("sociocult_info", 1, 5),
    "SCPR":  ("sociocult_pressure", 1, 5),
    "INTG":  ("tv_internalization", 1, 5),
    "INTA":  ("athlete_internal", 1, 5),
    "SMED":  ("social_media", 1, 6),
    "EDEQR": ("edeq_restraint", 0, 6),
    "EDEQC": ("edeq_eating_concern", 0, 6),
    "EDEQS": ("edeq_shape_concern", 0, 6),
    "EDEQW": ("edeq_weight_concern", 0, 6),
    "EDEQX": ("edeq_binge_purge", 0, 6),
}

ITEM_PAT = re.compile(r"^([A-Za-z]+)(\d+)\.(\d)\s*:")


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=180)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="alldata_subjectlevel_NO ID")
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    # bucket columns by prefix -> wave -> {itemnum: colname}
    buckets = {}
    for c in df.columns:
        m = ITEM_PAT.match(str(c))
        if not m or "MEAN SCALE SCORE" in c:
            continue
        prefix, itemnum, wave = m.groups()
        if prefix not in SCALES:
            continue
        buckets.setdefault(prefix, {}).setdefault(wave, {})[itemnum] = c

    os.makedirs(OUT_DIR, exist_ok=True)
    for prefix, (construct, vmin, vmax) in SCALES.items():
        if prefix not in buckets:
            continue
        frames = []
        for wave, items in sorted(buckets[prefix].items()):
            cols = [items[k] for k in sorted(items, key=int)]
            rename = {c: f"item_{i+1}" for i, c in enumerate(cols)}
            sub = df[["id"] + cols].rename(columns=rename)
            long = sub.melt(id_vars=["id"], value_vars=list(rename.values()),
                             var_name="item", value_name="resp")
            long["wave"] = int(wave)
            frames.append(long)
        long = pd.concat(frames, ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)]
        # EDI subscales (0-3) score as integers; keep as int where scale is integral
        if float(vmin).is_integer() and float(vmax).is_integer():
            # keep only integral values (drop any stray fractional artifacts)
            long = long[long["resp"] == long["resp"].round()]
            long["resp"] = long["resp"].astype(int)

        out_cols = ["id", "item", "resp", "wave"]
        long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

        out_name = f"stoyel_2021_{construct}"
        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
