#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GJW7TL
#   "Replication Data for: Thinking Machines, Pondering Humans: Public
#   Perception of Artificial Intelligence", Jason Jeffrey Jones (Stony Brook
#   University), https://jasonjones.ninja/thinking-machines-pondering-humans/
# DOI: 10.7910/DVN/GJW7TL
# License: CC BY-NC-SA 4.0, as stated on the deposit record (checked
#   2026-10-19). NC proceeds under datastandard.md "Before you start" (ruled
#   2026-10-01); Derived_License carries the NC restriction through.
#
# A decade of US surveys on attitudes to AI, run in two modes that are kept
# apart here because they put the same questions on different response scales:
#
#   * the "wide correlates" files -- one row per respondent, each attitude item
#     on a -3..+3 agreement scale (or 0/1 for the two technology checklists),
#     collected on Prolific/Lucid-style panels in 2023 and 2024;
#   * the Google-Surveys "one question" files -- long format, each response on
#     a 1-7 scale, with a response time and a survey date, mostly one question
#     per respondent (43,675 of 45,641 respondents in stacked-oneq answered a
#     single prompt; 1,864 answered the whole 10-item familiarity battery).
#
# Tables (10), each a battery that was administered as a battery:
#   jones_2026_ai_fear_2023        7 items  -3..3   500 ids
#   jones_2026_ai_fear_2021        7 items  1-7     102 ids  (same items, 1-7)
#   jones_2026_ai_art              6 items  -3..3   326 ids
#   jones_2026_ai_benefit          4 items  -3..3   498 ids  (grass_*)
#   jones_2026_ai_threat           5 items  -3..3   498 ids  (sinder_*)
#   jones_2026_trust_actors        5 items  -3..3   501 ids
#   jones_2026_tech_understanding  8 items  -3..3   501 ids
#   jones_2026_tech_familiarity   10 items  1-7   9,204 ids / 25,989 responses
#   jones_2026_tech_worried       12 items  0/1   1,009 ids (2023+2024)
#   jones_2026_tech_informed      12 items  0/1   1,009 ids (2023+2024)
#
# The 2023 and 2024 technology checklists are merged with cov_study naming the
# year: the two files carry identical column sets and the deposit's own Year
# column distinguishes them. 2024's ids are offset by 100000.
#
# NOT shipped:
#   * The stacked-oneq confidence battery (4 prompts, 10,883 respondents) and
#     trust battery (5 prompts, 13,227), because EVERY respondent answered
#     exactly one prompt of each -- no two items share a respondent, so neither
#     table can be calibrated. The script proves that rather than assuming it.
#     Both batteries are in the corpus as complete -3..3 batteries from
#     ai-trust-2023-wide.
#   * The three AGI items (Possible / Should / Rights, -3..3) administered to
#     Google Surveys 2021 (1,003), Prolific 2023 (459) and Prolific 2024 (501),
#     which merge into one 3-item table of ~1,963 respondents. Deferred with
#     the rest of the corpus's 3-4 item candidates pending a ruling on table
#     thinness -- it is otherwise clean and would be the deposit's flagship.
#     prolific-agi-2024-results.csv is the long-format twin of
#     agi-2024-wide-correlates.csv and carries no User_ID at all, so the wide
#     file is the one to build from if that ruling says ship.
#   * Single items and pairs: oppose_or_support, the checkers/chess belief
#     item, lobera_2020_ai_risk / _ai_benes (a 2-item scale on 1-5),
#     tech_more_benefits / new_tech_danger, worry_ai / worry_self_driving /
#     worry_facial (3 items on 0-6). Where the wide files carry a single
#     question about the respondent it ships as a covariate instead
#     (Risk_Preference, Generalized_Trust, Party_1, Party_2).
# Covariates: age, sex/gender, and per mode -- risk preference (0-10 self
#   report), generalized trust (the two-option GSS question, as the text the
#   respondent chose), party identification and lean on the wide files;
#   geography (US census region + state) and the survey's own sampling weight
#   on the Google-Surveys files.
# rt = RT/1000, the deposit's milliseconds converted to seconds.
# date = Survey_Date as Unix seconds (Google-Surveys files only).
# id: every file identifies respondents by a PLATFORM ACCOUNT ID -- 24-hex
#   Prolific ids in prolific-agi-2023-results, numeric Google ids elsewhere --
#   so per the 2026-09-20 PII narrowing each is replaced by a per-table
#   participant index, never a hash of it (24-hex Prolific ids are enumerable
#   from other public deposits).
# Item text: SHIPPED-ABLE AND OWED for the four Google-Surveys tables, where
#   the administered prompt is a column of the data file itself (Full_Prompt /
#   Prompt) and this script derives each item code from it reversibly -- see
#   oneq_code(). Not shipped in this commit; it is the next step for this
#   batch. The wide files carry no stems: their headers are short labels
#   (Extinction, grass_improve_life, understanding_ai), and the matching
#   wording lives in the book rather than the deposit. The one exception is
#   jones_2026_ai_fear_2023, whose seven items are the 2021 file's seven
#   prompts verbatim -- that is a cross-file mapping to make deliberately, not
#   a cheap one.

