"""Wang (2025), Mendeley Data -- growth mindset, cognitive fusion, impulse
control and automatic thoughts in Chinese junior high school students.

Source: https://data.mendeley.com/datasets/dt5hj5j792
DOI: 10.17632/dt5hj5j792
Data: raw data0124.xlsx (instrument in Questionnaire.docx, same deposit)
License: CC BY 4.0

516 junior high school students completing four instruments. Surfaced by the
2026-08-25 OpenAIRE/Mendeley pass; Mendeley Data has no discovery connector of
its own, so this deposit had not been seen by any prior run.

The deposit ships `Questionnaire.docx` alongside the data, giving the full
bilingual item text, the item count and the response scale for every
instrument -- which is what makes the source's opaque column naming safe to
map:

    GQ1-GQ6         Growth Mindset Scale (GMS)          6 items, 1-6
    TCQ1-TCQ9       Cognitive Fusion Questionnaire      9 items, 1-7
    CQ1-CQ4         Impulse Control Scale (SCS)         4 items, 1-5
    CQ1_A-CQ7_A
      + CQ8-CQ20    Automatic Thoughts Scale (ATS)     20 items, 0-4

Note the `CQ` prefix is reused for two different instruments in the source
file; only the questionnaire resolves it. The ATS's 20 items are split across
two naming schemes but the numbers are continuous (1-7 as `CQ*_A`, 8-20 as
`CQ*`), so the source names are kept -- they carry the published item number
and join directly to the item text.

Tables written
--------------
wang_2025_growth_mindset       6 items, 1-6
wang_2025_cognitive_fusion     9 items, 1-7
wang_2025_impulse_control      4 items, 1-5
wang_2025_automatic_thoughts  20 items, 0-4

Coding notes
------------
* **ATS `resp = 0` is a real scale point**, not missingness: the questionnaire
  states the scale as 0 = "Never", 1 = "Seldom", 2 = "Sometimes",
  3 = "Usually", 4 = "Always". 0 is by far the modal response (5,632 of
  10,317), as expected for negative automatic thoughts in a school sample.
* **TCQ `resp = 0` is NOT** -- the CFQ is documented as a 7-point scale
  anchored at 1 ("Very Inconsistent"), so 0 is out of range. It occurs 12
  times in 4,644 responses, 1-2 on every one of the nine items, and is set to
  NA rather than treated as an eighth category.
* **Two ATS responses of 5 on `CQ1_A`** exceed the documented 0-4 scale, and 5
  appears on no other item. That is the isolated-to-one-item signature of a
  data-entry error, so both are set to NA.
* GMS items 1-3 are the reverse-worded ones (marked `*` in the
  questionnaire). They are exported as stored, without reversal, so the file
  matches the source.
* `V58` (0/1/2, 485/30/1) corresponds to nothing in the questionnaire and is
  not exported.
"""

import io
import os

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/dt5hj5j792"
OUTDIR = "irw_output"

COVS = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Grade": "cov_grade",
    "Personal Ability": "cov_self_rated_ability",
    "Family Economic Situation": "cov_family_economic_situation",
}

SCALES = {
    "growth_mindset":     ([f"GQ{i}" for i in range(1, 7)],  (1, 6)),
    "cognitive_fusion":   ([f"TCQ{i}" for i in range(1, 10)], (1, 7)),
    "impulse_control":    ([f"CQ{i}" for i in range(1, 5)],  (1, 5)),
    "automatic_thoughts": ([f"CQ{i}_A" for i in range(1, 8)]
                           + [f"CQ{i}" for i in range(8, 21)], (0, 4)),
}


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60).json()
    xl = [f for f in meta["files"] if f["filename"].endswith(".xlsx")]
    assert len(xl) == 1, [f["filename"] for f in meta["files"]]
    # Fetch with requests, not pandas' urlopen: the CDN 403s a request with
    # no User-Agent.
    raw = requests.get(xl[0]["content_details"]["download_url"], timeout=300,
                       headers={"User-Agent": "Mozilla/5.0 (IRW-research)"})
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load().rename(columns={"Number": "id"})
    assert d["id"].is_unique
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for name, (items, (lo, hi)) in SCALES.items():
        missing = [c for c in items if c not in d.columns]
        assert not missing, (name, missing)

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        # Out-of-range values are documented above as sentinels or data-entry
        # errors; drop them rather than shipping an undocumented category.
        long.loc[~long["resp"].between(lo, hi), "resp"] = pd.NA
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(lo, hi).all()
        assert long.groupby("item")["resp"].nunique().min() > 1, f"{name}: constant item"
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"wang_2025_{name}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
