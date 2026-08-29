"""CMNI and CFNI in Ecuadorian female undergraduates who binge drink.

Source: Hernandez Mantilla, G. E., Sancerni Beitia, M. D. & Cortes Tomas,
M. T. (2024), Zenodo 10.5281/zenodo.13997042, CC BY 4.0 -- "Influence of
Gender on Binge Drinking among Female Ecuadorian Undergraduates: Masculine
and Feminine Norms". 782 respondents, all female.

Two instruments, two tables, both on the same 0-3 scale but measuring
conformity to opposite norm sets:

  hernandezmantilla_2024_cmni   Conformity to Masculine Norms Inventory
  hernandezmantilla_2024_cfni   Conformity to Feminine Norms Inventory (84)

DUPLICATE DEPOSIT. The same data is on Zenodo twice -- 10.5281/zenodo.12608500
(2024-07-01) and 10.5281/zenodo.13997042 (2024-10-26). The two files share 209
columns whose values are identical row for row; the earlier one differs only by
an extra SPSS `filter_$` scratch variable. Counted once, from the later record.

CMNI items 21, 35 and 46 have no plain `CMNI21`-style column: they were
administered in two gendered wordings (`Hombre_21` "In general, I control the
women in my life" vs `Mujer_21` "In general, my life is controlled by men").
Those are opposite-direction statements, not one item, so they ship as
separate items rather than being merged -- and they are answered by different
numbers of people (Mujer_ by ~775, Hombre_ by 75), which merging would hide.

Subscale scores (`Ganar_CMNI`, `Delgadez_CFNI`, ...) and the `*_SUMA_TOTAL`
columns are computed aggregates and are dropped. `P2_sexo` is single-valued
(the sample is all female) so it is recorded here, not shipped as a covariate.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 13997042
DUPLICATE_OF = 12608500
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALE = {0.0, 1.0, 2.0, 3.0}
N_CFNI = 84
GENDERED = ("Hombre_", "Mujer_")     # CMNI 21 / 35 / 46, two wordings each
COVARIATES = {
    "P5_edad_inicio": "cov_age_first_alcohol",
    "P20_Veces_Ult_6m": "cov_binge_episodes_6m",
    "BDsi_no": "cov_binge_drinker",
}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)

    cmni = sorted((c for c in df.columns if re.fullmatch(r"CMNI\d+", c)),
                  key=lambda c: int(c[4:]))
    cfni = sorted((c for c in df.columns if re.fullmatch(r"CFNI\d+", c)),
                  key=lambda c: int(c[4:]))
    gendered = [c for c in df.columns if c.startswith(GENDERED)]

    # The three gaps in CMNI numbering must be exactly the gendered pairs;
    # any other gap would mean items are genuinely missing from the file.
    gaps = sorted(set(range(1, 95)) - {int(c[4:]) for c in cmni})
    assert gaps == sorted({int(c.split("_")[1]) for c in gendered}), \
        f"CMNI numbering gaps {gaps} do not match gendered items {gendered}"
    assert [int(c[4:]) for c in cfni] == list(range(1, N_CFNI + 1)), \
        "CFNI numbering is not 1..84"

    d = df.rename(columns=COVARIATES).copy()
    for src, dst in COVARIATES.items():
        vl = meta.variable_value_labels.get(src)
        if vl:
            d[dst] = d[dst].map(vl)
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in [
        ("hernandezmantilla_2024_cmni", cmni + gendered),
        ("hernandezmantilla_2024_cfni", cfni),
    ]:
        observed = {v for v in pd.unique(d[cols].values.ravel()) if pd.notna(v)}
        assert observed <= SCALE, \
            f"{table}: off-scale response(s) {sorted(observed - SCALE)}"

        long = d.melt(id_vars=["id"] + list(COVARIATES.values()),
                      value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        out = long[["id", "item", "resp"] + list(COVARIATES.values())]
        out.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(out):,} responses | {out['id'].nunique():,} ids | "
              f"{out['item'].nunique()} items")


if __name__ == "__main__":
    main()