import re
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ACCESS = "https://dataverse.harvard.edu/api/access/datafile/{}?format=original"
FILES = {
    "agi-2024-wide": 14140125,
    "ai-art-2023-wide": 14140116,
    "ai-fear-2023-wide": 14140122,
    "ai-fear-2021-long": 14140117,
    "ai-indices-2023-wide": 14140120,
    "ai-indices-2024-wide": 14140114,
    "ai-scales-2023-wide": 14140118,
    "ai-trust-2023-wide": 14140124,
    "stacked-oneq-long": 14140121,
}
AGREE = {-3, -2, -1, 0, 1, 2, 3}
SEVEN = {1, 2, 3, 4, 5, 6, 7}

# Wide-file covariates: source column -> IRW name. Two files spell the same
# two questions in lower case, hence both keys.
WIDE_COVS = {
    "Age": "cov_age", "Sex": "cov_sex",
    "Risk_Preference": "cov_risk_preference", "risk_self_report": "cov_risk_preference",
    "Generalized_Trust": "cov_generalized_trust", "generalized_trust": "cov_generalized_trust",
    "Party_1": "cov_party", "Party_2": "cov_party_lean",
}
# table -> (source file, item columns, permitted values)
WIDE_TABLES = {
    "jones_2026_ai_fear_2023": ("ai-fear-2023-wide", [
        "Extinction", "Lose_Job", "Unfair_to_Individuals",
        "More_Income_Inequality", "Less_Freedom", "Overreliance",
        "Controlled_by_GSI"], AGREE),
    "jones_2026_ai_art": ("ai-art-2023-wide", [
        "Developed_Ethically", "Disclosure_Law", "Pay_Human_Creators",
        "AI_Art_Valuable", "Copyright_AI_Output", "Well_Informed"], AGREE),
    "jones_2026_ai_benefit": ("ai-scales-2023-wide", [
        "grass_improve_life", "grass_improve_work", "grass_use_in_future",
        "grass_positive_humanity"], AGREE),
    "jones_2026_ai_threat": ("ai-scales-2023-wide", [
        "sinder_fear_ai", "sinder_trust_ai", "sinder_destroy_humankind",
        "sinder_benefit_humankind", "sinder_job_losses"], AGREE),
    "jones_2026_trust_actors": ("ai-trust-2023-wide", [
        "trust_ai", "trust_congress", "trust_average_american",
        "trust_us_president", "trust_best_friend"], AGREE),
    "jones_2026_tech_understanding": ("ai-trust-2023-wide", [
        "understanding_ai", "understanding_algorithmic_bias",
        "understanding_large_language_models",
        "understanding_convolutional_neural_networks", "understanding_email",
        "understanding_phishing", "understanding_search_engine_optimization",
        "understanding_wireless_routers"], AGREE),
}
# The two 12-item technology checklists, pooled over the 2023 and 2024 files.
CHECKLIST_TOPICS = [
    "artificial_intelligence", "brain_implants", "facial_recognition_algorithms",
    "genetic_engineering", "military_drones", "new_vaccine_development",
    "nuclear_power", "quantum_computing", "robotics",
    "satellite_internet_service", "self_driving_cars", "synthetic_materials",
]
CHECKLISTS = {
    "jones_2026_tech_worried": "worried_",
    "jones_2026_tech_informed": "informed_",
}
# Wide columns deliberately left out of every table, with the reason.
WIDE_DROPPED = {
    "Possible": "AGI item 1 of 3 -- deferred on thinness",
    "Should": "AGI item 2 of 3 -- deferred on thinness",
    "Rights": "AGI item 3 of 3 -- deferred on thinness",
    "lobera_2020_ai_risk": "2-item scale on 1-5 -- too thin",
    "lobera_2020_ai_benes": "2-item scale on 1-5 -- too thin",
    "oppose_or_support": "single item",
    "worry_ai": "3-item worry triple on 0-6 -- deferred on thinness",
    "worry_self_driving": "3-item worry triple on 0-6 -- deferred on thinness",
    "worry_facial": "3-item worry triple on 0-6 -- deferred on thinness",
    "tech_more_benefits": "2-item pair -- too thin",
    "new_tech_danger": "2-item pair -- too thin",
    "Year": "carried as cov_study where two years merge",
}

