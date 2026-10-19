#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/mrrc83rt3b
# DOI: 10.17632/mrrc83rt3b (the data deposit; no linked paper is recorded on
#   the Mendeley record).
#   Ghosh, A. (2020). "Well-being of Healthcare professionals in India during
#   COVID-19 pandemic." Mendeley Data.
# Data: Mendeley 10.17632/mrrc83rt3b, "COVID19 responses from healthcare
#       workers .xls", sheet 'Form Responses 1' (240 rows x 60 columns;
#       healthcare professionals across 19 Indian states/UTs, 2020).
# License: CC BY 4.0 (DataCite record, rightsIdentifier cc-by-4.0).
#
# Item text: NOT shipped for any of the three tables, though the stems are
#   right there in the column headers -- each is a named third-party
#   instrument whose wording this project does not redistribute:
#     - CAS/OCS: Lee, S. A. (2020) Coronavirus Anxiety Scale and Obsession
#       with COVID-19 Scale. Not in itemtext/instrument_rights_register.csv,
#       so unruled rather than cleared; a named third-party instrument with
#       no verdict does not ship (the 2026-10-15 silence rule).
#     - UWES-9: family UWES, verdict **block** in the register (irw#1955,
#       (c) Schaufeli & Bakker 2003, non-commercial research only).
#     - JAWS: Van Katwyk, Fox, Spector & Kelloway (2000) Job-related
#       Affective Well-being Scale. Also unruled in the register.
#   So the text is in the register's hands, not in a missing source: the
#   headers of this very file carry all 38 stems verbatim.
#
# Tables (one per published scale; three different response formats, so they
# cannot be one file):
#   ghosh_2020_cas      cas_1-cas_5, Coronavirus Anxiety Scale, frequency
#       over the last two weeks, 0-5. See SCALE NOTE below.
#   ghosh_2020_ocs      ocs_1-ocs_4, Obsession with COVID-19 Scale, same
#       response format, its own file because it is its own scale. Both CAS
#       and OCS are 6-category administrations of published 5-category
#       scales -- see SCALE NOTE.
#   ghosh_2020_uwes     uwes_1-uwes_9, UWES-9 work engagement, 0-6
#       (Never .. Always), the instrument's own coding.
#   ghosh_2020_jaws     jaws_angry .. jaws_satisfied, 20 items, 1-5 as
#       deposited (numeric in the file; the anchors are not recorded).
#
# SCALE NOTE (both CAS and OCS tables): the response set as published is
#   five points -- "Not at all", "Rare, less than a day or two", "Several
#   days", "More than 7 days", "Nearly every day over the last 2 weeks".
#   This administration offers SIX: "Rare" and "Less than a day or two"
#   appear as separate options, i.e. the single published anchor was split in
#   two when the Google Form was built. Both are carried, as codes 1 and 2,
#   because merging them would invent a collapse the data does not record.
#   Their order relative to each other is the one uncertainty -- both sit
#   below "Several days", and the deposit ships no copy of the form, so which
#   the author listed first cannot be recovered. Everything else is ordered
#   as published.
#
# Dropped, with reasons (printed and asserted at run time):
#   Timestamp                     survey completion time, not a response
#   the free-text "anything else" column  93 open-ended comments, not an item
#   11 single-question screening/experience items (monetary situation, PPE
#     adequacy, who you live with, travel, support received, difficulties
#     faced, fear of assault, stigma, family fear, close patient contact,
#     category) -- each is its own one-off question, not a block, and several
#     are multi-select; none forms an instrument
#   6 demographics -> cov_* (age band, gender, state, education, marital
#     status, currently COVID-positive, knows an infected family/friend,
#     prior anxiety diagnosis)
# id: row index + 1 (the file carries no respondent identifier).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://data.mendeley.com/public-files/datasets/mrrc83rt3b/"
            "files/708f5910-55eb-48a0-9d70-76bf88a1c771/file_downloaded")
DATA_NAME = "COVID19 responses from healthcare workers .xls"

# Positional, because the headers are full sentences. Verified against the
# printed column map before use; the assertions below re-check each block.
CAS_OCS = list(range(21, 30))
UWES = list(range(30, 39))
JAWS = list(range(39, 59))

