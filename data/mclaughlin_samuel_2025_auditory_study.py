#!/usr/bin/env python3

import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREPROC_DIR = os.path.join(BASE_DIR, "Analysis", "Pre-processed_data")
OUT_DIR = os.path.join(BASE_DIR, "mclaughlin_samuel_2025_auditory_study")
SESSION1_OUT = "mclaughlin_samuel_2025_auditory_session_1.csv"
SESSION2_OUT = "mclaughlin_samuel_2025_auditory_session_2.csv"


def _irw_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def _load_covariates() -> pd.DataFrame | None:
    cov_df: pd.DataFrame | None = None

    def _merge_cov(new: pd.DataFrame | None) -> None:
        nonlocal cov_df
        if new is None or new.empty:
            return
        if "subject" not in new.columns:
            return
        if cov_df is None:
            cov_df = new.copy()
        else:
            cov_df = cov_df.merge(new, on="subject", how="outer")

    hhie_path = os.path.join(PREPROC_DIR, "HHIE.csv")
    if os.path.isfile(hhie_path):
        df = pd.read_csv(hhie_path)
        df = _irw_columns(df)
        if "subject" in df.columns and "hhie_score" in df.columns:
            df = df[["subject", "hhie_score"]].copy()
            df = df.rename(columns={"hhie_score": "cov_hhie_score"})
            _merge_cov(df)

    return cov_df


def _load_session1_covariates() -> pd.DataFrame | None:
    cov_df: pd.DataFrame | None = None

    def _merge_cov(new: pd.DataFrame | None) -> None:
        nonlocal cov_df
        if new is None or new.empty:
            return
        if "subject" not in new.columns:
            return
        if cov_df is None:
            cov_df = new.copy()
        else:
            cov_df = cov_df.merge(new, on="subject", how="outer")

    age_path = os.path.join(PREPROC_DIR, "Age.csv")
    if os.path.isfile(age_path):
        df = pd.read_csv(age_path)
        df = _irw_columns(df)
        if "subject" in df.columns and "age" in df.columns:
            df = df[["subject", "age"]].copy()
            df = df.rename(columns={"age": "cov_age"})
            _merge_cov(df)

    cb_path = os.path.join(PREPROC_DIR, "Counterbalances.csv")
    if os.path.isfile(cb_path):
        df = pd.read_csv(cb_path)
        df = _irw_columns(df)
        if "subject" in df.columns and "counterbalance" in df.columns:
            df = df[["subject", "counterbalance"]].copy()
            df["counterbalance"] = (
                df["counterbalance"].astype(str).str.replace("order", "", regex=False)
            )
            df["counterbalance"] = pd.to_numeric(df["counterbalance"], errors="coerce")
            df = df.rename(columns={"counterbalance": "cov_counterbalance"})
            _merge_cov(df)

    demo_path = os.path.join(PREPROC_DIR, "Demographics.csv")
    if os.path.isfile(demo_path):
        df = pd.read_csv(demo_path)
        df = _irw_columns(df)
        if "subject" in df.columns:
            keep_cols = [c for c in df.columns if c != "subject" and "quantised" in c]
            if keep_cols:
                demo_cov = df[["subject"] + keep_cols].copy()
                demo_cov = demo_cov.rename(columns={c: "cov_" + c for c in keep_cols})
                _merge_cov(demo_cov)

    return cov_df


def _session1_task_score_long(filename: str, score_col: str, item_name: str) -> pd.DataFrame | None:
    path = os.path.join(PREPROC_DIR, filename)
    if not os.path.isfile(path):
        return None
    df = pd.read_csv(path)
    df = _irw_columns(df)
    if "subject" not in df.columns or score_col not in df.columns:
        return None
    out = df[["subject", score_col]].copy()
    out = out.rename(columns={"subject": "id", score_col: "resp"})
    out["item"] = item_name
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    return out[["id", "item", "resp"]]


