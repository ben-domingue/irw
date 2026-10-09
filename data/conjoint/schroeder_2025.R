##Vice-presidential nominee conjoint (US) from
##Schroeder, E., & Campos, A. (2025). The influence of candidate traits on vice presidential
##nominee preference. Politics, Groups, and Identities.
##https://doi.org/10.1080/21565503.2025.2518532
##Replication data: Harvard Dataverse doi:10.7910/DVN/VQPVWG, CC0 1.0, no restricted files.
##File read: vpdata.csv (original format of vpdata.tab; a long Qualtrics export, one row per
##respondent x profile). Read as text, not run: "Replication Script - Schroeder & Campos
##2025.R". The deposit has no codebook or questionnaire and the article was not read, so the
##outcome wording is a PARAPHRASE and most covariates keep their codes.
##Usage: Rscript schroeder_2025.R <dir holding vpdata.csv> <output dir>
##
##599 US respondents (Prolific; Prolific IDs and Qualtrics ResponseIds in the file are
##dropped and respondents re-keyed 1-599 in file order). Up to 5 tasks of 2 hypothetical
##vice-presidential candidates (candidate_choices "traits<t><a|b>": task t, profile a = 1,
##b = 2), 5 attributes as text in the file: race (Asian/Black/Hispanic/White), gender
##(Female/Male), ideology (Conservative/Liberal/Moderate), region (Midwest/Northeast/South/
##West), experience (Governor/Member of House of Representatives/None/Senator).
##583 respondents have all 5 tasks; 16 lack 1-3 tasks (rows absent in the source).
##TASK 2 IS A FIXED PAIR: every respondent saw the same two profiles (1: Asian, Female,
##Conservative, Northeast, None; 2: Black, Male, Moderate, South, Member of House of
##Representatives), flagged trial_fixed_pair = 1. Tasks 1, 3-5 show all 384 combinations at
##near-equal rates. The fixed pair makes the pooled level shares unequal (level weights
##OBSERVED); the authors' code pools all 5 tasks.
##trial_party = the source column `party` (Democratic/Republican), constant within respondent:
##self-identified Democrats (pid3 = 1) all have Democratic, Republicans (pid3 = 2) Republican,
##others either. Presumably the party whose ticket the VP joins; not documented.
##Outcome: choice (`outcome`, 0/1): which of the two the respondent prefers as the vice-
##presidential nominee (paraphrase from the title; the authors model outcome ~ attributes with
##cjoint::amce). Exactly one profile chosen per task; no opt-out.
##Covariates (codes unless stated; the only labels are in the authors' script):
##  cov_age (years, 18+); cov_gender_code (1/2/3; the authors' script is inconsistent about
##  which code is female, so no text); cov_race_code (multi-select string; script: 1 White,
##  2 Black, 3 Latinx, 4 American Indian/Alaska Native, 5 Asian, 6 Native Hawaiian/Pacific
##  Islander); cov_party_id_code (pid3; script: 1 Democrat, 2 Republican, 3 Independent,
##  4-5 set missing); cov_dem_strength_code, cov_rep_strength_code, cov_ind_lean_code,
##  cov_ideology_code, cov_education_code, cov_income_code; feeling thermometers 0-100
##  (cov_therm_republicans, _democrats, _black_people, _feminists: rep_therm, dem_therm,
##  black_therm, fem_therm); cov_sexism_1..5 (1-5; script labels "Women at Home", "Special
##  Favors", "Women Complain", "Protected by Men", "Men Better for Politics");
##  cov_racial_resentment_1..4 (1-5; the script reverses items 2 and 3).
##Dropped: ResponseId, Prolific_ID (platform IDs), consent, page timers, the per-task
##questions Q41/likelihood_of_vote, Q42/Q20, Q22/Q23, Q50/Q51, Q54/Q55 (asked after each task
##about the task as a whole; wording and scales not in the deposit), attention_check_2
##(multi-select, correct answer not documented), group-identity, religion and born-again
##items (no labels). No survey weight.
##N: 599 respondents in the deposit; article N not checked.
##Spot check (article not accessible, no published number compared): OLS of choice on the
##attributes, SEs clustered by id: experience None -0.177 (0.020) vs House member, Black
##+0.108 (0.019) vs White, Male -0.041 (0.014), Conservative -0.130 vs Moderate.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "vpdata.csv"), encoding = "UTF-8")
stopifnot(uniqueN(s$ResponseId) == 599, uniqueN(s$Prolific_ID) == 599)
s[, id := match(ResponseId, unique(ResponseId))]
stopifnot(all(grepl("^traits[1-5][ab]$", s$candidate_choices)))
s[, task := as.integer(substr(candidate_choices, 7, 7))][, profile := fifelse(substr(candidate_choices, 8, 8) == "a", 1L, 2L)]
num <- function(x) suppressWarnings(as.integer(x))
d <- s[, .(id, task, profile, choice = as.integer(outcome),
           attr_race = candidate_race, attr_gender = candidate_gender, attr_ideology = candidate_ideology,
           attr_region = candidate_region, attr_experience = candidate_experience,
           trial_party = party, trial_fixed_pair = as.integer(task == 2),
           cov_age = num(age), cov_gender_code = num(gender), cov_race_code = race, cov_party_id_code = num(pid3),
           cov_dem_strength_code = num(dem_strength), cov_rep_strength_code = num(rep_strength), cov_ind_lean_code = num(ind_lean),
           cov_ideology_code = num(ideology), cov_education_code = num(education), cov_income_code = num(income),
           cov_therm_republicans = num(rep_therm), cov_therm_democrats = num(dem_therm), cov_therm_black_people = num(black_therm),
           cov_therm_feminists = num(fem_therm),
           cov_sexism_1 = num(sexism_1), cov_sexism_2 = num(sexism_2), cov_sexism_3 = num(sexism_3), cov_sexism_4 = num(sexism_4),
           cov_sexism_5 = num(sexism_5), cov_racial_resentment_1 = num(racial_resentment_1),
           cov_racial_resentment_2 = num(racial_resentment_2), cov_racial_resentment_3 = num(racial_resentment_3),
           cov_racial_resentment_4 = num(racial_resentment_4))]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)], all(d$cov_age >= 18))
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
fx <- d[task == 2, uniqueN(paste(attr_race, attr_gender, attr_ideology, attr_region, attr_experience)), profile]
stopifnot(all(fx$V1 == 1))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "schroeder_2025_vp_nominee.csv"))
