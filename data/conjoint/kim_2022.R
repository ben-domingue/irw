##Immigrant-admission conjoint (South Korea, COVID-19) from
##Kim, S. E., Shin, A. J., & Yang, Y. (2022). The usual suspects?: Attitudes towards
##immigration during the COVID-19 pandemic. Journal of Asian Public Policy, 17(2), 272-289.
##https://doi.org/10.1080/17516234.2022.2046686
##Replication data: Harvard Dataverse doi:10.7910/DVN/LQ38EP, CC0 1.0, no restricted files.
##File read: dat_conjoint_covid.rds (one data frame). The deposit has no codebook or
##questionnaire; the authors' analysis_conjoint_covid.R (read as text) is the only source for
##how columns are used. The article itself was not available (paywalled), so question wording,
##survey firm and field dates are NOT known here.
##Usage: Rscript kim_2022.R <raw dir> <output dir>
##
##1,687 South Korean respondents (the article abstract: "nearly 1,700 respondents in South
##Korea"), 5 tasks of 2 hypothetical immigrant profiles, 8 attributes. Outcomes:
##  choice  = `selected`, exactly one of the two profiles per task (the authors model it as
##            "probability of supporting admission", Figure 1 of their script). Forced choice.
##  rating_entry = `restriction`, a per-profile judgement stored in Korean: 입국 금지 (entry
##            banned) = 1, 입국 후 14일 격리 의무화 조건부 입국 허용 (entry allowed on condition of a
##            mandatory 14-day quarantine after entry) = 2, 입국 허용 (entry allowed) = 3.
##            The numeric order is ours (higher = more open), stated in design_outcomes; the
##            two profiles of a task differ on it in 2,195 of 8,435 tasks.
##Task = taskNum (recorded). PROFILE POSITION IS NOT RECORDED: the two rows of a task appear
##in an arbitrary order in the file (tasks are shuffled within respondent), so `profile` is
##the file row order within the task and carries no left/right meaning (profile_source
##unknown). Do not use it for position analyses.
##Attribute text: only the authors' English labels ship (respondents saw Korean, not
##deposited); used exactly as stored, including the authors' typos "High volumne of trade" and
##"Fluent communitation skills". Attribute order and randomization restrictions are not
##documented; every pair of levels occurs and level shares are near-equal (occupation 1/7
##each, others 1/2 or 1/3). Spot check: choice share 0.63 for vaccinated vs 0.37 unvaccinated,
##0.61 / 0.51 / 0.38 for 5 / 50 / 500 COVID cases per 10,000 (direction as in the abstract;
##the article's estimates were not available to compare).
##Covariates: cov_gender_code (the authors' `female` indicator, 1 = female; kept as a code
##because no codebook says what 0 covers), cov_college, cov_grad (the authors' 0/1 education
##indicators, kept as coded); cov_age_group (Age_Group text; blank for 3 respondents ->
##NA); cov_duration_sec (Qualtrics "Duration (in seconds)", whole survey).
##Dropped: Qualtrics ResponseId (re-keyed to integers in sorted ResponseId order),
##same_answer (the authors' straight-lining flag, derived). No survey weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "dat_conjoint_covid.rds")))
stopifnot(uniqueN(s$ResponseId) == 1687, s[, .N, ResponseId][, all(N == 10)],
          s[, .(.N, sum(selected)), .(ResponseId, taskNum)][, all(N == 2 & V2 == 1)])
s[, rown := .I]
setorder(s, ResponseId, taskNum, rown)
s[, profile := seq_len(.N), .(ResponseId, taskNum)]
rk <- c("입국 금지" = 1L, "입국 후 14일 격리 의무화 조건부 입국 허용" = 2L, "입국 허용" = 3L)
stopifnot(all(as.character(s$restriction) %in% names(rk)))
d <- s[, .(id = match(ResponseId, sort(unique(ResponseId))), task = as.integer(taskNum), profile = as.integer(profile),
           choice = as.integer(selected), rating_entry = unname(rk[as.character(restriction)]),
           attr_regime = as.character(regime_eng), attr_trade = as.character(trade_eng),
           attr_residence = as.character(residence_eng), attr_covid_cases = as.character(covid.cases_eng),
           attr_vaccine = as.character(vaccine_eng), attr_korean = as.character(korean_eng),
           attr_education = as.character(education_eng), attr_occupation = as.character(occupation_eng),
           cov_gender_code = as.integer(female), cov_college = as.integer(college), cov_grad = as.integer(grad),
           cov_age_group = fifelse(Age_Group == "", NA_character_, Age_Group),
           cov_duration_sec = as.numeric(Duration__in_seconds_))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kim_2022_immigration_covid.csv"))