def _build_session1_sb_irw() -> pd.DataFrame | None:
    part = _session1_task_score_long("SB_Session1.csv", "sb_score", "sb")
    if part is None or part.empty:
        return None
    out = part.copy()
    out["item"] = out["item"].astype(str).str.lower()

    cov_df = _load_session1_covariates()
    if cov_df is not None and not cov_df.empty:
        out = out.merge(cov_df, left_on="id", right_on="subject", how="left")
        if "subject" in out.columns:
            out = out.drop(columns=["subject"])
        empty_covs = []
        for c in out.columns:
            if not c.startswith("cov_"):
                continue
            col = out[c]
            if not col.notna().any():
                empty_covs.append(c)
            elif col.dropna().astype(str).str.strip().eq("").all():
                empty_covs.append(c)
        if empty_covs:
            out = out.drop(columns=empty_covs)

    core = [c for c in ["id", "item", "resp"] if c in out.columns]
    cov_cols = sorted([c for c in out.columns if c.startswith("cov_")])
    other = [c for c in out.columns if c not in core + cov_cols]
    out = out[core + other + cov_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, SESSION1_OUT)
    out.to_csv(out_path, index=False)
    print(f"{SESSION1_OUT}: rows={len(out)}, ids={out['id'].nunique()}, items={out['item'].nunique()}")
    return out


def _sb_item_long() -> pd.DataFrame | None:
    sb_path = os.path.join(PREPROC_DIR, "SB_Session2.csv")
    if not os.path.isfile(sb_path):
        return None
    df = pd.read_csv(sb_path)
    df = _irw_columns(df)
    if "subject" not in df.columns or "sb_score" not in df.columns:
        return None
    out = df[["subject", "sb_score"]].copy()
    out = out.rename(columns={"subject": "id", "sb_score": "resp"})
    out["item"] = "sb"
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    out = out[["id", "item", "resp"]]
    return out


def _mandarin_items_long() -> pd.DataFrame | None:
    mc_path = os.path.join(PREPROC_DIR, "MandarinChinese_Familiarity.csv")
    if not os.path.isfile(mc_path):
        return None
    df = pd.read_csv(mc_path)
    df = _irw_columns(df)
    if "subject" not in df.columns:
        return None
    lang_col = "familiarity_mc_language" if "familiarity_mc_language" in df.columns else None
    acc_col = "familiarity_mc_accent" if "familiarity_mc_accent" in df.columns else None
    if not lang_col and not acc_col:
        return None
    rows = []
    for _, r in df.iterrows():
        sid = r["subject"]
        if lang_col and pd.notna(r.get(lang_col)):
            rows.append({"id": sid, "item": "familiarity_mc_language", "resp": pd.to_numeric(r[lang_col], errors="coerce")})
        if acc_col and pd.notna(r.get(acc_col)):
            rows.append({"id": sid, "item": "familiarity_mc_accent", "resp": pd.to_numeric(r[acc_col], errors="coerce")})
    if not rows:
        return None
    out = pd.DataFrame(rows).dropna(subset=["resp"])
    out["item"] = out["item"].astype(str).str.lower()
    return out


def _load_summary_covariates() -> pd.DataFrame | None:
    cov_df: pd.DataFrame | None = None

    def _merge_cov(new: pd.DataFrame | None) -> None:
        nonlocal cov_df
        if new is None or new.empty:
            return
        if "subject" not in new.columns:
            return
        if cov_df is None:
            cov_df = new.copy()
        else:
            cov_df = cov_df.merge(new, on="subject", how="outer")

    age_path = os.path.join(PREPROC_DIR, "Age.csv")
    if os.path.isfile(age_path):
        df = pd.read_csv(age_path)
        df = _irw_columns(df)
        if "subject" in df.columns and "age" in df.columns:
            df = df[["subject", "age"]].copy()
            df = df.rename(columns={"age": "cov_age"})
            _merge_cov(df)

    cb_path = os.path.join(PREPROC_DIR, "Counterbalances.csv")
    if os.path.isfile(cb_path):
        df = pd.read_csv(cb_path)
        df = _irw_columns(df)
        if "subject" in df.columns and "counterbalance" in df.columns:
            df = df[["subject", "counterbalance"]].copy()
            df["counterbalance"] = (
                df["counterbalance"]
                .astype(str)
                .str.replace("order", "", regex=False)
            )
            df["counterbalance"] = pd.to_numeric(df["counterbalance"], errors="coerce")
            df = df.rename(columns={"counterbalance": "cov_counterbalance"})
            _merge_cov(df)

    demo_path = os.path.join(PREPROC_DIR, "Demographics.csv")
    if os.path.isfile(demo_path):
        df = pd.read_csv(demo_path)
        df = _irw_columns(df)
        if "subject" in df.columns:
            keep_cols: list[str] = []
            for c in df.columns:
                if c == "subject":
                    continue
                if "quantised" in c:
                    keep_cols.append(c)
            if keep_cols:
                demo_cov = df[["subject"] + keep_cols].copy()
                demo_cov = demo_cov.rename(columns={c: "cov_" + c for c in keep_cols})
                _merge_cov(demo_cov)

    return cov_df


