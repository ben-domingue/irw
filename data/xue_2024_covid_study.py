#!/usr/bin/env python3

import os
import re
import pandas as pd

COVID_DATA_DIR = "xue_2024_covid_study"
COVID_EXCEL = "Full-dataset and coding.xlsx"
COVID_SAV_EFA = "STUDY 2 (EFA).sav"
COVID_SAV_CFA = "Study 3 (CFA).sav"
OUT_FULL = "xue_2024_full_dataset.csv"
OUT_EFA = "xue_2024_study2_efa.csv"
OUT_CFA = "xue_2024_study3_cfa.csv"


def _irw_columns(df):
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))

SPSS_TEXT_LABEL_MAP = {
    "not at all concerned": 1,
    "extremely concerned": 7,
    "not at all": 1,
    "extremely": 7,
    "extremely agree": 7,
    "extremely disagree": 1,
    "not at all like me": 1,
    "very much like me": 7,
    "somewhat like me": 4,
    "like me": 5,
    "a little like me": 3,
    "not like me": 2,
}


def _spss_label_to_numeric(ser, text_map=None):
    if text_map is None:
        text_map = {}
    text_map_lower = {k.strip().lower(): v for k, v in text_map.items()}

    def one_val(x):
        if pd.isna(x):
            return None
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            return float(x) if not pd.isna(x) else None
        s = str(x).strip()
        m = re.match(r"^(\d+)", s)
        if m:
            return float(m.group(1))
        key = s.lower()
        return text_map_lower.get(key)
    return ser.map(one_val)


def convert_wide_to_irw(df, id_col, cov_cols, item_cols):
    df = df.copy()
    df = _irw_columns(df)
    id_vars = [id_col] + [c for c in cov_cols if c in df.columns]
    value_vars = [c for c in item_cols if c in df.columns]
    if not value_vars:
        return pd.DataFrame()
    out = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name="item", value_name="resp")
    out = out.rename(columns={id_col: "id"})
    rename = {c: "cov_" + c for c in cov_cols if c in out.columns and c != "id"}
    out = out.rename(columns=rename)
    out["item"] = out["item"].astype(str).str.lower().str.replace(" ", "_")
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"])
    out = out[~out["item"].str.startswith("tot_")]
    covs = [c for c in out.columns if c.startswith("cov_")]
    out = out[["id", "item", "resp"] + covs]
    return _irw_columns(out)


def convert_excel_to_irw(read_dir, write_dir, full_resp_0_4=False):
    xlsx_path = os.path.join(read_dir, COVID_EXCEL)
    if not os.path.isfile(xlsx_path):
        return None
    df = pd.read_excel(xlsx_path, sheet_name=0)
    df = _irw_columns(df)
    drop = [c for c in df.columns if str(c).lower().startswith("unnamed") or str(c).strip() == ""]
    df = df.drop(columns=drop, errors="ignore")
    id_col = "part_no" if "part_no" in df.columns else df.columns[0]
    excel_covs = ["age", "gender", "sex", "wave", "country", "education", "country_born", "country_live",
                  "employment_status", "field", "keep_job", "workplace", "financial_concern", "social_distancing"]
    cov_candidates = [c for c in excel_covs if c in df.columns]
    item_cols = [c for c in df.columns if c != id_col and c not in cov_candidates
                 and not str(c).lower().startswith("tot_") and not str(c).lower().startswith("ratio_")]
    for c in item_cols:
        if c in df.columns:
            df[c] = _spss_label_to_numeric(df[c], text_map=SPSS_TEXT_LABEL_MAP)
    out = convert_wide_to_irw(df, id_col, cov_candidates, item_cols)
    if out.empty:
        return None
    if full_resp_0_4:
        n_before = len(out)
        out = out[(out["resp"] >= 0) & (out["resp"] <= 4)]
        if len(out) < n_before:
            print("  %s: dropped %d rows with resp outside 0-4 (scale is 1-7; not recommended)" % (OUT_FULL, n_before - len(out)))
    out_path = os.path.join(write_dir, OUT_FULL)
    out.to_csv(out_path, index=False)
    print("  %s: rows=%d" % (OUT_FULL, len(out)))
    return out


def _sav_covs_study2():
    return ["gender", "age", "country_birth", "country_residence", "employment_status", "employment_field",
            "emplyoment_jobloss", "employment_wfh", "covid_financial_impact", "covid_social_distancing"]


def _sav_drop_study2():
    return ["progress", "duration__in_seconds_", "finished", "consent", "include", "q9_7_text", "q11_3_text",
            "total", "filter_$", "health", "existential", "relational", "lifestyle", "supply", "financial",
            "social_fabric", "vulnerable_groups", "healthcare_system", "political", "wellbeing", "social",
            "material", "societal", "structural"]


