"""Student evaluation of teaching, BARS questionnaires, two modalities.

Source: Matosas-Lopez, Luis. Two Zenodo deposits, both CC BY 4.0:

  10.5281/zenodo.15160903  blended-learning teaching   (1,436 students)
  10.5281/zenodo.15151307  face-to-face teaching       (888 students)

These are TWO DIFFERENT behaviourally-anchored rating scales (irw#2412), so
they ship as two tables:

  matosaslopez_2022_bars_teaching_blended
  matosaslopez_2022_bars_teaching_inperson   (face-to-face; `_face_to_face`
                                              would exceed the 40-character
                                              name cap, and `_inperson` is the
                                              spain_2024_politics_* precedent)

Both use ten 1-5 items whose Spanish dimension labels match in content and
order (Introduccion a la asignatura, Descripcion del sistema de evaluacion,
Gestion del tiempo, Disponibilidad general, Coherencia organizativa,
Implementacion del sistema de evaluacion, Resolucion de dudas, Capacidad
explicativa, Facilidad de seguimiento, Satisfaccion general; the face-to-face
file prefixes each with its number). But in a BARS the behavioural anchors ARE
the item content, and they differ in every dimension: the blended instrument
(Behav Sci 2022, Appendix A) describes LMS-centred behaviours, the face-to-face
one (the 2019 JUTLP instrument) classroom behaviours. Per-item means are
2.5-3.3 blended vs 3.8-4.3 face-to-face on every item. So BARS_k is a different
item in each table and the two must not be pooled on item code.

Until 2026-09-27 this script wrote one pooled table,
matosaslopez_2022_bars_teaching, with `cov_teaching_mode`, on the mistaken
premise that both deposits administer the same scale; that table was
withdrawn. Item codes are `BARS_1`..`BARS_10` taken from the shared label
order. `id` is the row number within each deposit (the pooled table offset the
face-to-face ids past the blended maximum, so its face-to-face id k is id
k - 1436 here).
"""
import os
import re

import pandas as pd
import requests

RECORDS = {"blended": 15160903, "face_to_face": 15151307}
SUFFIX = {"blended": "blended", "face_to_face": "inperson"}
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "matosaslopez_2022_bars_teaching"  # + "_" + SUFFIX[mode]

# The shared item order, keyed on a distinctive word of each Spanish label so
# the match does not depend on the numeric prefix or on column position.
ORDER = ["introducc", "descripc", "gesti", "disponibilidad", "coherencia",
         "implementaci", "resoluci", "capacidad", "facilidad", "satisfacci"]
COVARIATES = {"edad": "cov_age", "género": "cov_gender", "genero": "cov_gender",
              "grado": "cov_degree", "universidad": "cov_university"}


def fetch_raw(record, out_dir=None):
    rec = requests.get(f"https://zenodo.org/api/records/{record}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if x["key"].lower().endswith((".xlsx", ".xls", ".csv")))
    local = os.path.join(out_dir or "/tmp", f["key"])
    if not os.path.exists(local):
        r = requests.get(f["links"]["self"], timeout=600)
        r.raise_for_status()
        with open(local, "wb") as fh:
            fh.write(r.content)
    return local


def read_any(p):
    return pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)


def item_map(df):
    """Map each source column onto BARS_1..BARS_10 by its Spanish label."""
    out = {}
    for c in df.columns:
        key = re.sub(r"^\s*\d+\s*\.?-?\s*", "", str(c)).strip().lower()
        for i, stem in enumerate(ORDER, start=1):
            if key.startswith(stem):
                out[c] = f"BARS_{i}"
                break
    return out


def main(paths=None):
    items = [f"BARS_{i}" for i in range(1, 11)]
    os.makedirs(OUT_DIR, exist_ok=True)
    for mode, record in RECORDS.items():
        p = (paths or {}).get(mode) or fetch_raw(record)
        df = read_any(p)
        mapping = item_map(df)
        assert len(mapping) == 10, \
            f"{mode}: matched {len(mapping)} of 10 items -- labels changed?"
        assert len(set(mapping.values())) == 10, f"{mode}: duplicate item codes"
        df = df.rename(columns=mapping)
        df = df.rename(columns={c: COVARIATES[str(c).strip().lower()]
                                for c in df.columns
                                if str(c).strip().lower() in COVARIATES})
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1
        covs = [c for c in df.columns if str(c).startswith("cov_")]
        long = df.melt(id_vars=["id"] + covs, value_vars=items,
                       var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        covs = sorted(covs)
        long = long[["id", "item", "resp"] + covs]

        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == 10
        assert long["resp"].between(1, 5).all(), "the BARS scale is 1-5"

        name = f"{TABLE}_{SUFFIX[mode]}"
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
