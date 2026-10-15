##Wetland-conservation choice experiment (Malaysia) from
##Hassan, S., Olsen, S. B., & Thorsen, B. J. (2019). Urban-rural divides in preferences for wetland conservation in
##Malaysia. Land Use Policy, 84, 226-237. (Paper identified from the deposit description and a web search; the full
##text could not be retrieved, so no number or level text is checked against it.)
##Data: Mendeley Data doi:10.17632/3yjzwt26b4.1, CC BY 4.0 (Mendeley public API, data_licence). File read:
##"Data2014a for Subsidy Sample.xlsx" (one sheet, 4,836 rows x 135 columns; the model-ready estimation file).
##Usage: Rscript hassan_2019.R <dir holding the xlsx, any name ending .xlsx> <output dir>
##
##403 urban and rural households (face-to-face interviews, 2014), 12 choice sets each, 3 alternatives: wetland
##conservation programmes A and B and a third alternative with all attributes at level 1 and price 0 (the status quo).
##The status quo has stored levels, so it is a profile (profile 3), not an opt-out; every set has exactly one choice.
##Outcome: choice among the three alternatives (exact question wording not available).
##Attributes (deposit names): environmental protection zones (EnvQ), biodiversity protection (Biod), recreational
##services (Recr), flood (Flood), price = household cost as a reduction in subsidies for daily goods (Price).
##LABELS: CODES ONLY. The deposit stores levels 1-3 for the four quality attributes and numbers 0, 5, 10, 30, 90, 210,
##400 for price, with no codebook, no value labels and no level text; the dummy columns (EnvQM/EnvQH, FloodM/FloodL)
##suggest medium/high (flood: medium/low) against a base level, but nothing states the wording. attr_ cells
##therefore read "level 1/2/3" (price: the stored amount; currency and period unknown, probably Malaysian ringgit).
##In the status quo flood = level 3, the other three attributes level 1.
##Payment vehicle columns (Don/Sub/Tax) show only the subsidy vehicle (payment = 2 for all rows); other columns
##(income-interaction and urban/rural-split copies of every attribute) are derived and dropped.
##Restrictions: none documented; level weights: unknown (the design file is not in the deposit). Attribute order
##fixed (assumed). task = Set 1-12 as stored; profile = alternative 1-3.
##Covariates kept (codes, no codebook, hence _code): cov_age (years), cov_gender_code (0/1), cov_education_code (1-6),
##cov_urban_code (ResStat, 1 = the column Urban, 3,588 of 4,836 rows).
##Dropped: QID (row counter), area (10 survey areas), job, household composition, visit variables, income bands, all
##derived dummy and interaction columns.
##N vs paper: 403 respondents; the paper's N not seen.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fn <- list.files(raw, pattern = "[.]xlsx$", full.names = TRUE)[1]
x <- as.data.table(read_excel(fn, sheet = 1, guess_max = 1e5))
stopifnot(nrow(x) == 4836, uniqueN(x$IND) == 403, x[, .N, IND][, all(N == 12)], x[, all(sort(Set) == 1:12), IND][, all(V1)],
  all(x$choice %in% 1:3), x[, all(Env1 <- EnvQ3 == 1 & Biod3 == 1 & Recr3 == 1 & Flood3 == 3 & Price3 == 0)])
x[, id := match(IND, sort(unique(IND)))]
lv <- function(v) paste("level", as.integer(v))
mk <- function(k) x[, .(id, task = as.integer(Set), profile = k, choice = as.integer(choice == k),
  attr_environmental_protection = lv(get(paste0("EnvQ", k))), attr_biodiversity = lv(get(paste0("Biod", k))),
  attr_recreation = lv(get(paste0("Recr", k))), attr_flood = lv(get(paste0("Flood", k))),
  attr_price = as.character(as.integer(get(paste0("Price", k)))),
  cov_age = as.integer(age), cov_gender_code = as.integer(gender), cov_education_code = as.integer(edu),
  cov_urban_code = as.integer(ResStat))]
d <- rbindlist(lapply(1:3, mk))
stopifnot(!anyNA(d), d[, .N, .(id, task)][, all(N == 3)], d[, sum(choice), .(id, task)][, all(V1 == 1)],
  d[, uniqueN(cov_age), id][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hassan_2019_wetland_malaysia.csv"))
