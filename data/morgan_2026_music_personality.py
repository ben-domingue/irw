from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "morgan_2026_music_personality"
SRC = BASE / "osfstorage-archive (3)" / "data.csv"

ACTIVITY_RENAME = {
    "Purchase music subscription (Apple, Spotify, etc). ":            "music_act_subscribe",
    "Download music from streaming services (Apple, Spotify, etc.).": "music_act_download",
    "Share music with friends or colleagues. ":                       "music_act_share",
    "Read about musicians' biographies (online, books, magazines).":  "music_act_biography",
    "Update my playlists with new music.":                            "music_act_playlist",
    "Watch television programs or films about musicians.":            "music_act_tv",
    "Attend music concerts or recitals.":                             "music_act_concert",
    "Visit music shops with the intent of purchasing music. ":        "music_act_shop",
    "Play a musical instrument (including vocals).":                  "music_act_instrument",
    "Imagine myself performing a song while listening to it. ":       "music_act_imagine",
}


def _to_unix(series: pd.Series) -> pd.Series:
    """Source StartDate is e.g. '11/8/2023 11:22' (timezone-naive). Treat as
    UTC and convert to Unix seconds per the IRW `date` field spec."""
    ts = pd.to_datetime(series, format="%m/%d/%Y %H:%M", errors="coerce", utc=True)
    secs = (ts - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds()
    return secs.astype("Int64")


def _load() -> pd.DataFrame:
    df = pd.read_csv(SRC, dtype=str)
    # Drop SurveyMonkey "Response" sub-header row
    df = df.iloc[1:].reset_index(drop=True)
    # Promote "Custom Data 1" to id (integer participant id)
    df["id"] = pd.to_numeric(df["Custom Data 1"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["id"]).copy()
    df["date"] = _to_unix(df["StartDate"])
    df["cov_catch1"] = pd.to_numeric(df["Catch1"], errors="coerce").astype("Int64")
    df = df.rename(columns=ACTIVITY_RENAME)
    return df


def _melt(df: pd.DataFrame, item_cols: list[str], outfile: Path) -> int:
    cov = ["date", "cov_catch1"]
    id_vars = ["id"] + cov
    long = df[id_vars + item_cols].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["item"].str.lower()
    long = long[["id", "item", "resp", "date", "cov_catch1"]]
    outfile.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(outfile, index=False)
    return len(long)


def main() -> None:
    df = _load()
    plans = [
        ("bfi",            [c for c in df.columns if re.match(r"^BFI\d+$", c)]),
        ("stompr",         [c for c in df.columns if re.match(r"^STOMPR\d+$", c)]),
        ("pvq",            [c for c in df.columns if re.match(r"^ESS\d+$", c)]),
        ("music_activity", [c for c in df.columns if c.startswith("music_act_")]),
    ]
    for tag, item_cols in plans:
        out = OUT / f"morgan_2026_music_personality_{tag}.csv"
        n = _melt(df, item_cols, out)
        print(f"{out.name}: rows={n}, items={len(item_cols)}")


if __name__ == "__main__":
    main()
