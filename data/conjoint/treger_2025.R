##Policy-tool conjoints (Israel and US) from
##Treger, C. (2025). Changing the lens: The contingency of results from conjoint experiments on
##the outcome variable and the estimand. Research & Politics. https://doi.org/10.1177/20531680251351238
##(the do-file calls both data sets the "original study (Treger 2023)").
##Replication data: Harvard Dataverse doi:10.7910/DVN/AQYCXH, CC0 1.0. Files read (Stata originals,
##fetched with ?format=original for the value labels):
##  "Israel Data_Changing the Lens.dta" (datafile 11369851), "US Data_Changing the Lens.dta" (11369847).
##Read as text only: READ ME_Changing the Lens.txt, "Changing the Lens IL and US code.do".
##Not built from this deposit: Jensen et al. (2021) files (all_conjoint.dta, msa_survey_indiv.dta,
##strong_rep_dem_conjoint.dta; already jensen_2021_city_development_plans from the authors' deposit)
##and Leher et al. (2022) (Leher_replication_data.Rdata), both re-hosted for reanalysis.
##Usage: Rscript treger_2025.R <dir holding the two .dta files as named above> <output dir>
##
##Two tables, one per sample (separate fieldings, languages and promoter levels; the do-file analyses
##them separately): treger_2025_policy_tools_il (1,170 Qualtrics respondents, Hebrew, UserLanguage HE)
##and treger_2025_policy_tools_us (1,570 respondents, English). Each respondent saw 8 tasks of 2
##policy proposals. Task and profile are RECORDED in `proposal` (= 10 * task + profile, 11..82).
##Tasks come in domain blocks: tasks 1-2 Safety, 3-4 Health, 5-6 Welfare, 7-8 Morals; within each
##domain one of two policy goals (Safety: bike riding/swimming; Health: nutrition/smoking; Welfare:
##pension/working hours; Morals: euthanasia/pornography) is used for both of that domain's tasks
##(trial_domain, trial_goal; same for both profiles). Whether tasks were displayed in this block order
##is not stated in the deposit.
##Attributes (5): coercion level of the policy tool (Info / Nudge (IL) or Default/Decision (US) /
##Tax/Restriction / Ban/Mandate), public support (20%-30% ... 75%-85%, unknown), effectiveness,
##promoter (7 Israeli, 6 US levels), implementation date. Attribute text is the Stata VALUE-LABEL text
##(English short labels; for Israel the displayed Hebrew text is not in the deposit). The actual policy
##wording combined goal x coercion level (source variable policy_, e.g. "mandate_swim"; no wording
##ships), so attr_coercion is the level of the shown policy, not its text.
##Restriction OBSERVED: the two profiles of a task never share a coercion level (all 9,360 IL and
##12,560 US tasks); otherwise level shares are uniform (coercion 25%, public support 20%, etc.).
##Outcomes (wording not in the deposit; from the do-file): rating = support_, 1-7 support for the
##proposal (higher = more support; the do-file treats 5-7 as "supported"); choice = choice_, forced
##choice between the two proposals (exactly one chosen in every task; no opt-out).
##The authors flag low-quality respondents (IL `DROP`, 69; US `LQ`, 200) and drop them from their
##analyses; they are KEPT here with cov_low_quality (1 = flagged, 0 = not). The authors' analysed
##N is then 1,101 (IL) and 1,370 (US); the article's own N was not checked (publisher PDF blocked).
##Dropped: rid (US rid are panel UUIDs) and Qualtrics responseid (re-keyed to integers in source row
##order), start/end dates, distribution channel, language, consent, po_domain/po_goal codes (kept
##as text in trial_), policy_ (goal x coercion code), `type` (derived from coercion).
##Covariates from the Stata value labels: cov_gender (IL 0=male/1=female; US 1=male/2=female),
##cov_age_group (band text), cov_education (label text), cov_duration_sec (whole Qualtrics survey,
##durationinseconds); IL also cov_religiosity (Haredi/Religious/Traditional/Secular), cov_ussr
##(born in USSR, no/yes), cov_region, cov_origin; US also cov_region, cov_race, and
##cov_religion_code (Q93) / cov_religiosity_code (Q94), which carry no value labels.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(x) as.character(as_factor(x, levels = "labels"))
build <- function(file, q, ef, extra) {
  s <- as.data.table(read_dta(file.path(raw, file)))
  s[, id := match(responseid, unique(responseid))]
  s[, task := as.integer(proposal %/% 10)][, profile := as.integer(proposal %% 10)]
  stopifnot(s[, .N, .(id, task)][, all(N == 2)], s[, .N, id][, all(N == 16)], all(s$profile %in% 1:2))
  stopifnot(s[, sum(choice_), .(id, task)][, all(V1 == 1)], !anyNA(s$support_))
  stopifnot(s[, uniqueN(coer), .(id, task)][, all(V1 == 2)], s[, uniqueN(po_goal), .(id, task)][, all(V1 == 1)])
  d <- s[, .(id, task, profile, choice = as.integer(choice_), rating = as.integer(support_),
             attr_coercion = lab(coer), attr_public_support = lab(public_support),
             attr_effectiveness = lab(get(ef)), attr_promoter = lab(promoter), attr_implementation = lab(imp),
             cov_gender = c(male = "male", female = "female")[lab(gender)], cov_age_group = lab(age),
             cov_education = lab(edu), cov_duration_sec = as.numeric(durationinseconds),
             cov_low_quality = as.integer(!is.na(get(q)) & get(q) == 1))]
  d <- cbind(d, extra(s))
  d[, trial_domain := lab(s$po_domain)][, trial_goal := lab(s$po_goal)]
  stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_|^cov_gender$")]))
  setorder(d, id, task, profile); d
}
il <- build("Israel Data_Changing the Lens.dta", "DROP", "effect", function(s)
  s[, .(cov_religiosity = lab(relig), cov_ussr = lab(ussr), cov_region = lab(region), cov_origin = lab(origin))])
stopifnot(uniqueN(il$id) == 1170, il[cov_low_quality == 1, uniqueN(id)] == 69)
us <- build("US Data_Changing the Lens.dta", "LQ", "effective_", function(s)
  s[, .(cov_region = lab(region), cov_race = lab(race), cov_religion_code = as.integer(religion),
        cov_religiosity_code = as.integer(religiousity))])
stopifnot(uniqueN(us$id) == 1570, us[cov_low_quality == 1, uniqueN(id)] == 200)
fwrite(il, file.path(out, "treger_2025_policy_tools_il.csv"))
fwrite(us, file.path(out, "treger_2025_policy_tools_us.csv"))
