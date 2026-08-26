"""Goldberg (2018), ESCS -- the nominal-standard columns carved out of (27)
Skills, Possessions, and Abilities (SPA).

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/IOA6EE
DOI: 10.7910/DVN/IOA6EE
License: CC0 1.0

**This is IRW's experimental *nominal* standard, not the core standard.**
Output goes to `automated_finding/output_noncore/`, the response lives in a
`text` column rather than `resp`, and the biblio row belongs in the separate
nominal sheet -- not the main IRW dictionary.

`data/goldberg_2018_escs.py` builds the core-standard tables from this
collection. When it reaches SPA it sets aside 82 of the file's 528 columns
because their values are letters rather than ordinal codes. Eighty of those
are the forced-choice BFI pairs and are dichotomous, so that script ships them
as a core table itself; the two that remain are genuinely
multi-category and are handled here.

Table written (to output_noncore/)
----------------------------------
goldberg_2018_spa_computer_use   2 items, responses "A".."L"

What these are
--------------
The collection's `TechnicalReport_ESCS.doc` describes SPA as including
"79 new IPIP items ... plus **80 forced-choice BFI pairs**", and asks
respondents to indicate "their present computer use and skills".

* `COMPUT7` and `COMPUT9` are computer-use questions with up to twelve
  unlabelled categories ("A".."L") and no key for what they mean. Twelve
  unordered categories is genuinely nominal. Note the `COMPUT` family spans
  ten columns; the other eight are ordinal and stay in the core table, so
  membership here is decided by the values, not the name.
* `TRPAIR1`..`TRPAIR80`, the collection's 80 forced-choice BFI pairs, are
  **not** here. They have exactly two categories, and a dichotomy is trivially
  ordinal -- standard dichotomous IRT applies directly -- so
  `data/goldberg_2018_escs.py` ships them as the core table
  `goldberg_2018_spa_bfi_forced_choice` with "A"/"B" coded 1/2, matching CPI's
  own coding elsewhere in this collection. (ben-domingue, 2026-08-26.)

**A caveat**: this is only two items, and the collection ships no key for what
"A".."L" mean, so its analytic value is limited. It is included because the
carve-out was asked for explicitly; drop it if the thinness is not worth a row
in the nominal sheet.

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
    (re.compile(r"^COMPUT\d+$"), "spa_computer_use", 2),
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
