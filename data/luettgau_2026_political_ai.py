#!/usr/bin/env python3
# Source: https://academic.oup.com/pnasnexus/article/5/10/pgag305/8865178
# DOI: 10.1093/pnasnexus/pgag305 (Luettgau, L., Kirk, H.R., Hackenburg, K., Bergs, J., Davidson,
#   H., Ogden, H., Siddarth, D., Huang, S., & Summerfield, C. (2026). "Conversational AI increases
#   political knowledge as effectively as self-directed internet search." PNAS Nexus 5(10):
#   pgag305. Preprint arXiv:2509.05219.)
# Data: https://github.com/UKGovernmentBEIS/dhi1-analysis-public -- analysis code and pseudonymised
#   data published by the UK AI Security Institute. Two of its files ship here:
#     data/Ztable_misinfo_combined.csv   the RCTs' pre/post belief panel (studies 2 and 3)
#     data/survey_data/analysis.csv      the nationally representative survey (study 1)
#   with data/survey_data/{survey,options}_codebook.csv (tab-separated) supplying the survey's
#   question wording and response labels, and data/*_exclusions.csv the per-arm inclusion flags.
# License: Open Government Licence v3.0 -- verified in the repository's own LICENSE-DATA, which
#   scopes OGL v3.0 to data/, figures/ and the parameter_estimates/ directories and MIT to code/
#   only. Open, commercial use permitted, attribution required: "Contains public sector
#   information licensed under the Open Government Licence v3.0." The article itself carries the
#   same statement for its public sector information.
#
# PII: none to strip. The repository is pseudonymised by its publisher and says so: all twelve
#   demographic variables, exact age and the fieldwork panel's respondent identifier were removed
#   before deposit, because the underlying file holds UK GDPR Article 9 special-category data
#   (ethnicity, religion, disability, mental health, political opinion) at a level of detail that
#   makes most respondents unique. What is left is a positional subject index in the RCT tables and
#   a pseudonymous `P0001`-style code in the survey. The cost is that NO covariates ship with
#   either table -- data/demographics_aggregated.csv is marginal frequencies only, so there is
#   nothing person-level to carry.
#
# Item text: not shipped for luettgau_2026_political_knowledge. data/statement_sourcing.csv gives
#   31 statements with their provenance against the 64 items here, and carries no question number,
#   so there is no way to attach a statement to an item from the deposit -- that needs the
#   article's supplementary material, one hop outside it. Item text IS available for
#   luettgau_2026_source_trust (survey_codebook.csv, verbatim question stem plus the eight source
#   labels) and the item codes below preserve the Q1b_N mapping so it can be joined later.
#
# == luettgau_2026_political_knowledge: 64 items, 1-7, 2858 ids, 365824 responses ==============
#
# Studies 2 and 3 are randomised trials in which each participant was pseudo-randomly assigned two
# of four political topics (climate change, immigration, criminal justice, COVID-19 policy) to
# research, and then rated agreement with 16 statements per topic -- 8 true, 8 false -- on a
# 7-point scale, BEFORE and AFTER researching, for all four topics whether they had researched
# them or not. So the file is a complete 64-item x 2-occasion panel: 128 rows for every one of the
# 2,858 participants, no missingness, no duplicate key.
#
# `resp` is agreement with the statement, not correctness. Scoring it is left to the user:
# `itemcov_ground_truth` says whether the statement is true (1) or false (0), consistent within
# item on all 365,824 rows, which the script asserts rather than assumes.
#
# READ THIS BEFORE USING `resp`: the scale is stored AGREE-FIRST. 1 = agree, 7 = disagree. So a
# LOWER `resp` means MORE agreement with the statement, and the knowledge gain the article reports
# shows up here as researched true statements moving DOWN and researched false statements moving
# UP. It ships in the source's own coding, per the standard's "do not recode reverse-scored
# items", but the direction is undocumented in the deposit and nothing about the column announces
# it -- a user who assumes 7 = agree gets every sign backwards.
#
# The direction is not a guess. Three things fix it:
#   - The article: "True information received on average approximately one Likert scale point
#     higher agreement ratings than false information (beta_TRUE = .67)". In this file the items
#     flagged `ground_truth == true` average 3.45 against 4.09 for the false ones -- 0.64 points
#     LOWER. Higher agreement therefore means a lower stored value.
#   - The deposit's own pipeline reverses the column before modelling anything:
#     `y = 6 - (df['response'].values - 1)` for the misinfo, private and extreme outcomes (and,
#     notably, not for trust). beta_TRUE = +.67 is a coefficient on that reversed outcome.
#   - The most concentrated item in the file, covid_14, is a FALSE statement with 70% of its
#     responses at 7. Seventy percent flatly rejecting a piece of misinformation is an ordinary
#     result; seventy percent strongly endorsing it would not be.
# main() asserts all of this against the shipped frame, so the claim is tested on every run
# rather than left in a comment.
#
# `treat` is the WITHIN-subject manipulation -- whether this participant researched this topic --
# because that is the contrast with an untreated comparison in it. The article calls the two
# unresearched topics "non-researched within-subject controls". The BETWEEN-subject randomisation
# is not treatment-vs-control at all: in study 2 both arms research the topics and the comparison
# is modality (conversational AI against self-directed Google search), and in study 3 both arms
# use a chatbot and the comparison is its system prompt. That randomisation therefore ships as
# `cov_arm`, which is the one place the standard's "don't put the arm in a covariate" rule has to
# give, since two nested randomisations cannot both be `treat`.
#
#   cov_arm      ai_chatbot / google_search      (study 2, searchornot == 1, n = 1147)
#                prompted_chatbot / default_chatbot  (study 3, searchornot == 0, n = 1711)
#     The source's `iscontrol` is test/control; which arm that names comes from the article:
#     study 2's control arm is Google search and its test arm the chatbot, study 3's control arm
#     is GPT-4o under its default system prompt and its test arms GPT-4o prompted to be persuasive
#     or sycophantic.
#   cov_model_arm  the recruitment batch's model or prompting variant: GPT4o, claude, mistral
#     (study 2) or GPT4o_persuasion, GPT4o_sycophancy_both (study 3). It is the batch label, NOT
#     necessarily what the participant used: a study-2 control subject in the `claude` batch
#     researched with Google, and a study-3 control subject in the `GPT4o_persuasion` batch used
#     default-prompted GPT-4o.
#   cov_compliance  the subject-level compliance score (0-1) from five compliance questions per
#     researched topic. Measured POST-treatment, which is why the article's reported models drop
#     it -- conditioning on it can bias the treatment estimates -- and the repository ships both
#     pipelines so the difference can be inspected. Kept here because it is a real person-level
#     measurement, not a derivation of anything else in the file.
#
# `searchornot` is not shipped as its own column: it is exactly the study indicator (1 for the
# three study-2 model batches, 0 for the two study-3 prompting batches), so it is `cov_study`, and
# the script asserts the collinearity instead of trusting the name.
#
# The 2,858 subjects are already the analysis sample. Each arm's `*_exclusions.csv` has
# include == 1 for exactly as many rows as that arm has subjects here (382/364/401/734/977), so no
# exclusion step is owed; the script downloads the five files and checks it.
#
# Two gate warnings stand, both inspected and both the data rather than a defect:
#   imputed_values*  one item, covid_14, has 70% of its responses at 7. It is a false statement
#     that most of the sample rejects outright -- the check reports concentration, not a cause,
#     and the next most concentrated item sits at 38%.
#   multi_scale*     the four item-name prefixes are the four topics, not four instruments. One
#     instrument, 16 statements per topic, every participant answering all 64 both before and
#     after; splitting by topic would cut the within-subject researched/not-researched contrast
#     the design is built on. `itemcov_topic` carries the split for anyone who wants it.
#
# Not shipped from the same deposit, each for a stated reason:
#   Ztable_trust_combined.csv, Ztable_private_combined.csv
#       The trust battery and the privately-held-belief battery, 10 items each. Both hold ONE row
#       per (subject, topic, question) with `presented` labelling it pre or post, rather than the
#       pre/post pair the misinfo table has, so what a row is cannot be settled from the deposit:
#       a given subject-question is "pre" under one topic and "post" under another. Shipping it
#       would mean guessing whether `wave` is a timepoint or an artefact of how the analysis table
#       was assembled. Left for a human read of the article's supplement.
#   Ztable_extreme_combined.csv
#       attitude extremity -- a derivation of the private-belief responses (a sign flip relative
#       to the scale midpoint, values 0/2/4/6), not a response.
#   Ztable_dur_combined.csv
#       two task durations per subject. Whole-task completion time, not per-item response time, so
#       it is not `rt`; with no covariates to attach it to there is nothing to carry it on.
#   Ztable_indiv_combined.csv
#       subject-level compliance and search condition, both already carried as covariates above.
#   demographics_aggregated.csv, statement_sourcing.csv, parameter_estimates/
#       marginal frequencies, stimulus provenance, and fitted model output.
#
# == luettgau_2026_source_trust: 8 items, 1-4, 2499 ids =========================================
#
# Study 1's one battery: "In general, how much do you trust the following sources to provide
# accurate information about UK political issues or current affairs?" asked of all 2,499
# respondents about eight sources, with no branching and no missingness. 2,475 of the 2,499 keep
# at least one item after the "Don't know" drop below; the 24 who do not answered "Don't know"
# about all eight sources.
#
# The response scale is 1-4 as shipped, NOT the 1-5 the raw column holds. Per
# options_codebook.csv the five options are "Trust a great deal", "Trust to some extent", "Do not
# trust very much", "Do not trust at all", "Don't know" -- so 5 is a non-response sitting inside
# the valid range, and those 1,243 item-responses are dropped rather than recoded. The surviving
# scale runs 1 = trust a great deal to 4 = do not trust at all, i.e. HIGHER means LESS trust; the
# source's direction is preserved rather than reversed.
#
# Nothing else in analysis.csv is a scale. Q1a/Q1d/Q1e/Q3a/Q4a/Q4b/Q5a are binary
# selected/not-selected behaviour checklists that include "Other" and "None of the above" options;
# Q1c, Q2a-c, Q3b-d, Q4c-d and Q5b-j are single questions with unordered or
# partly-unordered option sets (e.g. Q5e: left-leaning / neutral / right-leaning / don't know),
# every one of them carrying its own "I don't know". Neither group is an item response battery.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

