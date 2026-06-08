from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/ireejj"
TITLE = ("Artificial Intelligence in Bosnia and Herzegovina: A Study on "
         "Awareness, Attitudes and Adoption")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Column prefixes → scale name; all items are 1-5 Likert
# P7: perceived AI benefit by sector (10 items)
# P8: perceived AI risk by sector (10 items)
# P12: AI governance support mechanisms (6 items)
# P14: trust in institutions to govern AI (6 items)
SCALE_PREFIXES = {
    "ai_benefit":     "P7_",
    "ai_risk":        "P8_",
    "ai_governance":  "P12_",
    "ai_trust":       "P14_",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    # ESM_1.xlsx is the main survey response file (N=386)
    url = "https://dataverse.harvard.edu/api/access/datafile/11076712"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def _cov_cols(df: pd.DataFrame) -> dict:
    """Return a mapping from original long column name to cov_* name."""
    cov = {}
    for col in df.columns:
        c = col.strip()
        if c.startswith("PD)"):
            cov[col] = "cov_gender"
        elif c.startswith("PE)"):
            cov[col] = "cov_age"
        elif c.startswith("PG)"):
            cov[col] = "cov_education"
        elif c.startswith("PA)"):
            cov[col] = "cov_region"
    return cov


def convert():
    raw = fetch_data()
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1

    cov_rename = _cov_cols(raw)
    raw = raw.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, prefix in SCALE_PREFIXES.items():
        item_cols = [c for c in raw.columns if c.startswith(prefix)]
        # Rename to short item labels (P7_1 → p7_1, etc.)
        rename = {c: c.split(".")[0].lower().replace(" ", "_") for c in item_cols}
        wide = raw[["id"] + cov_cols + item_cols].copy()
        wide = wide.rename(columns=rename)
        short_items = list(rename.values())

        long = wide.melt(
            id_vars=["id"] + cov_cols,
            value_vars=short_items,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"karajko2025_{scale}.csv"
        long.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          scale,
            "n_participants": long["id"].nunique(),
            "n_items":        long["item"].nunique(),
            "n_responses":    len(long),
            "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
            "license":        "cc0",
            "notes":          f"1-5 Likert; scale: {scale}; "
                              "N=386 adults in Bosnia and Herzegovina; "
                              "survey in Bosnian; resp direction unverified",
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
