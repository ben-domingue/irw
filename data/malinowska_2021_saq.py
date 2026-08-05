#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260926
# DOI: 10.1371/journal.pone.0260926
#
# Malinowska-Lipien I, Micek A, Gabrys T, Kozka M, Gajda K, Gniadek A, et al.
# (2021) Nurses and physicians attitudes towards factors related to
# hospitalized patient safety. PLoS ONE 16(12): e0260926.
#
# S1 Data (XLSX) = physicians, S2 Data (XLSX) = nurses. Both contain the
# Polish adaptation of the Safety Attitudes Questionnaire (SAQ), items
# bezp_1..bezp_36 (1-6 Likert) plus 5 supervisor-focused parallel items
# ("KIER 24A".."KIER 28A") interleaved among bezp_24..bezp_28 -- these are
# distinct items (different response values row-to-row from their bezp_*
# neighbor) on the same 1-6 scale, so kept as additional items (kier_24a..
# kier_28a). bezp_d_* demographic columns excluded (no codebook to confirm
# semantics). id_lekarza (physicians) is unique per row and used as id.
# id_pielegniarki (nurses) is NOT globally unique -- same numeric id reused
# across different hospitals -- so row index is used as id instead. Rows
# with every bezp_* item blank (no response to this instrument block, most
# likely a merged multi-purpose raw file) are dropped naturally by the
# resp NaN-drop step. A single stray resp=0 on bezp_9 (nurses file, 1
# occurrence vs. hundreds of valid 1-6 responses on that item) is dropped
# as a data-entry error.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

S1_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0260926.s001"
S2_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0260926.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_xlsx(url: str) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="Arkusz1")


def item_cols(df: pd.DataFrame) -> list[str]:
    core = [c for c in df.columns if c.startswith("bezp_") and not c.startswith("bezp_d")]
    kier = [c for c in df.columns if "KIER" in c]
    return core + kier


def sanitize(c: str) -> str:
    return c.strip().lower().replace(" ", "_")


def build_long(df: pd.DataFrame, items: list[str], use_row_index: bool) -> pd.DataFrame:
    d = df.copy()
    if use_row_index:
        d = d.reset_index(drop=True)
        d["id"] = d.index + 1
    else:
        d = d.rename(columns={"id_lekarza": "id"})
        d = d.dropna(subset=["id"])
    rename_map = {c: sanitize(c) for c in items}
    d = d.rename(columns=rename_map)
    item_names = list(rename_map.values())
    for c in item_names:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_names, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # drop isolated data-entry error (resp=0 on an otherwise 1-6 scale)
    long = long[long["resp"] != 0]
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)]
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 Data (physicians)...")
    phys = fetch_xlsx(S1_URL)
    phys_items = item_cols(phys)
    write_scale(build_long(phys, phys_items, use_row_index=False), "malinowska_2021_saq_physicians.csv")

    print("Fetching S2 Data (nurses)...")
    nurses = fetch_xlsx(S2_URL)
    nurse_items = item_cols(nurses)
    write_scale(build_long(nurses, nurse_items, use_row_index=True), "malinowska_2021_saq_nurses.csv")


if __name__ == "__main__":
    convert()