GH_RAW = ("https://raw.githubusercontent.com/UKGovernmentBEIS/"
          "dhi1-analysis-public/HEAD/{}")

TOPICS = ["climate", "covid", "criminal", "immigration"]
ARMS = {"GPT4o": 2, "claude": 2, "mistral": 2,
        "GPT4o_persuasion": 3, "GPT4o_sycophancy_both": 3}
# arm -> exclusions file stem, and the subject count the deposit's include flag must agree with
EXCLUSIONS = {"GPT4o": "GPT4o", "claude": "claude", "mistral": "mistral",
              "GPT4o_persuasion": "GPT4o_persuasion",
              "GPT4o_sycophancy_both": "GPT4o_sycophancy"}

# Q1b_N -> item code. The survey codebook's eight sources, in its own order.
TRUST_ITEMS = {"Q1b_1": "trust_newspapers",
               "Q1b_2": "trust_television",
               "Q1b_3": "trust_radio",
               "Q1b_4": "trust_ai_chatbots",
               "Q1b_5": "trust_social_media",
               "Q1b_6": "trust_other_internet",
               "Q1b_7": "trust_podcasts",
               "Q1b_8": "trust_internet_search"}
TRUST_DK = 5          # "Don't know", option 5 of 5 -- a non-response, dropped


