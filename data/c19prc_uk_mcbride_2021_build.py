"""Convert C19PRC-UK archives into IRW-standard long-format tables.

Multi-wave: add a new wave by appending to SOURCES and extending crosswalk.py.

Set C19PRC_TABLES=key1,key2 to build only those tables (e.g. socialdistance).
"""
import os
import re
import sys
import pandas as pd
import pyreadstat
from c19prc_uk_mcbride_2021_crosswalk import TABLES

# Directory holding the six C19PRC-UK .sav archives.
# Override with:  python build_irw.py <data_dir> [output_dir]
DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else "output"

FILES = {
    1: "C19PRC_UKW1W2_archive_final.sav",
    2: "C19PRC_UKW1W2_archive_final.sav",
    3: "C19PRC_UK_W3_archive_final.sav",
    4: "C19PRC_UK_W4_archive_final.sav",
    5: "C19PRC_UKW5_archive_final.sav",
    6: "C19PRC_UK_W6_archive_final.sav",
}
SOURCES = {w: os.path.join(DATA_DIR, f) for w, f in FILES.items()}

missing = sorted({p for p in SOURCES.values() if not os.path.exists(p)})
if missing:
    sys.exit("Missing input file(s) in '%s':\n  %s\n"
             "Pass the directory as the first argument, e.g. python build_irw.py ~/c19prc"
             % (DATA_DIR, "\n  ".join(os.path.basename(m) for m in missing)))

OUT = os.path.join(OUT_DIR, "tables")
PREFIX = "c19prc_uk_mcbride_2021"
os.makedirs(OUT, exist_ok=True)

CRT_KEY = {"CRT1": 1, "CRT2": 1, "CRT3": 1, "CRT4": 2, "CRT5": 3}

# GSS Wordsum: correct option index per item. Option 6 is always "Don't know".
# SPACE=room, BROADEN=widen, EMANATE=come, EDIBLE=fit to eat, ANIMOSITY=hatred,
# PACT=agreement, CLOISTERED=secluded, CAPRICE=whim, ACCUSTOM=get used to,
# ALLUSION=reference.
WORDSUM_KEY = {"Wordsum_1": 4, "Wordsum_2": 5, "Wordsum_3": 5, "Wordsum_4": 3,
               "Wordsum_5": 1, "Wordsum_6": 3, "Wordsum_7": 5, "Wordsum_8": 4,
               "Wordsum_9": 4, "Wordsum_10": 1}

frames, labels, vlabels = {}, {}, {}
for path in set(SOURCES.values()):
    d, m = pyreadstat.read_sav(path)
    frames[path] = d
    labels[path] = m.column_names_to_labels
    vlabels[path] = m.variable_value_labels
WAVE_DF = {w: frames[p] for w, p in SOURCES.items()}
WAVE_LAB = {w: labels[p] for w, p in SOURCES.items()}
WAVE_VLAB = {w: vlabels[p] for w, p in SOURCES.items()}


def item_wording(label):
    """Normalise an SPSS variable label to the item's wording. Cosmetic differences removed:
    1. the block preamble before the last ' - ' (it restates each wave's distancing rules);
    2. a leading item number 'N.' (the item's position in that wave's block);
    3. runs of whitespace, incl. the tab after the number in W1/W2 labels;
    4. curly apostrophes (W5 uses U+2019, W1/W2 a straight ').
    """
    s = re.sub(r"\s+", " ", label or "").strip()
    s = s.rsplit(" - ", 1)[-1]
    s = re.sub(r"^\d+\.\s*", "", s)
    return s.replace("\u2019", "'").strip()


def check_labels(key, sources):
    """sources: {item code: {wave: source column}}. Fail unless every code pooled across
    waves has the same item wording and the same value labels in each of those waves."""
    bad = []
    for code, cols in sorted(sources.items()):
        if len(cols) < 2:
            continue
        words = {w: item_wording(WAVE_LAB[w].get(c)) for w, c in cols.items()}
        vals = {w: WAVE_VLAB[w].get(c) for w, c in cols.items()}
        if len(set(words.values())) > 1:
            bad.append(f"{code}: wording differs {words}")
        if any(v != next(iter(vals.values())) for v in vals.values()):
            bad.append(f"{code}: value labels differ {vals}")
    if bad:
        sys.exit(f"{key}: pooled codes mix different questions:\n  " + "\n  ".join(bad))


