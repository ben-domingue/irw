from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

# Source (raw data): https://gitlab.com/a-bc/your-covid-19-risk-data
# Source (site/code): https://gitlab.com/a-bc/your-covid-19-risk
# Paper: Peters, Kwasnicka, ten Hoor et al. (2025), "Collecting behavioural
# data across countries during pandemics: Development of the COVID-19 Risk
# Assessment Tool", Behav Res 57, 223. https://doi.org/10.3758/s13428-025-02743-x
# GitHub issue: https://github.com/ben-domingue/irw/issues/1093
#
# License: same as `peters_2025_covid19_risk_dcts.py` -- the data repo's
# README states .csv data sets are anonymized and "existing in the public
# domain by definition"; approved by the authors directly (see BATCH_LOG.md,
# 2026-07-16/17).
#
# This is the follow-up half of the Peters 2025 dataset left undone by
# `peters_2025_covid19_risk_dcts.py` (the RAA belief-item family) -- the
# "risk-estimate/checkbox-array" columns: `work*`, `siCurrent*`,
# `siTrigger*`, `siIntention*`, `hwFrequency*`, `hwIntensity*`, each paired
# with an `*Est` column.
#
# MECHANISM (reverse-engineered from the raw data, not documented in the
# project's build script the way the RAA items were): each family is a
# LimeSurvey "checkboxes" question -- one column per selectable option,
# holding "Y" if selected and blank/NaN otherwise. The paired `*Est` column
# is NOT a per-person numeric estimate despite the name -- it only ever
# takes 1-2 distinct values for a given option, identical across every sid
# (country) checked, and those values are the tool's own fixed internal
# risk-scoring coefficients for that option (0 for the "safe" state, a
# constant e.g. 2.7 for the "risky" state) -- i.e. `*Est` is item metadata
# (the risk weight the tool's calculator applies), not a response. Its real
# usefulness here is different: `*Est` is non-null exactly when that
# specific checkbox option was actually administered to that respondent
# (this survey uses per-item skip logic/array_filter branching, e.g.
# `siIntention`'s LimeSurvey definition has `array_filter = "siCurrent"`),
# and null when the option was never shown. Confirmed exhaustively across
# two different sids: every row where the checkbox is "Y" has a non-null
# Est (0 counter-examples), so Est-not-null is a safe administration gate.
#
# Decoding rule per option: Est null -> not administered, excluded;
# Est not null & checkbox=="Y" -> resp=1; Est not null & checkbox blank ->
# resp=0.
#
# `siTrigger.other.` and `siIntention.other.` are "Other, please specify"
# free-text boxes (their Est column is a constant 0 with no admin-gating
# meaning) -- excluded as open-text columns, not part of the checklist.
#
# NOT covered by this script (single-item, can't be shipped as their own
# scale per IRW's no-single-item-scale rule): `proximity` (a single
# radiobutton item) and `DMQslider.nr.` (a single slider item).
REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

RAW_BASE = "https://gitlab.com/a-bc/your-covid-19-risk-data/-/raw/master/data/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FILES = [
    "YCR-dataPipeline--sid-100101--rids-1-4849.csv",
    "YCR-dataPipeline--sid-100101--rids-14548-19396.csv",
    "YCR-dataPipeline--sid-100101--rids-19397-24245.csv",
    "YCR-dataPipeline--sid-100101--rids-24246-29094.csv",
    "YCR-dataPipeline--sid-100101--rids-29095-33943.csv",
    "YCR-dataPipeline--sid-100101--rids-33944-38790.csv",
    "YCR-dataPipeline--sid-100101--rids-4850-9698.csv",
    "YCR-dataPipeline--sid-100101--rids-9699-14547.csv",
    "YCR-dataPipeline--sid-100102--rids-1-141.csv",
    "YCR-dataPipeline--sid-100103--rids-1-1479.csv",
    "YCR-dataPipeline--sid-100104--rids-1-254.csv",
    "YCR-dataPipeline--sid-100104--rids-1286-2448.csv",
    "YCR-dataPipeline--sid-100104--rids-255-1285.csv",
    "YCR-dataPipeline--sid-100105--rids-1-2450.csv",
    "YCR-dataPipeline--sid-100105--rids-2451-3888.csv",
    "YCR-dataPipeline--sid-100106--rids-1-439.csv",
    "YCR-dataPipeline--sid-100107--rids-1-455.csv",
    "YCR-dataPipeline--sid-100108--rids-1-586.csv",
    "YCR-dataPipeline--sid-100109--rids-1-162.csv",
    "YCR-dataPipeline--sid-100110--rids-1-2583.csv",
    "YCR-dataPipeline--sid-100110--rids-13027-13135.csv",
    "YCR-dataPipeline--sid-100110--rids-2584-5166.csv",
    "YCR-dataPipeline--sid-100110--rids-5167-9096.csv",
    "YCR-dataPipeline--sid-100110--rids-9097-13026.csv",
    "YCR-dataPipeline--sid-100111--rids-1-3616.csv",
    "YCR-dataPipeline--sid-100111--rids-11542-11662.csv",
    "YCR-dataPipeline--sid-100111--rids-3617-7231.csv",
    "YCR-dataPipeline--sid-100111--rids-7232-11541.csv",
    "YCR-dataPipeline--sid-100112--rids-1-225.csv",
    "YCR-dataPipeline--sid-100113--rids-1-915.csv",
    "YCR-dataPipeline--sid-100114--rids-1-2227.csv",
    "YCR-dataPipeline--sid-100115--rids-1-1374.csv",
    "YCR-dataPipeline--sid-100116--rids-1-2035.csv",
    "YCR-dataPipeline--sid-100116--rids-2036-2170.csv",
    "YCR-dataPipeline--sid-100117--rids-1-2034.csv",
    "YCR-dataPipeline--sid-100117--rids-2035-2625.csv",
    "YCR-dataPipeline--sid-100117--rids-2626-4138.csv",
    "YCR-dataPipeline--sid-100117--rids-4139-4246.csv",
    "YCR-dataPipeline--sid-100118--rids-1-560.csv",
    "YCR-dataPipeline--sid-100119--rids-1-1337.csv",
    "YCR-dataPipeline--sid-100120--rids-1-307.csv",
    "YCR-dataPipeline--sid-100121--rids-1-783.csv",
    "YCR-dataPipeline--sid-100121--rids-12635-16197.csv",
    "YCR-dataPipeline--sid-100121--rids-16198-16374.csv",
    "YCR-dataPipeline--sid-100121--rids-1815-3144.csv",
    "YCR-dataPipeline--sid-100121--rids-3145-4111.csv",
    "YCR-dataPipeline--sid-100121--rids-4112-4450.csv",
    "YCR-dataPipeline--sid-100121--rids-4451-8542.csv",
    "YCR-dataPipeline--sid-100121--rids-784-1814.csv",
    "YCR-dataPipeline--sid-100121--rids-8543-12634.csv",
]

