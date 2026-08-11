#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0265341
# S1 Dataset: https://doi.org/10.1371/journal.pone.0265341.s002
# DOI: 10.1371/journal.pone.0265341
#
# Warwas, Podgorniak-Krzykacz, Wiktorowicz, Gorniak (2022) "Demographic and
# generational determinants of Poles' participation in the sharing economy".
# Representative Polish sample, N=1000, CATI survey (2020). 8 binary
# Yes/No items on use of specific sharing-economy platforms/services
# (electronic banking, buy/sell goods online, free access to
# goods/services, crowdfunding, car sharing, accommodation booking,
# outdoor equipment sharing, locally-guided tours). Text "Yes"/"No " ->
# 1/0.

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0265341.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_RENAME = {
    "1. electronic banking": "electronic_banking",
    "2. purchase / sale of goods": "purchase_sale_goods",
    "3. free access to goods/services/knowledge/skills": "free_access_goods_services",
    "4. crowdfunding": "crowdfunding",
    "5. car sharing": "car_sharing",
    "6. accommodation booking": "accommodation_booking",
    "7. outdoor equipment sharing and exchange": "outdoor_equipment_sharing",
    "8. tours guided by locals": "tours_guided_by_locals",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns={"Gender": "cov_gender", "Age group": "cov_age_group",
                             "Voivodeship": "cov_voivodeship"})
    cov_cols = ["cov_gender", "cov_age_group", "cov_voivodeship"]

    df = df.rename(columns=ITEM_RENAME)
    item_cols = list(ITEM_RENAME.values())

    for c in item_cols:
        df[c] = df[c].astype(str).str.strip().map({"Yes": 1, "No": 0})

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "warwas_2022_sharing_economy"
    out_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
