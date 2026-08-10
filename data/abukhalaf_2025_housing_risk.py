from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0310665
# DOI: 10.1371/journal.pone.0310665
# Abukhalaf et al. (2025), "Exploring the relationship between housing
# conditions and risk perception in a disaster context". S1 Table (sheet
# "Total (Numbers)"). CC BY 4.0. N=816. Paper's own Methods text (Sec 3.3)
# confirms: "Each behavioral construct was measured through a set of
# questions in a Likert or Rising scales format. The answers were
# translated into percentages ... All behavioral constructs are
# metric/continuous data ranging from 0.0 to 1.0." The raw item values are
# genuinely continuous (not a clean 5-level Likert -- several respondents
# have decimal values between the nominal 0/.25/.5/.75/1 anchors from the
# "Rising scale" slider format), so resp is shipped as continuous 0-1
# rather than remapped to a discrete 1-5 code. Two separate constructs
# (risk perception vs. preparedness intention) shipped as two tables.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0310665.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Matched by distinctive prefix rather than full text -- the source file's
# ellipsis characters decode inconsistently across environments.
RISK_PREFIXES = {
    "Risk1 - 1.": "risk1_possibility",
    "Risk1 - 2.": "risk1_severity",
    "Risk1 - 3.": "risk1_wind_damage",
    "Risk1 - 4.": "risk1_flood",
    "the following is: - 1. Roof": "sev_roof",
    "the following is: - 2. Interior": "sev_interior",
    "the following is: - 3. Exterior glass": "sev_glass",
    "the following is: - 4. Exterior walls": "sev_walls",
    "the following is: - 5. Foundations": "sev_foundation",
    "Risk3 - 1.": "risk3_fire",
    "Risk3 - 2.": "risk3_outage",
    "Risk3 - 3.": "risk3_harm_severity",
    "Risk3 - 4.": "risk3_harm_possibility",
}

PREP_PREFIXES = {
    "following? - a)": "prep_kit",
    "following? - b)": "prep_evac_plan",
    "following? - c)": "prep_comm_plan",
}


def resolve_cols(df: pd.DataFrame, prefixes: dict) -> dict:
    col_map = {}
    for prefix, name in prefixes.items():
        matches = [c for c in df.columns if prefix in c]
        assert len(matches) == 1, f"expected 1 match for {prefix!r}, got {matches}"
        col_map[matches[0]] = name
    return col_map


def fetch_df() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Total (Numbers)")


def build_long(df: pd.DataFrame, col_map: dict, anchors: set[float]) -> pd.DataFrame:
    d = df.rename(columns=col_map)
    d = d.rename(columns={"#": "id"})
    item_cols = list(col_map.values())
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # Each item column has a handful of respondents sharing one repeated
    # non-anchor decimal value (e.g. 7 different ids all = 0.4199 on
    # risk1_flood, 9 different ids all = 0.5708 on risk1_wind_damage) --
    # the statistical fingerprint of a constant/mean imputation applied by
    # the authors for missing responses, not genuine per-respondent
    # slider values (a true continuous slider would not produce the exact
    # same decimal across many unrelated respondents). No imputation
    # language found in the paper text, but the pattern is unambiguous --
    # dropped as missing rather than shipped as real continuous data.
    long["resp"] = long["resp"].round(4)
    long = long[long["resp"].isin(anchors)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"]]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = fetch_df()

    risk_anchors = {0.0, 0.25, 0.5, 0.75, 1.0}
    prep_anchors = {round(i * 0.1, 1) for i in range(11)}

    risk = build_long(df, resolve_cols(df, RISK_PREFIXES), risk_anchors)
    risk.to_csv(OUT_DIR / "abukhalaf_2025_housing_risk.csv", index=False)
    print(f"housing_risk: rows={len(risk)} ids={risk['id'].nunique()} "
          f"items={risk['item'].nunique()} resp={risk['resp'].min():.2f}-{risk['resp'].max():.2f}")

    prep = build_long(df, resolve_cols(df, PREP_PREFIXES), prep_anchors)
    prep.to_csv(OUT_DIR / "abukhalaf_2025_disaster_prep.csv", index=False)
    print(f"disaster_prep: rows={len(prep)} ids={prep['id'].nunique()} "
          f"items={prep['item'].nunique()} resp={prep['resp'].min():.2f}-{prep['resp'].max():.2f}")


if __name__ == "__main__":
    convert()
