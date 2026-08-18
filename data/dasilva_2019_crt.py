#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_for_the_paper_Incomplete_Information_Choices_Cognitive_Ability_and_Personality/7582019
# DOI: 10.6084/m9.figshare.7582019.v1
# License: CC BY 4.0
#
# Companion to data/dasilva_2019_hexaco24.py, which ships the HEXACO-24 block
# of the same deposit. This script ships the Cognitive Reflection Test block.
#
# The workbook's "Base de dados" sheet holds every respondent (404 rows) with
# the CRT answers as free text, and the "Completas" sheet holds the 233
# respondents the authors scored, adding "Acerto N" (Sim/Nao = correct/
# incorrect) columns. The scoring is the authors' own, so responses are taken
# from "Completas" and mapped back onto "Base de dados" row order so that `id`
# matches dasilva_2019_hexaco24's `id` for the same respondent.
#
# Only the three classic CRT items are shipped. The workbook's items 4-6 are a
# conditional alternate form, shown only to respondents who said they already
# knew the classic items, and were answered by 22 people -- far below the
# sample-size floor -- so they are dropped rather than shipped as a sparse
# block of the same table.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://ndownloader.figshare.com/files/14080583"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# The three classic CRT items, in workbook column order.
CRT_COLS = [
    "Um bastão e uma bola custam $1,10. O bastão custa um real a mais do que a bola. Quanto custa a bola?",
    "Se são necessárias 5 máquinas por 5 minutos para se fazer 5 aparelhos, quanto tempo 100 máquinas fariam 100 aparelhos?",
    "Num lago há uma área coberta por vitórias-régias. Todos os dias a área dobra de tamanho. Se são precisos 48 dias para a área cobrir todo o lago, em quantos dias a área cobriria a metade do lago?",
]
SCORE_COLS = ["Acerto 1", "Acerto 2", "Acerto 3"]

RESP_MAP = {"Sim": 1, "Não": 0}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUT_DIR, "_dasilva_2019_crt_raw.xlsx")
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    with open(raw_path, "wb") as f:
        f.write(r.content)

    base = pd.read_excel(raw_path, sheet_name="Base de dados")
    comp = pd.read_excel(raw_path, sheet_name="Completas")
    os.remove(raw_path)

    for c in CRT_COLS:
        assert c in base.columns and c in comp.columns, f"missing column: {c!r}"
    for c in SCORE_COLS:
        assert c in comp.columns, f"missing column: {c!r}"
        assert set(comp[c].dropna().unique()) <= set(RESP_MAP), f"unexpected value in {c!r}"

    # id follows "Base de dados" row order, matching dasilva_2019_hexaco24.
    base = base.reset_index(drop=True)
    base.insert(0, "id", base.index + 1)

    # "Data" alone is not unique (one timestamp is shared by two distinct
    # respondents), so join on the timestamp plus the raw answers as well.
    # "Completas" holds cleaned numeric versions of the free-text answers, so
    # the answers themselves can't serve as a join key -- the submission
    # timestamp does. It is unique for all but one pair of respondents, and
    # that pair is separable because only one of the two answered all three
    # CRT items, which every "Completas" respondent by definition did.
    dup = base["Data"].duplicated(keep=False)
    complete = base[CRT_COLS].notna().all(axis=1)
    base_j = base[~dup | complete]
    assert not base_j["Data"].duplicated().any(), "ambiguous timestamps remain"

    merged = comp[["Data"] + SCORE_COLS].merge(base_j[["id", "Data"]], on="Data",
                                               how="left", validate="one_to_one")
    assert merged["id"].notna().all(), "some Completas rows did not match Base de dados"
    merged["id"] = merged["id"].astype(int)

    rename = {sc: f"CRT_{i}" for i, sc in enumerate(SCORE_COLS, start=1)}
    merged = merged.rename(columns=rename)

    long = merged.melt(id_vars=["id"], value_vars=list(rename.values()),
                       var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(RESP_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    out_name = "dasilva_2019_crt"
    long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
