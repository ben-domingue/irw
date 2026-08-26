"""Goldberg (2018), ESCS -- the nominal-standard columns carved out of (27)
Skills, Possessions, and Abilities (SPA).

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IOA6EE
DOI: 10.7910/DVN/IOA6EE
License: CC0 1.0

**This is IRW's experimental *nominal* standard, not the core standard.**
Output goes to `automated_finding/output_noncore/`, the response lives in a
`text` column rather than `resp`, and the biblio row belongs in the separate
nominal sheet -- not the main IRW dictionary.

`data/goldberg_2018_escs.py` builds the 19 core-standard tables from this
collection. When it reaches SPA it drops 82 of the file's 528 columns because
their values are letters, not ordinal codes. Those 82 are not junk -- they are
genuine responses in an unordered-category format -- so they are carved out
here instead of discarded.

Tables written (to output_noncore/)
-----------------------------------
goldberg_2018_spa_bfi_forced_choice   80 items, responses "A"/"B"
goldberg_2018_spa_computer_use         2 items, responses "A".."L"

What these are
--------------
The collection's `TechnicalReport_ESCS.doc` describes SPA as including
"79 new IPIP items ... plus **80 forced-choice BFI pairs**", and asks
respondents to indicate "their present computer use and skills".

* `TRPAIR1`..`TRPAIR80` are those forced-choice Big Five pairs: each item
  presents two descriptors and the respondent picks one. "A" and "B" identify
  which member of the pair was chosen, so the response is an unordered
  category -- the nominal standard's first subtype ("which option was picked,
  not correctness"). Coding it 0/1 would imply an order the instrument does
  not have.
* `COMPUT7` and `COMPUT9` are computer-use questions with up to twelve
  unlabelled categories ("A".."L"). Note the `COMPUT` family spans ten
  columns; the other eight are ordinal and stay in the core table, so
  membership here is decided by the values, not the name.

**A caveat on the computer-use table**: it is only two items, and the
collection ships no key for what "A".."L" mean, so its analytic value is
limited. It is included because the carve-out was asked for explicitly; drop
it if the thinness is not worth a row in the nominal sheet.

Coding notes
------------
* Blank strings are treated as missing, not as a category.
* Item ids keep their source names so item text can join back.
* No covariates are carried, matching the existing nominal outputs. The same
  `id` keys the 19 core ESCS tables, so demographics are joinable through
  those if needed.
"""

import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/IOA6EE"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = os.path.join("..", "automated_finding", "output_noncore")

BLOCKS = [
    (re.compile(r"^TRPAIR\d+$"), "spa_bfi_forced_choice", 80),
    (re.compile(r"^COMPUT\d+$"), "spa_computer_use",       2),
]


def _load() -> pd.DataFrame:
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    cands = [f["dataFile"] for f in meta["files"]
             if f["dataFile"]["filename"].endswith(".tab")
             and "scale" not in f["dataFile"]["filename"].lower()
             and not re.search(r"-1\.tab$", f["dataFile"]["filename"])]
    assert cands, [f["dataFile"]["filename"] for f in meta["files"]]
    f = max(cands, key=lambda x: x.get("filesize", 0))
    raw = s.get(f"{BASE}/api/access/datafile/{f['id']}", timeout=900)
    raw.raise_for_status()
    return pd.read_csv(io.BytesIO(raw.content), sep="\t", low_memory=False)


def main():
    d = _load()
    idcol = d.columns[0]
    assert d[idcol].is_unique

    os.makedirs(OUTDIR, exist_ok=True)
    for pat, suffix, n_expected in BLOCKS:
        # Only the letter-coded members of each family belong here. COMPUT in
        # particular spans ten columns of which eight are ordinal and already
        # live in the core table, so the family name alone is not the filter.
        def _is_nominal(c):
            co = pd.to_numeric(d[c], errors="coerce")
            return bool((co.isna() & d[c].notna()).any())

        items = [c for c in d.columns if pat.match(str(c)) and _is_nominal(c)]
        assert len(items) == n_expected, (suffix, len(items))

        long = d.rename(columns={idcol: "id"}).melt(
            id_vars=["id"], value_vars=items, var_name="item", value_name="text")
        long["text"] = long["text"].astype(str).str.strip()
        long = long[(long["text"] != "") & (long["text"].str.lower() != "nan")]
        long = long[["id", "item", "text"]]

        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["text"].nunique().min() > 1, f"{suffix}: constant item"

        path = os.path.join(OUTDIR, f"goldberg_2018_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"categories {sorted(long['text'].unique())[:12]}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