# The 2021 long file's seven fear prompts, matched to the 2023 wide file's own
# item codes by a distinctive phrase of each prompt, so the two tables share an
# item vocabulary. The eighth AI prompt (checkers and chess) is a single item
# and is dropped; the trust and risk prompts become covariates.
FEAR_2021 = {
    "extinction of human beings": "Extinction",
    "losing my job": "Lose_Job",
    "treated unfairly": "Unfair_to_Individuals",
    "more income inequality": "More_Income_Inequality",
    "less freedom": "Less_Freedom",
    "come to rely on": "Overreliance",
    "greedy, selfish or irresponsible": "Controlled_by_GSI",
}
ONEQ_COVS = {
    "can't be too careful in dealing with people": "cov_generalized_trust",
    "avoid taking risks": "cov_risk_preference",
}
# The three stacked-oneq batteries, each recognised by the stem it repeats and
# turned into an item code by the part that varies. One table per battery.
# Only the familiarity battery survives from stacked-oneq. The confidence (4
# prompts, 10,883 respondents) and trust (5 prompts, 13,227) batteries each
# turn out to carry EXACTLY ONE response per respondent -- no respondent
# answered two prompts of the same battery -- so no item can be tied to
# another through a shared respondent and the table cannot be calibrated at
# all. They are not shipped; the same two batteries are in the corpus from
# ai-trust-2023-wide (jones_2026_trust_actors) as complete batteries.
# Familiarity is different: 1,865 of its 9,204 respondents answered all ten
# prompts (18,650 of 25,989 responses), and the rest are singletons, so it is
# a genuine if sparse person-item matrix.
ONEQ_TABLES = {
    "jones_2026_tech_familiarity": (
        r"^How familiar are you with the following computer-related item\? (.+)$",
        "familiar_", 10),
}
ONEQ_NOT_SHIPPED = {
    "jones_2026_ai_confidence": (
        r"^How much confidence would you say you have in \*(.+)\*\?$", 4),
    "jones_2026_trust_actors_oneq": (
        r"^How much trust do you have in (.+) to do the right thing\?$", 5),
}


