#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/1IWRQA
# DOI: 10.7910/DVN/1IWRQA
#   Henderson, Michael (2023). "RAPID: Pandemic Anxiety, Recovery, and Inequality:
#   Evaluating Institutions and Policy in a Coronavirus Hotspot (NSF Award #2031591)"
#   [Data set]. Harvard Dataverse. Five-wave panel survey of adult Louisiana residents.
# Data: "Wave 1 Data" (file id 7047437), downloaded with format=original -- an SPSS
#       .sav, 1000 respondents x 191 columns, with full variable labels on every column
#       and value labels on every item. Each battery's columns share one label prefix
#       ("How worried are you -- <target>"), which is what this script keys on rather
#       than the q-numbers (those are not contiguous: the health-emotion battery runs
#       q2-q10 then q164, q165).
# License: CC0 1.0 (the Dataverse record's license is CC0 1.0 / CC0-1.0).
#
# Item text: shipped for 7 of the 8 tables (SPSS variable labels + value labels).
#   BOTH label levels are populated -- `column_names_to_labels` carries the
#   full battery prompt plus the per-item target ("How worried are you -- You or
#   someone in your family will get sick from coronavirus"), and
#   `variable_value_labels` carries the anchors for every item ("Extremely worried" ..
#   "Not at all worried", plus 8=skipped / 9=not asked). The batteries are
#   survey-authored items under the deposit's CC0, not a licensed instrument, with the
#   exception of the 4-item racial-resentment battery, whose item text is HELD: those
#   are the standard Kinder & Sanders symbolic-racism items and that instrument has no
#   row in itemtext/instrument_rights_register.csv, where silence does not ship.
#   Instrument identification for the seven shipped batteries: two stems were searched
#   verbatim ("Your local hospital will run out of necessary equipment like beds or
#   ventilators" and the comfort battery's activity list) and match no published
#   psychometric instrument -- the hits are the LSU Manship School / Public Policy
#   Research Lab's own 2020 Louisiana coronavirus survey releases, i.e. these are
#   survey-authored items covered by the deposit's own CC0. `item_text` is the SPSS
#   variable label verbatim, which is identical to the "Description" the deposit's
#   "Wave 1 Codebook.pdf" prints for that variable; the labels are the abbreviated
#   question text the deposit published, and no fuller wording exists in the deposit,
#   so nothing is padded out. `option_text`/`resp` come from the value labels; codes 8
#   ("skipped") and 9 ("not asked") are already NaN in the data and are not emitted.
#   mapping_basis=data_labels, text_source=study_materials.
#
# Item codes: <battery>_<slug of the label's own per-item suffix>, so the code is
#   derived from the wording rather than from column position, and is reversible. The
#   slug is lower-cased, non-alphanumerics collapsed to "_", truncated to 40 chars, and
#   asserted unique within its battery.
#
# Scope of this pass: wave 1 only. Waves 2-5 are in the same deposit and are the
#   obvious extension, but only the wave 1 file carries a `caseid` column -- the wave 2
#   file has no column of that name, so linking respondents across waves needs the
#   codebooks read first and is left as open work rather than guessed at.
#
# Batteries NOT shipped, with reasons:
#   "How much do you trust each of the following on coronavirus" (19 items) -- the
#     value labels run 1 "A great deal" .. 4 "Not at all" and then 5 "Don't know", so
#     the 5 is not a scale extreme and `resp` would carry two directions at once.
#   media-exposure batteries ("How many days in the past week ...") and the remaining
#     single questions, screeners, demographics, weights and open codes -- not
#     multi-item scales, or not ordinal responses.
# Tables (all 1000 respondents, wave 1):
#   henderson_2023_la_covid_health_emotion     11 items, 1-5
#   henderson_2023_la_covid_economic_emotion    9 items, 1-5
#   henderson_2023_la_covid_worry               8 items, 1-5
#   henderson_2023_la_covid_health_threat       9 items, 1-5
#   henderson_2023_la_covid_financial_threat    9 items, 1-5
#   henderson_2023_la_covid_comfort            14 items, 1-4
#   henderson_2023_la_covid_policy_support      9 items, 1-5
#   henderson_2023_la_covid_racial_resent       4 items, 1-5
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s3"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "henderson_2023_la_covid"
URL = "https://dataverse.harvard.edu/api/access/datafile/7047437?format=original"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# label prefix -> (table suffix, n items, permitted values)
BATTERIES = {
    "health risks of the coronavirus outbreak":
        ("health_emotion", "he", 11, [1, 2, 3, 4, 5]),
    "economic risks of the coronavirus outbreak":
        ("economic_emotion", "ee", 9, [1, 2, 3, 4, 5]),
    "How worried are you":
        ("worry", "worry", 8, [1, 2, 3, 4, 5]),
    "threat of the coronavirus outbreak to the health of":
        ("health_threat", "hthreat", 9, [1, 2, 3, 4, 5]),
    "threat of coronavirus to the financial situation of":
        ("financial_threat", "fthreat", 9, [1, 2, 3, 4, 5]),
    "comfortable or uncomfortable with":
        ("comfort", "comfort", 14, [1, 2, 3, 4]),
    "support or oppose the government doing each of the following":
        ("policy_support", "policy", 9, [1, 2, 3, 4, 5]),
    "Racial resentment":
        ("racial_resent", "rr", 4, [1, 2, 3, 4, 5]),
}
SKIP_BATTERY = "How much do you trust each of the following on coronavirus"


