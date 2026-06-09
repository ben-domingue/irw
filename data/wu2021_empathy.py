from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.3389/fpsyg.2021.708342.s001"
TITLE = ("Data_Sheet_1_Relationship Between Medical Students' Empathy and "
         "Occupation Expectation: Mediating Roles of Resilience and "
         "Subjective Well-Being")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Six scales, letter-prefixed item columns. Scale identities inferred from
# the aggregate subscale names in the trailing columns:
#   B(21i) → empathy (JSE-like; 认知移情+情感移情 aggregate)
#   C(25i) → resilience (CD-RISC-25; 坚韧性+力量性+乐观性 aggregate)
#   D(16i) → academic burnout (情绪低落+行为不当+成就感低 aggregate)
#   E(5i)  → life satisfaction (SWLS; 生活满意度 aggregate)
#   F(14i) → career expectation (职业声望+自我发展+福利收入 aggregate)
#   G(20i) → affect (PANAS-like; 积极情感+消极情感 aggregate)
SCALES = {
    "empathy":            [f"B{i}"  for i in range(1, 22)],
    "resilience":         [f"C{i}"  for i in range(1, 26)],
    "burnout":            [f"D{i}"  for i in range(1, 17)],
    "swls":               [f"E{i}"  for i in range(1, 6)],
    "career_expectation": [f"F{i}"  for i in range(1, 15)],
    "panas":              [f"G{i}"  for i in range(1, 21)],
}

# Aggregate/subscale columns to drop (not item responses)
AGGREGATE_COLS = {
    "职业声望", "自我发展", "福利收入", "坚韧性", "力量性", "乐观性",
    "认知移情", "情感移情", "情绪低落", "行为不当", "成就感低",
    "生活满意度", "积极情感", "消极情感", "主观幸福感",
    "心理弹性", "移情", "学习倦怠", "职业期望",
}

COV_MAP = {
    "年级": "cov_grade",
    "性别": "cov_sex",
    "学院": "cov_college",
    "专业": "cov_major",
    "学生干部": "cov_student_leader",
    "独生子女": "cov_only_child",
    "学习成绩": "cov_academic_performance",
    "收入": "cov_family_income",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    r = requests.get("https://api.figshare.com/v2/articles/16683931",
                     headers=UA, timeout=30)
    r.raise_for_status()
    files = r.json().get("files", [])
    url = next(f["download_url"] for f in files
               if f["name"].lower().endswith(".csv"))
    r2 = requests.get(url, headers=UA, timeout=60)
    r2.raise_for_status()
    return pd.read_csv(io.BytesIO(r2.content))


def convert():
    raw = fetch_data()

    # 学号 (student id) has many missing values; use row index as id
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1
    raw = raw.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        present = [c for c in items if c in raw.columns]
        if not present:
            print(f"  WARNING: no columns for scale {scale}")
            continue

        long = raw[["id"] + cov_cols + present].melt(
            id_vars=["id"] + cov_cols,
            value_vars=present,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"wu2021_{scale}.csv"
        long.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          scale,
            "n_participants": long["id"].nunique(),
            "n_items":        long["item"].nunique(),
            "n_responses":    len(long),
            "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
            "license":        "cc-by",
            "notes":          (f"Chinese medical students N≈588; "
                               f"id=row index (学号 missing for some rows); "
                               f"scale names inferred from aggregate columns; "
                               f"resp direction unverified"),
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)
        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")

    _write_index(existing)


def _load_index():
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, newline="") as f:
        return list(csv.DictReader(f))


def _write_index(rows):
    with open(INDEX_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    convert()
