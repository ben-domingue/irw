#!/usr/bin/env python3
# Source: Harvard Dataverse doi:10.7910/DVN/VPVH00 (J-PAL), "Replication data
#   for: Children's arithmetic skills do not transfer between applied and
#   academic mathematics". License: CC0 1.0 (Dataverse licence field).
# Paper: Banerjee AV, Bhattacharjee S, Chattopadhyay R, Duflo E, Ganimian AJ,
#   Rajah K, Spelke ES (2025). Nature 639, 673-681.
#   https://doi.org/10.1038/s41586-024-08502-w
# Issue: ben-domingue/irw#819.
#
# DOWNLOAD. Every file sits behind J-PAL's Dataverse guestbook 269 (a name,
#   an intended use, a position and a country; no licence terms). Ben
#   Domingue's response stated the use as the Item Response Warehouse
#   (2026-10-01). Through the API: POST
#   https://dataverse.harvard.edu/api/access/datafile/<id>?format=original
#   with a JSON body {"guestbookResponse": {...}} returns a signed URL. Files
#   used (all Stata .dta despite the .tab name):
#     10749696  3_School children survey (Study 3b)/0_deid_data.tab  -> s3b/
#     10749732  4_Market children (Study 3a - Wave 1)/0_deid_data.tab -> s3a_w1/
#   The item mapping follows the authors' setup_mm_20241015.do (file 10749668).
#
# TWO TABLES, two instruments, two samples, no shared items:
#
# banerjee_2025_arithmetic_school -- Study 3b, 300 Delhi school children
#   (classes 7-8). Items keep the survey's codes:
#     b1a b1b b1c b2 b3 b4  ASER arithmetic tool. Adaptive: b1c only after
#                           b1a wrong and b1b right; b2 only after a
#                           subtraction pass; b3/b4 (number recognition) only
#                           on failure. Unreached items are absent rows.
#     c{n}_v{k}  written abstract    d{n}_v{k}  oral abstract
#     e{n}_v{k}  oral anchored (word problem), with n = operation
#                (1 add, 2 subtract, 3 multiply, 4 divide) and k = survey
#                version 1-4. Each child got ONE version (cov_version), and
#                the versions use different numbers -- the same problem is
#                rotated across formats between versions -- so c1_v1 and
#                c1_v2 are different items.
#     f1  oral anchored market problem;  f2  pretend-market problem, scored
#         as the authors do: correct if the total is 110,111,113,114,115,
#         116,118 or 120 (individual prices exact or rounded by 1 or 5).
#   Not included: f3 (the market problem re-asked, with a randomised hint,
#   only of children who missed f1).
#
# banerjee_2025_arithmetic_market -- Study 3a wave 1, 372 working children
#   in Delhi markets. Only the problems every child got with the same
#   numbers, first attempt:
#     sub_{a}_{b}  oral abstract subtraction a - b. Two problems per child,
#                  each drawn from two variants by the survey's `subtract`
#                  randomisation (94-48 or 57-28; 95-49 or 55-29); the item
#                  code names the operands, read from subtract1a/1b/2a/2b.
#     div_{a}_{b}  oral abstract division a / b (35/3 or 75/7; 75/6 or 39/4),
#                  from divide1a/1b/2a/2b. Answers with a remainder count as
#                  the enumerator recorded them.
#     market_word  the applied market word problem (answer 137), first try.
#   Not included: the mystery-shopping and hypothetical-market questions
#   (built from each child's own goods, quantities and prices, so no two
#   children answer the same item), second attempts and post-hint attempts
#   (asked only after a wrong answer or under a randomised hint).
#   Wave 2 of Study 3a is a different instrument whose operands are drawn per
#   child; it is not built here (see #819).
#
# Scoring: resp = 1 correct, 0 incorrect, from the enumerators' coding
#   (*_num_calc / *_num_c, "Yes"/"No"), as the paper uses it. id fixes for
#   wave 1 are the authors' (setup do-file, "FIX DATA ENTRY ISSUES").

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")


def yesno(s):
    s = s.astype(str).str.strip()
    return np.where(s.isin(["Yes", "Correct"]), 1.0, np.where(s.isin(["No", "Incorrect"]), 0.0, np.nan))


