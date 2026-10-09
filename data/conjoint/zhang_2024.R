##Volunteer-project choice conjoint (China) from
##Zhang, R. (2024). Volunteer participation preferences [Data set]. Harvard Dataverse.
##No article is linked to the deposit and none was found; the deposit is the only source.
##Replication data: Harvard Dataverse doi:10.7910/DVN/3RGWG8, CC0 1.0. File read:
##DATA.dta (Dataverse "original format" download of DATA.tab; Stata value labels).
##No codebook, questionnaire or analysis code ships.
##Usage: Rscript zhang_2024.R <dir holding DATA.dta> <output dir>
##
##658 respondents, 6 paired tasks each (12 rows per respondent), 8 attributes of a
##hypothetical volunteer project. `task6` is the task within respondent (the source `task`
##is a running counter across the file) and `concept` the profile (1/2); both recorded.
##Outcome: choice = `response` (0/1); exactly one profile chosen in every one of the 3,948
##tasks, so no opt-out was offered (or none was recorded). Question wording is not in the
##deposit.
##Attribute text: the Stata value labels, which are the author's English labels
##(e.g. "With Communist Party branch", "Providing financial subsidies", six slogan levels).
##The covariates are stored in Chinese (occupation, health, experience), so the survey was
##fielded in Chinese; the Chinese attribute wording is not in the deposit.
##Randomization restrictions, level weights and attribute order are not documented; level
##shares are near-equal and every pair of levels occurs.
##Respondent ID: the source `id` is an 11-character survey-platform token; it is dropped and
##respondents are re-keyed by the source's sequential `id2` (one-to-one with `id`).
##Covariates (no codebook, so coded ones keep codes): cov_gender_code (gender, 0/1, mapping
##undocumented), cov_age (age, years), cov_education_code (0-5), cov_politic_code (0-3,
##political status, undocumented), cov_marriage_code, cov_income_code, cov_ses_code
##(socioeconomicstatus), cov_psm1-5 and cov_trust1-3 (item scores 1-7, wording not in the
##deposit; psm presumably public service motivation), cov_aga (1-7, undocumented), and the
##Chinese answer text of occupation, health (self-rated), experience (是/否, presumably prior
##volunteering) and willingness (asked only of those without experience; blank -> NA).
##Dropped: the author's derived means and dummies (aga_mean, aga_2, psm, psm_mean, psm_2,
##trust, trust_mean, trust_2, politic_2, income_2, socioeconomicstatus_3, occupation_4,
##Volunteerexperience, marriage_2, education_3, age_2, health_2) and the running `task`.
##No article, so no count check against a paper.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "DATA.dta"))
stopifnot(nrow(k) == 7896, length(unique(k$id)) == 658,
          nrow(unique(data.frame(k$id, k$id2))) == 658, length(unique(k$id2)) == 658)
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
d <- data.table(id = as.integer(k$id2), task = as.integer(k$task6), profile = as.integer(k$concept),
                choice = as.integer(k$response),
                attr_time = lab("Time"), attr_training = lab("Training"), attr_compensation = lab("Compensation"),
                attr_service_mode = lab("Servicemode"), attr_party_branch = lab("Politicalconnection"),
                attr_objective = lab("Projectobjective"), attr_disclosure = lab("Disclosure"), attr_slogan = lab("Slogan"))
stopifnot(!anyNA(d), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
          all(d$task %in% 1:6), all(d$profile %in% 1:2))
num <- c(cov_gender_code = "gender", cov_age = "age", cov_education_code = "education", cov_politic_code = "politic",
         cov_marriage_code = "marriage", cov_income_code = "income", cov_ses_code = "socioeconomicstatus",
         cov_psm1 = "psm1", cov_psm2 = "psm2", cov_psm3 = "psm3", cov_psm4 = "psm4", cov_psm5 = "psm5",
         cov_trust1 = "trust1", cov_trust2 = "trust2", cov_trust3 = "trust3", cov_aga = "aga")
for (n in names(num)) d[, (n) := as.integer(zap_labels(k[[num[[n]]]]))]
txt <- c(cov_occupation = "occupation", cov_health = "health", cov_experience = "experience", cov_willingness = "willingness")
for (n in names(txt)) { x <- trimws(as.character(k[[txt[[n]]]])); x[x == ""] <- NA; d[, (n) := x] }
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhang_2024_volunteer_projects.csv"))
