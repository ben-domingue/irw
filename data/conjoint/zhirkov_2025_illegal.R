##"Illegal" vs "undocumented" immigrant identification conjoint (US) from
##Zhirkov, K., & Brehm, R. H. (2025). Beliefs and opinions about "illegal" and "undocumented"
##immigrants: Conceptual replication of a null result. Research & Politics, 12(3), 20531680251355233.
##https://doi.org/10.1177/20531680251355233 (article CC BY-NC 4.0; not read: publisher blocks
##automated access, so design facts below come from the deposit and its description).
##Replication data: Harvard Dataverse doi:10.7910/DVN/ZVPACI, CC0 1.0, no restricted files.
##Files read (from replication_materials.zip): data/data_02_conjoint.dta (one row per
##respondent x pair x profile, with Stata value labels) and data/data_01_survey.dta
##(respondent covariates and the condition). The authors' code/*.do and *.R files were read
##as text (not run).
##Usage: Rscript zhirkov_2025_illegal.R <dir holding data_01_survey.dta, data_02_conjoint.dta> <output dir>
##
##1,083 respondents, 6 pairs each (task = source `pair`, profile = source `profile`), 8
##attributes: age (number of years, 25-54), years in the U.S. (1-19), gender, race, English,
##education, police record, benefits. The deposit description: "respondents are randomly asked
##to identify profiles that belong to 'illegal' or 'undocumented' immigrants". Outcome:
##choice = the profile picked as the "illegal" (trial_condition = illegal, source cond 1) or
##"undocumented" (trial_condition = undocumented, cond 2) immigrant; the condition labels come
##from the authors' code_02_Figure1.R (first cond == 1 model is plotted as "Illegal"). The
##verbatim instruction is not in the deposit. The choice is "which is more likely an
##unauthorized immigrant", not a preference. No opt-out is documented; 40 of 6,498 tasks have
##no chosen profile (source `chosen` 0 on both rows, presumably skipped) and are dropped as
##rows with no outcome: 12,916 rows remain. Three respondents (source respid 108, 610, 793)
##chose in none of their 6 pairs, so the table has 1,080 respondents. The authors' models keep
##those rows as not chosen (12,996 rows), so their AMCEs differ slightly from this table's:
##in the illegal condition this table gives less than college +10.25 pp, poor English +8.47,
##police record +7.69, benefits -5.15 (lm, SEs clustered by id) vs the authors' 10.24, 8.48,
##7.58, -5.10 (data_03_Figure1_estimates.csv).
##Attribute text is the authors' Stata value labels (gender Woman/Man, English Good/Poor,
##benefits None/Food stamps/Medicaid/SSI/Welfare, ...); the displayed wording may have been
##longer. Police record has 6 labelled levels but only 4 occur (no "Drunk driving",
##"Trespassing"), and "No record" is about half of all profiles: randomization weights were
##not uniform (restrictions = observed). Attribute order not recorded.
##Covariates: cov_age (years), cov_gender (1 = Male, 2 = Female), cov_race (1-8, labels in
##the .dta: 1 White .. 7 Other; 3 and 8 are both labelled Hispanic or Latino/a), cov_educ (1-6),
##cov_income (1-6), cov_pid8 (1 Strong Democrat .. 7 Strong Republican, 8 Other; no 4),
##cov_enforc_daca (DACA: oppose), cov_enforc_snct (sanctuary: oppose), cov_enforc_pprs
##(SB 1070: support), cov_enforc_wall (wall: support), each 1-7 as in the source (higher =
##more pro-enforcement per the authors' labels), cov_term_pref (1 = Illegal, 2 = Undocumented).
##Dropped: the authors' derived dummies (conj_*, female, white, nonwhite, college, pid7/3/2)
##and scale (enforc). No platform IDs in the deposit; id = source respid (1-1,083).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "data_02_conjoint.dta"))
s <- read_dta(file.path(raw, "data_01_survey.dta"))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
d <- data.table(id = as.integer(k$respid), task = as.integer(k$pair), profile = as.integer(k$profile),
                choice = as.integer(k$chosen),
                attr_age = as.character(k$attr_ages), attr_years_in_us = as.character(k$attr_stay),
                attr_gender = lab(k$attr_gend), attr_race = lab(k$attr_race), attr_english = lab(k$attr_engl),
                attr_education = lab(k$attr_educ), attr_police_record = lab(k$attr_crim), attr_benefits = lab(k$attr_welf))
stopifnot(d[, .N, id][, all(N == 12)], d[, .N, .(id, task)][, all(N == 2)], !anyNA(d))
d[, tsum := sum(choice), .(id, task)]
stopifnot(d[, all(tsum <= 1)], d[tsum == 0, uniqueN(paste(id, task))] == 40)
d <- d[tsum == 1][, tsum := NULL]
stopifnot(all(s$cond %in% 1:2))
cv <- data.table(id = as.integer(s$respid), trial_condition = c("illegal", "undocumented")[s$cond])
for (v in c("age", "gender", "race", "educ", "income", "pid8", "enforc_daca", "enforc_snct", "enforc_pprs",
            "enforc_wall", "term_pref")) cv[, paste0("cov_", v) := as.integer(zap_labels(s[[v]]))]
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d$id) == 1080, nrow(d) == 12916)
setcolorder(d, c("id", "task", "profile", "choice", "trial_condition"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "zhirkov_2025_illegal_undocumented.csv"))
