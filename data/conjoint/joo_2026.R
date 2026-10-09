##Candidate conjoint (Study 2) from
##Joo, M., Lemi, D. C., Merolla, J. L., & Sellers, A. H. (2026). Only for some women: Experimental
##evidence on descriptive representation and political engagement. Political Behavior.
##https://doi.org/10.1007/s11109-026-10139-6 (open access, CC BY 4.0)
##Replication data: Harvard Dataverse doi:10.7910/DVN/HKRUXU, CC0 1.0, no restricted files, no terms.
##File read: "Study 2.tab" (Dataverse original-format download = Stata .dta, one row per respondent x
##task x candidate). "Study 2 code.do" read as text. Study 1 (one vignette per respondent, 6 arms:
##representative gender x policy stance) is not built: only arm dummies are deposited, not the vignette
##text. NOTE: the public "Study 1.tab" holds zip codes, street numbers and GPS coordinates (not read here).
##Usage: Rscript joo_2026.R <dir holding study2.dta> <output dir>
##
##Qualtrics online panels, May 11-22 2017, n = 1,051 (article), ~1/3 each African American, Latinx and
##white, ~1/2 women. Respondents imagined a fictional district whose congressional representative retires
##and read 6 pairs of potential candidates (article). Six attributes, levels = the .dta value labels:
##race (White, Black, Hispanic, Asian American), gender, policy priority (5), party, ideology
##(Conservative, Moderate, Liberal) and parental status. The article lists five attributes and does not
##mention ideology, but ideology varies by profile in the file and the authors' models condition on it.
##"Complete randomization using the Conjoint Survey Design Tool" (article); attribute order not described.
##task = `task`, profile = `candidate`, both recorded.
##Outcomes (dv names = .dta variable labels):
##  choice          = dv1 "Vote Choice": select a candidate to vote for, with "I would not vote" offered
##                    after each task (article). 1,056 tasks (176 respondents, all 6 of their tasks) have
##                    no candidate chosen = opt-out.
##  choice_concerns = dv5 "Candidate addresses concerns": one candidate picked in every answered task.
##  rating_contact  = dv2 "Likelihood of Contact", rating_donate = dv3 "Likelihood of Donating",
##  rating_trust    = dv4 "Trustworthiness": per candidate, 1-4, stored raw. Wording, anchors and direction
##                    are not in the deposit or the article text read; the authors' derived `trust` = 5 - dv4
##                    (dropped) suggests 1 = most trustworthy for dv4.
##Dropped: 96 rows with no outcome at all; the authors' derived variables (voted/novote, same_party, trust,
##dummies, _est_*), Qualtrics ResponseId (v6), raw q* columns.
##Covariates: cov_age (age, years), cov_gender (women: 1 = female, 0 = male; .dta value labels Men/Women),
##cov_ideology (resp_ideology value-label text, 7-point; NA = missing or "Haven't thought much"),
##cov_nativity (value-label text), cov_black / cov_latino / cov_white, cov_democrat / cov_republican /
##cov_independent (0/1 dummies as deposited), cov_income_code and cov_education_code (income, ed_attain:
##codes, no labels in the deposit). No survey weight in the deposit.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- read_dta(file.path(raw, "study2.dta"))
stopifnot(nrow(r) == 12612, length(unique(r$respondent)) == 1051)
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = as.integer(r$respondent), task = as.integer(r$task), profile = as.integer(r$candidate),
                choice = as.integer(r$dv1), choice_concerns = as.integer(r$dv5),
                rating_contact = as.integer(r$dv2), rating_donate = as.integer(r$dv3), rating_trust = as.integer(r$dv4),
                attr_race = lab(r$race), attr_gender = lab(r$gender), attr_policy_priority = lab(r$policypriority),
                attr_party = lab(r$partyaffiliation), attr_ideology = lab(r$ideology),
                attr_parental_status = lab(r$parentalstatus))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
nat <- lab(r$nativity); ide <- lab(r$resp_ideology)
d[, `:=`(cov_age = as.integer(r$age), cov_gender = c("male", "female")[as.integer(zap_labels(r$women)) + 1L],
         cov_ideology = ide, cov_nativity = nat,
         cov_black = as.integer(zap_labels(r$black)), cov_latino = as.integer(zap_labels(r$latino)),
         cov_white = as.integer(zap_labels(r$white)), cov_democrat = as.integer(zap_labels(r$democrat)),
         cov_republican = as.integer(zap_labels(r$republican)), cov_independent = as.integer(zap_labels(r$independent)),
         cov_income_code = as.integer(zap_labels(r$income)), cov_education_code = as.integer(zap_labels(r$ed_attain)))]
d <- d[!(is.na(choice) & is.na(choice_concerns) & is.na(rating_contact) & is.na(rating_donate) & is.na(rating_trust))]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1, na.rm = TRUE)],
          d[, sum(choice_concerns), .(id, task)][, all(V1 == 1, na.rm = TRUE)],
          d[, .N, .(id, task, profile)][, all(N == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "joo_2026_descriptive_rep.csv"))
