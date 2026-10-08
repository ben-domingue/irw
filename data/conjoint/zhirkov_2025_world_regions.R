##Immigrant world-region classification conjoint (US) from
##Zhirkov, K. (2025). Americans' perceptions about immigrants from different world regions:
##Evidence from a multinomial conjoint experiment. Journal of Experimental Political Science,
##13(2), 192-202. https://doi.org/10.1017/XPS.2025.5 (CC BY 4.0; "Data and method" and Table 1
##read from the publisher's HTML).
##Replication data: Harvard Dataverse doi:10.7910/DVN/PTX4RU, CC0 1.0, no restricted files.
##File read (from replication_materials.zip): data/data_01_main.dta (one row per respondent x
##profile, attribute text in the *_full string columns, outcome and covariates with Stata value
##labels). readme.txt and code/*.do read as text.
##Usage: Rscript zhirkov_2025_world_regions.R <dir holding data/> <output dir>
##
##1,979 US adults (Lucid Theorem, August 2022), as in the article. Each classified 20 single
##profiles of hypothetical immigrants, one per survey page: task = source `profile` (Conjoint
##profile no.), profile = 1. Seven attributes shown as a two-column table (article Fig. 1): age
##(a number drawn from 20-39 or 40-59), gender, education (6), English proficiency, prior trips to
##the U.S. (No / Yes, on a visa / Yes, overstayed visa / Yes, unauthorized), government benefits,
##police record. Article Table 1 note: order of attributes randomized between respondents, constant
##within respondent (not recorded: no attrpos_); values independent and uniform, except that
##benefits and police record are "No benefits" / "No record" with probability 1/2 and otherwise one
##of 4 benefits / 3 offences with equal probability (level_weights nonuniform).
##Outcome: respondents guessed which world region each immigrant came from: Africa, Asia, Europe,
##Latin America or the Middle East (one answer per profile; `choice`, "Classification choice").
##This is a nominal classification of a single profile, not a pick among profiles, so it is stored
##as five 0/1 ratings, one per answer option, exactly one of which is 1 on each row:
##rating_africa, rating_asia, rating_europe, rating_latin_america, rating_middle_east.
##12 profiles with no answer are omitted (rows with no outcome).
##Covariates: cov_age (years), cov_gender (`female`, "Female vs. male", 1 -> female, 0 -> male),
##cov_education (educ labels), cov_income (income bracket labels), cov_race (race labels),
##cov_hispanic_code (`hispanic`, "Hispanic vs. not": 0/1 plus 540 rows coded 16, no value labels,
##so codes are kept), cov_party_id (pid8 labels, Strong Democrat .. Strong Republican, Other).
##Dropped: the authors' dichotomized attribute dummies (conj_ages .. conj_polr, conj_stvl),
##college, nhwhite, pid3, ethnoc, ethnoc_bin (derived). respid is already a 1..N integer.
##Same Lucid fielding month as zhirkov_2025_welfare_stereotypes (doi:10.7910/DVN/6SHF3S, 1,964
##respondents, a different experiment); the deposits do not say whether the samples overlap.
library(data.table); library(haven)
a <- commandArgs(TRUE); out <- a[2]
s <- read_dta(file.path(a[1], "data", "data_01_main.dta"))
lab <- function(v) { l <- attr(v, "labels"); unname(setNames(names(l), l)[as.character(as.numeric(v))]) }
d <- data.table(id = as.integer(s$respid), task = as.integer(s$profile), profile = 1L, ch = lab(s$choice),
                attr_age = as.character(s$conj_ages_full), attr_gender = s$conj_gend_full, attr_education = s$conj_educ_full,
                attr_english = s$conj_engl_full, attr_prior_trips = s$conj_trip_full, attr_benefits = s$conj_benf_full,
                attr_police_record = s$conj_polr_full,
                cov_age = as.integer(s$age), cov_gender = fifelse(as.numeric(s$female) == 1, "female", "male"),
                cov_education = lab(s$educ), cov_income = lab(s$income), cov_race = lab(s$race),
                cov_hispanic_code = as.integer(s$hispanic), cov_party_id = lab(s$pid8))
stopifnot(uniqueN(d$id) == 1979, d[, .N, id][, all(N == 20)], !anyDuplicated(d[, .(id, task)]), !anyNA(s$female))
d <- d[!is.na(ch)]
reg <- c(africa = "Africa", asia = "Asia", europe = "Europe", latin_america = "Latin America", middle_east = "Middle East")
stopifnot(all(d$ch %in% reg))
for (r in names(reg)) set(d, j = paste0("rating_", r), value = as.integer(d$ch == reg[[r]]))
d[, ch := NULL]
ac <- grep("^attr_", names(d), value = TRUE); stopifnot(!anyNA(d[, ..ac]), all(d[, sapply(.SD, function(v) all(nzchar(v))), .SDcols = ac]))
setcolorder(d, c("id", "task", "profile", paste0("rating_", names(reg)), ac)); setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhirkov_2025_immigrant_regions.csv"))
