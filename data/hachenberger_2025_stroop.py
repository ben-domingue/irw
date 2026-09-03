from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadr


BASE = Path(__file__).resolve().parent
DATA = BASE / "Data-Code"
OUT = BASE / "hachenberger_2025_stroop"


WEBEXEC_RENAME = {
    "Webexec_Attention":      "webexec_attention",
    "Webexec_Concentration":  "webexec_concentration",
    "Webexec_MultipleTasks":  "webexec_multipletasks",
    "Webexec_LosingThoughts": "webexec_losingthoughts",
    "Webexec_FinishTask":     "webexec_finishtask",
    "Webexec_Impulsivity":    "webexec_impulsivity",
}
WEBEXEC_ITEMS = list(WEBEXEC_RENAME)


def _read_rds(filename: str) -> pd.DataFrame:
    return pyreadr.read_r(str(DATA / filename))[None]


def _occasion(df: pd.DataFrame) -> pd.Series:
    max_beeps = int(df["Beep"].max())
    return ((df["Day"].astype(int) - 1) * max_beeps + df["Beep"].astype(int)).astype(int)


def _trial_base(rds: str, task: str) -> pd.DataFrame:
    df = _read_rds(rds).dropna(subset=["ID", "Day", "Beep"]).copy()
    df["wave"] = _occasion(df)
    df["resp"] = (1 - df["Error"]).astype(int)
    df["rt"] = pd.to_numeric(df["ResponseTime"], errors="coerce") / 1000.0

    if task == "stroop":
        df["item"] = df["Trialtype"].astype(str).str.lower()
    else:
        df["item"] = df["CodeTrial"].astype(str).str.lower()

    base = pd.DataFrame({
        "id": df["ID"].astype(int),
        "item": df["item"],
        "resp": df["resp"],
        "rt": df["rt"],
        "wave": df["wave"],
        "trial_number": df["Trial"].astype(int),
        "cov_day": df["Day"].astype(int),
        "cov_beep": df["Beep"].astype(int),
    })
    if task == "stroop":
        base["trial_stimulus"] = df["CodeTrial"].astype(str)
        base["_coderesponse"] = df["CodeResponse"]
        base["_correctresponse"] = df["CorrectResponse"]
    return base


def _emit_bin(base: pd.DataFrame, out_name: str, *, task: str) -> None:
    cols = ["id", "item", "resp", "rt", "wave", "trial_number", "cov_day", "cov_beep"]
    if task == "stroop":
        cols.append("trial_stimulus")
    out = base[cols].dropna(subset=["resp"]).copy()
    out = out.sort_values(["id", "wave", "trial_number"], kind="stable").reset_index(drop=True)
    path = OUT / out_name
    out.to_csv(path, index=False)
    print(f"{path.name}: rows={len(out):,}, ids={out['id'].nunique()}, "
          f"items={sorted(out['item'].unique())}, "
          f"wave_range=[{out['wave'].min()},{out['wave'].max()}], "
          f"rt_range=[{out['rt'].min():.2f},{out['rt'].max():.2f}]s, "
          f"accuracy={out['resp'].mean():.3f}")


def _emit_nominal(base: pd.DataFrame, out_name: str) -> None:
    out = base.dropna(subset=["_coderesponse"]).copy()
    out["text"] = out["_coderesponse"].astype(int)
    out["itemcov_correctresponse"] = out["_correctresponse"].astype("Int64")
    cols = ["id", "item", "text", "resp", "rt", "wave", "trial_number",
            "cov_day", "cov_beep", "trial_stimulus", "itemcov_correctresponse"]
    out = out[cols].sort_values(["id", "wave", "trial_number"], kind="stable").reset_index(drop=True)
    path = OUT / out_name
    out.to_csv(path, index=False)
    print(f"{path.name}: rows={len(out):,}, ids={out['id'].nunique()}, "
          f"items={sorted(out['item'].unique())}, "
          f"text_range=[{out['text'].min()},{out['text'].max()}], "
          f"resp_range=[{out['resp'].min()},{out['resp'].max()}]")


def _build_webexec(rds: str, out_name: str) -> None:
    df = _read_rds(rds).copy()
    df = df.dropna(subset=WEBEXEC_ITEMS, how="all")
    df["wave"] = df["Counter"].astype(int)

    sel = df[["ID", "wave", "Day", "Beep"] + WEBEXEC_ITEMS].rename(
        columns={"ID": "id", "Day": "cov_day", "Beep": "cov_beep", **WEBEXEC_RENAME})
    long = sel.melt(id_vars=["id", "wave", "cov_day", "cov_beep"],
                    value_vars=list(WEBEXEC_RENAME.values()),
                    var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_day", "cov_beep"]]
    long = long.sort_values(["id", "wave", "item"], kind="stable").reset_index(drop=True)

    path = OUT / out_name
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, "
          f"resp_range=[{long['resp'].min()},{long['resp'].max()}], "
          f"wave_range=[{long['wave'].min()},{long['wave'].max()}]")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    for rds, tag in [("MainStudy_Stroop.rds", "main"), ("PilotStudy_Stroop.rds", "pilot")]:
        base = _trial_base(rds, "stroop")
        _emit_bin(base, f"hachenberger_2025_stroop_{tag}_bin.csv", task="stroop")
        _emit_nominal(base, f"hachenberger_2025_stroop_{tag}_nominal.csv")

    for rds, tag in [("MainStudy_GoNoGo.rds", "main"), ("PilotStudy_GoNoGo.rds", "pilot")]:
        base = _trial_base(rds, "gonogo")
        _emit_bin(base, f"hachenberger_2025_gonogo_{tag}.csv", task="gonogo")

    _build_webexec("MainStudy_Data.rds",  "hachenberger_2025_webexec_main.csv")
    _build_webexec("PilotStudy_Data.rds", "hachenberger_2025_webexec_pilot.csv")


if __name__ == "__main__":
    main()
