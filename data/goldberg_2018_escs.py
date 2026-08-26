"""Goldberg (2018), Harvard Dataverse -- the Eugene-Springfield Community
Sample (ESCS).

Source: https://dataverse.harvard.edu/dataverse/ESCS-Data
License: CC0 1.0 (every dataset in the collection)

A community sample of ~1,100 adults in Eugene and Springfield, Oregon, mailed
a long series of personality, interest and health questionnaires over many
years. The collection holds 28 datasets; the same `id` runs through all of
them and joins to a shared demographics file, so the instruments below are
linked measurements on one panel rather than 19 unrelated samples.

Found 2026-08-26 by the educational-measurement/psychometric term sweep added
on 2026-08-25 -- `IPIP` was one of the probe terms that had never been
searched in any mode.

Tables written
--------------
One per instrument, `goldberg_2018_<acronym>`. All carry the shared
demographic covariates. See INSTRUMENTS below for the full list.

Which datasets are and are not included
---------------------------------------
Included: the 19 datasets whose file is a homogeneous block of ordinal item
responses on a single scale.

Deliberately excluded, because their columns mix raw items with derived or
non-ordinal material and the collection ships no codebook that would let the
two be separated safely:

    ( 3) NEO-PI-R                    275 cols spanning 175 distinct values 0-180
    (17) Comprehensive Health Survey 271 cols, 169 values 0-278
    (20) Six Factor Personality Q.   132 cols, 155 values 1-86
    (16) Self/Peer Inventories        93 cols,  92 values 1-94
    (21) Personality, Emotions, Att. 349 cols, 15 values 0-18
    ( 6) Activity Vector Analysis    values to 99,119 -- not item responses
    (22) Thematic Apperception Test  values to 11,289 -- not item responses
    (18) Multidimensional Personality Q. -- ships no raw `.tab` at all
    ( 0) Documentation and demographics -- used here as the covariate source

Those are worth a second pass with the collection's `TechnicalReport_ESCS.doc`
in hand; several are large and would be valuable if the raw items can be
isolated.

Coding notes
------------
* Each dataset ships `<NAME>.tab` (raw items) alongside `<NAME>_scales.tab`
  (derived scale scores) and `-1`-suffixed copies that are Dataverse version
  artifacts. Only the raw, unsuffixed file is read.
* **Missingness is real, not imputation.** Densities range from 0.65 (IPIP) to
  1.00; the IPIP file in particular combines every IPIP item ever administered
  to the sample across several mailings, so most respondents saw a subset.
  Every value in every included file is an integer within its scale -- there
  are no fractional cells anywhere in the collection.
* Demographics (`SEX`, `AGE`, `EDUC`, `ETHNIC`, `EMPLOY`, `MARITAL`) are
  joined from dataset ( 0) and carried as covariates. `SEXN` is dropped as a
  numeric duplicate of `SEX`.
* **SPA's letter-coded columns split two ways.** 82 of its 528 columns hold
  letters rather than the 0-9 ordinal block.
  - `TRPAIR1`..`TRPAIR80` are the collection's "80 forced-choice BFI pairs"
    (per `TechnicalReport_ESCS.doc`): each item offers two descriptors and the
    respondent picks one. With exactly **two** response categories the
    distinction between ordered and unordered is vacuous -- a dichotomy is
    trivially ordinal, and standard dichotomous IRT applies directly -- so
    this ships as a **core** table, `goldberg_2018_spa_bfi_forced_choice`,
    alongside the collection's other true/false instruments (CPI, HPI,
    JPI-R). "A" is coded 1 and "B" 2, matching CPI's own 1/2 coding in this
    same collection. **Which descriptor is "A" is a property of the form, not
    of the trait**, so the direction is arbitrary per item; a dichotomous
    model absorbs that, but do not read 1 < 2 as a trait ordering.
  - `COMPUT7` and `COMPUT9` have up to twelve unlabelled categories and stay
    genuinely nominal; `data/goldberg_2018_escs_nominal.py` ships those under
    IRW's experimental nominal standard (`text` column, output to
    `automated_finding/output_noncore/`, biblio row to the separate nominal
    sheet).
* **Zero-variance items are dropped** where they occur, not the instrument
  containing them; the per-table output reports how many and which.
* Source item names (`c1`..`c462`, `s1`..`s430`, ...) are kept so item text
  can join back; the IPIP deposit additionally ships `IPIP2539items.xls` with
  the text of all 2,539 items.
"""

