#!/usr/bin/env python3
# Source: https://osf.io/6un4h/
# DOI: 10.1038/s41598-025-85558-2
#   "The impact of labeling automotive AI as trustworthy or reliable on user
#   evaluation and technology acceptance" (Dorsch & Deroy, 2025), Scientific
#   Reports 15:1481.
# Data: OSF 6un4h, Data/ANON_Trust_in_AI_Main_Study.csv (Qualtrics export,
#       two header rows + 661 respondents x 52). English-speaking online
#       participants. The same folder's ANON_Trust_in_AI_Pilot.csv (64 rows)
#       is a different instrument (six items per vignette, other checks) and
#       is not used.
# License: CC BY 4.0 (OSF node licence, resolved via api.osf.io/v2/licenses;
#       article CC BY 4.0).
#
# Item text: shipped for dorsch_2025_ai_tam only (Qualtrics question-text
#   header row = the administered English stems; response labels are the
#   cells themselves). Not shipped for dorsch_2025_ai_vignettes: the stems are
#   in the same header row, but each item's vignette differs by condition
#   ("trustworthy" vs "reliable" wording) and the four statements repeat
#   across the three vignettes, so a single item_text per item cannot carry
#   what was asked; left for an item text pass.
#
# Tables (all 1-5: strongly disagree .. strongly agree, from the cell labels):
#   dorsch_2025_ai_vignettes  12 items: {planning, steering, parking}
#     assistance vignette x 4 statements (confident driving with it /
#     confident learning to drive with it / AI to blame / AI accountable).
#     Between-subjects: each person saw the "trustworthy AI" (T-) or the
#     "reliable AI" (R-) version; the paper says the vignettes are identical
#     except those key terms, so T- and R- columns share one item code
#     (planning_1 ..) and the condition is `treat` (1 = trustworthy label,
#     0 = reliable label). Nobody answered both versions (asserted).
#   dorsch_2025_ai_tam        8 exit-questionnaire TAM items (ease of use,
#     usefulness, intention, ability trust, benevolence, integrity, general
#     trust, attitude).
# Respondents: all 661 who consented are kept (partial completers keep what
#   they answered). The paper's exclusions (language check, attention check,
#   age) are NOT applied; the checks are carried as covariates instead:
#   cov_language_check_pass (selected exactly the four grammatical sentences)
#   and cov_induction_check_pass (selected exactly the two statements that
#   match the definition shown). Paper: 478 retained.
# id: row index. ResponseId (a Qualtrics platform id) is dropped, per the
#   2026-09-20 platform-ID ruling. No other identifiers: no IP, location,
#   email or names. Dropped: timestamps, duration, progress, consent, the
#   free-text gender-other cell, the multi-select expertise/experience lists.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://osf.io/download/9vk3p/"
LIKERT = {"strongly disagree": 1, "disagree": 2, "neutral": 3, "agree": 4,
          "strongly agree": 5}
GRAMMATICAL = {"Athletes often need to warm up.",
               "I just saw a moose running down the road!",
               "Where’s the pen I gave you yesterday?",
               "He was pulled over by the police for driving 120 miles per "
               "hour."}
CHECK_OK = {
    "T": {"If the AI is trustworthy, it will do the right thing for the "
          "right ethical reasons.",
          "Trustworthy AI cares about ethical norms and/or conceptualizes "
          "moral principles."},
    "R": {"If the AI is reliable, it will produce the expected outcome for "
          "the tasks it was assigned.",
          "Reliable AI consistently produces the expected outcome."},
}
SCEN = ["Planning", "Steering", "Parking"]
VIG = [f"{s} Assist_{k}" for s in SCEN for k in range(1, 5)]
TAM = [f"Exit Questionnaire_{k}" for k in range(1, 9)]
COVS = {"Demo: Gender": "cov_gender", "Demo: Age": "cov_age_band",
        "Demo: DL": "cov_drivers_licence", "Demo: Education": "cov_education"}
DROP = ["StartDate", "EndDate", "Progress", "Duration (in seconds)",
        "Finished", "RecordedDate", "ResponseId", "ResponseID",
        "UserLanguage", "Consent", "Demo: Gender_5_TEXT", "Demo: Expertise",
        "Demo: Experience", "Language Check", "Induction: Trust",
        "Induction: Reliable"]


def selset(x):
    if pd.isna(x):
        return None
    return set(x.split(","))