def _build_summary_irw() -> pd.DataFrame | None:
    frames: list[pd.DataFrame] = []

    def _add_wide_score(filename: str, value_col: str, item_name: str) -> None:
        path = os.path.join(PREPROC_DIR, filename)
        if not os.path.isfile(path):
            return
        df = pd.read_csv(path)
        df = _irw_columns(df)
        if "subject" not in df.columns or value_col not in df.columns:
            return
        tmp = pd.DataFrame(
            {
                "id": df["subject"],
                "item": item_name,
                "resp": pd.to_numeric(df[value_col], errors="coerce"),
            }
        )
        tmp = tmp.dropna(subset=["resp"])
        frames.append(tmp)

    _add_wide_score("HHIE.csv", "hhie_score", "hhie_score")
    _add_wide_score("Extraversion.csv", "extraversion_composite", "extraversion")

    _add_wide_score("DSA.csv", "dsa_score", "dsa_score")
    _add_wide_score("DSV.csv", "dsv_score", "dsv_score")
    _add_wide_score("FRA.csv", "fra_score", "fra_score")
    _add_wide_score("FRV.csv", "frv_score", "frv_score")
    _add_wide_score("SB_Session1.csv", "sb_score", "sb")

    amf_path = os.path.join(PREPROC_DIR, "Affect_Motivation_Fatigue.csv")
    if os.path.isfile(amf_path):
        df = pd.read_csv(amf_path)
        df = _irw_columns(df)
        needed = {"subject", "task_followed", "composite_affect", "composite_motivation", "composite_fatigue"}
        if needed.issubset(df.columns):
            long = df.melt(
                id_vars=["subject", "task_followed"],
                value_vars=["composite_affect", "composite_motivation", "composite_fatigue"],
                var_name="scale",
                value_name="resp",
            )
            long = long.dropna(subset=["resp"])
            long["item"] = (
                "composite_"
                + long["scale"].str.replace("composite_", "", regex=False)
                + "_"
                + long["task_followed"].astype(str).str.lower()
            )
            tmp = pd.DataFrame(
                {
                    "id": long["subject"],
                    "item": long["item"],
                    "resp": pd.to_numeric(long["resp"], errors="coerce"),
                }
            ).dropna(subset=["resp"])
            frames.append(tmp)

    if not frames:
        return None

    all_long = pd.concat(frames, ignore_index=True)
    all_long["item"] = all_long["item"].astype(str).str.lower()

    task_items = {"dsa_score", "dsv_score", "fra_score", "frv_score", "sb"}
    ids_with_task = set(all_long.loc[all_long["item"].isin(task_items), "id"].unique())
    if ids_with_task:
        all_long = all_long[all_long["id"].isin(ids_with_task)].copy()

    cov_df = _load_summary_covariates()
    if cov_df is not None and not cov_df.empty:
        merged = all_long.merge(cov_df, left_on="id", right_on="subject", how="left")
        if "subject" in merged.columns:
            merged = merged.drop(columns=["subject"])
        all_long = merged

    empty_covs: list[str] = []
    for c in all_long.columns:
        if not c.startswith("cov_"):
            continue
        col = all_long[c]
        if not col.notna().any():
            empty_covs.append(c)
            continue
        if col.dropna().astype(str).str.strip().eq("").all():
            empty_covs.append(c)
    if empty_covs:
        all_long = all_long.drop(columns=empty_covs)

    core = ["id", "item", "resp"]
    cov_cols = [c for c in all_long.columns if c.startswith("cov_")]
    other = [c for c in all_long.columns if c not in core + cov_cols]
    ordered = core + other + sorted(cov_cols)
    all_long = all_long[ordered]

    out_path = os.path.join(BASE_DIR, "lettuce_summary_irw.csv")
    all_long.to_csv(out_path, index=False)
    print(f"lettuce_summary_irw.csv: rows={len(all_long)}, ids={all_long['id'].nunique()}, items={all_long['item'].nunique()}")
    return all_long


