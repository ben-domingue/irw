from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0270888
# DOI: 10.1371/journal.pone.0270888
# Bartoli et al. (2022), "Driven by notifications - exploring the
# effects of badge notifications on user experience". S1 Dataset. CC BY
# 4.0. N=1010. Item = named app, resp = whether the respondent enabled/
# noticed badge notifications for that app (binary, encoded 0/100 in the
# source rather than 0/1 -- left as-is, still a valid ordinal response).
# The `Badge` column (unclear meaning, possibly a derived summary) is not
# shipped as an item.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0270888.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Group": "cov_group", "Age": "cov_age", "Gender": "cov_gender"}
ITEM_COLS = ["WhatsApp", "Gmail", "Youtube", "Facebook", "Amazon", "Impostazioni",
             "Linkedin", "Messenger", "SMS", "Telefono", "Shazam", "Outlook",
             "Calendario", "Justeat", "Teams"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "Participant ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "bartoli_2022_badge_notifications.csv"
    long.to_csv(out_path, index=False)
    print(f"bartoli_2022_badge_notifications: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
