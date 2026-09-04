"""Self-Compassion Scale (French validation) and four co-administered scales.

Source: Ilios Kotsou (2016), figshare 10.6084/m9.figshare.3122734, CC BY 4.0 --
"SCSdata", the validation data for the French version of the Self-Compassion
Scale. 1,554 respondents x 88 columns.

Six instruments ship as six tables. They use five different response formats
(1-7, 0-3, 1-6, 1-5), so a single table would make `resp` ambiguous:

  kotsou_2016_scs         26 items, 1-5  Self-Compassion Scale
  kotsou_2016_panas       20 items, 1-5  PANAS
  kotsou_2016_plc         15 items, 1-6
  kotsou_2016_bdi         13 items, 0-3  Beck Depression Inventory
  kotsou_2016_life_satisfaction  5 items, 1-7
  kotsou_2016_happiness    4 items, 1-7

**PANAS is stored as text, not numbers**: its 20 columns hold the strings
`A1`..`A5` rather than 1..5. Melting without converting would give a
non-numeric `resp` and the table would fail the ordinal check. The prefix is
stripped and the digit kept, with an assert that every observed value matches
`A[1-5]` so a different coding cannot pass through silently.

The BDI block is split across two naming styles -- `BDI_1`..`BDI_12` plus a
bare `BDI13` -- so it is matched with a pattern covering both; taking only
`BDI_\\d+` would silently ship a 12-item BDI.
"""
import os
import re

import pandas as pd
import requests

ARTICLE = 3122734
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {
    "kotsou_2016_scs": (r"^SCS\d+$", 26, (1, 5)),
    "kotsou_2016_panas": (r"^PANAS\d+$", 20, (1, 5)),
    "kotsou_2016_plc": (r"^PLC\d+$", 15, (1, 6)),
    "kotsou_2016_bdi": (r"^BDI_?\d+$", 13, (0, 3)),
    "kotsou_2016_life_satisfaction": (r"^LS_\d+$", 5, (1, 7)),
    "kotsou_2016_happiness": (r"^Bonh_\d+$", 4, (1, 7)),
}
COVARIATES = {"Sexe": "cov_sex", "Diplôme": "cov_education",
              "Pays": "cov_country"}

#: The survey has no collection date; the figshare record was published
#: 2016-03-27, so an age derived here is the respondent's age in 2016 and is
#: good to about a year.
SURVEY_YEAR = 2016


def birth_year(v):
    """Birth year from the free-text `Age` column, or None.

    **`Age` is not an age.** It is a date of birth typed by hand in a dozen
    formats -- 17011972, 23/09/1968, "31 03 1962", "02 octobre 1974",
    11.04.1986, 1978, 21/04/97 -- and it also holds values that are not dates
    at all ("CHENEE", "saint-avold", "8 mars", "09:4:53") and a handful of
    *survey* dates (19 Juin 2012, 31.03.2013) where the respondent entered the
    day they were filling the form in.

    Mapping the column straight to `cov_age` on the strength of its name is
    what put a `cov_age` of 236061972 into the corpus, with 82% of the column
    null because only the values that happened to parse as numbers survived
    (irw#1779). Reading the dates instead gives 1,517 of 1,554 respondents a
    real age where 278 had one.

    Two rules, both deliberately strict, because a wrong age is worse than a
    missing one:

    * a four-digit year counts only in [1900, 2005]. That refuses the 2012-2015
      survey dates rather than reading them as births, and refuses typos like
      1698 or 0960 rather than guessing.
    * a two-digit year counts only inside a complete date. "03/03" is a day and
      a month with no year at all, and taking its trailing 03 for 2003 invents
      a 13-year-old.
    """
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if s.isdigit():
        n = int(s)
        if 1900 <= n <= 2005:
            return n                                    # YYYY
        if len(s) in (7, 8):                            # DMMYYYY / DDMMYYYY
            y = int(s[-4:])
            return y if 1900 <= y <= 2005 else None
        if len(s) == 6:                                 # DDMMYY
            y = int(s[-2:])
            return 2000 + y if y <= 5 else 1900 + y
        return None
    m = re.findall(r"(?<!\d)(19\d{2}|200[0-5])(?!\d)", s)
    if m:
        return int(m[-1])
    # a complete date whose year is two digits: 21/04/97, "13 juin 84"
    # `(?<!\d)` on the capture matters: without it "19 Juin 2012" matches with
    # a year of 12 and becomes a birth in 1912.
    m = re.search(r"(?:\d{1,2}|[A-Za-zéû]+)\s*[/.\- ]\s*"
                  r"(?:\d{1,2}|[A-Za-zéû]+)\s*[/.\- ]?\s*(?<!\d)(\d{2})\s*$", s)
    if m:
        y = int(m.group(1))
        return 2000 + y if y <= 5 else 1900 + y
    return None


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    meta = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                        timeout=120).json()
    f = next(x for x in meta["files"]
             if x["name"].lower().endswith((".xls", ".xlsx", ".csv")))
    r = requests.get(f["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["name"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)

    item_cols = {}
    for table, (pat, n, _rng) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    # PANAS ships as 'A1'..'A5' strings.
    panas = item_cols["kotsou_2016_panas"]
    observed = set()
    for c in panas:
        observed |= set(df[c].dropna().astype(str))
    assert all(re.fullmatch(r"A[1-5]", v) for v in observed), \
        f"unexpected PANAS coding: {sorted(observed)}"
    for c in panas:
        df[c] = df[c].astype(str).str.extract(r"^A([1-5])$")[0].astype("Int64")

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    born = df["Age"].map(birth_year)
    df["cov_age"] = (SURVEY_YEAR - born).astype("Int64")
    assert df["cov_age"].dropna().between(13, 100).all(), \
        f"cov_age out of range: {df['cov_age'].min()}-{df['cov_age'].max()}"
    covs = [v for v in COVARIATES.values() if v in df.columns] + ["cov_age"]
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (_pat, n, (lo, hi)) in SCALES.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=item_cols[table],
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == n, table
        assert long["resp"].between(lo, hi).all(), \
            f"{table}: expected {lo}-{hi}, saw {long['resp'].min()}-{long['resp'].max()}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
