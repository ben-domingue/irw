from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331340
# DOI: 10.1371/journal.pone.0331340
# Yu et al. (2025), "The effect of mobile phone addiction on sleep
# procrastination in adolescents: The longitudinal mediating role of
# physical activity behavior". S1 File. CC BY 4.0. N=373, 3 waves
# (T0/T1/T2). Three raw-item scales: mobile phone addiction (SA, 22
# items), bedtime procrastination (BP, 9 items), physical activity (PE,
# 3 items). "Average score" columns (derived) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0331340.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "yu_2025_mobile_addiction": ("SA", range(1, 23)),
    "yu_2025_bedtime_procrastination": ("BP", range(1, 10)),
    "yu_2025_physical_activity": ("PE", range(1, 4)),
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, (code, item_range) in SCALES.items():
        frames = []
        for wave, prefix in enumerate(["T0", "T1", "T2"], start=1):
            cols = {f"{prefix}{code}{i}": f"{code}{i}" for i in item_range}
            sub = df[["id"] + list(cols.keys())].rename(columns=cols)
            long = sub.melt(id_vars=["id"], var_name="item", value_name="resp")
            long["wave"] = wave
            frames.append(long)
        long = pd.concat(frames, ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "wave"]]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
