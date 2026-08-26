"""Alloubani (2021), Harvard Dataverse -- anxiety among newly hired nurses at
a specialized oncology hospital (Jordan).

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OSXHWE
DOI: 10.7910/DVN/OSXHWE
License: CC0 1.0

181 newly hired nurses completing the State-Trait Anxiety Inventory. The
deposit's value labels identify the two forms unambiguously: the `Y1` block
is STAI Form Y-1 (state; "Not At All".."Very Much So") with reverse-keyed
labels on items 1, 2, 5, 8, 10, 11, 15, 16, 19, 20 -- exactly the published
Y-1 reverse set -- and the three `Y2P*` blocks are Form Y-2 (trait; "Almost
Never".."Almost Always") administered at three successive periods.

Tables written
--------------
alloubani_2021_stai_state   181 nurses x 20 items, 1-4
alloubani_2021_stai_trait   181 nurses x 20 items x 3 waves, 1-4

Coding notes
------------
* **State and trait are separate tables.** They are two different forms with
  different response wordings; only the trait form was repeated.
* `wave` on the trait table is the period, 1/2/3, from the source `P1`/`P2`/
  `P3` suffix. The state form was administered once and has no `wave`.
* **The deposited columns are mean-imputed.** Every variable label reads
  `SMEAN(Qn...)`, SPSS's series-mean replacement, and the imputed cells are
  exactly the non-integer values -- verified: each non-integer equals either
  the column's mean over the integer values or 5 minus it (the reversal was
  applied after imputation). Those cells are dropped, which restores the
  observed responses; nothing is imputed in the shipped tables.
* One cell, `Q9Y2P2_1` = 13 on a 1-4 item, is out of range on a single item
  and is dropped as a data-entry error.
* Item ids are the position within the 20-item form, so state item `Q7` and
  trait item `Q7` are different items on different forms -- which is why they
  are in different tables.
"""

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/OSXHWE"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"age": "cov_age", "gender": "cov_gender",
        "eduationalbakground": "cov_education",
        "Materialstatus": "cov_marital_status",
        "pastexperience": "cov_experience_months",
        "nursingunit": "cov_unit", "nationality": "cov_nationality"}
SKIP = {"Y1": "scored total for the state form",
        "Y2P1": "scored total, trait period 1",
        "Y2P2": "scored total, trait period 2",
        "Y2P3": "scored total, trait period 3"}


def parse(col):
    """('Q9Y2P2_1') -> (item number, block) ; block is 'Y1' or 'Y2P<n>'."""
    m = re.fullmatch(r"Q(\d+)(Y\d?P?\d?)_1", str(col))
    if not m:
        return None
    blk = m.group(2)
    if blk == "YP3":            # one column is misspelled Q16YP3_1
        blk = "Y2P3"
    return int(m.group(1)), blk


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    fid = meta["files"][0]["dataFile"]["id"]
    raw = s.get(f"{BASE}/api/access/datafile/{fid}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    open("/tmp/alloubani_stai.sav", "wb").write(raw.content)
    d, m = pyreadstat.read_sav("/tmp/alloubani_stai.sav")

    parsed = {c: parse(c) for c in d.columns}
    items = {c: p for c, p in parsed.items() if p}
    assert len(items) == 80, len(items)
    # the state form's reverse-keyed items must be the published Y-1 set,
    # which is what identifies the block as Form Y-1 rather than Y-2.
    rev = sorted(n for c, (n, b) in items.items() if b == "Y1"
                 and str(m.variable_value_labels[c][1.0]).startswith("Very"))
    assert rev == [1, 2, 5, 8, 10, 11, 15, 16, 19, 20], rev

    d["id"] = range(1, len(d) + 1)
    long = d.melt(id_vars=["id"] + list(COVS), value_vars=list(items),
                  var_name="src", value_name="resp")
    long = long.rename(columns=COVS)
    long["item"] = long["src"].map(lambda c: f"Q{items[c][0]}")
    long["block"] = long["src"].map(lambda c: items[c][1])
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")

    n_all = long["resp"].notna().sum()
    imputed = long["resp"].notna() & (long["resp"] % 1 != 0)
    out_of_range = long["resp"].notna() & ~long["resp"].between(1, 4)
    print(f"  dropped {imputed.sum()} SMEAN-imputed cells and "
          f"{(out_of_range & ~imputed).sum()} out-of-range cells "
          f"of {n_all} deposited values")
    long = long[long["resp"].notna() & ~imputed & ~out_of_range].copy()
    long["resp"] = long["resp"].astype(int)

    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for suffix, blocks in [("state", ["Y1"]),
                           ("trait", ["Y2P1", "Y2P2", "Y2P3"])]:
        t = long[long["block"].isin(blocks)].copy()
        cols = ["id", "item", "resp"]
        if len(blocks) > 1:
            t["wave"] = t["block"].str[-1].astype(int)
            cols.append("wave")
        t = t[cols + list(COVS.values())]

        assert t["resp"].between(1, 4).all()
        assert not t.duplicated(["id", "item"] + (["wave"] if len(blocks) > 1
                                                  else [])).any()
        assert t["item"].nunique() == 20
        checks = run_qc(t)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"alloubani_2021_stai_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        t.to_csv(path, index=False)
        n_id, n_it = t["id"].nunique(), t["item"].nunique()
        cells = n_id * n_it * len(blocks)
        total += len(t)
        print(f"{path}: {n_id} nurses x {n_it} items"
              f"{' x %d waves' % len(blocks) if len(blocks) > 1 else ''} = "
              f"{len(t)} responses, density {len(t) / cells:.3f}")

    for c in d.columns:
        if c in items or c in COVS or c == "id":
            continue
        assert c in SKIP, f"unaccounted source column: {c}"
        print(f"  skip {c}: {SKIP[c]}")
    print(f"\n2 tables, {total:,} responses")


if __name__ == "__main__":
    main()