def fetch(key: str) -> pd.DataFrame:
    r = requests.get(ACCESS.format(FILES[key]), headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_csv(BytesIO(r.content), low_memory=False)


def oneq_code(prefix: str, varying: str) -> str:
    """A reversible item code from the part of the prompt that varies:
    lower-cased, non-alphanumerics collapsed to one underscore, prefixed by the
    battery. 'Convolutional neural network' -> 'familiar_convolutional_neural_network';
    'government agencies that use Artificial Intelligence systems' ->
    'confidence_government_agencies_that_use_artificial_intelligence_systems'."""
    slug = re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", varying.lower())).strip("_")
    return prefix + slug


def participant_index(s: pd.Series) -> pd.Series:
    """Platform account ids -> 1..N in first-appearance order. Never a hash."""
    codes = {v: i + 1 for i, v in enumerate(pd.unique(s.dropna()))}
    return s.map(codes)


def unix_seconds(s: pd.Series) -> pd.Series:
    """Unix seconds, independent of the datetime64 resolution pandas picks --
    `.astype("int64")` is nanoseconds on pandas 2 and MICROseconds on pandas 3,
    and dividing by 1e9 regardless is how two IRW batches shipped dates 1000x
    too small. The window assert below is the second line of defence."""
    dt = pd.to_datetime(s, errors="coerce")
    secs = (dt - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
    ok = secs.dropna()
    assert ok.between(1_577_836_800, 1_735_689_600).all(), \
        (ok.min(), ok.max())  # 2020-01-01 .. 2025-01-01
    return secs.astype("float64")


def gate(t: pd.DataFrame, name: str, items: list, pv_set: set, construct: str) -> None:
    pv = {i: pv_set for i in items}
    cl = {i: construct for i in items}
    fails = [(c.name, c.detail) for c in
             run_qc(t, permitted_values=pv, item_constructs=cl) if c.status == "fail"]
    assert not fails, (name, fails)
    report = irw_validate.validate_frame(
        t, label=name, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        (name, [(f.check, f.message) for f in report.errors])
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")


def write(t: pd.DataFrame, name: str) -> None:
    t.to_csv(OUT_DIR / f"{name}.csv", index=False)
    extra = f" waves={t['wave'].nunique()}" if "wave" in t.columns else ""
    print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}"
          f"{extra}")


def do_wide(raw: dict) -> set:
    """The -3..3 agreement batteries. Returns the columns it consumed."""
    used = set()
    for name, (src, items, pv_set) in WIDE_TABLES.items():
        d = raw[src].reset_index(drop=True)
        d["id"] = d.index + 1
        missing = [c for c in items if c not in d.columns]
        assert not missing, (name, missing)
        used |= {(src, c) for c in items}
        cov_cols = [c for c in WIDE_COVS if c in d.columns]
        used |= {(src, c) for c in cov_cols}

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.rename(columns=WIDE_COVS)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        t = long.dropna(subset=["resp"]).copy()
        t["resp"] = t["resp"].astype(int)
        covs = sorted(c for c in t.columns if c.startswith("cov_"))
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t = t.reset_index(drop=True)

        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() == len(items)
        assert set(t["resp"].unique()) <= pv_set, (name, sorted(set(t["resp"])))
        gate(t, name, items, pv_set, name.replace("jones_2026_", ""))
        write(t, name)
    return used


def do_checklists(raw: dict) -> set:
    """The 0/1 'which of these worry you / do you feel informed about' lists,
    2023 and 2024 pooled with cov_study."""
    used = set()
    for name, prefix in CHECKLISTS.items():
        items = [prefix + topic for topic in CHECKLIST_TOPICS]
        parts = []
        for year, src, offset in ((2023, "ai-indices-2023-wide", 0),
                                  (2024, "ai-indices-2024-wide", 100000)):
            d = raw[src].reset_index(drop=True)
            assert (d["Year"] == year).all(), src
            d["id"] = d.index + 1 + offset
            missing = [c for c in items if c not in d.columns]
            assert not missing, (name, src, missing)
            used |= {(src, c) for c in items} | {(src, "Age"), (src, "Sex"),
                                                 (src, "Year")}
            long = d.melt(id_vars=["id", "Age", "Sex"], value_vars=items,
                          var_name="item", value_name="resp")
            long["cov_study"] = str(year)
            parts.append(long)
        t = pd.concat(parts, ignore_index=True).rename(
            columns={"Age": "cov_age", "Sex": "cov_sex"})
        t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        covs = sorted(c for c in t.columns if c.startswith("cov_"))
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t = t.reset_index(drop=True)

        assert not t.duplicated(["id", "item"]).any()
        assert t["item"].nunique() == 12
        assert set(t["resp"].unique()) == {0, 1}
        assert t.groupby("cov_study")["id"].nunique().min() >= 100
        assert t["id"].nunique() == 1009, t["id"].nunique()
        gate(t, name, items, {0, 1}, name.replace("jones_2026_", ""))
        write(t, name)
    return used


def do_fear_2021(raw: dict) -> None:
    d = raw["ai-fear-2021-long"].copy()
    assert d["User_ID"].nunique() == 102 and len(d) == 1020
    d["item"] = ""
    for phrase, code in FEAR_2021.items():
        hit = d["Full_Prompt"].str.contains(phrase, case=False, regex=False)
        assert hit.sum() == 102, (phrase, hit.sum())
        d.loc[hit, "item"] = code
    # The two covariate prompts, pivoted back onto the respondent.
    covs = {}
    for phrase, col in ONEQ_COVS.items():
        hit = d["Full_Prompt"].str.contains(phrase, case=False, regex=False)
        assert hit.sum() == 102, (phrase, hit.sum())
        covs[col] = d.loc[hit].set_index("User_ID")["Response"]
        d.loc[hit, "item"] = "__cov__"
    # Everything left over is the single checkers/chess item.
    left = d.loc[d["item"] == "", "Full_Prompt"].unique()
    assert len(left) == 1 and "checkers and chess" in left[0], left

    d = d[~d["item"].isin(["", "__cov__"])].copy()
    t = pd.DataFrame({
        "id": participant_index(d["User_ID"]),
        "item": d["item"],
        "resp": pd.to_numeric(d["Response"], errors="coerce"),
        "rt": d["RT"] / 1000.0,
        "date": unix_seconds(d["Survey_Date"]),
        "cov_age": d["Age"],
        "cov_gender": d["Gender"],
        "cov_geography": d["Geography"],
        "cov_weight": d["Weight"],
        "cov_generalized_trust": d["User_ID"].map(covs["cov_generalized_trust"]),
        "cov_risk_preference": d["User_ID"].map(covs["cov_risk_preference"]),
    }).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)

    name = "jones_2026_ai_fear_2021"
    items = sorted(t["item"].unique())
    assert len(items) == 7 and t["id"].nunique() == 102
    assert set(items) == set(FEAR_2021.values())
    assert set(t["resp"].unique()) <= SEVEN
    assert t["rt"].between(1, 200).all(), t["rt"].describe()
    gate(t, name, items, SEVEN, "ai_fear")
    write(t, name)


