from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "west_2021_retaliatory_aggression"
DATA = BASE / "osfstorage-archive (2)"


def _select(cols, pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [c for c in cols if rx.match(c)]


def _melt(df: pd.DataFrame, item_cols: list[str], cov_cols: list[str]) -> pd.DataFrame:
    id_vars = ["id"] + cov_cols
    long = df[id_vars + item_cols].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].str.lower().str.replace(".", "_", regex=False)
    return long[["id", "item", "resp"] + cov_cols]


def _canon_bscs(item: pd.Series) -> pd.Series:
    return item.str.replace(r"^bscs_", "bscs", regex=True)


def _canon_cast(item: pd.Series) -> pd.Series:
    return item.str.replace(r"p$", "p", regex=True).str.lower()


def _canon_bpaq(item: pd.Series) -> pd.Series:
    s = item.str.replace(r"^bp_?p(\d+)(r?)$", r"bpaq\1\2", regex=True)
    s = s.str.replace(r"^bpaq(\d+)p$", r"bpaq\1", regex=True)
    return s


def _canon_acq(item: pd.Series) -> pd.Series:
    return item.str.replace(r"^o_acq(\d+)$", r"acq_\1", regex=True)


def _load(path: Path, rename_map: dict[str, str], study_tag: str,
          id_source: str) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(DATA / path)
    df = df.rename(columns=rename_map)
    df["id"] = df[id_source]
    df["cov_study"] = study_tag
    cov = [c for c in df.columns if c.startswith("cov_")]
    return df, cov


def main() -> None:
    s1, c1 = _load(Path("Study 1/Data + Code/ITAP1_FINAL_OSF.csv"),
                   {"Gender": "cov_gender", "Provocation": "cov_provocation"}, "study1", "Participant")
    s2, c2 = _load(Path("Study 2/Data + Code/Study2_OSF.csv"),
                   {"Gender": "cov_gender"}, "study2", "Participant")
    s3, c3 = _load(Path("Study 3/Data + Code/Study3_OSF.csv"),
                   {"Gender": "cov_gender", "ColdPressor": "cov_coldpressor"}, "study3", "Participant")
    s4, c4 = _load(Path("Study 4/Data + Code/Study 4_OSF.csv"),
                   {"Age": "cov_age", "Gender": "cov_gender", "condition": "cov_condition"},
                   "study4", "subject")
    if "BAPQ5" in s4.columns:
        s4 = s4.rename(columns={"BAPQ5": "BPAQ5"})
    s5, c5 = _load(Path("Study 5/Data + Code/Study 5_OSF.csv"),
                   {"Gender": "cov_gender"}, "study5", "Participant")
    s6, c6 = _load(Path("Study 6/Data + Code/Study6_OSF.csv"),
                   {"Gender": "cov_gender"}, "study6", "Participant")

    cov_union = ["cov_age", "cov_gender", "cov_provocation",
                 "cov_coldpressor", "cov_condition", "cov_study"]

    def write(long: pd.DataFrame, name: str) -> None:
        long = long.reindex(columns=["id", "item", "resp"] + cov_union)
        for c in list(long.columns):
            if c.startswith("cov_") and long[c].isna().all():
                long = long.drop(columns=[c])
        if "cov_study" in long.columns:
            studies = sorted(long["cov_study"].dropna().unique())
            if len(studies) == 1:
                tag = studies[0]
                long = long.drop(columns=["cov_study"])
                name = name.replace("west_2021_retaliatory_aggression_",
                                    f"west_2021_retaliatory_aggression_{tag}_")
        out = OUT / name
        out.parent.mkdir(parents=True, exist_ok=True)
        long.to_csv(out, index=False)
        studies = sorted(long["cov_study"].dropna().unique()) if "cov_study" in long.columns else "(single-study, in filename)"
        print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, studies={studies}")

    parts = []
    for df, cov in [(s1, c1), (s2, c2), (s3, c3), (s4, c4), (s5, c5), (s6, c6)]:
        cols = _select(df.columns, r"^BSCS_?\d+r?$")
        if cols:
            m = _melt(df, cols, cov)
            m["item"] = _canon_bscs(m["item"])
            parts.append(m)
    write(pd.concat(parts, ignore_index=True), "west_2021_retaliatory_aggression_bscs.csv")

    parts = []
    for df, cov in [(s2, c2), (s3, c3), (s4, c4), (s5, c5), (s6, c6)]:
        cols = _select(df.columns, r"^ARS_\d+[a-zA-Z]+$")
        if cols:
            parts.append(_melt(df, cols, cov))
    write(pd.concat(parts, ignore_index=True), "west_2021_retaliatory_aggression_ars.csv")

    parts = []
    for df, cov in [(s2, c2), (s4, c4), (s5, c5), (s6, c6)]:
        cols = _select(df.columns, r"^CAST_\d+[Pp]$")
        if cols:
            m = _melt(df, cols, cov)
            m["item"] = _canon_cast(m["item"])
            parts.append(m)
    write(pd.concat(parts, ignore_index=True), "west_2021_retaliatory_aggression_cast.csv")

    parts = []
    for df, cov, pat in [
        (s1, c1, r"^BP_?p\d+r?$"),
        (s2, c2, r"^BP_?p\d+r?$"),
        (s4, c4, r"^BPAQ\d+r?$"),
        (s5, c5, r"^BPAQ\d+r?p$"),
        (s6, c6, r"^BP_?p\d+r?$"),
    ]:
        cols = _select(df.columns, pat)
        if cols:
            m = _melt(df, cols, cov)
            m["item"] = _canon_bpaq(m["item"])
            parts.append(m)
    write(pd.concat(parts, ignore_index=True), "west_2021_retaliatory_aggression_bpaq.csv")

    parts = []
    for df, cov, pat in [
        (s2, c2, r"^ACQ_\d+$"),
        (s3, c3, r"^ACQ_\d+$"),
        (s4, c4, r"^O_ACQ\d+$"),
    ]:
        cols = _select(df.columns, pat)
        if cols:
            m = _melt(df, cols, cov)
            m["item"] = _canon_acq(m["item"])
            parts.append(m)
    write(pd.concat(parts, ignore_index=True), "west_2021_retaliatory_aggression_acq.csv")

    cols = _select(s3.columns, r"^DT3_\d+Pr?$")
    write(_melt(s3, cols, c3), "west_2021_retaliatory_aggression_sd3_psychopathy.csv")

    cols = _select(s4.columns, r"^DEQ_\d+a$")
    write(_melt(s4, cols, c4), "west_2021_retaliatory_aggression_deq.csv")


if __name__ == "__main__":
    main()