def truth_flag(col: "pd.Series") -> "pd.Series":
    """`ground_truth` is the literal text "true"/"false" in the CSV, which a reader may hand
    back as bool or as str depending on its dtype inference. Accept either, reject anything
    else -- a silently all-False column would mislabel every item's veracity."""
    if col.dtype == bool:
        flag = col
    else:
        text = col.astype(str).str.strip().str.lower()
        assert set(text) == {"true", "false"}, sorted(set(text))
        flag = text == "true"
    out = flag.astype(int)
    assert set(out) == {0, 1} and 0.3 < out.mean() < 0.7, out.mean()
    return out


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def gh_fetch(repo_path: str, raw_dir: Path) -> Path:
    return download(GH_RAW.format(repo_path), raw_dir / Path(repo_path).name)


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def check_exclusions(raw_dir: Path, counts: "pd.Series") -> None:
    """The Ztables are the included sample already -- assert it, don't assume it."""
    for arm, stem in EXCLUSIONS.items():
        e = pd.read_csv(gh_fetch(f"data/{stem}_exclusions.csv", raw_dir))
        included = int((e["include"] == 1).sum())
        assert included == counts[arm], (arm, included, counts[arm])
        print(f"  {stem}_exclusions.csv: {included} of {len(e)} included "
              f"= {counts[arm]} subjects present")


