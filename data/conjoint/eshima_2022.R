##House of Councillors candidate conjoint (Japan) from
##Eshima, S., & Smith, D. M. (2022). Just a number? Voter evaluations of age in candidate-choice
##experiments. The Journal of Politics, 84(3), 1856-1861. https://doi.org/10.1086/719005
##Replication data: Harvard Dataverse doi:10.7910/DVN/EWDCQX, CC0 1.0, no restricted files.
##File read (from replication_material.zip): data/conjoint/processed_hoc_data.rds (the authors'
##processed tibble; the raw .dta it was built from is not deposited). README.md and
##code/conjoint.R, code/conjoint_functions.R read as text. The article and its appendix are
##paywalled and were not read, so design facts below come from the data and code only.
##Usage: Rscript eshima_2022.R <dir holding processed_hoc_data.rds> <output dir>
##
##2,018 Japanese respondents (a House of Councillors candidate experiment; the 2016 upper-house
##turnout item suggests fielding before or around the 2019 upper-house election, not
##verified), 20 rows each = 10 pairs of hypothetical candidates, 7 attributes.
##The file has NO task or profile column and identifies respondents by Qualtrics response ID
##(re-keyed here to 1..2,018 in file order). Rows of each respondent are contiguous; consecutive
##row pairs are taken as tasks (in all 20,180 pairs exactly one profile is chosen), so task and
##profile are INFERRED from row order; whether that order is the order shown is not documented.
##  choice: chooseprofile, forced choice between two candidates (exactly one chosen per pair).
##    Question wording not in the deposit (unknown).
##Attribute text: the authors' English factor labels, used as is; respondents saw Japanese
##(not deposited). incumbency (Newcomer / Former, 1 term / Former, 2+ terms / Current, 1 term /
##Current, 2+ terms), gender, education (High school / Regional university / University of
##Tokyo / Graduate school), local (Inside/Outside prefecture), occupation (Company employee /
##National bureaucrat / Newspaper reporter / Self-Defense Forces / Celebrity/talent), politics
##(No background / Prefectural assembly / MP secretary / Dynastic politician), age (42, 47, 55,
##69, 70). Levels are roughly uniform and every incumbency x age combination occurs;
##randomization restrictions and attribute order are not documented.
##trial_treat_group = the authors' treatment_group (T1-T4; one per respondent). The authors
##estimate marginal means by it; what the four arms were is not in the deposit (unknown).
##Covariates (authors' text labels): cov_age_group (respondent age in 6 bands), cov_age_leaders
##(5-point agree/disagree item named age_leaders; wording unknown), cov_past_turnout,
##cov_voted_hoc_2016. Dropped: Qualtrics response ID, the authors' collapsed age_group and
##age_leaders_collapsed. No survey weight.
##N: 2,018 in the deposit; the article was not checked (paywalled). Spot check: marginal means
##of choice by candidate age within respondent age band 18-29 (.61/.57/.55/.40/.36 for 42/47/55/
##69/70) equal the authors' stored results in data/conjoint/mm_subgroup_A.rds.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "processed_hoc_data.rds")))
rl <- rle(s$response_id)
stopifnot(all(rl$lengths == 20), !anyDuplicated(rl$values), nrow(s) == 40360)
s[, id := rep(seq_along(rl$values), rl$lengths)][, r := seq_len(.N), id]
s[, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L]
d <- s[, .(id, task = as.integer(task), profile = as.integer(profile), choice = as.integer(chooseprofile),
           attr_incumbency = as.character(c_incumbencyid), attr_gender = as.character(c_genderid),
           attr_education = as.character(c_educationid), attr_local = as.character(c_localid),
           attr_occupation = as.character(c_occupationid), attr_politics = as.character(c_politicsid),
           attr_age = as.character(c_ageid), trial_treat_group = as.character(treat_group_chr),
           cov_age_group = as.character(age_group5), cov_age_leaders = as.character(age_leaders),
           cov_past_turnout = as.character(past_turnout_habits), cov_voted_hoc_2016 = as.character(HoC_Voted_2016))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, uniqueN(trial_treat_group), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "eshima_2022_age_candidates.csv"))
