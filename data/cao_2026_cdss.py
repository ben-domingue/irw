"""Cao, Luo & Zhang (2026), figshare -- the double-edged effect of interaction
in clinical decision support systems.

Source: https://doi.org/10.6084/m9.figshare.33204345.v2
DOI: 10.6084/m9.figshare.33204345
License: CC BY 4.0

222 Chinese clinicians randomly assigned to an interactive or a rule-based
clinical decision support system and then measured on four 7-point scales.

Tables written
--------------
cao_2026_cdss_intention_to_use        222 x 3 items, 1-7
cao_2026_cdss_cognitive_load          222 x 6 items, 1-7
cao_2026_cdss_perceived_autonomy      222 x 4 items, 1-7
cao_2026_cdss_professional_knowledge  222 x 3 items, 1-7

Coding notes
------------
* The workbook has a Chinese sheet and an author-supplied English sheet with
  identical values; the English sheet is read so item ids and covariates are
  ASCII, and the two sheets are asserted to hold the same numbers.
* Four tables for four named constructs; the shared 1-7 format does not make
  them one instrument.
* `treat` is the randomly assigned mode (1 = interactive, 0 = rule-based).
* The autonomy block trips `run_qc`'s `resp_scale_mixed` check because only
  one of its four items was ever answered 7 (by 4 of 222 respondents). That is
  an unused top category on a left-skewed 1-7 scale, not a second scale, so
  the check is waived explicitly and loudly rather than by splitting a
  four-item subscale in two.
* Two `(reverse-coded)` columns are derived copies of `Q4-5` and `Q4-6`
  (verified `8 - x`) and are not shipped; `Decision-mode perception` is a
  single-item manipulation check; the four `X1`/`Y1`/`M1`/`M2` and
  `Professional knowledge (PK; mean score)` columns are scale means.
* The deposit carries no identifier column, so `id` is row position.
"""

import io
import os
import re
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

ARTICLE = 33204345
DOI = "10.6084/m9.figshare.33204345"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
SHEET = "Experiment 2 (English)"
BLOCKS = [("intention_to_use", "Intention to use", "Q3", 3),
          ("cognitive_load", "Cognitive load", "Q4", 6),
          ("perceived_autonomy", "Perceived autonomy", "Q5", 4),
          ("professional_knowledge", "Professional knowledge", "Q6", 3)]
COV_NAMES = {"Gender": "cov_gender", "Age": "cov_age_band",
             "Education": "cov_education",
             "Professional rank": "cov_professional_rank"}
TREAT = "Human-machine decision-making mode (1 = interactive, 0 = rule-based)"
# run_qc's resp_scale_mixed reads each item's observed maximum as its scale.
# In the autonomy block only Q5-4 reaches 7, and only 4 of 222 respondents
# chose it; the other three items top out at 6 with 5, 23 and 7 responses
# there. That is one left-skewed 1-7 scale with an unused top category on
# three items, not a 1-6 scale mixed with a 1-7 one -- every other block in
# this questionnaire is 1-7, and the items are one published subscale.
ALLOWED_FAILS = {
    ("perceived_autonomy", "resp_scale_mixed"):
        "three of four items never reach 7; unused top category, not a "
        "second scale",
}


def main():
    s = requests.Session()
    s.headers.update(UA)
    art = s.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                timeout=120).json()
    assert art["license"]["name"].startswith("CC BY"), art["license"]
    hit = [f for f in art["files"] if f["name"].lower().endswith(".xlsx")]
    assert len(hit) == 1, [f["name"] for f in art["files"]]
    raw = s.get(hit[0]["download_url"], timeout=600)
    raw.raise_for_status()
    book = pd.ExcelFile(io.BytesIO(raw.content))
    d = book.parse(SHEET)
    zh = book.parse([n for n in book.sheet_names if n != SHEET][0])
    num_en = d.select_dtypes("number").reset_index(drop=True)
    num_zh = zh.select_dtypes("number").reset_index(drop=True)
    assert num_en.shape == num_zh.shape
    assert (num_en.values == num_zh.values).all(), "sheets disagree"

    d["id"] = range(1, len(d) + 1)
    d["treat"] = d[TREAT].astype(int)
    for src, dest in COV_NAMES.items():
        d[dest] = d[src]

    # the reverse-coded columns must be derived, not separate responses
    for c in d.columns:
        m = re.match(r"^(Q\d-\d) .*\(reverse-coded\)$", str(c))
        if m:
            src = next(k for k in d.columns
                       if str(k).startswith(m.group(1))
                       and "reverse" not in str(k))
            assert (d[c] == 8 - d[src]).all(), c

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for suffix, label, prefix, n_expected in BLOCKS:
        items = [c for c in d.columns
                 if re.fullmatch(rf"{prefix}-\d {re.escape(label)}", str(c))]
        assert len(items) == n_expected, (suffix, items)
        shipped.update(items)

        long = d.melt(id_vars=["id", "treat"] + list(COV_NAMES.values()),
                      value_vars=items, var_name="item", value_name="resp")
        long["item"] = long["item"].str.split(" ").str[0].str.replace("-", "_")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "treat"]
                    + list(COV_NAMES.values())]

        assert long["resp"].between(1, 7).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"
               and (suffix, c.name) not in ALLOWED_FAILS]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])
        for c in checks:
            if c.status == "fail":
                print(f"  [waived] {suffix}: {c.name} -- "
                      f"{ALLOWED_FAILS[(suffix, c.name)]}")

        name = f"cao_2026_cdss_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} clinicians x {n_it} items = {len(long)} "
              f"responses, density {len(long) / (n_id * n_it):.3f}")

    accounted = shipped | set(COV_NAMES) | set(COV_NAMES.values()) | {
        "id", "treat", TREAT}
    for c in d.columns:
        if c in accounted:
            continue
        if "reverse-coded" in str(c):
            print(f"  skip {c}: derived reverse-scored copy")
        elif str(c).startswith(("X1", "Y1", "M1", "M2")) or "mean score" in str(c):
            print(f"  skip {c}: scale mean")
        elif str(c).startswith("Decision-mode perception"):
            print(f"  skip {c}: single-item manipulation check")
        elif str(c).startswith("Other"):
            print(f"  skip {c}: free-text 'other' rank")
        else:
            raise AssertionError(f"unaccounted source column: {c}")
    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