def political_knowledge(raw_dir: Path) -> pd.DataFrame:
    d = pd.read_csv(gh_fetch("data/Ztable_misinfo_combined.csv", raw_dir))
    print("raw shape", d.shape)
    assert len(d) == 365824, len(d)
    assert set(d["model"]) == set(ARMS), sorted(set(d["model"]))
    assert set(d["topic"]) == set(TOPICS), sorted(set(d["topic"]))
    assert set(d["response"]) == set(range(1, 8)), sorted(set(d["response"]))
    assert set(d["presented"]) == {"pre", "post"}
    # `presentation` is a vestigial second copy of `presented` -- the canonical pipeline
    # (data_analysis_pipeline_no_compliance.py) never reads it; `presented` is what every
    # reported model is built on, via df['time'] = (df['presented'] == 'post'). The two
    # disagree on 416 rows: 13 subjects in the claude, persuasion and sycophancy arms, one
    # topic each (32 rows = 16 statements x 2 occasions), where the topic's pre and post
    # labels are swapped between the columns. Both columns key the panel without duplicates,
    # so neither is self-evidently the broken one, and `presented` ships because it is the
    # one the published results rest on. 0.11% of rows; documented rather than dropped,
    # since dropping them would leave 13 subjects a topic short of the analysis sample.
    swapped = d[d["presentation"] != d["presented"]]
    assert len(swapped) == 416, len(swapped)
    assert swapped.groupby("subject").size().eq(32).all()
    print(f"  presented vs presentation: {len(swapped)} rows disagree "
          f"({swapped['subject'].nunique()} subjects x 1 topic); shipping `presented`, "
          f"the column the reported analysis uses")

    # `subject` is positional per arm (the deposit's README: groupby('model').cumcount() + 1), so
    # whether it collides across arms is a property of this file, not a guarantee. In the misinfo
    # table the numbering runs through -- 2,858 distinct values for 2,858 (arm, subject) pairs --
    # so it is usable as `id` unprefixed. Assert it; the private/extreme tables in the same
    # deposit restart at 1 in every arm and would need the arm folded in.
    pairs = d.drop_duplicates(["model", "subject"])
    counts = pairs.groupby("model")["subject"].size()
    assert d["subject"].nunique() == len(pairs) == 2858, (d["subject"].nunique(), len(pairs))
    print("  subjects per arm:", counts.to_dict())
    check_exclusions(raw_dir, counts)

    # searchornot is the study indicator, not a per-subject condition: assert the collinearity
    # rather than taking the column name's word for it.
    study = pairs.groupby("model")["searchornot"].agg(["nunique", "max"])
    assert (study["nunique"] == 1).all(), study
    for arm, n in ARMS.items():
        assert study.loc[arm, "max"] == (1 if n == 2 else 0), (arm, n)
    d["cov_study"] = d["model"].map(ARMS)
    assert d.drop_duplicates(["model", "subject"]).groupby("cov_study").size().to_dict() == \
        {2: 1147, 3: 1711}, "study sizes must match the article's n = 1147 / 1711"

    # One compliance score and one arm per subject -- both subject-level, so assert before use.
    per_sub = d.groupby("subject")[["sub_compliance", "iscontrol", "cov_study"]].nunique()
    assert (per_sub == 1).all().all(), per_sub.max()
    assert set(d["iscontrol"]) == {"test", "control"}

    out = pd.DataFrame({
        "id": d["subject"],
        "item": d["topic"] + "_" + d["question"].map("{:02d}".format),
        "resp": d["response"],
        "wave": d["presented"].map({"pre": 1, "post": 2}),
        "treat": (d["researched"] == "yes").astype(int),
        "cov_study": d["cov_study"],
        "cov_arm": [{(2, "test"): "ai_chatbot", (2, "control"): "google_search",
                     (3, "test"): "prompted_chatbot", (3, "control"): "default_chatbot"}[k]
                    for k in zip(d["cov_study"], d["iscontrol"])],
        "cov_model_arm": d["model"],
        "cov_compliance": d["sub_compliance"],
        "itemcov_topic": d["topic"],
        "itemcov_ground_truth": truth_flag(d["ground_truth"]),
    })
    assert out["item"].nunique() == 64, out["item"].nunique()

    # ground_truth and topic are item attributes: one value per item across every row, or the
    # itemcov_ prefix misdescribes them.
    per_item = out.groupby("item")[["itemcov_ground_truth", "itemcov_topic"]].nunique()
    assert (per_item == 1).all().all(), per_item.max()
    truth = out.drop_duplicates("item")["itemcov_ground_truth"].value_counts().to_dict()
    assert truth == {1: 32, 0: 32}, truth
    print(f"  64 items = 4 topics x 16 statements, {truth[1]} true / {truth[0]} false")

    # A complete panel: every subject x item x occasion exactly once, nothing missing.
    assert out.groupby("id").size().eq(128).all()
    assert not out.duplicated(["id", "item", "wave"]).any()
    assert out.notna().all().all()
    check_scale_direction(out)
    return out.sort_values(["id", "item", "wave"]).reset_index(drop=True)


