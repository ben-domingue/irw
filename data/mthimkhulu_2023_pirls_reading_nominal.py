"""PIRLS 2023 grade-4 reading -- the multiple-choice option choices, as
nominal-standard data.

Source: https://researchdata.up.ac.za/articles/dataset/_/24784086
DOI: 10.25403/UPresearchdata.24784086
License: CC BY 4.0

**IRW's experimental *nominal* standard, not the core standard.** Output goes
to `automated_finding/output_noncore/`, the response is a `text` column, and
the biblio row belongs in the separate nominal sheet -- not the main IRW
dictionary.

`data/mthimkhulu_2023_pirls_reading.py` builds the core achievement table, in
which the four multiple-choice items are scored 1/0 against the key marked by
an asterisk in their value labels. Scoring is what makes them commensurate
with the eleven constructed-response items, but it throws away *which*
distractor each learner chose. This table keeps that: the response is the
option letter itself, an unordered category.

Table written (to output_noncore/)
----------------------------------
mthimkhulu_2023_pirls_reading_mc   4 items, responses "A".."D"

Coding notes
------------
* Only items whose value labels carry the A/B/C/D option convention are
  included; the constructed-response items are already scores and belong in
  the core table alone.
* The option letter is taken from the item's own value labels, with the
  correctness asterisk stripped -- so "C*" becomes "C". The key is not encoded
  in this table; it is recoverable from the core table, or from the labels.
* `6` ("Not reached") and `9` ("Omitted or invalid") are missing codes and are
  dropped rather than treated as categories.
* The same learner `id` keys the core table, so the two join.
"""

import os
import re
import tempfile

import pandas as pd
import pyreadstat
import requests

FILES_API = "https://api.figshare.com/v2/articles/24784086/files"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = os.path.join("..", "automated_finding", "output_noncore")
MISSING = {6.0, 9.0}


def load():
    f = requests.get(FILES_API, headers=UA, timeout=60).json()
    sav = [x for x in f if x["name"].lower().endswith(".sav")]
    assert len(sav) == 1
    raw = requests.get(sav[0]["download_url"], headers=UA, timeout=900)
    raw.raise_for_status()
    path = os.path.join(tempfile.gettempdir(), "pirls2023.sav")
    with open(path, "wb") as fh:
        fh.write(raw.content)
    return pyreadstat.read_sav(path)


def main():
    d, meta = load()
    d = d.rename(columns={"IDSTUD": "id"})
    rows = []
    items = []
    for c in [c for c in d.columns if re.match(r"^RP\d+Z\d+$", str(c))]:
        vl = meta.variable_value_labels.get(c, {})
        opts = {k: str(v).strip().rstrip("*")
                for k, v in vl.items()
                if re.fullmatch(r"[A-Z]\*?", str(v).strip())}
        if len(opts) < 2:
            continue          # constructed-response item; scores, not options
        items.append(c)
        col = d[c].where(~d[c].isin(MISSING))
        sub = pd.DataFrame({"id": d["id"], "item": c, "text": col.map(opts)})
        rows.append(sub.dropna(subset=["text"]))

    assert items, "no multiple-choice items found"
    long = pd.concat(rows, ignore_index=True)
    long["id"] = long["id"].astype(int)
    long = long[["id", "item", "text"]]

    assert not long.duplicated(["id", "item"]).any()
    assert long.groupby("item")["text"].nunique().min() > 1

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "mthimkhulu_2023_pirls_reading_mc.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"categories {sorted(long['text'].unique())}, "
          f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
