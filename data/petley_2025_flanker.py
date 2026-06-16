from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "petley_2025_flanker"
DATA = BASE / "osfstorage-archive" / "Data"


STUDY1_CONDS = ["Cong", "Phono", "Seman", "Incong"]
STUDY2_CONDS = ["Cong", "Incong"]


def _melt(df: pd.DataFrame, conds: list[str]) -> pd.DataFrame:
    pieces = []
    for cond in conds:
        chunk = df[["SNUM", f"{cond}_nCorr", f"{cond}_nTrials",
                    f"{cond}_medianRT"]].copy()
        chunk.columns = ["id", "ncorr", "ntrials", "rt_median"]
        chunk["flank"] = cond.lower()
        pieces.append(chunk)
    long = pd.concat(pieces, ignore_index=True)
    long = long.dropna(subset=["ntrials", "ncorr"])
    long["ntrials"] = long["ntrials"].astype(int)
    long["ncorr"] = long["ncorr"].astype(int)
    long["rt_median"] = long["rt_median"].astype(float) / 1000.0
    return long


def _expand(long: pd.DataFrame, keep: list[str]) -> pd.DataFrame:
    long = long.reset_index(drop=True)
    correct = long.loc[long.index.repeat(long["ncorr"]), keep].copy()
    correct["resp"] = 1
    nincorrect = long["ntrials"] - long["ncorr"]
    incorrect = long.loc[long.index.repeat(nincorrect), keep].copy()
    incorrect["resp"] = 0
    out = pd.concat([correct, incorrect], ignore_index=True)
    out = out.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    if "wave" not in out.columns:
        out["wave"] = out.groupby(["id", "item"]).cumcount() + 1
    return out


def _study1(file_a: str, file_b: str, label_a: str, label_b: str,
            tag: str) -> None:
    parts = []
    for f, label in [(file_a, label_a), (file_b, label_b)]:
        long = _melt(pd.read_csv(DATA / f), STUDY1_CONDS)
        attend = label.lower().replace("attend", "")
        long["item"] = long["flank"]
        long["itemcov_attend"] = attend
        parts.append(long)
    long = pd.concat(parts, ignore_index=True)
    out_df = _expand(long, ["id", "item", "itemcov_attend", "rt_median"])
    out_df = out_df[["id", "item", "resp", "rt_median", "itemcov_attend"]]
    out = OUT / f"petley_2025_flanker_study1_{tag}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print(f"{out.name}: rows={len(out_df)}, items={sorted(out_df['item'].unique())}, "
          f"attend={sorted(out_df['itemcov_attend'].unique())}, "
          f"ids={out_df['id'].nunique()}, "
          f"rt_median_range=[{out_df['rt_median'].min():.3f},{out_df['rt_median'].max():.3f}]s")


def _study2(file1: str, file2: str, tag: str) -> None:
    parts = []
    for f, wave in [(file1, 1), (file2, 2)]:
        long = _melt(pd.read_csv(DATA / f), STUDY2_CONDS)
        long["item"] = long["flank"]
        long["wave"] = wave
        parts.append(long)
    long = pd.concat(parts, ignore_index=True)
    out_df = _expand(long, ["id", "item", "wave", "rt_median"])
    out_df = out_df[["id", "item", "resp", "rt_median", "wave"]]
    out = OUT / f"petley_2025_flanker_study2_{tag}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print(f"{out.name}: rows={len(out_df)}, items={sorted(out_df['item'].unique())}, "
          f"ids={out_df['id'].nunique()}, "
          f"waves={sorted(int(w) for w in out_df['wave'].unique())}, "
          f"rt_median_range=[{out_df['rt_median'].min():.3f},{out_df['rt_median'].max():.3f}]s")


def main() -> None:
    _study1("generated_flanker_attendChild_groupData.csv",
            "generated_flanker_attendWoman_groupData.csv",
            "AttendChild", "AttendWoman", "childwoman")
    _study1("generated_flankerMW_attendMan_groupData.csv",
            "generated_flankerMW_attendWoman_groupData.csv",
            "AttendMan", "AttendWoman", "manwoman")
    _study1("generated_flankerGM_attendGirl_groupData.csv",
            "generated_flankerGM_attendMan_groupData.csv",
            "AttendGirl", "AttendMan", "girlman")
    _study2("generated_auditoryTest1_groupData.csv",
            "generated_auditoryTest2_groupData.csv", "auditory")
    _study2("generated_visualTest1_groupData.csv",
            "generated_visualTest2_groupData.csv", "visual")


if __name__ == "__main__":
    main()
