"""Social-network addiction, self-esteem and family communication, Peru.

Source: Turpo Chaparro, J. E. (2026), Zenodo 10.5281/zenodo.20516198,
CC BY 4.0 -- "Dataset on Self-Esteem, Family Communication, and Social Network
Addiction among Peruvian university students". 354 respondents.

Three instruments, three tables -- three different response formats, so one
table would make `resp` ambiguous:

  turpochaparro_2026_social_network_addiction  24 items, 0-4  (`ARS*`)
  turpochaparro_2026_self_esteem               10 items, 1-4  (`AE*`)
  turpochaparro_2026_family_communication      10 items, 1-5  (`CF*`)

`ARST`, `OBS` and `FAL` are computed columns (the ARS total and two
validity/control indices) and are dropped. `Marca_temporal` is a submission
timestamp and `Acepta_participar_en_e` a consent flag, neither an item.
"""
import os
import re

import pandas as pd
import requests

RECORD = 20516198
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {
    "turpochaparro_2026_social_network_addiction": (r"^ARS\d+$", 24, (0, 4)),
    "turpochaparro_2026_self_esteem": (r"^AE\d+$", 10, (1, 4)),
    "turpochaparro_2026_family_communication": (r"^CF\d+$", 10, (1, 5)),
}
COVARIATES = {"Sexo": "cov_sex", "Edad": "cov_age",
              "Estado_civil": "cov_marital_status",
              "Universidad": "cov_university", "Religin": "cov_religion",
              "Usa_redes_sociales": "cov_uses_social_media",
              "Qu_red_social_usas_mas": "cov_main_social_network",
              "Dnde_se_conecta_a_las_redes_sociales": "cov_connects_from",
              "Con_qu_frecuencia_se_conecta_a_las_redes_sociales":
                  "cov_connection_frequency"}
# Computed indices: ARST is the addiction total, OBS/FAL/EXC its three
# subscale scores, and AUEST/COM the self-esteem and family-communication
# totals. None is an item.
COMPUTED = ["ARST", "OBS", "FAL", "EXC", "AUEST", "COM"]
DROP = ["Marca_temporal", "Acepta_participar_en_esta_investigacin"]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if x["key"].lower().endswith((".csv", ".xlsx", ".sav")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    if p.lower().endswith(".sav"):
        import pyreadstat
        try:
            df, _m = pyreadstat.read_sav(p, apply_value_formats=False)
        except Exception:
            df, _m = pyreadstat.read_sav(p, apply_value_formats=False,
                                         encoding="latin1")
    else:
        df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)

    item_cols = {}
    for table, (pat, n, _r) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    accounted = (set(sum(item_cols.values(), [])) | set(COVARIATES)
                 | set(COMPUTED) | set(DROP))
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = [v for v in COVARIATES.values() if v in df.columns]
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
        assert long["resp"].between(lo, hi).all(), f"{table}: expected {lo}-{hi}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
