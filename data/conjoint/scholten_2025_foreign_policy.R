##Military-action conjoint, U.S. public and State Department experts, from
##Scholten, M., & Zhirkov, K. (2026). Public and expert preferences in survey experiments in
##foreign policy: Evidence from parallel conjoint analyses. Political Science Research and
##Methods, 14, 1011-1018. https://doi.org/10.1017/psrm.2025.10026 (online 27 June 2025)
##Replication data: Harvard Dataverse doi:10.7910/DVN/F0TFGQ, CC0 1.0. File read:
##replication_materials.zip -> data/data_01_main.dta (Stata labels give the level text). The
##authors' .do files and logs were read as text.
##Usage: Rscript scholten_2025_foreign_policy.R <dir holding data_01_main.dta> <output dir>
##
##Feb-Jun 2023. Mass sample: Lucid Theorem U.S. adults (985); expert sample: U.S. Department of
##State employees recruited via LinkedIn (147). The two experiments are identical and the
##authors pool them to test sample differences (code_05_Table2.do, conj_x##sampl), so this is
##one table with cov_sample (Mass / Expert).
##6 paired tasks, 6 attributes (Table 1 of the article; level text from the Stata labels):
##reason for military action (Funding of terrorist groups / Nuclear program / Human rights
##violations), political regime (Autocracy / Democracy), dominant religion (Islam /
##Christianity), U.S. ally (No / Yes), military capability (Weak / Strong), amount of trade with
##the U.S. (Low / High). Values fully and independently randomized with uniform probabilities
##(restrictions none). Reason was always shown first; the order of the other five was
##randomized per respondent but is NOT in the deposit (no attrpos_).
##The file has no task column: each respondent has 12 consecutive rows alternating profile 1/2,
##so task is INFERRED from row order (checked: 12 rows per respondent, contiguous, profile
##alternates 1,2; at most one chosen profile per inferred pair).
##Outcomes (one screen, one experiment):
##  choice = against which of the two countries military action is more justified (article's
##    paraphrase; forced choice). 132 of 6,792 tasks have chosen = 0 on both profiles (no
##    answer recorded); the authors' regressions count them as 0. Here choice is left blank for
##    both profiles of those tasks; their ratings are kept.
##  rating = justification of military action against each country, 0-10, 0 = Completely
##    unjustified, 10 = Completely justified (article note to Supplement B). Higher = more
##    justified (i.e. more hawkish); not recoded.
##Covariates: cov_sample, cov_college (1 = college degree), cov_pid2 (1 Democrat, 2
##Republican; blank for independents/experts not answering). The ethnocentrism and hawkishness
##battery scores (ethnoc, hawk) and their median splits are derived scales and are dropped.
##Respondent ids are the authors' sequential respid.
##Rows with neither a choice nor a rating (57) are dropped; one mass respondent answered
##nothing: 1,131 respondents (984 mass, 147 expert), 13,527 rows; 37 rows have a choice but no
##rating. Count check: the article and the logs report 985 + 147 respondents (11,820 / 1,764
##rows, counting unanswered tasks as not chosen).
##Spot check: the mass-sample choice AMCEs (unanswered tasks set to 0) reproduce the authors'
##log to within 0.001 (e.g. Democracy -0.032, U.S. ally -0.059, Strong +0.041; SE 0.010).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "data_01_main.dta"))
lab <- function(v) as.character(as_factor(s[[v]]))
d <- data.table(id = as.integer(s$respid), profile = as.integer(s$profile), choice = as.integer(s$chosen),
                rating = as.integer(s$rating),
                attr_reason = lab("conj_reas"), attr_regime = lab("conj_regm"), attr_religion = lab("conj_relg"),
                attr_us_ally = lab("conj_ally"), attr_military = lab("conj_milt"), attr_trade = lab("conj_trde"),
                cov_sample = lab("sampl"), cov_college = as.integer(s$college), cov_pid2 = as.integer(zap_labels(s$pid2)))
stopifnot(all(rle(d$id)$lengths == 12), uniqueN(d$id) == 1132)
d[, r := seq_len(.N), id][, task := (r + 1L) %/% 2L]
stopifnot(d[, all(profile == 2L - r %% 2L)])
d[, r := NULL]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 <= 1)])
d[, none := sum(choice) == 0, .(id, task)][none == TRUE, choice := NA_integer_][, none := NULL]
stopifnot(d[is.na(choice), .N] == 264, d[cov_sample == "Mass", uniqueN(id)] == 985, d[cov_sample == "Expert", uniqueN(id)] == 147)
d <- d[!(is.na(choice) & is.na(rating))]
setcolorder(d, c("id", "task", "profile", "choice", "rating"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "scholten_2025_military_action.csv"))