def split_check(x):
    """Qualtrics joins multi-select choices with ','; the check statements
    contain commas themselves, so split on the known statements instead."""
    if pd.isna(x):
        return None
    found, rest = set(), x
    for s in sorted(CHECK_OK["T"] | CHECK_OK["R"] | EXTRA, key=len,
                    reverse=True):
        if s in rest:
            found.add(s)
            rest = rest.replace(s, "")
    assert not rest.strip(", "), rest
    return found


EXTRA = {"Trustworthy AI has nothing to do with the AI having moral "
         "principles or ethical norms.",
         "If the AI is trustworthy, it neither conceptualizes moral "
         "principles nor does it care about ethical norms.",
         "Reliable AI has nothing to do with the AI being effective or "
         "consistent.",
         "If the AI is reliable, it will neither produce the expected "
         "outcome, nor is it likely to do so in the future."}


def to_num(s):
    return s.str.strip().str.lower().map(LIKERT)


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    raw = pd.read_csv(io.BytesIO(r.content), encoding="utf-8",
                      encoding_errors="replace", dtype=str)
    d = raw.iloc[2:].reset_index(drop=True)
    assert d.shape == (661, 52), d.shape
    tcols = [f"T-{v}" for v in VIG]
    rcols = [f"R-{v}" for v in VIG]
    acc = set(tcols) | set(rcols) | set(TAM) | set(COVS) | set(DROP)
    assert set(d.columns) == acc and len(d.columns) == len(acc), \
        set(d.columns) ^ acc
    assert (d["Consent"] == "Yes, I consent").all()
    for c in [*tcols, *rcols, *TAM]:
        v = d[c].dropna().str.strip().str.lower()
        assert v.isin(LIKERT).all(), (c, set(v) - set(LIKERT))

    d.insert(0, "id", d.index + 1)
    has_t = d[tcols].notna().any(axis=1)
    has_r = d[rcols].notna().any(axis=1)
    assert not (has_t & has_r).any()
    d["treat"] = pd.NA
    d.loc[has_t, "treat"] = 1
    d.loc[has_r, "treat"] = 0
    ind_t, ind_r = d["Induction: Trust"], d["Induction: Reliable"]
    arm = pd.Series(pd.NA, index=d.index, dtype="object")
    arm[ind_t.notna()] = "T"
    arm[ind_r.notna()] = "R"
    assert not (ind_t.notna() & ind_r.notna()).any()
    assert ((d["treat"] == 1) <= (arm == "T")).all()

    def check_pass(i):
        a = arm[i]
        if pd.isna(a):
            return pd.NA
        sel = split_check(ind_t[i] if a == "T" else ind_r[i])
        return int(sel == CHECK_OK[a])
    d["cov_induction_check_pass"] = [check_pass(i) for i in d.index]
    d["cov_language_check_pass"] = [
        pd.NA if s is None else int(s == GRAMMATICAL)
        for s in d["Language Check"].map(selset)]
    for c, v in d[["cov_language_check_pass",
                   "cov_induction_check_pass"]].items():
        print(f"  {c}: {v.value_counts(dropna=False).to_dict()}")
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values()) + ["cov_language_check_pass",
                                      "cov_induction_check_pass"]
    for c in DROP:
        print(f"  drop {c}")

    # vignettes: coalesce T-/R- into one item code
    for v in VIG:
        code = v.replace(" Assist_", "_").lower()
        d[code] = to_num(d[f"T-{v}"]).fillna(to_num(d[f"R-{v}"]))
    vig_codes = [v.replace(" Assist_", "_").lower() for v in VIG]
    tam_codes = [f"tam_{k}" for k in range(1, 9)]
    for c, code in zip(TAM, tam_codes):
        d[code] = to_num(d[c])

    tables = {
        "dorsch_2025_ai_vignettes": (vig_codes, ["treat"]),
        "dorsch_2025_ai_tam": (tam_codes, []),
    }
    assert len(set(tables)) == len(tables)
    expect = {"dorsch_2025_ai_vignettes": int(d[tcols + rcols].notna()
                                              .sum().sum()),
              "dorsch_2025_ai_tam": int(d[TAM].notna().sum().sum())}
    for table, (items, extra) in tables.items():
        long = d.melt(id_vars=["id"] + extra + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        if extra:
            assert long["treat"].notna().all()
            long["treat"] = long["treat"].astype(int)
        long = long[["id", "item", "resp"] + extra + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert len(long) == expect[table], (len(long), expect[table])
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