def fetch() -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    p = RAW_DIR / "wave1.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def screen_for_pii(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"[pii] examined {df.shape[1]} columns, {len(text_cols)} of them string-typed")
    assert df.shape[1] > 0
    pats = [r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", r"\+?\d[\d \-()]{8,}",
            r"^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$",
            r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}"]
    hits = [(c, p) for c in text_cols for p in pats
            if df[c].dropna().astype(str).str.contains(p, regex=True, na=False).any()]
    assert not hits, hits
    print("[pii] no string column carries an identifier pattern; the file's only "
          "geography is parish (county-level), which is not shipped")


def slug(s: str, prefix: str) -> str:
    s = re.sub(r"^q\d+_grid\s*--\s*", "", s.strip())
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s.lower()).strip("_")
    return f"{prefix}_{s[:40].strip('_')}"


def emit(name: str, t: pd.DataFrame, pv: list) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert not t.duplicated(["id", "item"]).any(), name
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3, name
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {name} {c.name}: {c.detail[:160]}")
    rep = irw_validate.validate_frame(t, label=name, profile="upload",
                                      context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, (name, [(f.check, f.message) for f in rep.errors])
    for f in rep.warnings:
        print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
          f"resp={t['resp'].min():g}-{t['resp'].max():g}")


ITEMS_DIR = OUT_DIR / "items"
# The one battery whose item text is held rather than shipped.
HELD_ITEMTEXT = {"henderson_2023_la_covid_racial_resent":
                 "Kinder & Sanders racial-resentment items; no rights-register row"}
ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response", "option_text",
                 "resp"]
INSTRUMENT = ("LSU Manship School Public Policy Research Lab Louisiana coronavirus "
              "panel survey (Henderson, NSF #2031591), wave 1")


def write_itemtext(name: str, codes: dict, labels: dict,
                   value_labels: dict, resp_seen: set) -> None:
    """One row per item x response option, from the .sav's two label levels."""
    rows = []
    for col, code in codes.items():
        vl = value_labels[col]
        for val, text in sorted(vl.items()):
            if val not in resp_seen:
                continue  # 8 'skipped' / 9 'not asked': already NaN in the data
            rows.append({"table": name, "section_id": f"{name}_1", "item": code,
                         "instrument": INSTRUMENT, "instructions": "",
                         "section_prompt": "", "item_text": labels[col],
                         "correct_response": "", "option_text": text,
                         "resp": int(val)})
    t = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
    assert set(t["item"]) == set(codes.values()), name
    assert set(t["resp"]) == resp_seen, (name, sorted(set(t["resp"])), sorted(resp_seen))
    assert not t.duplicated(["item", "resp"]).any(), name
    assert (t["item_text"].str.len() > 0).all() and (t["option_text"].str.len() > 0).all()
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(ITEMS_DIR / f"{name}__items.csv", index=False)
    print(f"[itemtext] {name}__items.csv: {len(t)} rows "
          f"({t['item'].nunique()} items x {t['resp'].nunique()} options)")


def convert() -> None:
    df, meta = pyreadstat.read_sav(str(fetch()))
    assert df.shape == (1000, 191), df.shape
    screen_for_pii(df)
    labels = {c: str(meta.column_names_to_labels.get(c) or "") for c in df.columns}

    tables: dict[str, tuple[pd.DataFrame, list]] = {}
    used = {"caseid"}
    for prefix, (suffix, code_prefix, n, pv) in BATTERIES.items():
        cols = [c for c in df.columns if labels[c].startswith(prefix + " -- ")]
        assert len(cols) == n, (prefix, len(cols), n)
        codes = {c: slug(labels[c].split(" -- ", 1)[1], code_prefix) for c in cols}
        assert len(set(codes.values())) == n, (prefix, sorted(codes.values()))
        used |= set(cols)
        long = (df[["caseid"] + cols]
                .rename(columns={"caseid": "id", **codes})
                .melt(id_vars="id", var_name="item", value_name="resp"))
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all(), prefix
        long["id"] = long["id"].astype("int64")
        name = f"henderson_2023_la_covid_{suffix}"
        tbl = long[["id", "item", "resp"]].reset_index(drop=True)
        tables[name] = (tbl, pv)
        print(f"[codes] {name}: " + ", ".join(sorted(codes.values())))
        if name in HELD_ITEMTEXT:
            print(f"[itemtext] {name}: HELD -- {HELD_ITEMTEXT[name]}")
        else:
            write_itemtext(name, codes, labels,
                           {c: meta.variable_value_labels[c] for c in cols},
                           set(tbl["resp"].astype(int)))

    trust = [c for c in df.columns if labels[c].startswith(SKIP_BATTERY + " -- ")]
    assert len(trust) == 19, len(trust)
    skipped = [c for c in df.columns if c not in used]
    print(f"[books] 191 source columns: 1 id + {len(used) - 1} items shipped across "
          f"{len(tables)} tables; {len(skipped)} skipped -- of which {len(trust)} are "
          "the trust battery (value 5 is 'Don't know', not a scale extreme) and the "
          f"other {len(skipped) - len(trust)} are non-scale survey content "
          "(single questions, screeners, media-exposure day counts, demographics, "
          "the survey weight)")
    assert len(used) - 1 + len(skipped) == 190

    assert len(set(tables)) == len(tables)
    assert max(len(k) for k in tables) <= 40
    for name, (t, pv) in tables.items():
        emit(name, t, pv)


if __name__ == "__main__":
    convert()
