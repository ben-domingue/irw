##Immigrant-admission conjoint (Study 2) from
##Aviña, M. M. (2026). Perceived economic contributions increase positivity toward
##undocumented immigrants. Public Opinion Quarterly, 90(3), 591-629.
##https://doi.org/10.1093/poq/nfag012 (online 2026-04-04; Dataverse/Aviña et al. call it Aviña 2024)
##Replication data: Harvard Dataverse doi:10.7910/DVN/M4ZJTV (v3), CC0 1.0. Files read:
##study2.rds (conjoint, long), study1.rds (only to confirm the Study 1 arm coding),
##study2_codebook.xlsx (attribute names and levels), README.txt; code.R read as text, not run.
##Usage: Rscript avina_2026.R <dir holding study2.rds and study1.rds> <output dir>
##
##1,999 US adults (24-character hex respondent IDs of the Prolific type; re-keyed to
##integers), one survey in which Study 1 (an information experiment) came first and the
##Study 2 conjoint followed. Each respondent saw 5 pairs of hypothetical immigrants
##(choice_no = task, immigrant_no = profile), 5 attributes. The article is paywalled and
##the deposit has no questionnaire, so the exact question wording was NOT seen: the
##outcome is the codebook's "Immigrant selected (TRUE / FALSE)", a forced choice (every
##pair has exactly one selected profile; no opt-out). choice = selected.
##Attribute names follow the codebook ("Immigration status", "Country of origin",
##"Education level", "Current employment", "Total taxes paid in 2021"); levels are the
##factor labels in the file, which match the codebook and presumably the display text
##(including "Illegal alien"), but the display text could not be checked. Attribute order
##is not recorded. Randomization was NOT uniform: "Illegal alien" is about half of all
##profiles (9,892 of 19,990) and 2,430 of 9,995 pairs show two "Illegal alien" profiles;
##the codebook's bi_status marks pairs where both immigrants share a status.
##Kept: cov_survey_weight (weight), trial_study1_arm (Study 1 treatment the respondent
##  had just received: Control / Fact-check / Narratives, from immigration_t 0/1/2 and
##  bi_treatment; respondent-level, constant across tasks), cov_party (bi_pid and
##  independents combined: Democrats / Republicans / Independents; the split of leaners is
##  not documented), cov_race (White / Nonwhite), cov_nativity (US Native / Immigrant).
##Dropped: bi_educ, bi_income, bi_ideo (authors' high/low splits with the middle set
##  missing), bi_immigration (derived from Study 1 outcomes), bi_status (derived), the
##  platform IDs. The deposit has no finer respondent covariates.
##Count: 1,999 respondents x 5 tasks x 2 profiles = 19,990 rows, as in the deposit. The
##article's N could not be read (paywall; abstract gives none).
##Spot-check (descriptive only; no paper number was readable): weighted selection rate by
##  status is 0.61 naturalized citizen, 0.55 green card holder, 0.42 "Illegal alien".
suppressMessages(library(data.table))
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "study2.rds")))
s1 <- as.data.table(readRDS(file.path(raw, "study1.rds")))
stopifnot(s[, .N, id][, all(N == 10)], uniqueN(s$id) == 1999, setequal(s$id, s1$id))
arm <- s1[, .(id, trial_study1_arm = c("Control", "Fact-check", "Narratives")[as.integer(as.character(immigration_t)) + 1L])]
chk <- merge(unique(s[, .(id, bi_treatment)]), arm, by = "id")
stopifnot(chk[, all(ifelse(is.na(bi_treatment), "Control", bi_treatment) == trial_study1_arm)])
ids <- data.table(id = sort(unique(s$id)))[, nid := seq_len(.N)]
s <- merge(s, ids, by = "id")
s <- merge(s, arm, by = "id")
d <- s[, .(id = nid, task = as.integer(choice_no), profile = as.integer(immigrant_no), choice = as.integer(selected),
           attr_immigration_status = as.character(status), attr_country_of_origin = as.character(country),
           attr_education_level = as.character(skill), attr_current_employment = as.character(job),
           attr_total_taxes_paid_2021 = as.character(taxes), trial_study1_arm,
           cov_survey_weight = weight, cov_party = fcoalesce(bi_pid, independents), cov_race = bi_race, cov_nativity = bi_immstat)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "avina_2026_immigrant_admission.csv"))