COV_MAP = {
    "country": "cov_country",
    "age": "cov_age_band",
    "gender": "cov_gender",
    "lastpage": "cov_lastpage",
    "startlanguage": "cov_language",
}

FAMILIES = {
    "work": "peters_2025_work_precautions",
    "siCurrent": "peters_2025_si_current",
    "siTrigger": "peters_2025_si_trigger",
    "siIntention": "peters_2025_si_intention",
    "hwFrequency": "peters_2025_hw_frequency",
    "hwIntensity": "peters_2025_hw_intensity",
}


def fetch_data() -> pd.DataFrame:
    frames = []
    for fname in FILES:
        r = requests.get(RAW_BASE + fname, headers=UA, timeout=120)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content), low_memory=False)
        df = df.rename(columns={df.columns[0]: "orig_id"})
        m = re.search(r"sid-(\d+)", fname)
        df["sid"] = m.group(1)
        frames.append(df)
    full = pd.concat(frames, ignore_index=True, sort=False)
    full["id"] = full["sid"] + "-" + full["orig_id"].astype(str)
    assert full["id"].nunique() == len(full)
    return full


def build_family_items(raw_cols: list[str], family: str) -> list[tuple[str, str, str]]:
    """Returns [(checkbox_col, item_label, est_col)] for a family, skipping
    any option whose checkbox holds free text rather than a Y/blank marker
    (an 'Other, please specify' box) rather than assuming naming alone."""
    pattern = re.compile(rf"^{family}\.([a-zA-Z]+)\.$")
    out = []
    for c in raw_cols:
        m = pattern.match(c)
        if not m:
            continue
        suffix = m.group(1)
        est_col = f"{family}{suffix[0].upper()}{suffix[1:]}Est"
        if est_col not in raw_cols:
            continue
        out.append((c, suffix.lower(), est_col))
    return out


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    parsed = pd.to_datetime(raw["datestamp"], format="%Y-%m-%d %H:%M:%S", utc=True)
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    raw["date"] = ((parsed - epoch) / pd.Timedelta(seconds=1)).astype("int64")
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_cols = raw.columns.tolist()

    for family, out_name in FAMILIES.items():
        items = build_family_items(all_cols, family)
        frames = []
        for chk_col, label, est_col in items:
            # "Other, please specify" boxes hold free text, not Y/blank --
            # skip rather than assume from naming alone.
            non_null_vals = set(raw[chk_col].dropna().unique().tolist())
            if not non_null_vals <= {"Y"}:
                continue
            administered = raw[est_col].notna()
            resp = raw[chk_col].eq("Y").astype(int)
            sub = pd.DataFrame({
                "id": raw["id"], "item": label, "resp": resp,
                "date": raw["date"], **{c: raw[c] for c in cov_cols},
            })
            sub = sub[administered].reset_index(drop=True)
            frames.append(sub)

        long = pd.concat(frames, ignore_index=True)
        long = long[["id", "item", "resp", "date"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_path.name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
