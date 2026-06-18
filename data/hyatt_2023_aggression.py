from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "hyatt_2023_aggression"
DATA = BASE / "osfstorage-archive (4)" / "Data + Syntax"

def _norm_item(name: str) -> str:
    return name.lower().replace(".", "_")


def _select(cols: Iterable[str], pattern: str) -> list[str]:
    rx = re.compile(pattern)
    return [c for c in cols if rx.match(c)]


def _melt(
    df: pd.DataFrame,
    item_cols: list[str],
    cov_cols: list[str],
    extra_cols: list[str] | None = None,
) -> pd.DataFrame:
    extra = list(extra_cols or [])
    id_vars = ["id"] + extra + cov_cols
    long = df[id_vars + item_cols].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(_norm_item)
    return long[["id", "item", "resp"] + extra + cov_cols]


def _rename_demogs(df: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, list[str]]:
    df = df.copy()
    rename = {src: f"cov_{dst}" for src, dst in mapping.items() if src in df.columns}
    df = df.rename(columns=rename)
    return df, list(rename.values())

def _load_prelim1(id_offset: int) -> tuple[pd.DataFrame, list[str]]:
    p = DATA / "Preliminary Study 1 Data + Syntax/study 1 data_deidentified.csv"
    df = pd.read_csv(p)
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df, cov = _rename_demogs(
        df,
        {"age": "age", "gender": "gender", "ethnicity": "ethnicity",
         "race": "race", "marital": "marital"},
    )
    df["cov_study"] = "prelim1"
    return df, cov + ["cov_study"]


def _load_prelim2(id_offset: int) -> tuple[pd.DataFrame, list[str]]:
    p = DATA / "Preliminary Study 2 Data + Syntax/study 2_data_deidentified.csv"
    df = pd.read_csv(p)
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df, cov = _rename_demogs(
        df,
        {"age": "age", "gender": "gender", "ethnicity": "ethnicity",
         "race": "race", "marital": "marital"},
    )
    df["cov_study"] = "prelim2"
    return df, cov + ["cov_study"]


def _load_study1(id_offset: int) -> tuple[pd.DataFrame, list[str]]:
    p = DATA / "Study 1 Data + Syntax/study 1 data_deidentified.csv"
    df = pd.read_csv(p)
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df, cov = _rename_demogs(
        df,
        {"age": "age", "gender": "gender", "Ethnicity": "ethnicity",
         "Race": "race", "marital": "marital"},
    )
    df["cov_study"] = "s1"
    return df, cov + ["cov_study"]


def _load_study2(id_offset: int) -> tuple[pd.DataFrame, list[str]]:
    p = DATA / "Study 2 Data + Syntax/study 2 data_deidentified.csv"
    df = pd.read_csv(p)
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df, cov = _rename_demogs(
        df,
        {"age": "age", "gender": "gender", "race": "race"},
    )
    df["cov_study"] = "s2"
    return df, cov + ["cov_study"]


def _load_study3() -> tuple[pd.DataFrame, list[str]]:
    p = DATA / "Study 3 Data + Syntax/AEQ_Study 3.csv"
    df = pd.read_csv(p)
    df = df.rename(columns={"subject": "id", "Study": "wave", "condition": "cov_condition"})
    if "BAPQ5p" in df.columns:
        df = df.rename(columns={"BAPQ5p": "BPAQ5p"})
    df["cov_study"] = "s3"
    return df, ["cov_condition", "cov_study"]

def _scale_from(
    df: pd.DataFrame, cov: list[str], pattern: str,
    extra_cols: list[str] | None = None,
) -> pd.DataFrame:
    item_cols = _select(df.columns, pattern)
    if not item_cols:
        return pd.DataFrame(columns=["id", "item", "resp"] + (extra_cols or []) + cov)
    return _melt(df, item_cols, cov, extra_cols)


def _write(long: pd.DataFrame, name: str) -> None:
    for c in list(long.columns):
        if (c.startswith("cov_") or c == "wave") and long[c].isna().all():
            long = long.drop(columns=[c])
    if "cov_study" in long.columns:
        studies = sorted(long["cov_study"].dropna().unique())
        if len(studies) == 1:
            tag = studies[0]
            long = long.drop(columns=["cov_study"])
            name = name.replace("hyatt_2023_aggression_",
                                f"hyatt_2023_aggression_{tag}_")
    out = OUT / name
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    studies = sorted(long["cov_study"].dropna().unique()) if "cov_study" in long.columns else "(single-study, in filename)"
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, studies={studies}")

