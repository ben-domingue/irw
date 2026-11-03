#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260676
# DOI: 10.1371/journal.pone.0260676
# Paper: Martin, F., Bachert, K. E., Snow, L., Tu, H.-W., Belahbib, J., &
#   Lyn, S. A. (2021). Depression, anxiety, and happiness in dog owners and
#   potential dog owners during the COVID-19 pandemic in the United States.
#   PLOS ONE 16(12): e0260676.
# Data: journal.pone.0260676.s029 (S1 Data, .xlsx). Sheet "A1" holds 1,505
#   US adults (753 dog owners, 752 non-owners open to owning one), online
#   panel, 2020; sheet "Datamap" is the survey's own codebook (every stem and
#   every value label).
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# SEVEN output tables, one per administered block, each identified from the
# Datamap's stems (not from the column prefix):
#   martin_2021_pet_attitude    M1r1..18, 1-7 agree   Pet Attitude Scale (Templer et al. 1981)
#   martin_2021_pet_commitment  M2r1..10, 1-5         Miller-Rada Commitment to Pets Scale.
#                                 AS DEPOSITED the codes run BACKWARDS:
#                                 1 = Strongly Agree .. 5 = Strongly Disagree
#                                 (the Datamap's own value labels). Not recoded.
#   martin_2021_mspss           M3r1..12, 1-7         MSPSS (Zimet et al. 1988)
#   martin_2021_cesdr           M4r1..20, 1-5         CESD-R (Eaton et al. 2004):
#                                 1 = not at all or less than 1 day .. 5 = nearly
#                                 every day for 2 weeks
#   martin_2021_gad7            M5r1..7,  0-3         GAD-7
#   martin_2021_ohq             M7r1..29, 1-6 agree   Oxford Happiness Questionnaire
#                                 (Hills & Argyle 2002), negatively-worded items
#                                 NOT reversed (as deposited)
#   martin_2021_covid_impact    S6r1..4,  1-5         study-authored: how negatively the
#                                 pandemic affected finances / emotions / health /
#                                 lifestyle. 1 = extremely negative effect .. 5 = no
#                                 negative effect at all (Datamap labels).
# Not shipped: M6 (the GAD-7 functional-difficulty follow-up, one item, asked
#   of 1,104 of 1,505); S1r1..6 pet-ownership checkboxes and S2 (non-owners'
#   interest in a dog, 752 respondents, only 4/5 observed) -- screeners;
#   QDevice, iStartr1, noanswerS3_n99, MRK_Age (a banding of S3); S5 (state)
#   and States_Division are geographic codes and are dropped under the
#   2026-10-20 ruling; the four-level Census region is kept.
#
# `id` is the row index (the deposit's `record` is a survey-platform record
# number, unique, not used).
#
# Item text: SHIPPED for four tables (gad7, mspss, cesdr, covid_impact) from
#   the Datamap sheet: stems from the "[M3r1] | ..." rows, anchors from each
#   block's "Values" rows, block prompt as `instructions`. Item ids are the
#   source column names, so there is no positional step. HELD for
#   pet_attitude and pet_commitment (named third-party scales, no grant in
#   the register -- held, 2026-11-02) and ohq (register: block). The held
#   text is in the same Datamap sheet.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("MARTIN_RAW", "journal.pone.0260676.s029.xlsx")
N_ROWS = 1505

# table -> (prefix, n_items, lo, hi, instrument name for item text or None)
BLOCKS = {
    "martin_2021_pet_attitude": ("M1r", 18, 1, 7, None),
    "martin_2021_pet_commitment": ("M2r", 10, 1, 5, None),
    "martin_2021_mspss": ("M3r", 12, 1, 7,
                          "Multidimensional Scale of Perceived Social Support (MSPSS)"),
    "martin_2021_cesdr": ("M4r", 20, 1, 5,
                          "Center for Epidemiologic Studies Depression Scale - Revised (CESD-R)"),
    "martin_2021_gad7": ("M5r", 7, 0, 3, "Generalized Anxiety Disorder-7 (GAD-7)"),
    "martin_2021_ohq": ("M7r", 29, 1, 6, None),
    "martin_2021_covid_impact": ("S6r", 4, 1, 5,
                                 "Perceived negative impact of COVID-19 (study-authored)"),
}
ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response",
                 "option_text", "resp"]


def parse_datamap(dm):
    """{block: {'prompt': str, 'values': {code: label}, 'items': {col: stem}}}
    plus single-question entries {col: {'prompt':..., 'values':...}}."""
    out, cur = {}, None
    for _, r in dm.iterrows():
        cells = [str(x).strip() for x in r if pd.notna(x) and str(x).strip()]
        if not cells:
            continue
        first = cells[0]
        if first.startswith("Values:"):
            continue
        m_block = re.match(r"^([A-Z]\w*?): (.*)$", first)          # "M1: Please answer ..."
        m_single = re.match(r"^\[(\w+)\]: (.*)$", first)           # "[S4]: Are you...?"
        m_item = re.match(r"^\[(\w+)\]$", first)                   # "[M1r1]" | stem
        if m_block and not first.startswith("["):
            cur = out.setdefault(m_block.group(1), {"prompt": m_block.group(2), "values": {}, "items": {}})
        elif m_single:
            cur = out.setdefault(m_single.group(1), {"prompt": m_single.group(2), "values": {}, "items": {}})
        elif m_item and cur is not None:
            cur["items"][m_item.group(1)] = cells[1]
        elif cur is not None and re.fullmatch(r"-?\d+", first) and len(cells) >= 2:
            cur["values"][int(first)] = cells[1]
    return out


