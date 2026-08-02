from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0311352
# DOI: 10.1371/journal.pone.0311352
# Rodriguez Quiroga et al. (2024), "Validation of the Argentine version
# of the epistemic trust, mistrust, and credulity questionnaire". S1
# Table (semicolon-delimited). CC BY 4.0. N=1018. 15-item Epistemic
# Trust, Mistrust, and Credulity Inventory (ETMCI), item-numbering
# preserved from the source.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0311352.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"e{i}" for i in range(1, 16)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def convert():
    df = fetch().rename(columns={"ID": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "rodriguezquiroga_2024_epistemic_trust.csv"
    long.to_csv(out_path, index=False)
    print(f"rodriguezquiroga_2024_epistemic_trust: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