def unix(series):
    s = pd.to_datetime(series, errors="coerce")
    return ((s - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")).where(s.notna())


# person covariates: taken from the earliest wave in which the person appears
cov_parts = []
for w in sorted(SOURCES):
    d = WAVE_DF[w]
    if f"W{w}_Age_year" not in d.columns:
        continue
    cov_parts.append(pd.DataFrame({"id": d["pid"].astype(str), "cov_age": d[f"W{w}_Age_year"],
                                   "cov_gender": d[f"W{w}_Gender"], "_w": w})
                     .dropna(subset=["cov_age", "cov_gender"], how="all"))
cov = (pd.concat(cov_parts).sort_values("_w")
       .drop_duplicates("id", keep="first").drop(columns="_w"))
cov["cov_gender"] = cov["cov_gender"].map({1: "male", 2: "female", 3: "transgender",
                                           4: "prefer_not_say", 5: "other"})

dates = {w: pd.DataFrame({"id": WAVE_DF[w]["pid"].astype(str), "date": unix(WAVE_DF[w][f"W{w}_StartDate"])})
         for w in SOURCES}

manifest = []
ONLY = [k for k in os.environ.get("C19PRC_TABLES", "").split(",") if k]

for spec in TABLES:
    key, stems, waves = spec["key"], spec["stems"], spec["waves"]
    if ONLY and key not in ONLY:
        continue
    item_code = spec.get("item_code", {})
    sources = {}   # final item code -> {wave: source column}, for check_labels
    wave_specific = set(spec.get("wave_specific", []))
    rev_waves = set(spec.get("reverse_waves", []))
    rev_max = spec.get("reverse_max")
    recode = spec.get("recode")
    parts = []

    for w in waves:
        if w not in WAVE_DF:      # wave's source file not supplied for this run
            continue
        d = WAVE_DF[w]
        ren = spec.get("rename", {}).get(w, {})
        # a rename to None means the stem was not asked at this wave
        present = [s for s in stems
                   if ren.get(s, s) is not None and f"W{w}_{ren.get(s, s)}" in d.columns]
        if not present:
            continue
        sub = d[["pid"] + [f"W{w}_{ren.get(s, s)}" for s in present]].copy()
        sub.columns = ["id"] + present
        sub["id"] = sub["id"].astype(str)
        long = sub.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])

        if recode == "crt":
            long["resp"] = [1 if CRT_KEY[i] == r else 0 for i, r in zip(long["item"], long["resp"])]
        elif recode == "wordsum":
            long["resp"] = [1 if WORDSUM_KEY[i] == r else 0
                            for i, r in zip(long["item"], long["resp"])]
        elif recode == "yesno":
            long["resp"] = long["resp"].map({1.0: 1, 2.0: 0})
            long = long.dropna(subset=["resp"])
        elif recode == "protect":
            long = long[long["resp"] != 5]

        # harmonise response direction where anchors were flipped between waves
        if w in rev_waves:
            long["resp"] = rev_max - long["resp"]

        codes = {s: f"{s}_W{w}" if s in wave_specific else s for s in present}
        codes.update({s: c for s, c in item_code.get(w, {}).items() if s in codes})
        long["item"] = long["item"].map(codes)
        for s in present:
            sources.setdefault(codes[s], {})[w] = f"W{w}_{ren.get(s, s)}"

        long["wave"] = w
        long = long.merge(dates[w], on="id", how="left")
        parts.append(long)


    if not parts:
        continue
    if spec.get("check_labels"):
        check_labels(key, sources)
    out = pd.concat(parts, ignore_index=True).merge(cov, on="id", how="left")
    out = out[["id", "item", "resp", "wave", "date", "cov_age", "cov_gender"]]
    out["resp"] = out["resp"].astype(int)
    out["id"] = out["id"].astype(str)   # IDs are opaque strings for some W4 booster respondents
    for c in ("date", "cov_age"):        # whole numbers: write 1616709626, not 1616709626.0
        v = pd.to_numeric(out[c])
        if (v.dropna() % 1 == 0).all():
            out[c] = v.astype("Int64")
    out = out.sort_values(["id", "wave", "item"])
    out.to_csv(f"{OUT}/{PREFIX}_{key}.csv", index=False)

    manifest.append(dict(
        table=f"{PREFIX}_{key}", instrument=spec["instrument"],
        waves="|".join(str(x) for x in sorted(out["wave"].unique())),
        n_rows=len(out), n_persons=out["id"].nunique(), n_items=out["item"].nunique(),
        resp_min=int(out["resp"].min()), resp_max=int(out["resp"].max()),
        scale=spec["scale"], file=f"{PREFIX}_{key}.csv"))

m = pd.DataFrame(manifest)
print(f"Wrote {len(m)} tables ({m.n_rows.sum():,} rows) to {OUT}")