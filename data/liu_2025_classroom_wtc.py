from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0328226
# DOI: 10.1371/journal.pone.0328226
# EFL classroom study, N=623, 5-point Likert (1-5), no missing values. Four
# validated instruments administered in one questionnaire block (per the
# paper's Measures section 2.2.1-2.2.4, each with its own reported
# Cronbach's alpha) -- shipped as four separate scale files matching that
# reporting granularity, with item names encoding the paper's own named
# sub-dimensions within each scale:
#   - Classroom Interaction Scale (Wu & Gao, adapted): learner-instructor
#     (ci_li_1-7) + learner-learner (ci_ll_1-4) dimensions, alpha=.889
#   - Willingness to Communicate in English Scale (Peng & Woodrow): wtc_1-10,
#     alpha=.921
#   - Speaking Self-Efficacy Scale (Wang & Sun): linguistic (sse_ling_1-5),
#     self-regulatory (sse_selfreg_1-3), delivery (sse_deliv_1-2),
#     performance (sse_perf_1-4), alpha=.939
#   - Foreign Language Enjoyment Scale short form (Botes et al.): personal
#     (fle_personal_1-3), teacher (fle_teacher_1-3), social (fle_social_1-3)
#     sub-scales -- grouped by actual item content, since the raw column
#     order does not match the order the paper's prose happens to list the
#     three FLE sub-scales in. alpha=.898
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0328226.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Gender": "cov_gender",
    "Grade ": "cov_grade",
    "Academic Disciplines": "cov_academic_discipline",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Number": "id", **COV_MAP})
    return df


def _write(df: pd.DataFrame, cov_cols: list[str], mapping: dict[str, str], out_name: str):
    item_cols = list(mapping.keys())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].map(mapping)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_MAP.values())
    cols = list(df.columns)
    item_cols_all = cols[len(["id"] + cov_cols):]
    assert len(item_cols_all) == 44, f"expected 44 item columns, got {len(item_cols_all)}"

    ci_li = item_cols_all[0:7]
    ci_ll = item_cols_all[7:11]
    wtc = item_cols_all[11:21]
    sse_ling = item_cols_all[21:26]
    sse_selfreg = item_cols_all[26:29]
    sse_deliv = item_cols_all[29:31]
    sse_perf = item_cols_all[31:35]
    fle_personal = item_cols_all[35:38]
    fle_teacher = item_cols_all[38:41]
    fle_social = item_cols_all[41:44]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ci_map = {c: f"ci_li_{i+1}" for i, c in enumerate(ci_li)}
    ci_map.update({c: f"ci_ll_{i+1}" for i, c in enumerate(ci_ll)})
    _write(df, cov_cols, ci_map, "liu_2025_classroom_interaction")

    wtc_map = {c: f"wtc_{i+1}" for i, c in enumerate(wtc)}
    _write(df, cov_cols, wtc_map, "liu_2025_willingness_communicate")

    sse_map = {c: f"sse_ling_{i+1}" for i, c in enumerate(sse_ling)}
    sse_map.update({c: f"sse_selfreg_{i+1}" for i, c in enumerate(sse_selfreg)})
    sse_map.update({c: f"sse_deliv_{i+1}" for i, c in enumerate(sse_deliv)})
    sse_map.update({c: f"sse_perf_{i+1}" for i, c in enumerate(sse_perf)})
    _write(df, cov_cols, sse_map, "liu_2025_speaking_selfefficacy")

    fle_map = {c: f"fle_personal_{i+1}" for i, c in enumerate(fle_personal)}
    fle_map.update({c: f"fle_teacher_{i+1}" for i, c in enumerate(fle_teacher)})
    fle_map.update({c: f"fle_social_{i+1}" for i, c in enumerate(fle_social)})
    _write(df, cov_cols, fle_map, "liu_2025_foreign_lang_enjoyment")


if __name__ == "__main__":
    convert()