def do_stacked(raw: dict) -> None:
    d = raw["stacked-oneq-long"].copy()
    assert len(d) == 60564 and d["Full_Prompt"].nunique() == 22
    claimed = set()
    for name, (pattern, prefix, n_items) in ONEQ_TABLES.items():
        m = d["Full_Prompt"].str.extract(pattern, expand=False)
        sub = d[m.notna()].copy()
        sub["item"] = [oneq_code(prefix, v) for v in m[m.notna()]]
        assert sub["item"].nunique() == n_items, (name, sub["item"].nunique())
        claimed |= set(sub["Full_Prompt"].unique())

        # 101 respondent-prompt pairs appear twice in the file, all of them on
        # the "confidence in *companies that use AI*" prompt, each under two
        # different Survey_Dates -- and in every one of the 101 the response is
        # IDENTICAL across the two dates. Zero disagreement over 101 repeats is
        # a duplication signature rather than a re-measurement, so the later
        # row is dropped instead of being carried as a second wave.
        dup = sub.duplicated(["User_ID", "item"], keep=False)
        if dup.any():
            pairs = sub.loc[dup].groupby(["User_ID", "item"])
            assert (pairs["Response"].nunique() == 1).all()
            assert (pairs["Survey_Date"].nunique() == 2).all()
            print(f"  {name}: dropped {dup.sum() // 2} duplicate response(s) "
                  f"-- same respondent, same prompt, same answer, two dates")
            sub = sub.sort_values("Survey_Date").drop_duplicates(
                ["User_ID", "item"], keep="first")

        t = pd.DataFrame({
            "id": participant_index(sub["User_ID"]),
            "item": sub["item"],
            "resp": pd.to_numeric(sub["Response"], errors="coerce"),
            "rt": sub["RT"] / 1000.0,
            "date": unix_seconds(sub["Survey_Date"]),
            "cov_age": sub["Age"],
            "cov_gender": sub["Gender"],
            "cov_geography": sub["Geography"],
            "cov_weight": sub["Weight"],
        }).dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t.sort_values(["id", "item"]).reset_index(drop=True)

        items = sorted(t["item"].unique())
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        assert set(t["resp"].unique()) <= SEVEN
        assert t["rt"].between(0.5, 4000).all(), t["rt"].describe()
        gate(t, name, items, SEVEN, name.replace("jones_2026_", ""))
        write(t, name)

    for name, (pattern, n_items) in ONEQ_NOT_SHIPPED.items():
        m = d["Full_Prompt"].str.extract(pattern, expand=False)
        sub = d[m.notna()]
        assert m[m.notna()].nunique() == n_items, name
        claimed |= set(sub["Full_Prompt"].unique())
        per_person = sub.groupby("User_ID")["Full_Prompt"].nunique()
        assert (per_person == 1).all(), (name, per_person.max())
        print(f"  NOT shipped {name}: {n_items} prompts, "
              f"{sub['User_ID'].nunique()} respondents, every one of them "
              f"answering exactly one prompt of the battery")

    # Account for the remaining prompts in the file.
    leftover = set(d["Full_Prompt"].unique()) - claimed
    assert len(leftover) == 3, leftover
    for p in sorted(leftover):
        print(f"  dropped stacked-oneq prompt (single item): {p[:80]}")


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = {k: fetch(k) for k in FILES}
    used = do_wide(raw) | do_checklists(raw)
    do_fear_2021(raw)
    do_stacked(raw)

    # Balance the books on the wide files: every column is an item, a
    # covariate, or named in WIDE_DROPPED.
    for src in ("agi-2024-wide", "ai-art-2023-wide", "ai-fear-2023-wide",
                "ai-indices-2023-wide", "ai-indices-2024-wide",
                "ai-scales-2023-wide", "ai-trust-2023-wide"):
        for col in raw[src].columns:
            if (src, col) in used or col in WIDE_COVS or col in WIDE_DROPPED:
                continue
            raise AssertionError(f"unaccounted column {src}:{col}")
    for col, why in sorted(WIDE_DROPPED.items()):
        print(f"  dropped {col}: {why}")


if __name__ == "__main__":
    convert()