import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
DEMOGRAPHICS = ("10.7910/DVN/VGMXJX", "demographics.tab")

# doi, raw file, table suffix, expected item count, (lo, hi)
INSTRUMENTS = [
    ("10.7910/DVN/GCV3ZZ", "EPS.tab",      "eps",      579, (1, 7)),
    ("10.7910/DVN/IOA6EE", "SPA.tab",      "spa",      528, (0, 9)),
    ("10.7910/DVN/GHYMEV", "525PDA.tab",   "pda525",   525, (1, 7)),
    ("10.7910/DVN/LHHONE", "SDV.tab",      "sdv",      517, (1, 9)),
    ("10.7910/DVN/XJ6MXH", "PRS.tab",      "prs",      508, (1, 7)),
    ("10.7910/DVN/LXKJIV", "BRI.tab",      "bri",      504, (1, 5)),
    ("10.7910/DVN/QYKXUE", "PAS.tab",      "pas",      498, (1, 7)),
    ("10.7910/DVN/VBLMYO", "CPI.tab",      "cpi",      462, (1, 2)),
    ("10.7910/DVN/BTNABX", "PPQ.tab",      "ppq",      432, (0, 9)),
    ("10.7910/DVN/WV5BYC", "SBO.tab",      "sbo",      430, (1, 5)),
    ("10.7910/DVN/ZNGS1K", "360PDA.tab",   "pda360",   360, (1, 9)),
    ("10.7910/DVN/ANMXHR", "CISS.tab",     "ciss",     320, (1, 6)),
    ("10.7910/DVN/DUP1TT", "JPI-R.tab",    "jpir",     300, (0, 1)),
    ("10.7910/DVN/MH6FCC", "DOP.tab",      "dop",      299, (1, 9)),
    ("10.7910/DVN/TERJAK", "TCI.tab",      "tci",      295, (1, 5)),
    ("10.7910/DVN/YMBILD", "HPI.tab",      "hpi",      206, (0, 1)),
    ("10.7910/DVN/ID7PMC", "16PF.tab",     "pf16",     186, (0, 3)),
    ("10.7910/DVN/SVGXVF", "HPQ.tab",      "hpq",       40, (0, 5)),
    ("10.7910/DVN/UF52WY", "IPIP2539.tab", "ipip",    2539, (1, 5)),
]

COVS = {"SEX": "cov_sex", "AGE": "cov_age", "EDUC": "cov_education",
        "ETHNIC": "cov_ethnicity", "EMPLOY": "cov_employment",
        "MARITAL": "cov_marital_status"}

_S = requests.Session()
_S.headers.update(UA)


def _fetch(doi: str, filename: str | None = None) -> pd.DataFrame:
    """Read a dataset's raw item file.

    `filename` is optional and only used to disambiguate. Filenames in this
    collection are not predictable (`525_PDA.tab` vs `525PDA_words.txt`,
    `JPI-R.tab`, `16PF.tab`), so the raw file is selected by rule rather than
    hardcoded: the largest `.tab` that is neither a `_scales` file (derived
    scale scores) nor a `-1` copy (a Dataverse version artifact).
    """
    meta = _S.get(f"{BASE}/api/datasets/:persistentId/",
                  params={"persistentId": f"doi:{doi}"}, timeout=120
                  ).json()["data"]["latestVersion"]
    files = [f["dataFile"] for f in meta["files"]]
    if filename:
        exact = [f for f in files if f["filename"] == filename]
        if exact:
            files = exact
    cands = [f for f in files if f["filename"].endswith(".tab")
             and "scale" not in f["filename"].lower()
             and not re.search(r"-1\.tab$", f["filename"])]
    assert cands, (doi, [f["filename"] for f in files])
    f = max(cands, key=lambda x: x.get("filesize", 0))
    raw = _S.get(f"{BASE}/api/access/datafile/{f['id']}", timeout=900)
    raw.raise_for_status()
    return pd.read_csv(io.BytesIO(raw.content), sep="\t", low_memory=False)


