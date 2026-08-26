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
One per **instrument block**, `goldberg_2018_<mailing>[_<block>]`, all carrying
the shared demographic covariates.

**Why blocks and not one table per mailing.** These are omnibus mailings: a
single questionnaire commonly bundles several distinct instruments on
different response scales. `TechnicalReport_ESCS.doc` says so explicitly --
the Personal Reactions Survey, for instance, contains "the new 192-item
HEXACO Personality Inventory", the 20 BAS/BIS items, 23 Gray-Wilson markers,
and preference ratings for "Music (22 kinds), Reading (35 kinds)". Shipping a
mailing as one table would mix 1-5, 1-7, 1-3 and 1-4 responses under one
`resp` column, which is both wrong per the data standard and quietly
misleading. So each mailing is split into blocks by column-name family and
response scale, and each block ships as its own table.

Block names come from the technical report where it identifies them
unambiguously (the item counts match: `pc`[192] is the HEXACO-PI, `v`[342] the
VIA-IS adaptation, `value`[66] the Schwartz Value Survey); otherwise the
source prefix is used as-is rather than guessed at.

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
* **Zero-variance items are dropped** where they occur, not the block
  containing them; the per-table output reports how many and which.
* **Administrative columns are excluded.** `submiss` in the HPQ and `smiss`
  in the 16PF are missing-response counts, not items -- each is the only
  column in its file outside the instrument's scale, and `submiss` is 94.8%
  zero where all 39 real HPQ items are 1-5 with no zeros at all.
* **Blocks smaller than MIN_BLOCK items are not shipped.** A three-column
  fragment is not an instrument; the run prints what it skipped.
* **Count columns are excluded**: the PPQ's `vitamin*` records how many
  supplements a respondent takes, not a rating.
* Source item names (`c1`..`c462`, `s1`..`s430`, ...) are kept so item text
  can join back; the IPIP deposit additionally ships `IPIP2539items.xls` with
  the text of all 2,539 items.
