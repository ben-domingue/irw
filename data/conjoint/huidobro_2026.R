##Coalition-partner conjoint with Spanish mayors (elite sample) from
##Huidobro, A. (2026). Partners in government: Politicians' gender preferences in coalition
##formation. Political Science Research and Methods. Advance online publication.
##https://doi.org/10.1017/psrm.2025.10077
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZQIFHG, CC0 1.0. File read: main_database.tab
##(Dataverse "original format" .dta download). main_analysis.do and replication_log.txt read as text
##(not run); design and wording from the article.
##Usage: Rscript huidobro_2026.R <dir holding main_database.dta> <output dir>
##
##huidobro_2026_coalition_partner: an ELITE sample of Spanish mayors (online survey, 2018-19).
##  Mayors are told they won 5 of 13 council seats and choose a coalition partner: "If you could
##  choose between two partners to form a government coalition with the following two leaders,
##  which one would you choose?" 2 tasks of 2 hypothetical party leaders, 6 attributes: gender
##  (Man / Woman), age (27, 36, 45, 54, 66), education (Primary, Secondary, University,
##  Doctorate), previous electoral terms on the council (None, One, Two), party ideology (Extrem
##  Left, Center-Left, Center, Center-Right, Extrem Right; spelling as in the deposit), party seats
##  (1-4). The survey was in Spanish; attr_* hold the author's English value labels.
##  TASK AND PROFILE ARE INFERRED FROM ROW ORDER: the file has 4 rows per respondent (id_conjoint)
##  and no task/profile column. Consecutive row pairs form a task (every pair has exactly one
##  chosen profile or no answer on both), and the follow-up ratings exist only on the second pair,
##  which the article says were asked about the second-round profiles, so pair 1 = task 1. profile
##  is the row order within the pair; whether that was the left/right screen position is not
##  documented.
##  Outcomes:
##    choice = person (forced choice, no opt-out).
##    rating_similar_preferences, rating_easy_communication, rating_capacity_to_govern,
##      rating_trustworthy = polpref, easycomu, capacity, confidence: agreement (1 = strongly
##      disagree, 5 = strongly agree) with statements about each second-task leader (similar
##      political preferences to the mayor's own, easy to communicate with, capacity to govern,
##      trustworthy; exact wording in the article's Appendix B). Task 2 only; empty in task 1.
##  Counts: 1,018 respondent ids; 133 tasks have no attributes and 273 no choice. Rows without
##  attributes or without any outcome are dropped: 913 respondents remain, 905 with at least one
##  choice. The author's main model uses 3,526 rows / 905 clusters, which this table reproduces;
##  the article text reports 979 mayors and 3,324 observations (not reconciled here).
##  Covariates (the deposit's grouped codes; the author withheld ungrouped data because the
##  combination would identify mayors): cov_female (1 = woman), cov_over50 (1 = 50 or older),
##  cov_education (1 primary, 2 secondary, 3-4 university; the do-file pools 3 and 4),
##  cov_ideology (1 left, 2 center, 3 right). To limit re-identification the party, municipality
##  population group, seniority, occupation, plans to run again, majority status, feminist-movement
##  and honesty-task variables and page timings are NOT carried.
##  Spot check: lm(choice ~ attributes) gives Woman +.0899 and University +.0543, as in the
##  author's replication_log.txt.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k0 <- read_dta(file.path(raw, "main_database.dta"))
k <- as.data.table(zap_labels(k0))
lab <- function(v) as.character(as_factor(k0[[v]]))
stopifnot(k[, .N, id_conjoint][, all(N == 4)])
k[, r := seq_len(.N), id_conjoint][, `:=`(task = (r + 1L) %/% 2L, profile = 2L - r %% 2L)]
stopifnot(k[task == 1, all(is.na(polpref))], k[!is.na(person), sum(person), .(id_conjoint, task)][, all(V1 == 1)],
          k[, uniqueN(is.na(person)), .(id_conjoint, task)][, all(V1 == 1)])
d <- data.table(id = as.integer(k$id_conjoint), task = as.integer(k$task), profile = as.integer(k$profile),
                choice = as.integer(k$person),
                rating_similar_preferences = as.integer(k$polpref), rating_easy_communication = as.integer(k$easycomu),
                rating_capacity_to_govern = as.integer(k$capacity), rating_trustworthy = as.integer(k$confidence),
                attr_gender = lab("gender"), attr_age = lab("age"), attr_education = lab("edu"), attr_terms = lab("legis"),
                attr_ideology = lab("ideolog"), attr_seats = lab("seats"),
                cov_female = as.integer(k$genderresp), cov_over50 = as.integer(k$ageresp_g),
                cov_education = as.integer(k$edurespondent), cov_ideology = as.integer(k$ideolresp_g))
stopifnot(d[, all(attr_education %in% c("Primary", "Secondary", "University", "Doctorate", NA))])
d <- d[!is.na(attr_gender)]
stopifnot(!anyNA(d[, .(attr_age, attr_education, attr_terms, attr_ideology, attr_seats)]))
d <- d[!(is.na(choice) & is.na(rating_similar_preferences) & is.na(rating_easy_communication) &
         is.na(rating_capacity_to_govern) & is.na(rating_trustworthy))]
stopifnot(d[!is.na(choice), .N] == 3526, d[!is.na(choice), uniqueN(id)] == 905)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "huidobro_2026_coalition_partner.csv"))