def school():
    df, meta = pyreadstat.read_dta(SRC / "s3b" / "0_deid_data.tab")
    vlab = meta.variable_value_labels
    df["id"] = (df["a_school_id"].astype("Int64").astype(str) + "-" +
                df["g_class"].astype("Int64").astype(str) + "-" +
                df["a_student_id2"].astype("Int64").astype(str))
    assert df["id"].is_unique
    df["version_n"] = df["version"].str.extract(r"(\d)").astype(int)

    items = {}
    for q in ["b1a", "b1b", "b1c", "b2"]:
        items[q] = yesno(df[f"{q}_answer_num_calc"])
    for q in ["b3", "b4"]:
        items[q] = pd.to_numeric(df[f"{q}_correct"], errors="coerce").to_numpy()
    for s in "cde":
        for n in (1, 2, 3, 4):
            for k in (1, 2, 3, 4):
                code = f"{s}{n}_v{k}"
                v = yesno(df[f"{s}{n}_answer_v{k}_num_calc"])
                v[df["version_n"].to_numpy() != k] = np.nan  # not this child's version
                items[code] = v
    items["f1"] = yesno(df["f1_answer_num_calc"])
    f2 = pd.to_numeric(df["f2_answer_num"], errors="coerce")
    items["f2"] = np.where(f2.isna(), np.nan, f2.isin([110, 111, 113, 114, 115, 116, 118, 120]).astype(float))

    wide = pd.DataFrame(items)
    wide["id"] = df["id"]
    sex = df["g_sex"].map(vlab.get("g_sex", {1: "Girl", 2: "Boy"}))
    wide["cov_gender"] = sex.str.extract(r"^(Girl|Boy)")[0].map({"Girl": "female", "Boy": "male"})
    wide["cov_age"] = pd.to_numeric(df["g_age"], errors="coerce").astype("Int64")
    wide["cov_grade"] = pd.to_numeric(df["g_class"], errors="coerce").astype("Int64")
    wide["cov_school"] = df["a_school_id"].astype("Int64")
    wide["cov_version"] = df["version_n"]
    wide["cov_incentives"] = df["incentives"].map({"Yes": 1, "No": 0}).astype("Int64")
    covs = [c for c in wide.columns if c.startswith("cov_")]
    long = wide.melt(id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp"] + covs]


def market():
    df, meta = pyreadstat.read_dta(SRC / "s3a_w1" / "0_deid_data.tab")
    d = df["a_date"].astype(str)
    m, c = df["a_market_id"].astype(int).copy(), df["a_child_id"].astype(int).copy()
    # The authors' id corrections, in their order.
    m[(m == 22) & (d == "2023-03-29")] = 98
    c[(c == 2) & (m == 23) & (d == "2023-03-31")] = 11
    c[(c == 6) & (m == 23) & (d == "2023-03-31")] = 12
    sel = (m == 27) & (c == 16) & (df["a_surveyor_name"] == 8); assert sel.sum() == 1; m[sel] = 20
    sel = (m == 37) & (c == 40); assert sel.sum() == 1; c[sel] = 42
    m[(m == 22) & (d == "2023-03-31")] = -9999
    m[(m == 21) & (d == "2023-04-18")] = 22
    m[(m == -9999) & (d == "2023-03-31")] = 21
    m[(m == 18) & (d == "2023-04-03")] = 9
    m[(m == 98) & (d == "2023-03-29")] = 26
    for old, new in [(1, 10), (2, 11), (3, 12), (4, 13), (5, 14)]:
        c[(m == 22) & (c == old) & (d == "2023-04-27")] = new
    df["id"] = (m * 100 + c).astype(str).str.zfill(4)
    assert df["id"].is_unique, "wave-1 ids not unique after the authors' fixes"

    ver = df["version"].astype(int)
    rows = []
    for _, r in df.iterrows():
        v = int(r["version"])
        def add(item, val):
            if val in ("Yes", "No"):
                rows.append((r["id"], item, 1 if val == "Yes" else 0))
        add(f"sub_{int(r['subtract1a'])}_{int(r['subtract1b'])}", str(r[f"d{v}_abstract1_first_answer_num_c"]))
        add(f"sub_{int(r['subtract2a'])}_{int(r['subtract2b'])}", str(r[f"d{v}_abstract2_first_answer_num_c"]))
        add(f"div_{int(r['divide1a'])}_{int(r['divide1b'])}", str(r["f_division1_answer_num_c"]))
        add(f"div_{int(r['divide2a'])}_{int(r['divide2b'])}", str(r["f_division2_answer_num_c"]))
        add("market_word", str(r["e_market_first_answer_num_c"]))
    long = pd.DataFrame(rows, columns=["id", "item", "resp"])
    vl = meta.variable_value_labels
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_gender": df["g_gender"].map({1: "female", 2: "male"}),
        "cov_age": pd.to_numeric(df["c_age"], errors="coerce").astype("Int64"),
        "cov_attending_school": df["g_attending_school"].map({1: "school", 2: "madrassa only", 3: "no"}),
        "cov_market": m.astype(int),
        "cov_version": ver,
    })
    return long.merge(cov, on="id", how="left")


if __name__ == "__main__":
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    for name, f in [("banerjee_2025_arithmetic_school", school), ("banerjee_2025_arithmetic_market", market)]:
        t = f()
        assert not t.duplicated(["id", "item"]).any()
        pv = {i: {0, 1} for i in t["item"].unique()}  # every item scored correct/incorrect
        fails = [(c.name, c.detail) for c in run_qc(t, permitted_values=pv) if c.status == "fail"]
        assert not fails, fails
        t.to_csv(out / f"{name}.csv", index=False, na_rep="")
        rep = irw_validate.validate_file(str(out / f"{name}.csv"), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, [(f.check, f.message) for f in rep.errors]
        print(name, len(t), "rows", t["id"].nunique(), "ids", t["item"].nunique(), "items")