"""

import collections
import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
DEMOGRAPHICS = ("10.7910/DVN/VGMXJX", "demographics.tab")

# doi, raw file (a hint only -- see _fetch), mailing slug
MAILINGS = [
    ("10.7910/DVN/GCV3ZZ", "EPS.tab",      "eps"),
    ("10.7910/DVN/IOA6EE", "SPA.tab",      "spa"),
    ("10.7910/DVN/GHYMEV", "525_PDA.tab",  "pda525"),
    ("10.7910/DVN/LHHONE", "SDV.tab",      "sdv"),
    ("10.7910/DVN/XJ6MXH", "PRS.tab",      "prs"),
    ("10.7910/DVN/LXKJIV", "BRI.tab",      "bri"),
    ("10.7910/DVN/QYKXUE", "PAS.tab",      "pas"),
    ("10.7910/DVN/VBLMYO", "CPI.tab",      "cpi"),
    ("10.7910/DVN/BTNABX", "PPQ.tab",      "ppq"),
    ("10.7910/DVN/WV5BYC", "SBO.tab",      "sbo"),
    ("10.7910/DVN/ZNGS1K", "360PDA.tab",   "pda360"),
    ("10.7910/DVN/ANMXHR", "CISS.tab",     "ciss"),
    ("10.7910/DVN/DUP1TT", "JPI-R.tab",    "jpir"),
    ("10.7910/DVN/MH6FCC", "DOP.tab",      "dop"),
    ("10.7910/DVN/TERJAK", "TCI.tab",      "tci"),
    ("10.7910/DVN/YMBILD", "HPI.tab",      "hpi"),
    ("10.7910/DVN/ID7PMC", "16PF.tab",     "pf16"),
    ("10.7910/DVN/SVGXVF", "HPQ.tab",      "hpq"),
    ("10.7910/DVN/UF52WY", "IPIP2539.tab", "ipip"),
]

# Blocks the technical report names unambiguously; the item counts match.
# (mailing, source prefix) -> table suffix. Anything unlisted keeps its prefix.
BLOCK_NAMES = {
    ("dop", "ai_"):    "avocational_interests",
    ("dop", "vig_"):   "ab5c_vignettes",
    ("eps", "q"):      "ipip",
    ("eps", "rcesd"):  "cesd",
    ("eps", "event"):  "life_events",
    ("eps", "spirit"): "spirituality",
    ("ppq", "v"):      "via_strengths",
    ("ppq", "bel"):    "beliefs",
    ("prs", "pc"):     "hexaco",
    ("prs", "books"):  "reading_preferences",
    ("prs", "tv"):     "tv_preferences",
    ("prs", "music"):  "music_preferences",
    ("prs", "movies"): "movie_preferences",
    ("sdv", "d"):      "ipip_temperament",
    ("sdv", "value"):  "schwartz_values",
    ("sdv", "desir"):  "desirability",
    ("sdv", "view"):   "views",
    ("sdv", "likely"): "likelihood",
    ("spa", "PQ"):     "ipip",
    ("spa", "MEDHIS"): "medical_history",
    ("spa", "CHGTRT"): "changeability",
    ("spa", "YSKILL"):  "skills",
    ("spa", "ABILITY"): "talents",
    ("spa", "PSKILL"):  "skill_proficiency",
    ("spa", "VINTELL"): "beliefs_about_intelligence",
    ("prs", "mpr"):     "mpr",
}

# Whole blocks to exclude, with the reason: administrative counts and
# quantity counts, neither of which is an item response.
BLOCK_DROP = {
    ("hpq", "submiss"): "missing-response count, not an item",
    ("pf16", "smiss"):  "missing-response count, not an item",
    ("ppq", "vitamin"): "count of supplements taken, not a rating",
    ("spa", "COMPUT"):  "grab-bag of unrelated computer questions on mixed "
                        "2/3/5-point formats, not one instrument",
}

# Prefix patterns that are quantity counts rather than responses. The
# technical report describes the SPA's POS* block as "the number of each of
# 133 types of possessions that they own" -- a count of objects owned, not a
# rating of anything.
DROP_PREFIX_RE = {"spa": re.compile(r"^POS")}

# Several prefixes that are one instrument. The report describes the SPA as
# asking respondents to rate "their knowledge of examples (real and not) from
# each of seven diverse cultural domains (e.g., musical artists)" -- the seven
# FAM* families are those domains, so they belong in one table with the domain
# recoverable from the item name.
PREFIX_GROUPS = {
    "spa": [(re.compile(r"^FAM"), "cultural_familiarity")],
}

# Mailings that are a single instrument whatever their column prefixes. The
# IPIP file is described as "Combined data for all IPIP items administered to
# this sample": one 2,539-item bank, prefixed by whichever mailing each item
# arrived in. Splitting on those prefixes would produce fourteen tables that
# are one instrument.
SINGLE_INSTRUMENT = {"ipip"}

# A mailing whose items share one prefix but two scales. The report says the
# PAS holds "216 person-descriptive adjectives" (rated 1-7) alongside "160
# additional IPIP items" and "122 items from previously published scales"
# (1-5). The prefix cannot separate them; the per-item scale can.
SCALE_SPLIT = {"pas": {5: "ipip_scales", 7: "adjectives"}}

# Mailings where each adjective occupies its own column. Pool the
# single-column families into one block per scale rather than shipping
# hundreds of one-item tables.
POOLED = {"eps": "adjectives", "sdv": "adjectives"}

MIN_BLOCK = 5   # fewer columns than this is a fragment, not an instrument

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


def _scales_for(maxima):
    """The genuine response scales inside one prefix family.

    Splitting on each item's *observed* maximum is wrong: an item nobody
    answered at the top of the scale looks like its own scale. So a maximum
    only counts as a real scale if a substantial share of the family reaches
    it; everything else is mapped up to the nearest real scale at or above it.
    That keeps the PAS's genuine 1-5/1-7 split (281 vs 213 items) while
    leaving the 360 adjectives as one 1-9 scale despite 20 of them topping
    out at 8.
    """
    n = sum(maxima.values())
    real = sorted(m for m, c in maxima.items() if c >= max(2, 0.25 * n))
    return real or [max(maxima)]


def _blocks(d, items, mailing, num):
    """Group a mailing's item columns into instrument blocks.

    Rules, in order:

    1. **Different response scales are always different tables.** Mixing 1-5
       and 1-9 responses under one `resp` column is the defect this split
       exists to fix. Scales are decided per prefix family by `_scales_for`.
    2. **Within a scale, a prefix is only its own table if the technical
       report names it.** Otherwise same-scale prefixes are pooled. Without
       this the IPIP bank -- 2,539 items on one 1-5 scale, prefixed by
       whichever mailing each item arrived in -- shatters into nine tables
       that are really one instrument.
    """
    by_prefix = collections.OrderedDict()
    for c in items:
        v = num[c].dropna()
        if v.empty or v.nunique() < 2:
            continue
        prefix = re.sub(r"\d+$", "", str(c)) or "(bare)"
        if mailing in SINGLE_INSTRUMENT:
            prefix = ""
        else:
            for rx, name in PREFIX_GROUPS.get(mailing, []):
                if rx.match(prefix):
                    prefix = name
                    break
        by_prefix.setdefault(prefix, []).append((c, int(v.max())))

    # Where each item has its own column name (the adjective lists), a
    # per-family scale vote is meaningless -- every family has one member, so
    # its own maximum always "wins" and 20 adjectives nobody rated 9 become a
    # phantom 1-8 scale. Pool all singleton families and vote once over them.
    singleton = [t for p, cols in by_prefix.items() if len(cols) == 1 for t in cols]
    shared = (_scales_for(collections.Counter(m for _, m in singleton))
              if len(singleton) >= MIN_BLOCK else None)

    groups = collections.OrderedDict()
    for prefix, cols in by_prefix.items():
        named = ((mailing, prefix) in BLOCK_NAMES
                 or any(n == prefix for _, n in PREFIX_GROUPS.get(mailing, []))
                 or mailing in SINGLE_INSTRUMENT)
        if mailing in SCALE_SPLIT:
            scales = sorted(SCALE_SPLIT[mailing])
        elif named:
            # The technical report calls this one instrument, so trust it over
            # a scale vote: the 18 SPA skill items are one block even though
            # eight of them top out at 5 and ten at 6.
            scales = [max(m for _, m in cols)]
        elif len(cols) == 1 and shared:
            scales = shared
        else:
            scales = _scales_for(collections.Counter(m for _, m in cols))
        for c, mx in cols:
            hi = min((sc for sc in scales if mx <= sc), default=max(scales))
            groups.setdefault((prefix, hi), []).append(c)
    return groups


def _suffix(mailing, prefix, hi, groups):
    if mailing in SCALE_SPLIT:
        return SCALE_SPLIT[mailing][hi]
    if len(groups) == 1 or mailing in SINGLE_INSTRUMENT:
        return ""                       # single-instrument mailing
    named = BLOCK_NAMES.get((mailing, prefix))
    if named:
        return named
    return re.sub(r"[^0-9a-z]+", "_", prefix.lower()).strip("_")


def main():
    dem = _fetch(*DEMOGRAPHICS).rename(columns={"ID": "id"}).rename(columns=COVS)
    dem = dem[["id"] + [c for c in COVS.values() if c in dem.columns]]
    assert dem["id"].is_unique
    cov_cols = [c for c in dem.columns if c != "id"]

    os.makedirs(OUTDIR, exist_ok=True)
    total = n_tables = 0
    written = set()
    for doi, filename, mailing in MAILINGS:
        d = _fetch(doi, filename)
        idcol = d.columns[0]
        assert d[idcol].is_unique, f"{mailing}: {idcol} is not unique"
        items = list(d.columns[1:])

        # Letter-coded columns are not ordinal; SPA's forced-choice pairs are
        # handled separately and its 12-category ones go to the nominal script.
        num = d[items].apply(pd.to_numeric, errors="coerce")
        items = [c for c in items if not (num[c].isna() & d[c].notna()).any()]

        groups = _blocks(d, items, mailing, num)
        for (prefix, hi), cols in groups.items():
            reason = BLOCK_DROP.get((mailing, prefix))
            rx = DROP_PREFIX_RE.get(mailing)
            if reason is None and rx and rx.match(prefix):
                reason = "quantity count, not an item response"
            if reason:
                print(f"  [skip] {mailing}/{prefix} ({len(cols)} cols): {reason}")
                continue
            if len(cols) < MIN_BLOCK:
                print(f"  [skip] {mailing}/{prefix} ({len(cols)} cols): "
                      f"below MIN_BLOCK={MIN_BLOCK}")
                continue

            long = d.rename(columns={idcol: "id"}).melt(
                id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
            long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
            long = long.dropna(subset=["resp"])
            assert (long["resp"] % 1 == 0).all(), f"{mailing}/{prefix}: fractional"
            long["resp"] = long["resp"].astype(int)

            nun = long.groupby("item")["resp"].nunique()
            constant = sorted(nun[nun <= 1].index)
            if constant:
                long = long[~long["item"].isin(constant)]
            if long["item"].nunique() < MIN_BLOCK:
                print(f"  [skip] {mailing}/{prefix}: below MIN_BLOCK after "
                      f"dropping {len(constant)} constant item(s)")
                continue

            long = long.merge(dem, on="id", how="left")
            long = long[["id", "item", "resp"] + cov_cols]
            assert not long.duplicated(["id", "item"]).any()

            observed_hi = int(long["resp"].max())
            suffix = _suffix(mailing, prefix, observed_hi, groups)
            name = f"goldberg_2018_{mailing}" + (f"_{suffix}" if suffix else "")
            # Two buckets can still land on the same name (a named block
            # spanning scales, or two pooled groups whose observed maxima
            # coincide). Writing both would silently lose the first, so
            # disambiguate on the source prefix and fail if even that clashes.
            if name in written:
                extra = re.sub(r"[^0-9a-z]+", "_", prefix.lower()).strip("_") or f"n{len(written)}"
                name = f"{name}_{extra}"
            assert name not in written, f"duplicate table name {name}"
            written.add(name)
            path = os.path.join(OUTDIR, f"{name}.csv")
            long.to_csv(path, index=False)
            n_id, n_it = long["id"].nunique(), long["item"].nunique()
            total += len(long); n_tables += 1
            note = f"  [{len(constant)} constant dropped]" if constant else ""
            print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
                  f"resp {long['resp'].min()}-{long['resp'].max()}, "
                  f"density {len(long)/(n_id*n_it):.3f}{note}", flush=True)

    total += _forced_choice(dem, cov_cols); n_tables += 1
    print(f"\n{n_tables} tables, {total:,} responses")


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