def _convert_transcription_long(
    filename: str,
    task_label: str,
    audio_col: str = "audio",
    trial_col: str | None = "trial",
    talker_col: str | None = None,
) -> pd.DataFrame | None:
    in_path = os.path.join(PREPROC_DIR, filename)
    if not os.path.isfile(in_path):
        print(f"Skipping {filename}: file not found.")
        return None

    df = pd.read_csv(in_path)
    if df.empty:
        print(f"Skipping {filename}: file is empty.")
        return None

    df = _irw_columns(df)

    if "subject" not in df.columns:
        print(f"Skipping {filename}: no 'Subject' column.")
        return None

    id_col = "subject"
    for req in [audio_col, "correct", "incorrect"]:
        if req.lower() not in df.columns:
            print(f"Skipping {filename}: expected column '{req}'.")
            return None

    item_series = df[audio_col.lower()].astype(str)
    df["item"] = (task_label + "_" + item_series).str.lower()
    df["id"] = df[id_col]

    trial_cols: list[str] = []
    if trial_col is not None and trial_col.lower() in df.columns:
        tcol = trial_col.lower()
        df["trial_index"] = df[tcol]
        trial_cols.append("trial_index")

    itemcov_cols: list[str] = ["itemcov_response_type"]
    extra_itemcov: list[str] = []
    if talker_col is not None and talker_col.lower() in df.columns:
        icol = talker_col.lower()
        df["itemcov_talker"] = df[icol]
        itemcov_cols.append("itemcov_talker")
        extra_itemcov = ["itemcov_talker"]

    base_cols = ["id", "item"] + trial_cols + extra_itemcov
    correct_df = df[base_cols + ["correct"]].copy()
    correct_df = correct_df.rename(columns={"correct": "resp"})
    correct_df["resp"] = pd.to_numeric(correct_df["resp"], errors="coerce")
    correct_df["itemcov_response_type"] = "correct"
    correct_df = correct_df.dropna(subset=["resp"])
    correct_df = correct_df[["id", "item", "resp"] + trial_cols + itemcov_cols]

    incorrect_df = df[base_cols + ["incorrect"]].copy()
    incorrect_df = incorrect_df.rename(columns={"incorrect": "resp"})
    incorrect_df["resp"] = pd.to_numeric(incorrect_df["resp"], errors="coerce")
    incorrect_df["itemcov_response_type"] = "incorrect"
    incorrect_df = incorrect_df.dropna(subset=["resp"])
    incorrect_df = incorrect_df[["id", "item", "resp"] + trial_cols + itemcov_cols]

    out = pd.concat([correct_df, incorrect_df], ignore_index=True)
    out = _irw_columns(out)

    out_name = f"{task_label.lower()}_irw.csv"
    out_path = os.path.join(BASE_DIR, out_name)
    out.to_csv(out_path, index=False)
    print(
        f"{out_name}: rows={len(out)}, ids={out['id'].nunique()}, items={out['item'].nunique()}"
    )
    return out


