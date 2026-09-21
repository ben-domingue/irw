#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0205389
# DOI: 10.1371/journal.pone.0205389
# Data: journal.pone.0205389_S1_File.sav (S1 File, "Data used in study")
# License: CC BY 4.0 (verified on the article page and in Crossref metadata)
#
# Simo-Sanz, Ballestar-Tarin & Martinez-Sabater (2018), "Smartphone
# Addiction Inventory (SPAI): Translation, adaptation and validation of
# the tool in Spanish adult population." PLOS ONE. N=2,958.
#
# The deposit is a single SPSS file holding one instrument at item level:
# the Spanish SPAI, 26 items (i1..i26) on a 1-4 agreement scale, complete
# for every respondent. Everything else in the file is either a
# demographic/usage descriptor (carried as cov_*) or a composite derived
# from the 26 items (dropped -- see below).
#
# Item text: not shipped -- the .sav carries NO variable labels at all
# (0 of 52 columns) and value labels for exactly one variable
# (`estudios`), none of them on i1..i26. Both label levels checked. The
# administered Spanish wording of the 26 SPAI items is printed in the
# article's own Table 2 (item-by-item, Spanish), which is a page fetch
# away but not in this deposit; the English original is Lin et al. (2014).
import os
import numpy as np
import pandas as pd
import pyreadstat

RAW = os.environ.get("SPAI_SAV", "journal.pone.0205389_S1_File.sav")
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "automated_finding", "irw_output")

ITEMS = [f"i{n}" for n in range(1, 27)]

# Derived from the 26 items (subscale and total scores) -- composites, not
# responses, so they are dropped rather than carried.
COMPOSITES = ["SPAI_tot", "SPAI_FINAL", "F1_craving", "F2_afectacion",
              "F3_sueño", "F4_tolerancia"]
# Banded recodes of `edad`, which is kept in full.
REDUNDANT = ["edad_gr", "edadgrup"]

COVS = {
    "edad": "cov_age",
    "sexo": "cov_sex",
    "estudios": "cov_education",
    "comunidad": "cov_region",
    "primermovil": "cov_age_first_phone",
    "uso_trabajo": "cov_use_work",
    "uso_familia1": "cov_use_family1",
    "uso_familia2": "cov_use_family2",
    "uso_info": "cov_use_info",
    "uso_social": "cov_use_social",
    "uso_game": "cov_use_gaming",
    "horas_dia": "cov_hours_per_day",
    "dinero": "cov_monthly_spend",
    "apagado_noche": "cov_off_at_night",
    "olvido": "cov_forgets_phone",
    "fantasma": "cov_phantom_vibration",
    "molestia": "cov_bothered_without_phone",
    "dependencia": "cov_self_rated_dependence",
}


def main():
    df, meta = pyreadstat.read_sav(RAW)

    # Balance the books: every source column is an item, a covariate, a
    # composite, or a redundant recode. Anything else is a bug.
    accounted = set(ITEMS) | set(COVS) | set(COMPOSITES) | set(REDUNDANT)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"columns: {len(ITEMS)} items, {len(COVS)} covariates, "
          f"{len(COMPOSITES)} composites dropped, {len(REDUNDANT)} recodes dropped")

    # No id column in the deposit; rows are respondents.
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"])

    # SPAI is a 1-4 scale; nothing outside it should survive.
    bad = long.loc[~long["resp"].isin([1, 2, 3, 4]), "resp"].unique()
    assert len(bad) == 0, f"off-scale resp values: {bad}"
    assert (long["resp"] % 1 == 0).all(), "fractional resp -- check for imputation"

    long["item"] = long["item"].str.replace(r"^i", "SPAI_", regex=True)
    long = long[["id", "item", "resp"] + cov_cols]

    n = long["id"].nunique()
    assert n >= 100, f"below the 100-id floor: {n}"
    print(f"{len(long):,} responses | {n:,} ids | {long['item'].nunique()} items")

    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, "simo_sanz_2018_spai.csv")
    long.to_csv(out, index=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
