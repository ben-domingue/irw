"""Reduced Morningness-Eveningness Questionnaire and Trait Meta-Mood Scale.

Source: Antunez Vilchez, J. M. & Adan, A., Zenodo 10.5281/zenodo.18681288,
CC BY 4.0 -- "Circadian Typology and Emotional Intelligence in Healthy
Adults". 1,015 respondents.

Two instruments, two tables:

  antunez_2013_tmms24   24 items, 1-5  (Trait Meta-Mood Scale, `IE1`..`IE24`)
  antunez_2013_rmeq      5 items       (reduced MEQ, `RMEQ1`..`RMEQ5`)

The rMEQ's five items genuinely differ in response format -- observed ranges
are 1-4, 1-5 and 0-6 across the block -- which is a property of the published
instrument (its items offer four, five and six anchored options plus a
clock-time item), not a coding error. No single-range assert is applied to it
for that reason; each item's own range is checked to be within 0-6 instead.

Six derived columns are dropped: `TC_TOT` is the rMEQ total, `Cronotipo` the
chronotype band derived from it, and `Atencion_emocional` /
`Claridad_emocional` / `Reparacion_emocional` / `Atencion_recod` the TMMS
subscale scores and a recode.
"""
import os
import re

import pandas as pd
import requests

RECORD = 18681288
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".csv"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_csv(fetch_raw(path))
    ie = [c for c in df.columns if re.match(r"^IE\d+$", str(c))]
    rmeq = [c for c in df.columns if re.match(r"^RMEQ\d+$", str(c))]
    assert len(ie) == 24, f"expected 24 TMMS items, found {len(ie)}"
    assert len(rmeq) == 5, f"expected 5 rMEQ items, found {len(rmeq)}"

    covs = {}
    for c in df.columns:
        s = str(c)
        if s in ("Sexo", "Edad", "Estadocivil", "Situaciónlaboral",
                 "Niveldeestudios") or s.startswith("¿"):
            covs[c] = "cov_" + re.sub(r"[^a-z0-9]+", "_",
                                      s.lower().strip("¿?"))[:40].strip("_")
    df = df.rename(columns=covs).reset_index(drop=True)
    cov_names = sorted(set(covs.values()))
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols, rng in [("antunez_2013_tmms24", ie, (1, 5)),
                             ("antunez_2013_rmeq", rmeq, (0, 6))]:
        long = (df.melt(id_vars=["id"] + cov_names, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_names]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == len(cols), table
        assert long["resp"].between(*rng).all(), f"{table}: expected {rng}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