def main() -> None:
    S3_MAX = 234
    p1, p1_cov = _load_prelim1(S3_MAX)
    p2, p2_cov = _load_prelim2(S3_MAX + 335)
    s1, s1_cov = _load_study1(S3_MAX + 335 + 323)
    s2, s2_cov = _load_study2(S3_MAX + 335 + 323 + 308)
    s3, s3_cov = _load_study3()

    cov_union = ["cov_age", "cov_gender", "cov_ethnicity", "cov_race",
                 "cov_marital", "cov_condition", "cov_study"]

    aeq_p1 = _scale_from(p1, p1_cov, r"^AE\d+(_R)?$")
    aeq_p1["item"] = "prelim1_" + aeq_p1["item"]
    aeq_p2 = _scale_from(p2, p2_cov, r"^AE\d+$")
    aeq_p2["item"] = "prelim2_" + aeq_p2["item"]
    aeq_s1 = _scale_from(s1, s1_cov, r"^AE\d+$")
    aeq_s1["item"] = "s1_" + aeq_s1["item"]
    aeq_s2 = _scale_from(s2, s2_cov, r"^AE_\d+$")
    aeq_s2["item"] = aeq_s2["item"].str.replace(
        r"^ae_(\d+)$", lambda m: f"aeq{int(m.group(1)):02d}", regex=True
    )
    aeq_s3 = _scale_from(s3, s3_cov, r"^AEQ\d+$", extra_cols=["wave"])
    aeq_s3["item"] = aeq_s3["item"].str.replace(
        r"^aeq(\d+)$", lambda m: f"aeq{int(m.group(1)):02d}", regex=True
    )
    aeq = pd.concat([aeq_p1, aeq_p2, aeq_s1, aeq_s2, aeq_s3], ignore_index=True)
    aeq = aeq.reindex(columns=["id", "item", "resp", "wave"] + cov_union)
    _write(aeq, "hyatt_2023_aggression_aeq.csv")

    rpa = pd.concat([
        _scale_from(p1, p1_cov, r"^rpa\d+$"),
        _scale_from(p2, p2_cov, r"^rpa\d+$"),
    ], ignore_index=True).reindex(columns=["id", "item", "resp"] + cov_union)
    _write(rpa, "hyatt_2023_aggression_rpa.csv")

    cab = pd.concat([
        _scale_from(p1, p1_cov, r"^CAB\d+$"),
        _scale_from(p2, p2_cov, r"^CAB\d+$"),
    ], ignore_index=True).reindex(columns=["id", "item", "resp"] + cov_union)
    _write(cab, "hyatt_2023_aggression_cab.csv")

    neo = pd.concat([
        _scale_from(p1, p1_cov, r"^NEO_[NEOAC]\d+$"),
        _scale_from(p2, p2_cov, r"^NEO\d+$"),
        _scale_from(s3, s3_cov, r"^NEO\d+[neoac]r?$", extra_cols=["wave"]),
    ], ignore_index=True).reindex(columns=["id", "item", "resp", "wave"] + cov_union)
    _write(neo, "hyatt_2023_aggression_neo.csv")

    _write(
        _scale_from(p2, p2_cov, r"^EPA_V\d+$").reindex(columns=["id", "item", "resp"] + cov_union),
        "hyatt_2023_aggression_epa.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^SSIS\d+r?$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_ssis.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^ACME_\d+[CDR]r?$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_acme.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^BPAQ\d+[pvah]r?$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_bpaq.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^DAQ\d+$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_daq.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^CAST_\d+(V|P|VI)r?$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_cast.csv",
    )
    _write(
        _scale_from(s3, s3_cov, r"^SRP(el|ca|ip|ct)_\d+r?$", extra_cols=["wave"])
            .reindex(columns=["id", "item", "resp", "wave"] + cov_union),
        "hyatt_2023_aggression_srp4.csv",
    )


if __name__ == "__main__":
    main()