def convert_lettuce_entertain_to_irw():
    out_files: list[pd.DataFrame] = []

    out_accent = _convert_transcription_long(
        filename="Accent_Transcription_Long.csv",
        task_label="accent",
        audio_col="Audio",
        trial_col="Trial",
        talker_col="Talker",
    )
    if out_accent is not None:
        out_files.append(out_accent)

    out_noise = _convert_transcription_long(
        filename="Noise_Transcription_Long.csv",
        task_label="noise",
        audio_col="Audio",
        trial_col="Trial",
        talker_col=None,
    )
    if out_noise is not None:
        out_files.append(out_noise)

    cov_df = _load_covariates()
    mandarin_df = _mandarin_items_long()
    sb_df = _sb_item_long()
    extra_item_dfs = [d for d in (mandarin_df, sb_df) if d is not None and not d.empty]
    merged_accent: pd.DataFrame | None = None
    merged_noise: pd.DataFrame | None = None
    if cov_df is not None and not cov_df.empty:
        for df in out_files:
            if "id" not in df.columns:
                continue
            merged = df.merge(cov_df, left_on="id", right_on="subject", how="left")
            if "subject" in merged.columns:
                merged = merged.drop(columns=["subject"])

            empty_covs = []
            for c in merged.columns:
                if not c.startswith("cov_"):
                    continue
                col = merged[c]
                if not col.notna().any():
                    empty_covs.append(c)
                    continue
                if col.dropna().astype(str).str.strip().eq("").all():
                    empty_covs.append(c)
            if empty_covs:
                merged = merged.drop(columns=empty_covs)

            if extra_item_dfs:
                ids_here = set(merged["id"].unique())
                for extra_df in extra_item_dfs:
                    extra = extra_df[extra_df["id"].isin(ids_here)].copy()
                    if not extra.empty and cov_df is not None:
                        extra = extra.merge(cov_df, left_on="id", right_on="subject", how="left")
                        if "subject" in extra.columns:
                            extra = extra.drop(columns=["subject"])
                        for c in merged.columns:
                            if c not in extra.columns:
                                extra[c] = pd.NA
                        extra = extra[merged.columns]
                        merged = pd.concat([merged, extra], ignore_index=True)

            core = [c for c in ["id", "item", "resp"] if c in merged.columns]
            trial_cols = [c for c in merged.columns if c.startswith("trial_")]
            itemcov_cols = [c for c in merged.columns if c.startswith("itemcov_")]
            cov_cols = [c for c in merged.columns if c.startswith("cov_")]
            other = [c for c in merged.columns if c not in core + trial_cols + itemcov_cols + cov_cols]
            ordered = core + trial_cols + itemcov_cols + other + sorted(cov_cols)
            merged = merged[ordered]

            out_name = None
            if (df["item"].astype(str).str.startswith("accent_")).any():
                out_name = "accent_irw.csv"
                merged_accent = merged
            elif (df["item"].astype(str).str.startswith("noise_")).any():
                out_name = "noise_irw.csv"
                merged_noise = merged
            if out_name is not None:
                out_path = os.path.join(BASE_DIR, out_name)
                merged.to_csv(out_path, index=False)

    session2_parts: list[pd.DataFrame] = []
    if merged_accent is not None or merged_noise is not None:
        if merged_accent is not None:
            ia = merged_accent["item"].astype(str)
            session2_parts.append(merged_accent[ia.str.startswith("accent_")])
            extras = merged_accent[~ia.str.startswith("accent_")]
            if not extras.empty:
                session2_parts.append(extras.drop_duplicates(subset=["id", "item"], keep="first"))
        if merged_noise is not None:
            session2_parts.append(
                merged_noise[merged_noise["item"].astype(str).str.startswith("noise_")]
            )
        if session2_parts:
            all_trials = pd.concat(session2_parts, ignore_index=True)
            os.makedirs(OUT_DIR, exist_ok=True)
            session2_path = os.path.join(OUT_DIR, SESSION2_OUT)
            all_trials.to_csv(session2_path, index=False)
            print(
                f"{SESSION2_OUT}: rows={len(all_trials)}, ids={all_trials['id'].nunique()}, items={all_trials['item'].nunique()}"
            )
    else:
        combined_frames: list[pd.DataFrame] = []
        for fname in ("accent_irw.csv", "noise_irw.csv"):
            path = os.path.join(BASE_DIR, fname)
            if os.path.isfile(path):
                combined_frames.append(pd.read_csv(path))
        if combined_frames:
            all_trials = pd.concat(combined_frames, ignore_index=True)
            os.makedirs(OUT_DIR, exist_ok=True)
            session2_path = os.path.join(OUT_DIR, SESSION2_OUT)
            all_trials.to_csv(session2_path, index=False)
            print(
                f"{SESSION2_OUT}: rows={len(all_trials)}, ids={all_trials['id'].nunique()}, items={all_trials['item'].nunique()}"
            )

    _build_session1_sb_irw()

    if not out_files:
        print("No IRW datasets were produced from lettuce_entertain.")
    return out_files


if __name__ == "__main__":
    convert_lettuce_entertain_to_irw()

