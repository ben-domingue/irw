##Citizen preferences for their legislative body: paired conjoint of legislature designs, from
##Williams, N. S., Hitefield, A. A., & Kimbrell, K. L. (2026). Citizen preferences for their legislative body.
##Journal of Elections, Public Opinion and Parties (JEPOP; per the deposit title; no article DOI in the deposit).
##Replication data: Harvard Dataverse doi:10.7910/DVN/Y9Q1KU, CC0 1.0. Files read: Legislature_analysis.rds
##(data.frame, loaded with readRDS), Replication_Analysis_JEPOP.R (read as text). The deposit's README and the R
##code header carry the title of a different paper ("From Reinvasion Shock to Realignment?"), a copy-paste slip;
##the analysis code is the legislature conjoint.
##Usage: Rscript williams_2026.R <dir holding Legislature_analysis.rds> <output dir>
##
##449 respondents (US, inferred: Democrat / Republican party identification, US-dollar income bands; the deposit
##names no sample, fielding date or country), 5 contests (task 1-5) of 2 hypothetical legislatures (profile 1/2),
##6 attributes: agenda (3 levels), bipartisanship, checks on the executive, party in control, gender makeup,
##racial makeup (3 levels). choice = Chosen_legis (1 = chosen; exactly one chosen per contest, verified, no
##opt-out). The question wording is NOT in the deposit (outcome question `unknown`).
##Attribute level text is the authors' analysis labels as stored (the deposit ships no questionnaire); the
##displayed wording may be longer ("Party_strength", an unused column, holds "Legislators emphasize economic
##growth" for the agenda levels), so these are labels, not verified displayed text.
##Source quirks: 10 respondents have fewer than 5 contests (1 with 2, 3 with 3, 6 with 4; the other 439 have 5)
##and are kept as they are; contest_no is the task index (recorded, not necessarily the
##order shown). Attribute order, restrictions, level probabilities are not documented (no pair of levels is
##missing: restrictions `unknown`, not `none`).
##Covariates: cov_gender (Gender Man/Woman -> male/female), cov_age (Age, years; values above 100 set NA: the
##source holds an impossible 530), cov_education (Education, answer text), cov_party_id (Party_id_base text:
##Democrat/Republican/Independent), cov_race (Race text), cov_income (Income band text),
##cov_survey_weight (Weight, per respondent; the authors weight all models with it).
##Dropped: derived columns (Gender_num, Age_num, Education_num, Race_num, Age_cut, Education_cut, Partisan_gender,
##Race_dem, Party_strength) and the follow-up strength/identity items (Rep_strength, Dem_strength, Closer_party,
##Cons_ideo, White_identity, Black_identity, whose coding is not documented). The raw caseID (a Qualtrics
##ResponseId) is re-keyed to an integer id.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "Legislature_analysis.rds")))
s[, id := as.integer(factor(caseID, levels = unique(caseID)))]
stopifnot(s[, uniqueN(id)] == 449, s[, .N, .(id, contest_no)][, all(N == 2)],
          s[, sum(Chosen_legis), .(id, contest_no)][, all(V1 == 1)], s[, uniqueN(Weight), id][, all(V1 == 1)])
ch <- function(x) as.character(x)
d <- s[, .(id, task = as.integer(contest_no), profile = as.integer(Profile), choice = as.integer(Chosen_legis),
           attr_agenda = ch(Agenda), attr_bipartisanship = ch(Bipartisanship), attr_checks = ch(Checks),
           attr_party_in_control = ch(`Party in control`), attr_gender_makeup = ch(`Gender makeup`),
           attr_racial_makeup = ch(`Racial makeup`),
           cov_gender = c(Man = "male", Woman = "female")[ch(Gender)],
           cov_age = fifelse(Age > 100, NA_integer_, as.integer(Age)),
           cov_education = ch(Education), cov_party_id = ch(Party_id_base), cov_race = ch(Race),
           cov_income = ch(Income), cov_survey_weight = Weight)]
stopifnot(!anyNA(d[, .(attr_agenda, attr_bipartisanship, attr_checks, attr_party_in_control, attr_gender_makeup, attr_racial_makeup)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "williams_2026_legislature_prefs.csv"))
