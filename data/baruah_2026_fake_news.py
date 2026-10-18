"""Fake News Quotient: information literacy, fact-checking tactics, trust-repair.

Source: https://zenodo.org/records/20382648
DOI: 10.5281/zenodo.20382648
Data: Master data.sav (SPSS, 226 respondents x 46 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: shipped (SPSS variable labels carry the full English stem for every
  item; value labels carry all five anchors). Both label levels checked and
  both populated.

Four study-authored scales by Karabi Baruah, all on one 1-5 Likert
("Strongly Disagree" .. "Strongly agree"), shipped as one table each:

  QFI    10 items  cues used to IDENTIFY fake news
  QFTA   10 items  fact-checking TACTICS applied
  TRR_P1  7 items  trust-repair response: own reactions
  TRR_P2  7 items  trust-repair response: attributed causes

TRR_P1 and TRR_P2 are two separately-worded blocks (reactions vs. attributions),
not one 14-item scale, so they stay apart.

Dropped, each with a reason printed at build time: the four `*_Mean` columns are
derived subscale means, and QFI_rel / TRR_duration / TRR_feelings are single
categorical questions about the episode rather than items of any scale -- they
become covariates. Demographics ship as cov_*.
"""
import os

import pandas as pd
import pyreadstat

RAW = os.environ.get(
    "BARUAH_RAW",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/"
    "5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.20382648/"
    "Master data.sav")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {
    "qfi":     [f"QFI{i}" for i in range(1, 11)],
    "qfta":    [f"QFTA{i}" for i in range(1, 11)],
    "trr_own": [f"TRR_P1_{i}" for i in range(1, 8)],
    "trr_att": [f"TRR_P2_{i}" for i in range(1, 8)],
}
COVS = {"Gender": "cov_gender", "Course_Level": "cov_course_level",
        "Annual_income": "cov_annual_income",
        "Frequency": "cov_social_media_frequency",
        "Victim": "cov_fake_news_victim",
        "QFI_rel": "cov_how_encountered",
        "TRR_duration": "cov_emotion_duration",
        "TRR_feelings": "cov_would_feel_again"}
DERIVED = ["QFI_Mean", "QFTA_Mean", "TRR_P1_mean", "TRR_P2_mean"]
SCALE = {1, 2, 3, 4, 5}


def main():
    d, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels = meta.column_names_to_labels or {}
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")

    # Balance the books: every source column is an item, a covariate, or a
    # printed skip.
    used = set(COVS)
    for cols in SCALES.values():
        used |= set(cols)
    for c in DERIVED:
        print(f"  skip {c!r}: derived subscale mean, not an observed response")
        used.add(c)
    unaccounted = [c for c in d.columns if c not in used]
    for c in unaccounted:
        print(f"  UNACCOUNTED {c!r} (label={labels.get(c)!r})")
    assert not unaccounted, f"{len(unaccounted)} source column(s) unaccounted for"

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()

    for name, cols in SCALES.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: missing {missing}"
        long = d.melt(id_vars=["id"] + list(COVS), value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        bad = set(long["resp"].unique()) - SCALE
        assert not bad, f"{name}: resp outside {sorted(SCALE)}: {sorted(bad)}"
        # Per-item, not merged: an error isolated to one item is a data-entry
        # fault even when the pooled range looks fine.
        for it, g in long.groupby("item"):
            b = set(g["resp"].unique()) - SCALE
            assert not b, f"{name}/{it}: {sorted(b)}"
        assert long["id"].nunique() >= 100, long["id"].nunique()
        assert long["item"].nunique() > 1, "single-item table"

        long = long.rename(columns=COVS)
        out = long[["id", "item", "resp"] + [COVS[c] for c in COVS]]
        table = f"baruah_2026_{name}"
        assert table not in written, f"duplicate output name {table}"
        written.add(table)
        p = os.path.join(OUT, f"{table}.csv")
        out.to_csv(p, index=False)
        print(f"  {table}: {out['id'].nunique()} ids x "
              f"{out['item'].nunique()} items = {len(out)} responses -> {p}")


if __name__ == "__main__":
    main()
