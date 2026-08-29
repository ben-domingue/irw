"""Torok et al. (2025), Zenodo -- "Trust, Awareness, and Risk Perception in the
Online Environment", a 1,003-respondent CATI survey of the Hungarian adult
population (fielded 2019).

Source: https://zenodo.org/records/15168213
DOI: 10.5281/zenodo.15168213
Data: hungary_online_trust_2019_10_15.sav
License: CC BY 4.0
Item text: shipped (SPSS variable + value labels carry the full Hungarian
    stem, per-item wording and every response anchor; the deposit also
    includes CATI_questionnaire.docx, not needed)

Tables written
--------------
torok_2025_internet_use_frequency      18 items, 1-5
torok_2025_manipulation_fear           13 items, 1-5
torok_2025_news_consumption             5 items, 1-3
torok_2025_news_source_frequency        8 items, 1-5
torok_2025_news_source_trust            8 items, 1-5
torok_2025_social_media_effects         4 items, 1-5
torok_2025_facebook_uses                4 items, 1-5
torok_2025_data_disclosure              8 items, 1-2
torok_2025_legality_knowledge           8 items, 1-2
torok_2025_data_security               12 items, 1-4
torok_2025_ai_acceptance                4 items, 1-3
torok_2025_discourse_responsibility     6 items, 1-5

Coding notes
------------
* Each table is one of the questionnaire's own item batteries, identified by
  the shared stem in its SPSS variable labels (`I2_1..I2_18` all begin "Milyen
  gyakorisággal használja Ön az internetet a következő célokra?"). Item ids are
  the source column names.
* **99 is the survey's no-answer / don't-know sentinel**, declared as such in
  every value-label set that uses it ("Nincs válasz", "Nem tudja"). Dropped as
  missing rather than shipped as a response level; the item text tables
  likewise carry only the substantive anchors.
* Batteries deliberately not shipped, all of them non-ordinal:
  `E4` (which devices -- check-all, each column constant at its own option
  index, so there is no response scale), `M10` (same shape), `M6` (five forced
  choices between two unranked statements, "a) ... b) ..."), and the many
  single-question items (`E1`-`E7`, `I1`, `I4`, ...), which would each be a
  one-item table.
* Response counts vary across tables because the internet-behaviour batteries
  were only asked of internet users (`E3`), so N per table is reported at
  write time rather than assumed to be 1,003.
* Covariates: `cov_region` (REGIO), `cov_county` (MEGYE),
  `cov_settlement_type` (TELTIP_2), `cov_age` (D2_1, years),
  `cov_gender` (D3), `cov_education` (D4, 6 categories),
  `cov_household_size` (D5_1), `cov_children_under14` (D6_1). The settlement
  *name* (`TELEP_1`, 486 distinct municipalities) is not shipped -- it is far
  more granular than the survey's own design requires.
"""

import csv
import os
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
ITEMDIR = os.path.join(AF, "itemtext_output")
REC = "15168213"
FILENAME = "hungary_online_trust_2019_10_15.sav"
MISSING = {99.0, -1.0, -2.0}

# prefix -> (table suffix, n items, max valid resp)
BATTERIES = [
    ("I2", "internet_use_frequency", 18, 5),
    ("I3", "manipulation_fear", 13, 5),
    ("H1", "news_consumption", 5, 3),
    ("M2", "news_source_frequency", 8, 5),
    ("M3", "news_source_trust", 8, 5),
    ("M5", "social_media_effects", 4, 5),
    ("M8", "facebook_uses", 4, 5),
    ("M14", "data_disclosure", 8, 2),
    ("M16", "legality_knowledge", 8, 2),
    ("M15", "data_security", 12, 4),
    ("M17", "ai_acceptance", 4, 3),
    ("M18", "discourse_responsibility", 6, 5),
]
COVS = {"REGIO": "cov_region", "MEGYE": "cov_county",
        "TELTIP_2": "cov_settlement_type", "D2_1": "cov_age",
        "D3": "cov_gender", "D4": "cov_education",
        "D5_1": "cov_household_size", "D6_1": "cov_children_under14"}


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{FILENAME}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == FILENAME)
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
    return pyreadstat.read_sav(path)


def split_stem(label):
    """Battery labels are '<shared stem> - <item>' or '<stem> ... <item>?'."""
    if " - " in label:
        stem, item = label.split(" - ", 1)
        return stem.strip(), item.strip()
    if " … " in label:
        stem, item = label.split(" … ", 1)
        return stem.strip(), item.strip()
    return "", label.strip()


def write_items(name, cols, labels, vls, maxresp):
    rows = []
    stems = {split_stem(labels[c])[0] for c in cols}
    instructions = stems.pop() if len(stems) == 1 and stems != {""} else ""
    for c in cols:
        _, text = split_stem(labels[c])
        for val, opt in sorted(vls[c].items()):
            if val in MISSING or val > maxresp:
                continue
            # unlabeled midpoints of a 1-5 anchor set come through as the
            # bare number ("2"); leave those blank rather than padding
            label = "" if opt.strip() == str(int(val)) else opt
            rows.append([name, f"{name}_1", c, instructions or name,
                         instructions, "", text, "", label, int(val)])
    path = os.path.join(ITEMDIR, f"{name}__items.csv")
    assert not os.path.exists(path), name
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["table", "section_id", "item", "instrument",
                    "instructions", "section_prompt", "item_text",
                    "correct_response", "option_text", "resp"])
        w.writerows(rows)
    return len(rows)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(ITEMDIR, exist_ok=True)
    df, meta = load()
    labels, vls = meta.column_names_to_labels, meta.variable_value_labels
    assert len(df) == 1003, len(df)
    d = df.rename(columns={"sys_cptid": "id"})
    assert d["id"].is_unique

    total, itext, ntab = 0, 0, 0
    for prefix, suffix, n, maxresp in BATTERIES:
        cols = [f"{prefix}_{i}" for i in range(1, n + 1)]
        for c in cols:
            assert c in d.columns, c
        long = d[["id"] + cols + list(COVS)].melt(
            id_vars=["id"] + list(COVS), value_vars=cols,
            var_name="item", value_name="resp")
        long = long[~long["resp"].isin(MISSING)].dropna(subset=["resp"])
        long = long.rename(columns=COVS)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + list(COVS.values())]

        assert long["resp"].between(1, maxresp).all(), prefix
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100, (prefix, long["id"].nunique())
        assert long["item"].nunique() == n
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"torok_2025_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        total += len(long)
        ntab += 1
        print(f"{name}: {long['id'].nunique()} respondents x {n} items = "
              f"{len(long)} responses")
        itext += write_items(name, cols, labels, vls, maxresp)

    print(f"\n{ntab} tables, {total:,} responses; {itext} item text rows")


if __name__ == "__main__":
    main()
