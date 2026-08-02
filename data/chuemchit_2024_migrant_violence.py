from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0300388
# DOI: 10.1371/journal.pone.0300388
# Chuemchit et al. (2024), "Discrimination and violence against women
# migrant workers in Thailand during the COVID-19 pandemic: A
# mixed-methods study". S2 File. CC BY 4.0. N=494.
# Two clean 5-item binary scales by violence type (economic/cyber/
# psychological/physical/sexual): partner violence (`p*12` prefix, with
# legitimate missingness for respondents without a partner in the past 12
# months) and non-partner violence (`np*12` prefix, no missingness). The
# file's other ~65 cryptic q-number columns (q75-q124 etc., no item text,
# most under 50% non-missing in this file alone) are not shipped without
# a codebook.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0300388.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PARTNER_ITEMS = ["peco12", "pcyb12", "ppsy12", "pphy12", "psex12"]
NONPARTNER_ITEMS = ["npeco12", "nppsy12", "npcyb12", "npphy12", "npsex12"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    partner = df.melt(id_vars=["id"], value_vars=PARTNER_ITEMS, var_name="item", value_name="resp")
    partner["resp"] = pd.to_numeric(partner["resp"], errors="coerce")
    partner = partner.dropna(subset=["resp"]).reset_index(drop=True)
    partner = partner[["id", "item", "resp"]]
    partner.to_csv(OUT_DIR / "chuemchit_2024_partner_violence.csv", index=False)
    print(f"chuemchit_2024_partner_violence: rows={len(partner)} ids={partner['id'].nunique()} "
          f"items={partner['item'].nunique()} resp={partner['resp'].min():.0f}-{partner['resp'].max():.0f}")

    nonpartner = df.melt(id_vars=["id"], value_vars=NONPARTNER_ITEMS, var_name="item", value_name="resp")
    nonpartner["resp"] = pd.to_numeric(nonpartner["resp"], errors="coerce")
    nonpartner = nonpartner.dropna(subset=["resp"]).reset_index(drop=True)
    nonpartner = nonpartner[["id", "item", "resp"]]
    nonpartner.to_csv(OUT_DIR / "chuemchit_2024_nonpartner_violence.csv", index=False)
    print(f"chuemchit_2024_nonpartner_violence: rows={len(nonpartner)} ids={nonpartner['id'].nunique()} "
          f"items={nonpartner['item'].nunique()} resp={nonpartner['resp'].min():.0f}-{nonpartner['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