def lab(series, values, drop=("Prefer not to answer", "Prefer not to say")):
    s = series.map(values)
    return s.where(~s.isin(drop))


def convert():
    df = pd.read_excel(RAW, sheet_name="A1").copy()
    dm = pd.read_excel(RAW, sheet_name="Datamap", header=None)
    assert len(df) == N_ROWS and df["record"].is_unique
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 131 and txt == []   # all-numeric: no free text, no names/emails

    meta = parse_datamap(dm)
    df["id"] = range(1, N_ROWS + 1)
    v = {k: meta[k]["values"] for k in ["S4", "Region", "D1", "D1b", "D2", "D3", "D4", "D5", "D6", "D7",
                                         "S7", "S8", "S9", "S10"]}
    assert v["S4"] == {1: "Male", 2: "Female", 3: "Other", 4: "Prefer not to answer"}
    assert meta["MRK_Sample"]["values"] == {1: "DOG OWNER SAMPLE", 2: "OPEN DOG NON-OWNER SAMPLE"}
    owner = df["MRK_Sample"] == 1
    assert (owner == (df["S1r1"] == 1)).all()
    for c in ["S7", "S8", "S9", "S10"]:            # dog questions asked of owners only
        assert df.loc[~owner, c].isna().all() and df.loc[owner, c].notna().all(), c
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_dog_owner": owner.astype(int),
        "cov_age": df["S3"],
        "cov_gender": lab(df["S4"], v["S4"]),
        "cov_region": df["Region"].map(v["Region"]),
        "cov_household_size": df["D1"].map(v["D1"]),
        "cov_marital_status": lab(df["D1b"], v["D1b"]),
        "cov_education": lab(df["D2"], v["D2"]),
        "cov_employment": lab(df["D3"], v["D3"]),
        "cov_urbanicity": df["D4"].map(v["D4"]),
        "cov_hispanic": df["D5"].map(v["D5"]),
        "cov_race": lab(df["D6"], v["D6"]),
        "cov_income": lab(df["D7"], v["D7"]),
        "cov_n_dogs": df["S7"].map(v["S7"]),
        "cov_dog_age": df["S8"].map(v["S8"]),
        "cov_dog_ownership_duration": df["S9"].map(v["S9"]),
        "cov_assistance_dog": df["S10"].map(v["S10"]),
    })
    cov_cols = [c for c in cov.columns if c != "id"]
    cov_src = {"MRK_Sample", "S3", "S4", "Region", "D1", "D1b", "D2", "D3", "D4", "D5", "D6", "D7",
               "S7", "S8", "S9", "S10"}

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    assert len(set(BLOCKS)) == len(BLOCKS)
    used, total = set(), 0
    for name, (prefix, k, lo, hi, instrument) in BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, k + 1)]
        assert [c for c in df.columns if re.fullmatch(prefix + r"\d+", c)] == cols, name
        block = meta[prefix[:-1]]
        assert sorted(block["items"]) == sorted(cols), name
        assert sorted(block["values"]) == list(range(lo, hi + 1)), (name, block["values"])
        used |= set(cols)
        wide = df[["id"] + cols]
        assert int(wide[cols].isna().sum().sum()) == 0, name
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), name
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS and long["item"].nunique() == k
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={k} resp={lo}-{hi}")

        if instrument:
            prompt = re.sub(r"\s*\|\s*[Dd]ependent variable\s*$", "", block["prompt"]).strip()
            prompt = re.sub(r"\.(?=[A-Z])", ". ", prompt)   # "right now.Please" in the Datamap
            rows = []
            for c in cols:
                for code in range(lo, hi + 1):
                    rows.append({"table": name, "section_id": f"{name}_1", "item": c,
                                 "instrument": instrument, "instructions": prompt,
                                 "section_prompt": "NA", "item_text": block["items"][c],
                                 "correct_response": "NA", "option_text": block["values"][code],
                                 "resp": code})
            it = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
            assert it["item_text"].str.len().gt(6).all()
            assert set(it["item"]) == set(long["item"]) and set(it["resp"]) >= set(long["resp"])
            it.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"), index=False)
            print(f"  item text: {len(it)} rows")

    dropped = [c for c in df.columns if c not in used and c not in cov_src and c != "id"]
    expected = {"record", "QDevice", "iStartr1", "S1r1", "S1r2", "S1r3", "S1r4", "S1r5", "S1r6",
                "S2", "noanswerS3_n99", "MRK_Age", "S5", "States_Division", "M6"}
    print(f"{len(used)} item columns shipped, {len(cov_src)} covariate sources, dropped: {dropped}")
    assert set(dropped) == expected, set(dropped) ^ expected
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