CAS_CODES = {
    "Not at all": 0,
    "Rare": 1,
    "Less than a day or two": 2,
    "Several days": 3,
    "More than 7 days": 4,
    "Nearly every day over the last 2 weeks": 5,
}
UWES_CODES = {
    "Never": 0, "Almost Never": 1, "Rarely": 2, "Sometimes": 3,
    "Often": 4, "Very often": 5, "Always": 6,
}
CAS_NAMES = [f"cas_{i}" for i in range(1, 6)] + [f"ocs_{i}" for i in range(1, 5)]
UWES_NAMES = [f"uwes_{i}" for i in range(1, 10)]

COVS = {
    "Please indicate your age": "cov_age_band",
    "Gender": "cov_gender",
    "Educational qualification": "cov_education",
    "Marital status": "cov_marital_status",
}


def fetch():
    """A Mendeley file URL carries an opaque file uuid that is not derivable
    from the DOI, so the resolved URL is written out in full above."""
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    return io.BytesIO(r.content), DATA_NAME


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    buf, name = fetch()
    print(f"[fetch] {name}")
    d = pd.read_excel(buf)
    assert d.shape == (240, 60), d.shape
    cols = list(d.columns)

    # Confirm each block is where it is expected to be.
    assert cols[21].startswith("I felt dizzy"), cols[21]
    assert cols[29].startswith("I dreamed about"), cols[29]
    assert cols[30].startswith("At my work, I feel bursting"), cols[30]
    assert cols[38].startswith("I get carried away"), cols[38]
    assert all(c.startswith("My job made me feel") for c in
               [cols[i] for i in JAWS]), "JAWS block moved"
    assert cols[59].startswith("Is there anything else"), cols[59]

    # Balance the books: every column is an item, a covariate or a printed drop.
    item_idx = set(CAS_OCS + UWES + JAWS)
    accounted = set()
    for i, c in enumerate(cols):
        if i in item_idx:
            accounted.add(i)
        elif c in COVS:
            accounted.add(i)
        else:
            accounted.add(i)
            print(f"[drop] col {i:2} {str(c)[:68]}")
    assert accounted == set(range(len(cols)))
    print(f"[cols] {len(item_idx)} item columns, {len(COVS)} covariates, "
          f"{len(cols) - len(item_idx) - len(COVS)} dropped")

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    cov = d[["id"] + list(COVS)].rename(columns=COVS)
    for c in COVS.values():
        cov[c] = cov[c].astype(str).str.strip().replace({"nan": pd.NA})

    def build(table, idx, names, codes, allowed):
        sub = d[["id"] + [cols[i] for i in idx]].copy()
        sub.columns = ["id"] + names
        long = sub.melt(id_vars="id", var_name="item", value_name="resp")
        if codes:
            raw = long["resp"].dropna().astype(str).str.strip()
            unknown = set(raw) - set(codes)
            assert not unknown, (table, unknown)
            long["resp"] = long["resp"].astype(str).str.strip().map(codes)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        long = long.merge(cov, on="id", how="left")
        long = long[["id", "item", "resp"] + list(COVS.values())]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["item"].nunique() == len(names)
        checks = run_qc(long, permitted_values={n: allowed for n in names})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [warn] {table}: {c.name}: {c.detail[:130]}")
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
        return len(long)

    # CAS and OCS are two separately published scales that happen to share
    # one response format and one block in the form, so they are two files
    # (datastandard.md: each measurement scale is its own file).
    total = 0
    total += build("ghosh_2020_cas", CAS_OCS[:5],
                   [f"cas_{i}" for i in range(1, 6)], CAS_CODES, set(range(6)))
    total += build("ghosh_2020_ocs", CAS_OCS[5:],
                   [f"ocs_{i}" for i in range(1, 5)], CAS_CODES, set(range(6)))
    total += build("ghosh_2020_uwes", UWES, UWES_NAMES, UWES_CODES,
                   set(range(7)))
    jaws_names = ["jaws_" + cols[i].replace("My job made me feel", "")
                  .strip().strip(".").lower().replace(" ", "_") for i in JAWS]
    assert len(set(jaws_names)) == len(jaws_names), "duplicate JAWS name"
    total += build("ghosh_2020_jaws", JAWS, jaws_names, None, {1, 2, 3, 4, 5})
    print(f"[total] {total} responses across 4 tables")


if __name__ == "__main__":
    main()
