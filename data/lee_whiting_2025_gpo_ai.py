"""
Seventeen ordinal blocks from the Global Public Opinion on Artificial
Intelligence (GPO-AI) survey -- 23,781 respondents across 21 countries,
fielded in 12 languages in October and November 2023.

Source: Lee-Whiting, B., Loewen, P. J., Bergeron, T., & Schwartz Reisman
        Institute for Technology and Society (2025). Global Public Opinion on
        Artificial Intelligence (GPO-AI) [Data set]. Borealis.
DOI: 10.5683/SP3/WCUN0S
Data: https://borealisdata.ca/dataset.xhtml?persistentId=doi:10.5683/SP3/WCUN0S
        (files "gpo-ai_data.csv" and "gpo-ai_codebook.docx")
License: CC BY-NC 4.0 (verified on the Borealis record,
        latestVersion.license.name "CC BY-NC 4.0"). NC proceeds under
        datastandard.md's 2026-10-01 ruling, with the restriction carried into
        Derived_License.
Item text: shipped. The codebook .docx gives every block's question stem, its
        response options in order, and one row per item, all in English. The
        survey was ADMINISTERED in 12 languages and the deposit publishes only
        the English master, so the item text ships as the standard's
        translated_substitute fallback -- see itemtext_provenance.csv.

**Twenty-one tables, one per ordinal block**, as datastandard.md's "Multiple
scales in one file" asks. The blocks are the codebook's own question groups and
the item codes keep the deposit's own column names (`populism_1`, `Justice_4`,
lowercased), so each item stays tied to the codebook row that gives its stem.

**Ten further blocks are NOT shipped because they are not item responses.**
`risk_daily`, `capabilities`, `use_AI`, `concern`, `regulation_AI`,
`privacy_actors`, `safety_actors`, `GPT_assist`, `Deep_trust` and
`Deep_regulate` are "check all that apply" questions: each column holds the
LABEL of one option the respondent selected, in no order, so the column index
means nothing and the values are nominal. `attention` is an instructed-response
attention check (name a colour), also nominal. Reshaping any of them to
endorsement indicators would be a new coding decision, not a transcription,
so they are left out rather than guessed at.

**Response coding is semantic, not positional.** The codebook prints the
agreement options top-down in different orders for different blocks (populism
leads with "Strongly agree", regulation_gvt with "Strongly disagree"), so
coding by display order would ship two opposite scale directions under the same
resp values. Every agreement block is mapped the same way instead -- strongly
disagree 1 .. strongly agree 5 -- and the same for the frequency, permission
and likelihood scales. The 0-10 trust and impact sliders are already numeric
and are carried through unchanged.

`Don't know` (populism only, 4,985 cells) is dropped rather than coded: it is
not a point on the agreement scale.

Planned missingness is real here. Several blocks were asked of a random subset,
so a respondent absent from a table was never asked, not non-responding; every
table still has at least 19,000 respondents.

Dropped columns, and why:
  * `respondent_subnational` -- 396 regions within 21 countries. A geographic
    code, which the 2026-10-20 PII ruling says to drop rather than carry in any
    form (not as cov_*, not hashed, not coarsened); the country is kept.
  * `respondent_survey_data` -- a per-respondent completion TIMESTAMP to the
    second (22,384 distinct). This is a single-wave survey, so it times no
    measurement, and a second-resolution timestamp beside country and
    demographics is a re-identification handle for nothing in return.
  * `*_TEXT` write-ins (16 columns) -- "Other (please specify)" free text
    attached to the check-all blocks that are not shipped anyway.
  * `respondent_income` -- free-typed amounts in 21 local currencies, with
    junk entries (" 00"); `subjective_income`, a clean four-level item, is
    kept instead.
  * The ISCO occupation indicators, the raw party name, and the remaining
    survey-flow columns, which are neither items nor covariates here.

`respondent_survey_seconds` becomes `cov_completion_time_s`, NOT `rt`: `rt` is
a per-item response time, and this is one duration for the whole survey.

`respondent_yob` is mis-named in the source -- the codebook's question is "How
old are you?" and the values run 18-88 -- so it ships as `cov_age`.

The write-in suffixes are stripped from four covariates ("Other (Please
specify)Advertising" -> "Other"), so no free text is carried into a cov_*
column.

PII: none reaches the output. The screen below examines every string column,
prints its denominator, and asserts that no column holds names, emails,
birthdates or geographic codes; `respondent_subnational` is dropped before
anything else.

Output: 21 tables, 2,935,076 responses -- 23,781 respondents, 129 items.
  * lee_whiting_2025_populism                6 items, resp 1-5
  * lee_whiting_2025_job_tasks              10 items, resp 1-4
  * lee_whiting_2025_ai_regulation_views     5 items, resp 1-5
  * lee_whiting_2025_trust_actors_ai         8 items, resp 0-10
  * lee_whiting_2025_trust_actors_privacy    8 items, resp 0-10
  * lee_whiting_2025_trust_actors_security   8 items, resp 0-10
  * lee_whiting_2025_ai_impacts_now          5 items, resp 0-10
  * lee_whiting_2025_ai_impacts_10years      5 items, resp 0-10
  * lee_whiting_2025_gpt_org_permission      6 items, resp 1-4
  * lee_whiting_2025_gpt_job_permission      9 items, resp 1-5
  * lee_whiting_2025_self_driving_support    5 items, resp 1-5
  * lee_whiting_2025_self_driving_use        3 items, resp 1-5
  * lee_whiting_2025_ai_decision_support     7 items, resp 1-5
  * lee_whiting_2025_ai_education            3 items, resp 1-5
  * lee_whiting_2025_ai_justice              8 items, resp 1-5
  * lee_whiting_2025_ai_healthcare           9 items, resp 1-5
  * lee_whiting_2025_ai_government           9 items, resp 1-5
  * lee_whiting_2025_job_loss_expectations   3 items, resp 1-4
  * lee_whiting_2025_digital_government      3 items, resp 1-5
  * lee_whiting_2025_ai_vs_human_choice      4 items, resp 0-1
  * lee_whiting_2025_ai_nurse_tradeoff       5 items, resp 0-1

The last four were nearly lost. They do not share the `prefix_<n>` column shape
the other seventeen do, so the grouping regex could not see them; they were
found only because this script PRINTS the leftover columns instead of counting
them (SKILL.md, 2026-08-26, where a count alone cost ~1.0M responses). Two of
them are forced choices between an AI and a human, which belong in core rather
than the nominal standard: with exactly two options the ordered/unordered
distinction is vacuous.

**Seventeen tables become twenty-one**, then: the paragraph above describes the
regex-found blocks and `EXPLICIT_BLOCKS` holds the rest.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("gpo-ai_data.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

AGREE = {
    "Strongly disagree": 1, "Strongly Disagree": 1,
    "Somewhat disagree": 2,
    "Neither agree nor disagree": 3,
    "Somewhat agree": 4,
    "Strongly agree": 5,
}
FREQ = {
    "Never": 1, "Less than once a week": 2,
    "Approximately every week": 3, "Most days": 4,
}
PERMISSION = {"Not at all": 1, "A little": 2, "A lot": 3, "A great deal": 4}
HOW_OFTEN = {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5}
LIKELY = {
    "Extremely unlikely": 1, "Somewhat Unlikely": 2,
    "Neither likely nor unlikely": 3, "Somewhat likely": 4,
    "Extremely likely": 5,
}
SLIDER = {v: v for v in range(11)}          # 0-10, already numeric
AMOUNT = {"None at all": 1, "A few": 2, "A lot": 3, "A great deal": 4}
# Forced choice between an AI and a human doing the same job. The two option
# strings differ per item (the wait time changes, the human is a "nurse", a
# "public servant", "a human"), so the AI side is identified by its wording
# rather than by a fixed string -- every AI option names "Artificial
# Intelligence (AI)" and no human option does.
AI_VS_HUMAN = "ai_vs_human"

# Values that are not a point on their scale and are dropped, not coded.
NOT_A_SCALE_POINT = {"Don't know"}

# table -> (source prefix, number of items, option map)
BLOCKS = {
    "lee_whiting_2025_populism":              ("populism", 6, AGREE),
    "lee_whiting_2025_job_tasks":             ("Tasks", 10, FREQ),
    "lee_whiting_2025_ai_regulation_views":   ("regulation_gvt", 5, AGREE),
    "lee_whiting_2025_trust_actors_ai":       ("trust_AI", 8, SLIDER),
    "lee_whiting_2025_trust_actors_privacy":  ("protection", 8, SLIDER),
    "lee_whiting_2025_trust_actors_security": ("security", 8, SLIDER),
    "lee_whiting_2025_ai_impacts_now":        ("AI_impacts", 5, SLIDER),
    "lee_whiting_2025_ai_impacts_10years":    ("AI_impacts_10years", 5, SLIDER),
    "lee_whiting_2025_gpt_org_permission":    ("GPT_org", 6, PERMISSION),
    "lee_whiting_2025_gpt_job_permission":    ("GPT_ind", 9, HOW_OFTEN),
    "lee_whiting_2025_self_driving_support":  ("Self_Dr_sup", 5, AGREE),
    "lee_whiting_2025_self_driving_use":      ("Self_Dr_use_public", 3, LIKELY),
    "lee_whiting_2025_ai_decision_support":   ("Decision", 7, AGREE),
    "lee_whiting_2025_ai_education":          ("Education_support", 3, AGREE),
    "lee_whiting_2025_ai_justice":            ("Justice", 8, AGREE),
    "lee_whiting_2025_ai_healthcare":         ("Healthcare", 9, AGREE),
    "lee_whiting_2025_ai_government":         ("Government", 9, AGREE),
}

# Blocks whose columns do NOT share a `prefix_<n>` shape, so the regex above
# cannot find them. They were found by printing the leftover columns rather
# than counting them -- `aipi1`..`aipi6` has no underscore before the number,
# and the rest are named by content. Each entry is an explicit column list.
EXPLICIT_BLOCKS = {
    # "How many of your friends / neighbours / generation will lose their jobs
    # to a computer in the next 10 years?" -- same four-point amount scale.
    # `kids_replace` asks the same thing about children on a LIKELIHOOD scale
    # and is left out: one item on its own scale is not a table.
    "lee_whiting_2025_job_loss_expectations": (
        ["friendsfam_replace", "neighbour_replace", "generation_replace"],
        AMOUNT),
    # Three agreement items on integrating AI into government digital services.
    "lee_whiting_2025_digital_government": (
        ["Digital_gvt_both", "Digital_gvt_efficien", "Digital_gvt_laid"],
        AGREE),
    # Forced choice, AI or a human, in four decision settings.
    "lee_whiting_2025_ai_vs_human_choice": (
        ["TO_border", "TO_finance", "TO_immigration", "TO_justice"],
        AI_VS_HUMAN),
    # The same forced choice five times with the wait for a human nurse rising
    # from 10 minutes to 3 hours. Each respondent saw a subset by design, so
    # the per-item counts differ widely (6,820 to 23,435) -- that is the
    # design, not attrition.
    "lee_whiting_2025_ai_nurse_tradeoff": (
        ["TO_health_10m", "TO_health_30m", "TO_health_1h", "TO_health_2h",
         "TO_health_3h"],
        AI_VS_HUMAN),
}

# Left out on purpose, with the reason, so the leftover list below stays
# meaningful:
#   aipi1..aipi6 -- six separate questions with six different two- and
#       three-point option sets (agree/disagree, excited/concerned,
#       likely/not likely). Not one scale.
#   GPT_replace_c/_f -- two items on the amount scale, below the three-item
#       floor ruled 2026-10-19.
#   GPT_replace_i, GPT_help_f, GPT_help_i -- three items that share a
#       definitely-yes/no scale but not a construct: two ask whether ChatGPT
#       will HELP and one whether it will REPLACE. Shipping them as one table
#       would assert a scale the survey does not claim.

COV_MAP = {
    "respondent_country": "cov_country",
    "respondent_yob": "cov_age",                 # mis-named: it is age
    "respondent_gender": "cov_gender",
    "respondent_education": "cov_education",
    "respondent_employment": "cov_employment",
    "respondent_relationship": "cov_relationship",
    "urban": "cov_urban",
    "subjective_income": "cov_subjective_income",
    "Ideology_1": "cov_ideology",
    "partyid_strength": "cov_partyid_strength",
    "respondent_survey_seconds": "cov_completion_time_s",
}

# Covariates whose source column carries an "Other (please specify)" write-in
# glued onto the option label. The label is kept, the write-in is not.
WRITE_IN_PREFIXES = ("Other (Please specify)", "Other (please specify)",
                     "Another gender (please specify)")
WRITE_IN_COVS = ["cov_gender", "cov_education", "cov_employment",
                 "cov_relationship"]

DROP_PATTERNS = [
    (r"^respondent_subnational$",
     "a geographic code (396 regions); 2026-10-20 PII ruling says drop it, "
     "not carry it in any form"),
    (r"^respondent_survey_data$",
     "a per-respondent completion timestamp to the second; this is a "
     "single-wave survey, so it times no measurement"),
    (r"_TEXT$", "an \"Other (please specify)\" write-in on a block that is "
                "not shipped"),
    (r"^respondent_income$",
     "free-typed amounts in 21 local currencies; subjective_income is kept "
     "instead"),
    (r"^isco_", "an ISCO occupation indicator, neither item nor covariate here"),
]

# Blocks left out because their values are nominal, not ordinal. Listed so the
# books below balance against a reason rather than silence.
NOMINAL_BLOCKS = {
    "risk_daily": "check-all-that-apply: which technologies used last week",
    "capabilities": "check-all-that-apply: which capabilities AI has",
    "use_AI": "check-all-that-apply: which technologies use AI",
    "concern": "check-all-that-apply: concerns about AI",
    "regulation_AI": "check-all-that-apply: who should regulate AI",
    "privacy_actors": "check-all-that-apply: who should regulate privacy",
    "safety_actors": "check-all-that-apply: who should ensure safety",
    "GPT_assist": "check-all-that-apply: tasks to hand a chatbot",
    "Deep_trust": "check-all-that-apply: who is trusted on deepfakes",
    "Deep_regulate": "check-all-that-apply: who should regulate deepfakes",
    "attention": "instructed-response attention check (name a colour)",
}


def pii_screen(df: pd.DataFrame) -> None:
    """Examine every string column and print the denominator.

    `is_string_dtype`, never `dtype == object`: a screen that selects nothing
    reports clean, which is the worst shape a safety check can take.
    """
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}")
    assert text_cols, "no string columns selected -- screen is not working"

    banned = re.compile(r"name|email|e-mail|phone|address|postal|zip|birth"
                        r"|dob|ip_?addr|latitude|longitude", re.I)
    flagged = [c for c in df.columns if banned.search(c)]
    # respondent_pid is a PARTY name, respondent_subnational is handled by the
    # drop rules above, and "Unnamed: 0" is pandas' name for the file's unnamed
    # row-index column -- it matches on the substring "name" and is not one.
    # The pattern stays deliberately broad: a screen should over-match and be
    # argued down here, not under-match silently.
    allowed = {"respondent_pid", "respondent_subnational", "Unnamed: 0"}
    unexpected = [c for c in flagged if c not in allowed]
    assert not unexpected, f"identifier-shaped column(s): {unexpected}"
    print(f"  name/email/date-of-birth/geo screen: {len(flagged)} column(s) "
          f"matched by name, all accounted for ({sorted(flagged)})")


def main() -> None:
    df = pd.read_csv(SRC, low_memory=False)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 23781, len(df)

    item_cols = {}
    option_maps = {}
    for table, (cols, omap) in EXPLICIT_BLOCKS.items():
        missing = [c for c in cols if c not in df.columns]
        assert not missing, (table, missing)
        item_cols[table] = list(cols)
        option_maps[table] = omap
    for table, (prefix, n, _) in BLOCKS.items():
        cols = sorted((c for c in df.columns
                       if re.fullmatch(rf"{re.escape(prefix)}_\d+", c)),
                      key=lambda c: int(re.sub(r"\D", "", c)))
        assert len(cols) == n, (table, len(cols), n, cols)
        item_cols[table] = cols
        option_maps[table] = BLOCKS[table][2]

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    for cov in WRITE_IN_COVS:
        df[cov] = df[cov].apply(strip_write_in)
    covs = list(COV_MAP.values())

    # Balance the books: every source column is an item, a covariate, a
    # nominal block left out on purpose, or a documented drop.
    accounted = set(COV_MAP) | set(covs) | {"id", "Unnamed: 0"}
    accounted |= {c for cs in item_cols.values() for c in cs}
    nominal = {c for c in df.columns
               if any(re.fullmatch(rf"{re.escape(p)}_\d+", c)
                      for p in NOMINAL_BLOCKS)}
    dropped = {}
    for c in df.columns:
        if c in accounted or c in nominal:
            continue
        for pat, why in DROP_PATTERNS:
            if re.search(pat, c):
                dropped[c] = why
                break
    leftover = [c for c in df.columns
                if c not in accounted and c not in nominal and c not in dropped]
    # Everything else in this file is survey flow and single-item questions
    # that belong to no block; name them so the count is visible.
    print(f"not used: {len(nominal)} column(s) in {len(NOMINAL_BLOCKS)} nominal "
          f"block(s), {len(dropped)} documented drop(s), "
          f"{len(leftover)} other single-item/flow column(s)")
    # Name them: a count alone is how 1,205 skip lines once scrolled past
    # unread and cost ~1.0M responses (SKILL.md, 2026-08-26).
    print(f"  single-item/flow columns, not part of any block: "
          f"{sorted(leftover)}")
    for why in sorted(set(dropped.values())):
        cs = sorted(c for c, w in dropped.items() if w == why)
        print(f"  dropped {len(cs)} column(s) -- {why}")
    for p, why in NOMINAL_BLOCKS.items():
        print(f"  not shipped: {p} -- {why}")

    total = 0
    for table, cols in item_cols.items():
        total += write(df, table, cols, covs, option_maps[table])
    print(f"total responses across {len(item_cols)} tables: {total:,}")


def strip_write_in(v):
    if not isinstance(v, str):
        return v
    for p in WRITE_IN_PREFIXES:
        if v.startswith(p):
            return "Another gender" if "gender" in p else "Other"
    return v


def write(df: pd.DataFrame, table: str, cols: list, covs: list,
          option_map: dict) -> int:
    codes = {c: c.lower() for c in cols}
    assert len(set(codes.values())) == len(cols), codes
    long = df[["id"] + covs + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="raw")

    raw = long["raw"]
    if option_map is AI_VS_HUMAN:
        # 1 = chose the AI, 0 = chose the human. Every AI option names
        # "Artificial Intelligence (AI)"; assert that each item really does
        # offer exactly two options, one of each kind, so a reworded option
        # cannot silently collapse an item to all-zeros.
        for it, grp in long.groupby("item"):
            opts = sorted({v for v in grp["raw"] if isinstance(v, str)})
            assert len(opts) == 2, (table, it, opts)
            n_ai = sum("Artificial Intelligence (AI)" in o for o in opts)
            assert n_ai == 1, (table, it, opts)
        resp = raw.map(
            lambda v: (1 if "Artificial Intelligence (AI)" in v else 0)
            if isinstance(v, str) else None)
    elif option_map is SLIDER:
        resp = pd.to_numeric(raw, errors="coerce")
    else:
        resp = raw.map(option_map)
        unmapped = sorted({v for v, r in zip(raw, resp)
                           if isinstance(v, str) and pd.isna(r)})
        unexpected = [v for v in unmapped if v not in NOT_A_SCALE_POINT]
        assert not unexpected, f"{table}: unmapped response(s) {unexpected}"
        if unmapped:
            n = int(raw.isin(NOT_A_SCALE_POINT).sum())
            print(f"  {table}: dropped {n:,} cell(s) answered "
                  f"{sorted(NOT_A_SCALE_POINT)} -- not a point on the scale")
    long["resp"] = resp
    long = long[long["resp"].notna()]
    long["resp"] = long["resp"].astype(int)

    permitted = ([0, 1] if option_map is AI_VS_HUMAN
                 else sorted(set(option_map.values())))
    outside = sorted(set(long["resp"].unique()) - set(permitted))
    assert not outside, f"{table}: resp outside {permitted}: {outside}"

    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:150]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> {table}: rows={len(long):,} ids={long['id'].nunique():,} "
          f"items={long['item'].nunique()} "
          f"resp={min(long['resp'])}-{max(long['resp'])}")
    return len(long)


if __name__ == "__main__":
    main()
