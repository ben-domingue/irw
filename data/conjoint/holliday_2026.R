##Nationalized-policy candidate conjoints (US, Lucid) from
##Holliday, D. E., & Rudkin, A. (2026). DC on my mind: Voter evaluations of nationalized
##policy positions in state and local elections. The Journal of Politics.
##https://doi.org/10.1086/741831
##Replication data: Harvard Dataverse doi:10.7910/DVN/HKVNTU, CC0 1.0. Files read, from
##jop_reproduction.zip: data_inputs/survey/intermediate/merged_weighted_data.rds (the
##authors' cleaned, weighted conjoint rows), data_inputs/survey/raw/policies.csv and
##policies_local.csv (the position texts); the cleaning scripts (cleaning/*.R), the online
##appendix, and the question-text header row of each raw Qualtrics export were read as text.
##PII: the raw Qualtrics exports in the zip (data_inputs/survey/raw/exported_wave_*.csv) carry
##IP addresses, latitude/longitude and Lucid respondent ids; this script never reads them.
##Usage: Rscript holliday_2026.R <dir holding jop_reproduction/> <output dir>
##
##Design. Each task showed two candidates (Candidate A / B), each with positions on 4
##policies drawn from a pool; both candidates were described on the same 4 policies, and
##each position was the affirmative or the negated text, e.g. "Substantially reduce the size
##of the U.S. military (federal government)" / "Not substantially reduce ...". The 4 rows
##are stored as attr_<policy> ("(not shown)" = policy not in that task); which row each policy took
##is in the raw exports only, so no attrpos_. Pool: 10 national policies plus 10 state
##policies (state tables) or 9 municipal policies (municipal table). 10 tasks per
##respondent: tasks 1-5 "Given this choice, which federal House of Representatives
##candidate would you prefer?", tasks 6-10 the same for a "state assembly" (state tables)
##or "city council" (municipal table) candidate -> trial_office. Forced choice, exactly one
##selected per task, no opt-out. Task numbers follow the Qualtrics question order; whether
##the two office blocks were ever shown in another order is not documented.
##THREE tables, one per fielding/design (the authors analyse these cells separately):
##  holliday_2026_policy_state_2021: 2021 pilot wave, House vs state assembly, no party
##    labels (1,377 respondents).
##  holliday_2026_policy_state_2022: 2022 wave, House vs state assembly, every candidate
##    also shown a party label (attr_party: Democrat / Republican) (1,537 respondents).
##  holliday_2026_policy_municipal: 2022 wave, House vs city council; party labels shown to
##    a random half of respondents (trial_show_party 1/0; attr_party "(not shown)" when not shown)
##    (3,027 respondents).
##The appendix-10 extra wave (May 2025, a different provider, 8 tasks, assistance
##conditions) is a separate, appendix-only experiment and is NOT built here.
##The authors dropped speeders and attention-check failures before this file (completion.R);
##counts above are after their cleaning. The article's N was not checked.
##Check: agreement on military size (candidate position = respondent's baseline), weighted
##OLS on the 2021 table: 0.292, N = 4,934 profiles, as in the deposit's
##figures/saved_objects/data_figure_2_amce.csv (0.2923, N 4,934).
##Covariates: cov_survey_weight (the authors' raked weight, Nationscape targets);
##cov_party_id (the authors' pid3, cleaning/scripts/weights.R: Democrat / Republican from P1,
##independents who lean ("Closer to the Democratic/Republican Party", P1.I) folded into the
##party, P1.I "Neither" = Independent); cov_age_group (the authors' bands from weights.R:
##18-23, 24-29, 30-39, 40-49, 50-59, 60-69, 70+); cov_gender ("male"/"female", the authors'
##Male/Female from weights.R, Lucid gender 1 = Male, 2 = Female, lowercased); cov_education
##(the authors' text from weights.R, which COLLAPSES Lucid's education codes: 1 and -3105 No
##high school diploma, 3-4 Some college, 7-8 Graduate degree; Lucid's own labels are not in
##the deposit); cov_race, cov_hispanic, cov_region, cov_household_income (text as stored),
##and cov_baseline_<policy>: the respondent's own
##answer on that policy asked separately (1 = agrees with the affirmative text, 0 = with the
##negated text), which the authors use to code candidate-respondent agreement. Lucid's
##unlabelled numeric codes (hhi, ethnicity, political_party), the P1 party items and the
##weighting cells are dropped. ResponseId (Qualtrics) re-keyed to integers per table.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
J <- file.path(raw, "jop_reproduction", "data_inputs", "survey")
s <- as.data.table(readRDS(file.path(J, "intermediate", "merged_weighted_data.rds")))
ps <- fread(file.path(J, "raw", "policies.csv")); pm <- fread(file.path(J, "raw", "policies_local.csv"), encoding = "UTF-8")
setnames(pm, 1, "label")
stopifnot(nrow(s) == 117500, s[, .N, .(ResponseId, conjoint_id, side)][, all(N == 1)],
          s[, sum(selected), .(ResponseId, conjoint_id)][, all(V1 == 1)], all(s$side %in% c("a", "b")))
build <- function(x, pol, office, name) {
  x <- copy(x)
  key <- sort(unique(x$ResponseId))
  d <- x[, .(id = match(ResponseId, key), task = as.integer(conjoint_id), profile = match(side, c("a", "b")),
             choice = as.integer(selected))]
  n_shown <- integer(nrow(x))
  for (i in seq_len(nrow(pol))) {
    v <- pol$label[i]; val <- x[[v]]
    stopifnot(all(val %in% c(0, 1, NA)))
    d[, paste0("attr_", v) := fifelse(is.na(val), "(not shown)", fifelse(val == 1, pol$pos_level[i], pol$neg_level[i]))]
    n_shown <- n_shown + !is.na(val)
  }
  stopifnot(all(n_shown == 4))
  if (any(!is.na(x$party_text))) d[, attr_party := fifelse(is.na(x$party_text), "(not shown)", x$party_text)]
  d[, trial_office := fifelse(x$conjoint_id <= 5, "federal House of Representatives", office)]
  if (uniqueN(x$showParty) > 1) d[, trial_show_party := as.integer(x$showParty)]
  d[, `:=`(cov_survey_weight = x$weights, cov_party_id = as.character(x$pid3), cov_age_group = as.character(x$age),
           cov_gender = tolower(as.character(x$gender)), cov_race = as.character(x$race), cov_hispanic = as.character(x$hispanic),
           cov_education = as.character(x$education), cov_region = as.character(x$region),
           cov_household_income = as.character(x$household_income))]
  stopifnot(all(d$cov_gender %in% c("female", "male")))
  for (v in pol$label) d[, paste0("cov_baseline_", v) := as.integer(x[[paste0("policy_", v)]])]
  stopifnot(d[, uniqueN(cov_survey_weight), id][, all(V1 == 1)], !anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(name, ".csv")))
  cat(name, nrow(d), uniqueN(d$id), "\n")
}
w1 <- s[wave == 1 & comparison == "state"]; stopifnot(all(w1$showParty == 0), all(is.na(w1$party_text)))
w2s <- s[wave == 2 & comparison == "state"]; stopifnot(all(w2s$showParty == 1), !anyNA(w2s$party_text))
w2m <- s[wave == 2 & comparison == "municipal"]
stopifnot(w2m[, all(is.na(party_text) == (showParty == 0))])
build(w1, ps, "state assembly", "holliday_2026_policy_state_2021")
build(w2s, ps, "state assembly", "holliday_2026_policy_state_2022")
build(w2m, pm, "city council", "holliday_2026_policy_municipal")
