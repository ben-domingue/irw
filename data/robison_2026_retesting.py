from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
COG = BASE / "Data" / "Cognitive"
SR = BASE / "Data" / "Self-report"
ACAD = BASE / "Data" / "Academic"
OUT = BASE / "robison_2026_retesting"




def _build_covariates() -> pd.DataFrame:
    demo = pd.read_csv(SR / "demographics_deidentified.csv")
    demo = demo.rename(columns={"SubjectId": "id"})
    demo["id"] = demo["id"].astype(str)
    race_cols = ["AmerIndian", "Asian", "Black", "Hispanic", "Hawaii", "White", "Other"]
    def _race(row):
        hits = [c for c in race_cols if row.get(c) == 1]
        return ",".join(hits) if hits else pd.NA
    demo["cov_race"] = demo.apply(_race, axis=1)
    demo = demo.rename(columns={
        "Age": "cov_age",
        "Gender": "cov_gender",
        "NativeEnglish": "cov_native_english",
        "ColorBlind": "cov_color_blind",
        "WearsGlasses": "cov_wears_glasses",
        "NormalVision": "cov_normal_vision",
        "NormalHearing": "cov_normal_hearing",
        "Medication": "cov_medication",
    })
    demo = demo[["id", "cov_age", "cov_gender", "cov_race",
                 "cov_native_english", "cov_color_blind",
                 "cov_wears_glasses", "cov_normal_vision",
                 "cov_normal_hearing", "cov_medication"]]

    acad = pd.read_csv(ACAD / "gpa_major_deidentified.csv")
    acad = acad.rename(columns={"subject": "id"})
    acad["id"] = acad["id"].astype(str)
    acad = acad.sort_values(["id", "TERM"]).drop_duplicates("id", keep="last")
    acad = acad.rename(columns={
        "cumulative_gpa": "cov_gpa",
        "major": "cov_major",
        "major_type": "cov_major_type",
    })[["id", "cov_gpa", "cov_major", "cov_major_type"]]

    return demo.merge(acad, on="id", how="outer")


def _melt_self_report(filename: str, out_name: str, id_col: str = "subject",
                      keep_pattern: str | None = None,
                      drop_exact: list[str] | None = None) -> None:
    import re as _re
    df = pd.read_csv(SR / filename)
    df = df.rename(columns={id_col: "id"})
    item_cols = [c for c in df.columns if c != "id"]
    if keep_pattern:
        item_cols = [c for c in item_cols if _re.match(keep_pattern, c)]
    if drop_exact:
        item_cols = [c for c in item_cols if c not in drop_exact]
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    _write(long, out_name)


RT_IN_MS = {"antisaccade", "raven", "ls", "ns", "sart", "letter",
            "color", "orientation", "lettercomp", "digitcomp", "recognition",
            "cued_recall", "ifr"}


def _read_two(task: str, id_col: str = "subject") -> pd.DataFrame:
    parts = []
    for wave in (1, 2):
        p = COG / f"{task}_session{wave}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p, low_memory=False)
        d = d.rename(columns={id_col: "id"})
        d = d.dropna(subset=["id"]).copy()
        d["id"] = d["id"].apply(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else str(x))
        if "session" not in d.columns:
            d["session"] = wave
        d["wave"] = wave
        if task in RT_IN_MS and "rt" in d.columns:
            d["rt"] = pd.to_numeric(d["rt"], errors="coerce") / 1000.0
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


_COVARIATES: pd.DataFrame | None = None


def _get_covariates() -> pd.DataFrame:
    global _COVARIATES
    if _COVARIATES is None:
        _COVARIATES = _build_covariates()
    return _COVARIATES


