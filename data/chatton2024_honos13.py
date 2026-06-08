from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_6084_m9_figshare_26631202_v1.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
OUT_FILE   = OUT_DIR / "chatton2024_honos13.csv"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.6084/m9.figshare.26631202.v1"
TITLE = "A 13-item Health of the Nation Outcome Scale (HoNOS-13): validation by IRT in patients with substance use disorder"
SCALE = "HoNOS-13"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def convert() -> pd.DataFrame:
    df = pd.read_csv(QUEUE_FILE)

    # HonosE* = entry (wave 1), HonosS* = sortie/exit (wave 2).
    entry_items = [i for i in df["item"].unique() if str(i).startswith("HonosE")]
    exit_items  = [i for i in df["item"].unique() if str(i).startswith("HonosS")]

    def _item_num(label):
        return label.replace("HonosE", "").replace("HonosS", "")

    entry = df[df["item"].isin(entry_items)].copy()
    entry["item"] = entry["item"].apply(_item_num).apply(lambda n: f"honos_{int(n):02d}")
    entry["wave"] = 1

    exit_ = df[df["item"].isin(exit_items)].copy()
    exit_["item"] = exit_["item"].apply(_item_num).apply(lambda n: f"honos_{int(n):02d}")
    exit_["wave"] = 2

    out = pd.concat([entry, exit_], ignore_index=True)
    out = out[["id", "item", "resp", "wave"]].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False)

    _update_index(out)

    print(f"{OUT_FILE.name}: rows={len(out)} ids={out['id'].nunique()} "
          f"items={out['item'].nunique()} waves=2 "
          f"resp_range={int(out['resp'].min())}-{int(out['resp'].max())}")
    return out


def _update_index(df: pd.DataFrame) -> None:
    row = {
        "file":           OUT_FILE.name,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          SCALE,
        "n_participants": df["id"].nunique(),
        "n_items":        df["item"].nunique(),
        "n_responses":    len(df),
        "resp_range":     f"{int(df['resp'].min())}-{int(df['resp'].max())}",
        "license":        "cc-by",
        "notes":          "HoNOS-13; wave=1 entry, wave=2 sortie/exit; "
                          "substance use disorder patient sample; 0-4 severity scale; "
                          "resp direction unverified",
        "status":         "cleaned",
    }

    existing = []
    if INDEX_FILE.exists():
        with open(INDEX_FILE, newline="") as f:
            existing = [r for r in csv.DictReader(f) if r.get("file") != row["file"]]

    with open(INDEX_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(existing)
        writer.writerow(row)


if __name__ == "__main__":
    convert()
