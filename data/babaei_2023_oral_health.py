from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0284366
# DOI: 10.1371/journal.pone.0284366
# Babaei et al. (2023). One-year oral health outcome of a community-based
# trial in schoolchildren aged 6-7 years old in Tehran, Iran. PLOS ONE.
# Data: S1 File (SAV), https://doi.org/10.1371/journal.pone.0284366.s002
# (s001 is the CONSORT PDF checklist, not data.)
#
# Raw SAV has 739 children x 3 waves (baseline, one-year follow-up "_p",
# and a further follow-up "_p2"). Three raw item groups are shipped:
#   QB  - child brushing/hygiene behavior (3 items, 1-5 Likert + "do not
#         know"=6 sentinel, filtered out)
#   QC  - mother's reported hygiene behavior for the child (3 items, same
#         1-5 scale + 6=sentinel)
#   QD  - caries/gum-disease knowledge & attitude, agree/disagree (16
#         items, 1-4 scale + 5="do not know" sentinel, filtered out; a
#         single stray non-integer value (2.0046...) on QD13 baseline is
#         a data-entry glitch, also dropped)
# Excluded: DI/CI/OHIS (clinical dental-exam indices, not survey items),
# QD*.A0 / *_A_p1 / *_A_p2 (reverse-coded companion/recode columns), and
# demographic/SES columns (used as cov_* instead).
# No PII: `IC` = intervention/control group (not identity-card), `id` is a
# sequential study code.

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SAV_URL = "https://doi.org/10.1371/journal.pone.0284366.s002"

COV_COLS = {
    "District": "cov_district",
    "Gender": "cov_gender",
    "IC": "cov_group",  # 1=control, 2=intervention
}

# (wave label, wave number, suffix used on column names for that wave)
WAVES = [("baseline", 1, ""), ("followup1", 2, "_p"), ("followup2", 3, "_p2")]

QB_BASE = ["QB1.brush_lastmonth_child", "QB2.toothpaste_lastmonth_child", "QB3.betweenmeal_child"]
QC_BASE = ["QC10.brush_lastmonth_mother", "QC11.toothpaste_lastmonth_mother", "QC12.betweenmeal_mother"]
QD_BASE = [
    "QD13.caries_gum_otherbody", "QD14.caries_gum_important", "QD15.caries_gum_less_otherdiseases",
    "QD16.natural_losingteeth", "QD17.milkteeth_notimportant", "QD18.hereditary_caries",
    "QD19.plaque_caries", "QD20.plaque_gum", "QD21.sweet_caries", "QD22.notprevent_caries",
    "QD23.brush_nottoothpaste", "QD24.fluoride_usefull", "QD25.salt_mouthwash",
    "QD26.lesssugar_preventcaries", "QD27.brush_prevent_gum", "QD28.school.goodplace",
]


def fetch_data() -> pd.DataFrame:
    import pyreadstat

    r = requests.get(SAV_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = OUT_DIR.parent / "_tmp_babaei2023.sav"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(r.content)
    df, _ = pyreadstat.read_sav(str(tmp))
    tmp.unlink(missing_ok=True)
    return df


def find_wave_col(df: pd.DataFrame, base: str, suffix: str) -> str | None:
    """Column names shift case/prefix (QD<->DQ) across waves; match by digits+stem."""
    if suffix == "":
        return base if base in df.columns else None
    target = base + suffix
    if target in df.columns:
        return target
    # try QD<->DQ swap and minor stem variants for the _p/_p2 waves
    stem_num = base.split(".")[0]  # e.g. "QD17"
    num = "".join(ch for ch in stem_num if ch.isdigit())
    for c in df.columns:
        cnum = "".join(ch for ch in c.split(".")[0].split("_")[0] if ch.isdigit())
        if cnum == num and c.endswith(suffix) and (c.upper().startswith("QD") or c.upper().startswith("DQ")):
            return c
    return None


def build_scale(df: pd.DataFrame, base_items: list[str], cov_cols: list[str],
                 lo: int, hi: int, sentinel: int) -> pd.DataFrame:
    frames = []
    for wave_label, wave_num, suffix in WAVES:
        cols_map = {}
        for base in base_items:
            col = find_wave_col(df, base, suffix)
            if col is not None and col in df.columns:
                item_name = base.split(".", 1)[0]  # e.g. QD13
                cols_map[col] = item_name
        if not cols_map:
            continue
        sub = df[["id"] + cov_cols + list(cols_map.keys())].rename(columns=cols_map)
        sub["wave"] = wave_num
        item_names = list(cols_map.values())
        long = sub.melt(
            id_vars=["id", "wave"] + cov_cols,
            value_vars=item_names,
            var_name="item",
            value_name="resp",
        )
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # drop sentinel ("do not know") and any stray non-integer glitch values
    long = long[long["resp"] != sentinel]
    long = long[(long["resp"] % 1 == 0)]
    long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp", "wave"] + cov_cols
    return long[col_order].sort_values(["id", "item", "wave"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns=COV_COLS)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    cov_cols = [c for c in COV_COLS.values() if c in df.columns]

    scales = [
        (QB_BASE, "babaei_2023_child_hygiene_behavior.csv", 1, 5, 6),
        (QC_BASE, "babaei_2023_mother_hygiene_behavior.csv", 1, 5, 6),
        (QD_BASE, "babaei_2023_oral_kap.csv", 1, 4, 5),
    ]
    for base_items, fname, lo, hi, sentinel in scales:
        long = build_scale(df, base_items, cov_cols, lo, hi, sentinel)
        write_scale(long, fname)


if __name__ == "__main__":
    convert()