def main():
    dem = _fetch(*DEMOGRAPHICS).rename(columns={"ID": "id"}).rename(columns=COVS)
    dem = dem[["id"] + [c for c in COVS.values() if c in dem.columns]]
    assert dem["id"].is_unique
    cov_cols = [c for c in dem.columns if c != "id"]

    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for doi, filename, suffix, n_expected, (lo, hi) in INSTRUMENTS:
        d = _fetch(doi, filename)
        idcol = d.columns[0]
        items = list(d.columns[1:])
        assert len(items) == n_expected, (suffix, len(items), n_expected)
        n_declared = len(items)
        assert d[idcol].is_unique, f"{suffix}: {idcol} is not unique"

        # Some files interleave letter-coded multiple-choice columns with the
        # ordinal block (SPA has 82 such columns, values "A".."H"). Those are
        # nominal, so they are not IRW responses at all -- drop the whole
        # column, not just its cells, and report how many.
        nonnumeric = []
        for c in items:
            co = pd.to_numeric(d[c], errors="coerce")
            if (co.isna() & d[c].notna()).any():
                nonnumeric.append(c)
        items = [c for c in items if c not in nonnumeric]

        long = d.rename(columns={idcol: "id"}).melt(
            id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        # Everything that survives is integral; a fractional value would mean a
        # derived column slipped into the block.
        assert (long["resp"] % 1 == 0).all(), f"{suffix}: fractional values present"
        long["resp"] = long["resp"].astype(int)

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        # Zero-variance items carry no information and are not item responses
        # in any useful sense; drop them rather than the whole instrument, the
        # same call made for `liu_2025_ydcy`'s constant YDCY1.
        nun = long.groupby("item")["resp"].nunique()
        constant = sorted(nun[nun <= 1].index)
        if constant:
            long = long[~long["item"].isin(constant)]
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        long = long.merge(dem, on="id", how="left")
        long = long[["id", "item", "resp"] + cov_cols]

        path = os.path.join(OUTDIR, f"goldberg_2018_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        drops = []
        if nonnumeric:
            drops.append(f"{len(nonnumeric)} non-numeric col(s) dropped: {nonnumeric[:3]}")
        if constant:
            drops.append(f"{len(constant)} constant item(s) dropped: {constant[:3]}")
        note = ("  [" + "; ".join(drops) + "]") if drops else ""
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}{note}", flush=True)
    total += _forced_choice(dem, cov_cols)
    print(f"\n{len(INSTRUMENTS) + 1} tables, {total:,} responses")


def _forced_choice(dem, cov_cols) -> int:
    """SPA's 80 forced-choice BFI pairs, as a dichotomous core table."""
    d = _fetch("10.7910/DVN/IOA6EE")
    idcol = d.columns[0]
    items = [c for c in d.columns if re.match(r"^TRPAIR\d+$", str(c))]
    assert len(items) == 80, len(items)

    long = d.rename(columns={idcol: "id"}).melt(
        id_vars=["id"], value_vars=items, var_name="item", value_name="choice")
    long["choice"] = long["choice"].astype(str).str.strip()
    long = long[long["choice"].isin(["A", "B"])]
    long["resp"] = long["choice"].map({"A": 1, "B": 2})
    long = long.drop(columns=["choice"]).merge(dem, on="id", how="left")
    long = long[["id", "item", "resp"] + cov_cols]

    assert long["resp"].isin([1, 2]).all()
    assert long.groupby("item")["resp"].nunique().min() > 1
    assert not long.duplicated(["id", "item"]).any()

    path = os.path.join(OUTDIR, "goldberg_2018_spa_bfi_forced_choice.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
          f"resp 1-2 (A/B), density {len(long)/(n_id*n_it):.3f}")
    return len(long)


if __name__ == "__main__":
    main()
