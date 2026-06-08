from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/zzpuwb"
TITLE = ("Reliability and construct validation of the Blended Learning "
         "Usability Evaluation–Questionnaire with interprofessional clinicians "
         "in Canada: a methodological study")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# BLUE-Q has 3 sections; open-text columns are excluded.
# Column indices (0-based) in the raw spreadsheet after reading with header=None.
# ID=0, Role=1, Gender=2; Likert items listed below; open-text cols omitted.
SECTIONS = {
    "pedagogical": {
        "cols": list(range(3, 13)),   # 10 items
        "items": [f"ped{i}" for i in range(1, 11)],
    },
    "synchronous": {
        "cols": list(range(15, 21)),  # 6 items
        "items": [f"sync{i}" for i in range(1, 7)],
    },
    "asynchronous": {
        "cols": list(range(23, 30)),  # 7 items
        "items": [f"async{i}" for i in range(1, 8)],
    },
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/10809863"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=None)


def convert():
    raw = fetch_data()

    # Row 0: section banners; row 1: item text; rows 2+: data
    data = raw.iloc[2:].reset_index(drop=True)

    id_col     = data[0]
    cov_role   = data[1]
    cov_gender = data[2]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for section, cfg in SECTIONS.items():
        cols  = cfg["cols"]
        items = cfg["items"]

        wide = data[cols].copy()
        wide.columns = items
        wide.insert(0, "id",         id_col.values)
        wide.insert(1, "cov_role",   cov_role.values)
        wide.insert(2, "cov_gender", cov_gender.values)

        long = wide.melt(
            id_vars=["id", "cov_role", "cov_gender"],
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_role", "cov_gender"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"arora2025_blueq_{section}.csv"
        long.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          f"blueq_{section}",
            "n_participants": long["id"].nunique(),
            "n_items":        long["item"].nunique(),
            "n_responses":    len(long),
            "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
            "license":        "cc0",
            "notes":          f"1-5 Likert; BLUE-Q section: {section}; "
                              "N=40 interprofessional clinicians (Canada); "
                              "open-text columns excluded; resp direction unverified",
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)

        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")

    _write_index(existing)


def _load_index():
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, newline="") as f:
        return list(csv.DictReader(f))


def _write_index(rows):
    with open(INDEX_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    convert()
