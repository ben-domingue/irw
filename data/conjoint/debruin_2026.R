##Crisis x executive-action vignette conjoint (United States, Lucid, July 2022) from
##De Bruin, E., & Jones, C. W. (forthcoming). Public support for undermining executive accountability in
##times of crisis. European Journal of Political Research. (Not yet published when this was built; no DOI.)
##Replication data: Harvard Dataverse doi:10.7910/DVN/E75DHD, CC0 1.0 (released 2026-10-05). File read:
##"De Bruin and Jones EJPR Replication Data.dta" (Dataverse "original format"). "De Bruin and Jones EJPR
##Replication File.do" read as text, not run. Dataverse description: "an original conjoint experiment over
##a large and nationally representative sample of Americans". No questionnaire or article was available,
##so the vignette template and the question wording were not seen.
##Usage: Rscript debruin_2026.R <dir holding the .dta> <output dir>
##
##Each respondent read 5 text vignettes (task = Task_No; one profile per task) about a president
##responding to a situation, and rated the response. Qualtrics stored the displayed text pieces as embedded
##data; the attributes keep those pieces verbatim:
##  attr_situation  = opening (9 situations; the context label is in the .dta as `context`, e.g. "A pandemic";
##                    the situation also fixes `people` and `end`, so those are not separate attributes;
##                    one of the 9, "High traffic and congestion", is the non-crisis "situation" control)
##  attr_party      = party ("Democratic" / "Republican")
##  attr_gender     = genderUpper ("He" / "She"; the vignette refers to the president by pronoun)
##  attr_age        = age ("46-year-old" / "55-year-old" / "70-year-old")
##  attr_election   = election ("in a landslide" / "with a comfortable margin" / "with a thin margin")
##  attr_action     = actionend (10 actions, long form; the short form `action` is also in the data, e.g.
##                    "declare a state of emergency")
##All 9 x 10 x 2 x 2 x 3 x 3 level pairs occur; situations and actions vary across a respondent's tasks
##but can repeat (only 1,056 respondents saw 5 different situations).
##Outcome:
##  rating = rating_numeric, 6-point approval of the president's action, 1 Strongly disapprove, 2 Disapprove,
##           3 Somewhat disapprove, 4 Somewhat approve, 5 Approve, 6 Strongly approve (the .dta's `rating` text;
##           higher = more approval). Wording not seen: paraphrase. approval_dummy (4-6) is derived, dropped.
##Not kept: the follow-up items asked only after task 5 (ThreatCountry/Personal, *Responsible, HowLikely,
##HowEffective, HowConsistentwDem, WhenPermitted; their wording is undocumented), the manipulation-check
##answers (Manipulation1_First/Second, Manipulation4 and the second rating rating1_second for a re-shown
##scenario), and the authors' derived codings (attribute_*, crisis_type, action_type, *_undermined, libNotion,
##authNotion, majNotion, auth_pers, copartisan, Republican/Democrat, *_omit, num_*).
##PII dropped: IPAddress, LocationLatitude/Longitude, Lucid_zip, Lucid_rid, ResponseId, RandomID, dates.
##One Lucid panelist (Lucid_rid) completed twice: only the earlier response is kept, so 4,191 respondents
##(4,192 ResponseIds in the file). Paper N not checked.
##Covariates: cov_age (Age, self-reported years; the top code "90 or older" is NA), cov_gender (the authors' `female` dummy: 1 = female, 0 = male;
##it equals Lucid_gender 2/1), cov_race (Race, text), cov_ideology (PolIdeology, text; "Not sure" kept),
##cov_political_interest (PolEngagement), cov_satisfied_democracy, cov_democracy_good, cov_strong_leader_good,
##cov_experts_good (answer text), cov_<x>_essential (the 10 "essential characteristic of democracy" items,
##1-10 as stored), cov_manners_vs_curiosity, cov_obedience_vs_self_reliance, cov_independence_vs_respect,
##cov_well_behaved_vs_considerate (child-rearing items, answer text), cov_attention1_answer (Attention1
##answer text as stored), cov_failed_manipulation1_first / _second / cov_failed_manipulation4 (the
##authors' 0/1 flags), cov_duration_sec (Durationinseconds, whole survey). Lucid profile variables keep the
##panel's codes (no labels in the deposit): cov_hhi_code, cov_ethnicity_code, cov_hispanic_code,
##cov_education_code, cov_party_id_code (the authors' code treats 1, 2, 3, 6 as Democrats and 5, 8, 9, 10 as
##Republicans), cov_region_code. No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(zap_labels(read_dta(file.path(raw, "De Bruin and Jones EJPR Replication Data.dta"))))
x[, start := as.POSIXct(StartDate, format = "%m/%d/%y %H:%M", tz = "UTC")]
stopifnot(!anyNA(x$start), x[, .N, ResponseId][, all(N == 5)])
first <- unique(x[, .(ResponseId, Lucid_rid, start)])[order(start)][, .SD[1], Lucid_rid]
x <- x[ResponseId %in% first$ResponseId]
ids <- unique(x$ResponseId)
lv <- c("Strongly disapprove", "Disapprove", "Somewhat disapprove", "Somewhat approve", "Approve", "Strongly approve")
stopifnot(x[, all(rating == lv[rating_numeric])], x[, all(female == (Lucid_gender == 2))])
txt <- function(v) { v <- as.character(v); v[v == ""] <- NA; v }
d <- x[, .(id = match(ResponseId, ids), task = as.integer(Task_No), profile = 1L, rating = as.integer(rating_numeric),
  attr_situation = opening, attr_party = party, attr_gender = genderUpper, attr_age = age, attr_election = election,
  attr_action = actionend,
  cov_age = suppressWarnings(as.integer(Age)), cov_gender = ifelse(female == 1, "female", "male"), cov_race = txt(Race),
  cov_ideology = txt(PolIdeology), cov_political_interest = txt(PolEngagement),
  cov_satisfied_democracy = txt(SatisfiedwDemocracy), cov_democracy_good = txt(DemocracyGood),
  cov_strong_leader_good = txt(StrongLeaderGood), cov_experts_good = txt(ExpertsGood),
  cov_elections_essential = ElectionsEssential, cov_majority_rule_essential = MajorityRuleEssential,
  cov_womens_rights_essential = WomensRightsEssential, cov_violent_order_essential = ViolentOrderEssential,
  cov_govt_limit_freedoms_essential = GovtCanLimitFreedomsEssential, cov_civil_rights_essential = CivilRightsEssential,
  cov_minority_accepts_essential = MinorityAcceptsMajRuleEssential, cov_ruling_party_essential = RulingPartyEssential,
  cov_majority_law_change_essential = MajorityLawChangeEssential, cov_term_limits_essential = TermLimitsEssential,
  cov_manners_vs_curiosity = txt(MannersvCuriosity), cov_obedience_vs_self_reliance = txt(ObediencevSelfReliance),
  cov_independence_vs_respect = txt(IndepvRespectforElders), cov_well_behaved_vs_considerate = txt(WellBehavedvConsiderate),
  cov_attention1_answer = txt(Attention1),
  cov_failed_manipulation1_first = as.integer(FailedManipulation1_First),
  cov_failed_manipulation1_second = as.integer(FailedManipulation1_Second),
  cov_failed_manipulation4 = as.integer(FailedManipulation4),
  cov_duration_sec = as.integer(Durationinseconds),
  cov_hhi_code = as.integer(Lucid_hhi), cov_ethnicity_code = as.integer(Lucid_ethnicity),
  cov_hispanic_code = as.integer(Ludic_hispanic), cov_education_code = as.integer(Lucid_eduation),
  cov_party_id_code = as.integer(Lucid_political_party), cov_region_code = as.integer(Lucid_region))]
stopifnot(!anyNA(d[, .(rating, attr_situation, attr_party, attr_gender, attr_age, attr_election, attr_action)]),
          d[, .N, .(id, task)][, all(N == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "debruin_2026_crisis_accountability.csv"))
cat(nrow(d), "rows,", uniqueN(d$id), "respondents\n")
