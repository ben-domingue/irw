##Mediterranean deep-sea ecosystem services discrete choice experiment (Italy) from
##Carlesi, L., Cubero Dudinskaya, E., Danovaro, R., D'Onghia, G., Mandolesi, S., Naspetti, S., & Zanoli, R. (2023).
##Estimating preferences for Mediterranean deep-sea ecosystem services: A discrete choice experiment. Marine Policy.
##https://doi.org/10.1016/j.marpol.2023.105593 (paywalled; not read). Data: Mendeley Data doi:10.17632/23tjmx64xc.2
##(Zanoli & Carlesi), CC BY 4.0 (Mendeley API). File read: Deep_sea_Final_Nlogit_Dec2015.dta (Stata, with Italian value
##labels); Deep_sea_R3.csv (same 800 respondents, dummy-coded) not used. Usage: Rscript carlesi_2023.R <dir holding the
##.dta> <output dir>
##
##800 Italian household respondents (the Mendeley description says the data are the reduced sample of 544 without
##lexicographic preferences or attribute non-attendance, but both files hold 800 ids and no flag identifying 544:
##N MISMATCH, all 800 kept). 9 choice sets each (BLOCK 1-4, fixed blocked design; idd = set 1-9). Each set: a
##submarine canyon alternative (altij 1), a cold-water coral alternative (altij 2) and "nessuna" (none, altij 3, all
##attributes 0): an opt-out (opt_out = yes; row dropped; choice 0 on both profiles when chosen, 3,264 of 7,200 sets;
##45%). The labelled habitat is a level of attr_habitat (Canyon / Coral).
##Attributes: biodiversity (stored 5/10/15), climate regulation (stored 0.5/1), scientific value (stored 0/1: here
##attr_scientific_value "0"/"1"), price (stored 10,20,...,60; euros per household presumably). LABELS: codes only. The
##displayed wording, units and meaning of the biodiversity, climate and scientific-value levels are not in the deposit
##and the article is paywalled; the stored numbers are kept as text. Ben decides.
##Restrictions/level weights: not documented. Outcome: choice among canyon / coral / none (wording unknown).
##Covariates: cov_gender (Male: Femmina/Maschio -> female/male, dta labels), cov_age (years), cov_area (zona labels:
##Nord/Centro/Sud e isole), cov_education (Edu value labels, Italian), cov_household_income (Income value labels,
##Italian bands). Dropped: knowledge/importance items, other covariates. Respondent key = ID (1-800).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(read_dta(list.files(raw, pattern = "[.]dta$", full.names = TRUE)[1]))
stopifnot(nrow(x) == 21600, uniqueN(x$ID) == 800, x[, .N, .(ID, idd)][, all(N == 3)], x[, sum(choice), .(ID, idd)][, all(V1 == 1)])
stopifnot(x[altij == 3, all(scie == 0 & clima == 0 & bio == 0 & price == 0)], x[altij < 3, all(price > 0 & bio > 0 & clima > 0)])
lab <- function(v) as.character(as_factor(v))
x[, `:=`(g = lab(Male), edu = lab(Edu), inc = lab(Income), area = lab(zona))]
inc_clean <- function(s) gsub("&#39;", "'", gsub("&ugrave;", "u", s))
p <- x[altij < 3]
d <- p[, .(id = ID, task = as.integer(idd), profile = as.integer(altij), choice = as.integer(choice),
  attr_habitat = c("Canyon", "Coral")[altij], attr_biodiversity = as.character(bio), attr_climate_regulation = as.character(clima),
  attr_scientific_value = as.character(scie), attr_price = as.character(price), trial_block = as.integer(BLOCK),
  cov_gender = ifelse(g == "Maschio", "male", ifelse(g == "Femmina", "female", NA_character_)), cov_age = ifelse(Age >= 15 & Age <= 100, as.integer(Age), NA_integer_),
  cov_area = area, cov_education = edu, cov_household_income = inc_clean(inc))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "carlesi_2023_deep_sea.csv"))