def check_scale_direction(out: pd.DataFrame) -> None:
    """The header's agree-first finding, tested against the frame being shipped. If a future
    re-download flips the coding, or `ground_truth` turns out to mean something other than the
    statement's veracity, these three inequalities break instead of silently reversing every
    sign a user computes."""
    m = out.groupby("itemcov_ground_truth")["resp"].mean()
    assert m[1] < m[0] - 0.4, m.to_dict()
    moved = out[out["treat"] == 1].groupby(["itemcov_ground_truth", "wave"])["resp"].mean()
    assert moved[(1, 2)] < moved[(1, 1)] - 0.05, moved.to_dict()   # true: toward agreement
    assert moved[(0, 2)] > moved[(0, 1)] + 0.05, moved.to_dict()   # false: toward rejection
    still = out[out["treat"] == 0].groupby(["itemcov_ground_truth", "wave"])["resp"].mean()
    print(f"  scale direction: resp 1 = agree, 7 = disagree. true {m[1]:.2f} vs false "
          f"{m[0]:.2f} (article: true gets ~1 point HIGHER agreement); researched true "
          f"{moved[(1, 1)]:.3f} -> {moved[(1, 2)]:.3f}, researched false {moved[(0, 1)]:.3f} "
          f"-> {moved[(0, 2)]:.3f}, unresearched true {still[(1, 1)]:.3f} -> "
          f"{still[(1, 2)]:.3f}, unresearched false {still[(0, 1)]:.3f} -> {still[(0, 2)]:.3f}")


def source_trust(raw_dir: Path) -> pd.DataFrame:
    d = pd.read_csv(gh_fetch("data/survey_data/analysis.csv", raw_dir))
    cb = pd.read_csv(gh_fetch("data/survey_data/options_codebook.csv", raw_dir), sep="\t")
    print("raw shape", d.shape)
    assert len(d) == 2499, len(d)
    assert d["ID"].nunique() == len(d)

    # The "Don't know" reading is the codebook's, not an inference: for each Q1b_N the five option
    # labels are listed in value order, and the fifth is "Don't know". Check all eight.
    labels, cur = {}, None
    for value, label in zip(cb["Value"], cb["Label"]):
        if isinstance(value, str) and value.strip():
            cur = value.strip()
            labels[cur] = []
        labels[cur].append(label.strip().replace("’", "'"))
    for q in TRUST_ITEMS:
        assert labels[q] == ["Trust a great deal", "Trust to some extent",
                             "Do not trust very much", "Do not trust at all",
                             "Don't know"], (q, labels[q])
    print(f"  options_codebook: option {TRUST_DK} of 5 is \"Don't know\" on all "
          f"{len(TRUST_ITEMS)} Q1b items -- an in-range non-response, dropped")

    # IDs are pseudonymous P0001-style codes assigned in row order; carry the number.
    num = d["ID"].str.fullmatch(r"P\d{4}")
    assert num.all(), d.loc[~num, "ID"].head().tolist()
    wide = pd.DataFrame({"id": d["ID"].str[1:].astype(int)})
    assert wide["id"].tolist() == list(range(1, len(d) + 1)), "ID is not row order"
    for src, item in TRUST_ITEMS.items():
        col = pd.to_numeric(d[src], errors="coerce")
        assert col.notna().all(), src
        assert set(col) <= set(range(1, 6)), (src, sorted(set(col)))
        wide[item] = col.astype(int)

    t = wide.melt(id_vars="id", var_name="item", value_name="resp")
    dk = int((t["resp"] == TRUST_DK).sum())
    t = t[t["resp"] != TRUST_DK].copy()
    print(f"  dropped {dk} \"Don't know\" item-responses of {dk + len(t)}; "
          f"{t['id'].nunique()} of {len(d)} respondents retain at least one item")
    assert set(t["resp"]) == {1, 2, 3, 4}, sorted(set(t["resp"]))
    return t.sort_values(["id", "item"]).reset_index(drop=True)


def main() -> None:
    raw_dir = RAW_ROOT / "luettgau_2026"
    emit({"luettgau_2026_political_knowledge": (political_knowledge(raw_dir), range(1, 8)),
          "luettgau_2026_source_trust": (source_trust(raw_dir), range(1, 5))})


if __name__ == "__main__":
    main()
