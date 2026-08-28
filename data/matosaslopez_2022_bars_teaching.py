"""Student evaluation of teaching, BARS questionnaire, two modalities.

Source: Matosas-Lopez, Luis. Two Zenodo deposits, both CC BY 4.0:

  10.5281/zenodo.15160903  blended-learning teaching   (1,436 students)
  10.5281/zenodo.15151307  face-to-face teaching       (888 students)

Both administer the *same* 10-item behaviourally-anchored rating scale on a
1-5 scale -- the Spanish item labels are identical in content and order
(Introduccion a la asignatura, Descripcion del sistema de evaluacion, Gestion
del tiempo, Disponibilidad general, Coherencia organizativa, Implementacion
del sistema de evaluacion, Resolucion de dudas, Capacidad explicativa,
Facilidad de seguimiento, Satisfaccion general); the face-to-face file merely
prefixes each with its number ("1.- Introduccion...").

They therefore ship as ONE table with `cov_teaching_mode`, per the
same-instrument rule, rather than as two tables differing only in delivery
mode. Item codes are `BARS_1`..`BARS_10` taken from that shared order. The
face-to-face ids are offset past the blended sample's maximum.
"""
import os
import re

import pandas as pd
import requests

RECORDS = {"blended": 15160903, "face_to_face": 15151307}
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "matosaslopez_2022_bars_teaching"

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
    frames, id_offset = [], 0
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
        df["id"] = df.index + 1 + id_offset
        id_offset = int(df["id"].max())
        df["cov_teaching_mode"] = mode
        frames.append(df)

    items = [f"BARS_{i}" for i in range(1, 11)]
    parts = []
    for df in frames:
        covs = [c for c in df.columns if str(c).startswith("cov_")]
        parts.append(df.melt(id_vars=["id"] + covs, value_vars=items,
                             var_name="item", value_name="resp"))
    long = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    covs = sorted(c for c in long.columns if str(c).startswith("cov_"))
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 10
    assert long["resp"].between(1, 5).all(), "the BARS scale is 1-5"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
