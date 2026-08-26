"""Mthimkhulu, Roux & Mihai (2023), University of Pretoria -- PIRLS 2023
grade-4 reading achievement, English and isiZulu.

Source: https://researchdata.up.ac.za/articles/dataset/_/24784086
DOI: 10.25403/UPresearchdata.24784086
Data: Grade 4 Reading Literacy Achievement data ... (PIRLS2023).sav
License: CC BY 4.0

South African grade-4 learners' item-level responses to the PIRLS 2023
achievement booklets. Found by the 2026-08-26 triage of the
educational-measurement term sweep -- large-scale reading assessment is
exactly the material the term gap was hiding, and `PIRLS` is in the
relevance filter's instrument list precisely for this.

Table written
-------------
mthimkhulu_2023_pirls_reading   15 items, resp 0-3

A companion nominal table (the raw multiple-choice option chosen) is built by
`data/mthimkhulu_2023_pirls_reading_nominal.py`.

Structure
---------
The file holds 12,422 learners x 73 columns, but only 15 of those columns are
items: `RP51Z01`..`RP51Z15`, the released "Octopuses" informational passage.
The rest are plausible values (`ASRREA01`-`05` and the four other
five-value achievement sets), sampling weights (`WGTADJ*`, `WGTFAC*`) and
identifiers. Plausible values are imputed proficiency draws, not responses,
and are excluded.

**PIRLS uses matrix sampling**: each learner receives one of 18 booklets, so
only 1,894 of the 12,422 saw this passage and per-item counts run 1,122-1,769.
The table is therefore 1,894 learners deep, not 12,422, and that is the
correct denominator rather than a defect.

Coding notes
------------
* **Item text is in the SPSS variable labels** ("WHAT DO OCTOPUSES USE TO MAKE
  DOORS", "TWO WAYS THAT OCTOPUSES ESCAPE THEIR PREDATORS"), and item ids are
  the source column names, so an item-text pass joins directly.
* **The 11 constructed-response items are already scored** and ship as stored:
  seven are 0-1 (Unacceptable/Acceptable), three are 0-2 (No/Partial/Complete
  Comprehension) and one is 0-3. Per-item maxima therefore vary by design,
  as in `lee_2020_alcohol_use`.
* **The 4 multiple-choice items are scored here, not shipped raw.** They store
  which option was chosen (1-4 = A-D), which is nominal; the correct option is
  marked with an asterisk in each item's own value labels (`C*`, `A*`, `B*`),
  so the script reads the key off the file and scores 1 = correct, 0 = not.
  Scoring is what makes them commensurate with the constructed-response items
  in a single achievement table. The discarded information -- which distractor
  a learner picked -- is preserved separately in the nominal companion table.
* `6` ("Not reached") and `9` ("Omitted or invalid") are the instrument's
  missing codes and are set to NA. Neither actually occurs in this file, but
  the script filters them so a future version cannot slip them in as scores.
* Covariates: learner sex, test language, booklet, and the school and class
  ids, which make the nesting available.
"""

import io
import os
import re
import tempfile

import pandas as pd
import pyreadstat
import requests

FILES_API = "https://api.figshare.com/v2/articles/24784086/files"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
MISSING = {6.0, 9.0}

COVS = {"ITSEX": "cov_sex", "ITLANG_SA": "cov_test_language",
        "IDBOOK": "cov_booklet", "IDSCHOOL": "cov_school", "IDCLASS": "cov_class"}


def load():
    f = requests.get(FILES_API, headers=UA, timeout=60).json()
    sav = [x for x in f if x["name"].lower().endswith(".sav")]
    assert len(sav) == 1, [x["name"] for x in f]
    raw = requests.get(sav[0]["download_url"], headers=UA, timeout=900)
    raw.raise_for_status()
    path = os.path.join(tempfile.gettempdir(), "pirls2023.sav")
    with open(path, "wb") as fh:
        fh.write(raw.content)
    return pyreadstat.read_sav(path)


def mc_key(value_labels):
    """The correct option's numeric code, read off the asterisk convention."""
    starred = [k for k, v in value_labels.items() if str(v).strip().endswith("*")]
    return starred[0] if len(starred) == 1 else None


def main():
    d, meta = load()
    items = [c for c in d.columns if re.match(r"^RP\d+Z\d+$", str(c))]
    assert items, "no RP items found"

    d = d.rename(columns={"IDSTUD": "id"}).rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]
    assert d["id"].is_unique

    scored = d[["id"] + cov_cols].copy()
    n_mc = 0
    for c in items:
        col = d[c].where(~d[c].isin(MISSING))
        key = mc_key(meta.variable_value_labels.get(c, {}))
        if key is not None:
            col = (col == key).astype(float).where(col.notna())
            n_mc += 1
        scored[c] = col

    long = scored.melt(id_vars=["id"] + cov_cols, value_vars=items,
                       var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].between(0, 3).all()
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "mthimkhulu_2023_pirls_reading.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(n_id*n_it):.3f} "
          f"[{n_mc} multiple-choice items scored against their own key]")


if __name__ == "__main__":
    main()
