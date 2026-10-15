##Water-service improvement choice experiment (Puerto Rico) from
##Tavarez, H., & Elbakidze, L. (2024). Willingness to pay for ancillary water service improvements in Puerto Rico.
##Water Economics and Policy, 10(1), 2350010. https://doi.org/10.1142/s2382624x23500108
##(article behind a paywall; not read. Citation from a web search that listed it as a reference; the match to this
##deposit rests on the deposit title "WTP for water service improvements in Puerto Rico (data)" and the first author.)
##Data: Mendeley Data doi:10.17632/dhbb5xhdvh.1, CC BY 4.0 (Mendeley public API, data_licence). File read:
##"Tavarez - WTP for water service improvement data.xlsx" (one sheet, 19,124 rows = 683 respondents x 7 tasks x 4 concepts).
##Usage: Rscript tavarez_2024.R <dir holding the xlsx, any name ending .xlsx> <output dir>
##
##Online survey (Sawtooth Software per the deposit description), 683 residents of Puerto Rico. Each of 7 tasks:
##three water-service packages (concept 1-3) and a fourth concept coded 0 on every attribute with cost 0 = "none"
##(no attributes: opt_out = yes, rows dropped; chosen in 1,666 of 4,374 kept tasks). The column `dep` is the chosen concept
##(exactly one 1 per answered task); about 400 tasks have no 1 at all (unanswered) and are dropped.
##LABELS: CODES ONLY. Attributes in the file: days (1-3), quality (1-3), notification (1-3), restriction (1-3), cost
##(1, 3, 6, 9, 12, 15). The deposit has no codebook and the article is not open, so attribute levels read "level 1/2/3"
##(in file order) and cost is the stored number (currency and period not stated; the none concept has cost 0).
##The attribute names suggest days without water service, water-quality problem, advance notification and restriction
##level, but no source states the wording. Level frequencies: days level 1 appears in 42% of the profiles, levels 2
##and 3 in 29% each (non-uniform).
##Restrictions: none documented; level weights: observed (days level 1 about twice as frequent). Attribute order fixed
##(assumed). task = the file's task 1-7 (assumed order shown); profile = concept.
##Covariates kept (codes, no codebook, hence _code): cov_age (years), cov_gender_code (0/1), cov_education_code (1-5),
##cov_income_code (1-6), cov_dependents (count). Dropped: rank_1..rank_5 (a respondent-level ranking whose meaning is
##not given), complexity, scarcity, future_scarcity, cistern, municipality (free-typed place names).
##683 ids in the file; one id carries two different people's covariates (two ages, genders, municipalities) and is dropped: 682 respondents in the table.
##N vs paper: article not read.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fn <- list.files(raw, pattern = "[.]xlsx$", full.names = TRUE)[1]
x <- as.data.table(read_excel(fn, sheet = 1, guess_max = 1e5))
stopifnot(nrow(x) == 19124, x[, .N, id][, all(N == 28)], x[, .N, .(id, task)][, all(N == 4)])
bad <- x[, .(n = uniqueN(paste(age, gender, income, education, dependents, municipality))), id][n > 1, id]
x <- x[!id %in% bad]
ans <- x[, .(s = sum(dep)), .(id, task)][s == 1, .(id, task)]
stopifnot(x[concept == 4, all(days == 0 & quality == 0 & notification == 0 & restriction == 0 & cost == 0)])
x <- merge(x, ans, by = c("id", "task"))
x[, rid := match(id, sort(unique(id)))]
lv <- function(v) paste("level", as.integer(v))
d <- x[concept < 4, .(id = rid, task = as.integer(task), profile = as.integer(concept), choice = as.integer(dep),
  attr_days = lv(days), attr_quality = lv(quality), attr_notification = lv(notification), attr_restriction = lv(restriction),
  attr_cost = as.character(as.integer(cost)),
  cov_age = ifelse(age >= 15 & age <= 100, as.integer(age), NA_integer_), cov_gender_code = as.integer(gender),
  cov_education_code = as.integer(education), cov_income_code = as.integer(income), cov_dependents = as.integer(dependents))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^task$|^profile$")]), d[, .N, .(id, task)][, all(N == 3)],
  d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tavarez_2024_water_puerto_rico.csv"))
