from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.6084/m9.figshare.32114668.v1"
TITLE = ("Pre- and Post-Intervention Data Matrix: Cognitive Development "
         "Assessment in Early Childhood Education")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# 4 subscales; column indices (0-based) in raw sheet after header rows stripped.
# Person ID = col 0 (No.), Gender = col 1 (M-F), Group = col 3.
# Item columns start at 4; subscale boundaries from the merged header row.
SUBSCALES = {
    "attention": {
        "cols":  list(range(4, 9)),
        "items": [f"att{i}" for i in range(1, 6)],
    },
    "memory": {
        "cols":  list(range(9, 14)),
        "items": [f"mem{i}" for i in range(1, 6)],
    },
    "language": {
        "cols":  list(range(14, 19)),
        "items": [f"lang{i}" for i in range(1, 6)],
    },
    "logical_thinking": {
        "cols":  list(range(19, 22)),
        "items": [f"log{i}" for i in range(1, 4)],
    },
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> dict[str, pd.DataFrame]:
    url = "https://ndownloader.figshare.com/files/64067737"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))
    return {
        "Pre-Intervention":  xl.parse("Pre-Intervention",  header=None),
        "Post-Intervention": xl.parse("Post-Intervention", header=None),
    }


def _parse_sheet(raw: pd.DataFrame, wave: int) -> pd.DataFrame:
    # Rows 0-2 are title/header; data starts at row 3
    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = range(raw.shape[1])
    out = pd.DataFrame({
        "id":         data[0],
        "cov_sex":    data[1],
        "cov_group":  data[3],
        "wave":       wave,
    })
    for cfg in SUBSCALES.values():
        for item, col in zip(cfg["items"], cfg["cols"]):
            out[item] = pd.to_numeric(data[col], errors="coerce")
    return out


def convert():
    sheets = fetch_data()
    wide_pre  = _parse_sheet(sheets["Pre-Intervention"],  wave=1)
    wide_post = _parse_sheet(sheets["Post-Intervention"], wave=2)
    wide = pd.concat([wide_pre, wide_post], ignore_index=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, cfg in SUBSCALES.items():
        long = wide[["id", "wave", "cov_sex", "cov_group"] + cfg["items"]].melt(
            id_vars=["id", "wave", "cov_sex", "cov_group"],
            var_name="item",
            value_name="resp",
        )
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "wave", "cov_sex", "cov_group"]]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        fname = f"yandun2026_{scale}.csv"
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
            "license":        "cc-by",
            "notes":          f"1-5 scale; cognitive development subscale: {scale}; "
                              "pre/post intervention (wave=1/2); N=50 children Ecuador; "
                              "cov_group=Control/Treatment; resp direction unverified",
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)

        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"wave={sorted(long['wave'].unique())} "
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
