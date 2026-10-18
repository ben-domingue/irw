"""Job demands, social support and work-family conflict among remote workers.

Source: https://zenodo.org/records/7703332
DOI: 10.5281/zenodo.7703332
Data: Data Analysis.sav_12122021_latest with Mediation.sav
      (SPSS, 315 respondents x 60 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: NOT shipped, although the stems are right there. Both label levels
  checked: variable labels carry the full English stem for all 34 items, value
  labels are populated for the demographics only. Every one of the three
  shipped blocks is a named third-party instrument -- Netemeyer et al.'s
  Work-Family Conflict scale, and job-demand / social-support blocks of the
  COPSOQ family -- and none has a located grant, so the 2026-10-15 silence
  rule (Ben, counsel 2026-10-08) makes the WORDING a hold. The response tables
  carry positional codes and expose none of it. Register-row requests for all
  three are in TODO.

WITHHELD, and this is the finding worth keeping:

  WE1..WE9  is the **UWES-9 verbatim** -- "At my work, I feel that I am
    bursting with energy", "At my job, I feel strong and vigorous", "I am
    enthusiastic about my job", "My job inspires me", ... on the UWES's own
    0-6 frequency scale. The register BLOCKS the UWES, but its matcher is
    `^uwes` with **zero** item-text patterns, so neither `rights.py` nor the
    sweep can reach a deposit that calls the items WE1..WE9.
  PWB1..PWB5  is the **WHO-5 Well-Being Index verbatim** -- "I have felt
    cheerful and in good spirits", "I have felt calm and relaxed", "I have
    felt active and vigorous", "I woke up feeling fresh and rested", "My daily
    life has been filled with things that interest me", on WHO-5's 0-5 scale.
    The register BLOCKS it, with matcher `^who5|^who_5` and again **zero**
    text patterns.

Both would have shipped on an automated rights check. They were caught only by
reading the stems, which is the concrete case for the 154 inert `block` rows
counted by `itemtext/check_register_coverage.py`.

Shipped (one table per scale, each on its own asserted range):

  jd    6 items, 1-6   job demands
  ss    4 items, 1-6   social support from colleagues and supervisor
  wfc  10 items, 1-7   work-family conflict (both directions)

The five `New_*` columns are subscale means and the fifteen `Z*`/`Std*`
columns are z-scores of those means -- all derived, all skipped with a reason.
"""
import os

import pandas as pd
import pyreadstat

RAW = os.environ.get(
    "WALTON_RAW",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/"
    "5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.7703332/"
    "Data Analysis.sav_12122021_latest with Mediation.sav")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {
    "jd":  ([f"JD{i}" for i in range(1, 7)], {1, 2, 3, 4, 5, 6}),
    "ss":  ([f"SS{i}" for i in range(1, 5)], {1, 2, 3, 4, 5, 6}),
    "wfc": ([f"WFC{i}" for i in range(1, 11)], {1, 2, 3, 4, 5, 6, 7}),
}
WITHHELD = {**{f"WE{i}": "UWES-9 verbatim -- register `block`, matcher ^uwes "
                         "cannot see a WE* code" for i in range(1, 10)},
            **{f"PWB{i}": "WHO-5 verbatim -- register `block`, matcher "
                          "^who5|^who_5 cannot see a PWB* code"
               for i in range(1, 6)}}
COVS = {"GENDER": "cov_gender", "AGE": "cov_age_group",
        "MARITAL": "cov_marital", "EDUCATION": "cov_education",
        "POSITION": "cov_position_level", "MONTH": "cov_remote_months"}


def main():
    d, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    d.columns = [str(c).strip() for c in d.columns]
    labels = {str(k).strip(): v for k, v in
              (meta.column_names_to_labels or {}).items()}
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")

    used = set(COVS)
    for cols, _ in SCALES.values():
        used |= set(cols)
    for c, why in WITHHELD.items():
        if c in d.columns:
            print(f"  WITHHELD {c!r}: {why}")
            used.add(c)
    for c in d.columns:
        if c in used:
            continue
        lab = str(labels.get(c) or "")
        if c.startswith("New_"):
            print(f"  skip {c!r}: derived subscale mean")
        elif c.startswith(("ZNew_", "ZSco", "StdZ")):
            print(f"  skip {c!r}: derived z-score ({lab})")
        else:
            print(f"  skip {c!r}: not an item of a shipped scale ({lab})")
        used.add(c)
    assert not [c for c in d.columns if c not in used]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, (cols, scale) in SCALES.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: {missing}"
        long = d.melt(id_vars=["id"] + list(COVS), value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - scale
            assert not bad, f"{name}/{it}: {sorted(bad)} outside {sorted(scale)}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
        long = long.rename(columns=COVS)
        table = f"walton_2023_{name}"
        assert table not in written
        written.add(table)
        long[["id", "item", "resp"] + [COVS[c] for c in COVS]].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