def convert_study2_efa_to_irw(read_dir, write_dir):
    path = os.path.join(read_dir, COVID_SAV_EFA)
    if not os.path.isfile(path):
        return None
    try:
        df = pd.read_spss(path)
    except Exception:
        return None
    df = _irw_columns(df)
    drop = [c for c in df.columns if any(c.startswith(p) for p in ["z", "stdz", "filter_"])]
    drop += [c for c in _sav_drop_study2() if c in df.columns]
    df = df.drop(columns=drop, errors="ignore")
    id_col = "id"
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)
    cov_candidates = [c for c in _sav_covs_study2() if c in df.columns]
    item_cols = [c for c in df.columns if c not in ["id"] + cov_candidates]
    for c in item_cols:
        if c in df.columns:
            df[c] = _spss_label_to_numeric(df[c])
    out = convert_wide_to_irw(df, id_col, cov_candidates, item_cols)
    if out.empty:
        return None
    out = out[(out["resp"] >= 1) & (out["resp"] <= 7)]
    out_path = os.path.join(write_dir, OUT_EFA)
    out.to_csv(out_path, index=False)
    print("  %s: rows=%d" % (OUT_EFA, len(out)))
    return out


def _sav_covs_study3():
    return ["gender", "age", "country", "emp_status", "emp_filed", "keep_job", "work_env", "covid_infected",
            "finance_threat", "sd_practice", "covid_stress", "pcvd_ses", "pol_or", "gender_2", "data_type", "cfa_rep"]


def convert_study3_cfa_to_irw(read_dir, write_dir):
    path = os.path.join(read_dir, COVID_SAV_CFA)
    if not os.path.isfile(path):
        return None
    try:
        df = pd.read_spss(path)
    except Exception:
        return None
    df = _irw_columns(df)
    id_col = "part_no" if "part_no" in df.columns else "id"
    if id_col not in df.columns:
        df["id"] = range(1, len(df) + 1)
        id_col = "id"
    cov_candidates = [c for c in _sav_covs_study3() if c in df.columns]
    item_cols = [c for c in df.columns if c != id_col and c not in cov_candidates]
    for c in item_cols:
        if c in df.columns:
            df[c] = _spss_label_to_numeric(df[c], text_map=SPSS_TEXT_LABEL_MAP)
    out = convert_wide_to_irw(df, id_col, cov_candidates, item_cols)
    if out.empty:
        return None
    out = out[(out["resp"] >= 1) & (out["resp"] <= 7)]
    out_path = os.path.join(write_dir, OUT_CFA)
    out.to_csv(out_path, index=False)
    print("  %s: rows=%d" % (OUT_CFA, len(out)))
    return out


def sav_to_csv(read_dir, write_dir):
    for sav_name, csv_name in [
        (COVID_SAV_EFA, "STUDY_2_EFA_original.csv"),
        (COVID_SAV_CFA, "Study_3_CFA_original.csv"),
    ]:
        path = os.path.join(read_dir, sav_name)
        if not os.path.isfile(path):
            continue
        try:
            df = pd.read_spss(path)
        except Exception:
            continue
        df = _irw_columns(df)
        out_path = os.path.join(write_dir, csv_name)
        df.to_csv(out_path, index=False)
        print("  %s (wide, original): %d rows, %d cols" % (csv_name, len(df), len(df.columns)))


def convert_covid_to_irw(full_resp_0_4=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    study_dir = os.path.join(script_dir, COVID_DATA_DIR)
    if os.path.isdir(study_dir):
        read_dir = script_dir
        write_dir = study_dir
    else:
        read_dir = script_dir
        write_dir = script_dir
    out_files = []

    sav_to_csv(read_dir, write_dir)

    try:
        excel_out = convert_excel_to_irw(read_dir, write_dir, full_resp_0_4=full_resp_0_4)
        if excel_out is not None:
            out_files.append(excel_out)
    except Exception as e:
        print("  %s: skipped (%s)" % (OUT_FULL, e))

    study2_out = convert_study2_efa_to_irw(read_dir, write_dir)
    if study2_out is not None:
        out_files.append(study2_out)

    study3_out = convert_study3_cfa_to_irw(read_dir, write_dir)
    if study3_out is not None:
        out_files.append(study3_out)

    data_dir = os.path.join(script_dir, "Data")
    if os.path.isdir(data_dir):
        csvs = sorted([f for f in os.listdir(data_dir) if f.endswith(".csv")])
        for i, fname in enumerate(csvs):
            path = os.path.join(data_dir, fname)
            df = pd.read_csv(path)
            df = _irw_columns(df)
            cols = list(df.columns)
            id_col = "id" if "id" in cols else (cols[0] if cols else None)
            if id_col is None:
                df["id"] = range(1, len(df) + 1)
                id_col = "id"
            cov_candidates = [c for c in ["age", "gender", "sex", "wave", "country", "education"] if c in cols]
            item_cols = [c for c in cols if c != id_col and c not in cov_candidates]
            out = convert_wide_to_irw(df, id_col, cov_candidates, item_cols)
            if out.empty:
                continue
            base_name = os.path.splitext(fname)[0]
            out_name = base_name + "_irw.csv"
            out_path = os.path.join(write_dir, out_name)
            out.to_csv(out_path, index=False)
            print("  %s: rows=%d" % (out_name, len(out)))
            out_files.append(out)

    if not out_files:
        print("No COVID data found. Place CSV(s) in covid/Data/ or Full-dataset and coding.xlsx in covid/.")
    return out_files


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Convert COVID/Xue 2024 data to IRW")
    p.add_argument("--full-resp-0-4", action="store_true",
                   help="(Deprecated) Scale is 1-7; only use if you need to restrict to 0-4 for legacy reasons")
    args = p.parse_args()
    convert_covid_to_irw(full_resp_0_4=args.full_resp_0_4)