def _write(df: pd.DataFrame, out_name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if "id" in df.columns:
        df = df.copy()
        df["id"] = df["id"].astype(str)
        cov = _get_covariates()
        df = df.merge(cov, on="id", how="left")
    standard = [c for c in ["id", "item", "resp", "wave", "treat", "rt", "date"] if c in df.columns]
    rest = [c for c in df.columns if c not in standard]
    df = df[standard + rest]
    path = OUT / out_name
    df.to_csv(path, index=False)
    info = f"{path.name}: rows={len(df):,}, ids={df['id'].nunique()}, items={df['item'].nunique()}"
    if "resp" in df.columns and pd.api.types.is_numeric_dtype(df["resp"]):
        info += f", resp_range=[{df['resp'].min()},{df['resp'].max()}]"
    if "wave" in df.columns:
        info += f", waves={sorted(df['wave'].dropna().unique().tolist())}"
    print(info)


def _emit_trial(df: pd.DataFrame, out_name: str, *, item_col: str, resp_col: str,
                rt_col: str | None = None, trial_extras: list[str] | None = None,
                trial_col: str | None = None,
                rename_extras: dict[str, str] | None = None) -> None:
    keep = ["id", "wave", item_col, resp_col]
    if rt_col and rt_col in df.columns:
        keep.append(rt_col)
    if trial_col and trial_col in df.columns:
        keep.append(trial_col)
    if trial_extras:
        keep.extend([c for c in trial_extras if c in df.columns])
    d = df[keep].copy()
    d = d.rename(columns={item_col: "item", resp_col: "resp"})
    if rt_col and rt_col in d.columns:
        d = d.rename(columns={rt_col: "rt"})
    if trial_col and trial_col in d.columns:
        d = d.rename(columns={trial_col: "trial_number"})
    if trial_extras:
        auto = {c: (rename_extras.get(c, f"trial_{c.lower()}") if rename_extras else f"trial_{c.lower()}")
                for c in trial_extras if c in d.columns}
        d = d.rename(columns=auto)
    d = d.dropna(subset=["id"])
    try:
        d["item"] = pd.to_numeric(d["item"]).astype("Int64").astype(str)
    except (ValueError, TypeError):
        d["item"] = d["item"].astype(str)
    d = d.dropna(subset=["item", "resp"])
    d["resp"] = pd.to_numeric(d["resp"], errors="coerce")
    d = d.dropna(subset=["resp"])
    if d["resp"].dropna().apply(lambda x: float(x).is_integer()).all():
        d["resp"] = d["resp"].astype(int)
    for c in list(d.columns):
        if c in ("id", "item", "resp", "wave", "rt"):
            continue
        vals = d[c].dropna().unique()
        if len(vals) <= 1:
            d = d.drop(columns=[c])
    sort_cols = ["id", "wave", "item"] if "wave" in d.columns else ["id", "item"]
    if "trial_number" in d.columns:
        sort_cols.append("trial_number")
    d = d.sort_values(sort_cols, kind="stable").reset_index(drop=True)
    standard = [c for c in ["id", "item", "resp", "wave", "treat", "rt", "date"] if c in d.columns]
    rest = [c for c in d.columns if c not in standard]
    d = d[standard + rest]
    _write(d, out_name)


def _melt_self_report_psqi() -> None:
    import re as _re
    df = pd.read_csv(SR / "psqi.csv").rename(columns={"subject": "id"})

    item_cols = [c for c in df.columns if _re.match(r"^psqi_q(5[a-k]|[6-9]|10)a?$", c)]
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    _write(long, "robison_2026_retesting_psqi.csv")


def build_selfreport() -> None:
    _melt_self_report("big_five_inventory.csv", "robison_2026_retesting_bfi.csv",
                      keep_pattern=r"^bfi\d+$")
    _melt_self_report("ces-d.csv", "robison_2026_retesting_cesd.csv",
                      keep_pattern=r"^cesd\d+$")
    _melt_self_report_psqi()
    _melt_self_report("state_trait_anxiety.csv", "robison_2026_retesting_stai.csv",
                      keep_pattern=r"^(calm|tense|upset|relaxed|content|worried)[12]$")
    _melt_self_report("perceptions_of_academic_stress.csv",
                      "robison_2026_retesting_pas.csv", keep_pattern=r"^pas\d+$")

def build_cognitive() -> None:
    for task in ("flanker", "stroop", "simon"):
        df = _read_two(task, id_col="subID")
        df["stimulus"] = df["stimulus"].astype(str)
        df["itemcov_conflict"] = df["stimulusConflict"].map({0: "congruent", 1: "incongruent"}).fillna("unknown")
        _emit_trial(df, f"robison_2026_retesting_{task}.csv",
                    item_col="stimulus", resp_col="correct",
                    rt_col="rt", trial_col="trial",
                    trial_extras=["itemcov_conflict"],
                    rename_extras={"itemcov_conflict": "itemcov_conflict"})

    df = _read_two("antisaccade")
    df["target_side"] = df["target_side"].astype(str).str.lower()
    _emit_trial(df, "robison_2026_retesting_antisaccade.csv",
                item_col="target_side", resp_col="acc", rt_col="rt",
                trial_col="trial")

    df = _read_two("raven")
    _emit_trial(df, "robison_2026_retesting_raven.csv",
                item_col="item", resp_col="acc", rt_col="rt")

    for task in ("ls", "ns"):
        df = _read_two(task)
        _emit_trial(df, f"robison_2026_retesting_{task}.csv",
                    item_col="item", resp_col="acc", rt_col="rt")

    df = _read_two("sart")
    _emit_trial(df, "robison_2026_retesting_sart.csv",
                item_col="trialtype", resp_col="hit", rt_col="rt",
                trial_col="trial", trial_extras=["falsealarm", "block"])

    # choicert dropped per Ben: 2-choice speeded task, accuracy at ceiling, the measure is RT.

    df = _read_two("letter")
    _emit_trial(df, "robison_2026_retesting_letter.csv",
                item_col="trialtype", resp_col="acc", rt_col="rt",
                trial_col="trial", trial_extras=["block", "setsize"])

    df = _read_two("color")
    _emit_trial(df, "robison_2026_retesting_color.csv",
                item_col="trialtype", resp_col="acc", rt_col="rt",
                trial_col="trial", trial_extras=["block"])

    df = _read_two("orientation")
    _emit_trial(df, "robison_2026_retesting_orientation.csv",
                item_col="trial_type", resp_col="acc", rt_col="rt",
                trial_col="trial", trial_extras=["block"])

    for task in ("lettercomp", "digitcomp"):
        df = _read_two(task)
        df = df[df["acc"].isin([0, 1, 0.0, 1.0])].copy()
        df["match"] = df["match"].astype(str).str.lower()
        _emit_trial(df, f"robison_2026_retesting_{task}.csv",
                    item_col="match", resp_col="acc", rt_col="rt",
                    trial_col="trial", trial_extras=["block", "target_length"])

    df = _read_two("recognition")
    df["old_new"] = df["old_new"].astype(str).str.lower()
    _emit_trial(df, "robison_2026_retesting_recognition.csv",
                item_col="old_new", resp_col="acc", rt_col="rt",
                trial_col="subtrial", trial_extras=["list", "phase"])

    df = _read_two("cued_recall")
    df = df[df["phase"].astype(str).str.lower() == "recall"].copy()
    df["resp"] = (df["response"].astype(str).str.strip().str.lower() ==
                  df["target"].astype(str).str.strip().str.lower()).astype(int)
    df["item"] = df["cue"].astype(str)
    _emit_trial(df, "robison_2026_retesting_cued_recall.csv",
                item_col="item", resp_col="resp", rt_col="rt",
                trial_extras=["list", "phase", "serial_position"])

    df = _read_two("ifr")
    if "correct" in df.columns:
        df = df.dropna(subset=["serial_position"]).copy()
        df["item"] = "position_" + df["serial_position"].astype(int).astype(str)
        _emit_trial(df, "robison_2026_retesting_ifr.csv",
                    item_col="item", resp_col="correct", rt_col="rt",
                    trial_extras=["list", "phase", "target"])

    for task in ("rspan", "ospan", "symspan"):
        df = _read_two(task)
        percol = {"rspan": "lettertotal", "ospan": "lettertotal", "symspan": "spantotal"}[task]
        df["item"] = "set_" + df["setsize"].astype(str)
        _emit_trial(df, f"robison_2026_retesting_{task}.csv",
                    item_col="item", resp_col=percol,
                    trial_extras=["list"])

    df = _read_two("paper_folding", id_col="subid")
    df = df[df["match"].isin([0, 1, 0.0, 1.0])].copy()
    _emit_trial(df, "robison_2026_retesting_paper_folding.csv",
                item_col="answer", resp_col="match", trial_col="trial",
                trial_extras=["response"])

    df = _read_two("tot", id_col="SubID")
    df["item"] = df["itemLabel"].astype(str)
    _emit_trial(df, "robison_2026_retesting_tot.csv",
                item_col="item", resp_col="Grade",
                rt_col="TimeToRespond", trial_col="TrialNum",
                trial_extras=["Difficulty"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_selfreport()
    build_cognitive()


if __name__ == "__main__":
    main()
