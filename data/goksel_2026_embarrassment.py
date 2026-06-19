from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "goksel_2026_embarrassment"
DATA = BASE / "osfstorage-archive (1)"


def _load_study(folder: str, n: str, id_offset: int, study_tag: str) -> pd.DataFrame:
    p = DATA / folder / f"Study{n} Cleaned Data.xls"
    df = pd.read_excel(p)
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df["cov_study"] = study_tag
    cov_rename = {
        "age":               "cov_age",
        "Age_participant":   "cov_age",
        "gender":            "cov_gender",
        "Gender_participant": "cov_gender",
        "display":           "cov_display",
        "story":             "cov_story",
        "attention":         "cov_attention",
    }
    df = df.rename(columns={k: v for k, v in cov_rename.items() if k in df.columns})
    return df


def _melt(df: pd.DataFrame, item_cols: list[str], rename: dict[str, str]) -> pd.DataFrame:
    cov = [c for c in ["cov_age", "cov_gender", "cov_display", "cov_story",
                       "cov_attention", "cov_study"] if c in df.columns]
    id_vars = ["id"] + cov
    present = [c for c in item_cols if c in df.columns]
    if not present:
        return pd.DataFrame(columns=["id", "item", "resp"] + cov)
    long = df[id_vars + present].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(rename).fillna(long["item"])
    long["item"] = long["item"].str.lower()
    return long[["id", "item", "resp"] + cov]


def _write(parts: list[pd.DataFrame], name: str) -> None:
    long = pd.concat([p for p in parts if len(p)], ignore_index=True)
    cov_union = ["cov_age", "cov_gender", "cov_display", "cov_story",
                 "cov_attention", "cov_study"]
    long = long.reindex(columns=["id", "item", "resp"] + cov_union)
    for c in list(long.columns):
        if c.startswith("cov_") and long[c].isna().all():
            long = long.drop(columns=[c])
    out = OUT / name
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    studies = sorted(long["cov_study"].dropna().unique()) if "cov_study" in long.columns else []
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, studies={studies}")


def main() -> None:
    s1 = _load_study("Study 1",  "1",  0,                  "s1")
    s2 = _load_study("Study 2",  "2",  600,                "s2")
    s3 = _load_study("Study 3",  "3",  600 + 399,          "s3")
    s4 = _load_study("Study 4",  "4",  600 + 399 + 602,    "s4")
    s5 = _load_study("Study 5",  "5",  600 + 399 + 602 + 303, "s5")
    s6 = _load_study("Study 6",  "6",  600 + 399 + 602 + 303 + 600, "s6")
    sS1 = _load_study("Study S1", "S1", 600 + 399 + 602 + 303 + 600 + 809, "sS1")
    sS2 = _load_study("Study S2", "S2", 600 + 399 + 602 + 303 + 600 + 809 + 300, "sS2")

    def _cols(prefix: str, n: int) -> list[str]:
        return [f"{prefix}_{i}" for i in range(1, n + 1)]

    def _id(items): return {c: c for c in items}

    auth = _cols("authenticity", 12)
    _write([_melt(s1, auth, _id(auth)), _melt(s2, auth, _id(auth)),
            _melt(s4, auth, _id(auth)), _melt(s6, auth, _id(auth))],
           "goksel_2026_embarrassment_authenticity.csv")

    wcm = _cols("WCM", 12)
    _write([_melt(s2, wcm, _id(wcm)), _melt(s4, wcm, _id(wcm)),
            _melt(s6, wcm, _id(wcm))],
           "goksel_2026_embarrassment_wcm.csv")

    res = _cols("resilience", 9)
    _write([_melt(s1, res, _id(res)), _melt(s4, res, _id(res))],
           "goksel_2026_embarrassment_resilience.csv")

    sc = _cols("socialcompetence", 10)
    _write([_melt(s1, sc, _id(sc)), _melt(s4, sc, _id(sc))],
           "goksel_2026_embarrassment_socialcompetence.csv")

    req_5 = _cols("required_emb", 3)
    act_5 = _cols("actual_emb", 3)
    _write([_melt(s5, req_5, _id(req_5)),
            _melt(s5, act_5, _id(act_5))],
           "goksel_2026_embarrassment_emb_perception.csv")

    wc = _cols("warmth_competence", 8)
    _write([_melt(s1, wc, _id(wc))], "goksel_2026_embarrassment_warmth_competence.csv")

    for tag, prefix, n in [("puremorality", "puremorality", 8),
                            ("purewarmth", "purewarmth", 8),
                            ("moralityandwarmth", "moralityandwarmth", 8)]:
        cols = _cols(prefix, n)
        _write([_melt(s3, cols, _id(cols))],
               f"goksel_2026_embarrassment_{tag}.csv")

    app = _cols("appeasement", 3)
    _write([_melt(s5, app, _id(app))],
           "goksel_2026_embarrassment_appeasement.csv")

    for tag, prefix, n in [("affectivetrust", "affectivetrust", 6),
                            ("liking", "liking", 4),
                            ("similarity", "similarity", 3)]:
        cols = _cols(prefix, n)
        _write([_melt(sS1, cols, _id(cols))],
               f"goksel_2026_embarrassment_{tag}.csv")

    sn = _cols("socialnorm", 2)
    _write([_melt(sS2, sn, _id(sn))],
           "goksel_2026_embarrassment_socialnorm.csv")


if __name__ == "__main__":
    main()
