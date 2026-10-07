##Two conjoint experiments from
##Hainmueller, J., Hopkins, D. J., & Yamamoto, T. (2014). Causal inference in conjoint
##analysis: Understanding multidimensional choices via stated preference experiments.
##Political Analysis, 22(1), 1-30. https://doi.org/10.1093/pan/mpt024
##Replication data: Harvard Dataverse doi:10.7910/DVN/THJYQR, CC0 1.0. Files read:
##candidate.dta and immigrant.dta (Dataverse "original format" downloads, which keep
##the Stata value labels; the .tab versions do not).
##Usage: Rscript hainmueller_2014.R <dir holding the two .dta files> <output dir>
##
##hainmueller_2014_candidate: 311 MTurk respondents, up to 6 pairs of hypothetical
##  presidential candidates, 8 attributes. Outcomes: forced choice (selected) and a
##  7-point rating stored in the source as 0, 1/6, ..., 1 and recoded here to 1..7.
##  The file has NO task or profile column. Consecutive rows within a respondent form a
##  pair (every one of the 1,733 pairs has exactly one selected profile), so task and
##  profile are INFERRED from row order. Respondents with fewer than 6 pairs (122) are
##  numbered by the order of their observed pairs. resID's value labels are MTurk
##  worker IDs; only the numeric code is kept. 10 missing ratings stay missing (the
##  choice on those rows is kept).
##hainmueller_2014_immigrant: 1,396 respondents, 5 pairs of immigrant profiles, 9
##  attributes, forced choice. Randomization was restricted (some jobs only with some
##  education levels; persecution only with some countries). Row positions of the
##  language and prior-trips attributes are kept as attrpos_*. The same 1,396
##  respondents ship with the cjoint R package (immigrationconjoint); AMCEs computed
##  from this table match cjoint's to 1e-14.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) { l <- attr(x, "labels"); names(l)[match(x, l)] }

h <- read_dta(file.path(raw, "candidate.dta"))
d <- data.table(id = as.integer(zap_labels(h$resID)))
d[, r := seq_len(.N), id][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L][, r := NULL]
d[, choice := as.integer(h$selected)]
d[, rating := as.integer(round(h$rating * 6)) + 1L]
amap <- c(atmilitary = "military_service", atreligion = "religion", ated = "college", atprof = "profession",
          atinc = "income", atrace = "race_ethnicity", atage = "age", atmale = "gender")
for (v in names(amap)) d[, paste0("attr_", amap[[v]]) := lab(h[[v]])]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hainmueller_2014_candidate.csv"))

m <- read_dta(file.path(raw, "immigrant.dta"))
d <- data.table(id = as.integer(m$CaseID), task = as.integer(m$contest_no), profile = as.integer(m$profile),
                choice = as.integer(zap_labels(m$Chosen_Immigrant)))
imap <- c(FeatEd = "education", FeatGender = "gender", FeatCountry = "origin", FeatReason = "application_reason",
          FeatJob = "profession", FeatExp = "job_experience", FeatPlans = "job_plans", FeatTrips = "prior_trips", FeatLang = "language")
for (v in names(imap)) d[, paste0("attr_", imap[[v]]) := lab(m[[v]])]
d[, attrpos_language := as.integer(m$LangPos)][, attrpos_prior_trips := as.integer(m$PriorPos)]
d[, cov_ethnocentrism := as.numeric(m$ethnocentrism)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hainmueller_2014_immigrant.csv"))
