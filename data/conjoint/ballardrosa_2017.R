##Income-tax plan conjoint (US) from
##Ballard-Rosa, C., Martin, L., & Scheve, K. (2017). The structure of American income tax policy
##preferences. The Journal of Politics, 79(1), 1-16. https://doi.org/10.1086/687324
##Replication data: Harvard Dataverse doi:10.7910/DVN/NGRGS5, CC0 1.0. File read:
##us_fullsurvey_taxplan_level.dta (datafile 2799745; the authors' plan-level file with Stata value
##labels). Read as text only: "Replication BRMS.do". The same data are re-hosted in Leeper, Hobolt &
##Tilley's deposit doi:10.7910/DVN/ARHZU4 (ballard-rosa.dta, held there as a re-host) and ship as
##`taxes` in the cregg R package (the 2,000 revenue-condition respondents).
##Usage: Rscript ballardrosa_2017.R <dir holding the .dta> <output dir>
##
##2,250 US adults (YouGov online survey, June 4-11 2014, starttime/endtime columns), 8 tasks
##(`table` 1-8) of two tax plans (`plan` A = profile 1, B = profile 2), both RECORDED; 36,000 rows.
##Attributes (Stata value labels): the marginal tax rate in six income brackets -- under $10,000
##(0/5/15/25%), $10,000-$35,000, $35,000-$85,000, $85,000-$175,000 (5/15/25/35%), $175,000-$375,000
##(5-45%), over $375,000 (5-55%) -- and the plan's revenue relative to current revenue (5 levels,
##"Much more revenue (>125%)" ... "Much less revenue (<75%)"). Bracket bounds as in the authors' value
##labels (rand_tax_val) and do-file headings; the displayed bracket wording is not in the deposit.
##Arm: 2,000 respondents saw the revenue attribute (saw_revenue = 1; the authors' main analysis
##sample, "$rev_condition") and 250 did not; for those 250 the file still holds a generated revenue
##level, which was not displayed, so attr_revenue is "(not shown)" and trial_saw_revenue = 0.
##Rates and revenue: no randomization restriction is documented; all rate pairs occur (checked for
##the lowest vs highest bracket below). Level weights not documented.
##Outcome: choice = chose_plan (pref_plan A/B; question wording not in the deposit; paraphrase
##"which plan do you prefer"); exactly one plan chosen in every task, no skips, no opt-out.
##Dropped (PII/free text): ID (YouGov caseid, re-keyed to integers in source order), why_chose_plan
##and every *_other / *_open / *_t text field; inputstate (unlabelled FIPS code); start/end dates and
##page timings; the authors' derived dummies, indices and recodes (cj_* dummies, rate_* numeric
##copies, taxrate1-6/taxrev duplicates, *_dum, *_score, age groups, party dummies, etc.); other survey
##items (economic games, life events, parents' jobs, attitudes) are not kept.
##Covariates (value labels of the .dta): cov_survey_weight (weight), cov_birth_year (birthyr),
##cov_age (the authors' age, = 2014 - birthyr), cov_gender (1 Male -> male, 2 Female -> female),
##cov_education (educ label text), cov_party_id (pid3 text: Democrat/Republican/Independent/Other/
##Not sure), cov_party_id7 (pid7 text, incl. "Not sure"), cov_race (race text), cov_ideology
##(conservative_ideology text), cov_hh_income (hh_income, Q27 text; Skipped/Not Asked -> NA),
##cov_attention_pass (attentioncheck_pass 1/0), cov_duration_sec (length: whole survey, seconds;
##equals 60 x the authors' `minutes`).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "us_fullsurvey_taxplan_level.dta")))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
stopifnot(nrow(s) == 36000, uniqueN(s$ID) == 2250, s[, .N, ID][, all(N == 16)])
s[, id := match(ID, unique(ID))]
stopifnot(s[, sum(chose_plan), .(id, table)][, all(V1 == 1)], all(s$plan %in% 1:2), s[, .N, .(id, table, plan)][, all(N == 1)])
stopifnot(s[, uniqueN(saw_revenue), id][, all(V1 == 1)], s[saw_revenue == 1, uniqueN(id)] == 2000)
stopifnot(abs(s$length / 60 - s$minutes) < 1)
d <- s[, .(id, task = as.integer(table), profile = as.integer(plan), choice = as.integer(chose_plan),
  attr_rate_under_10k = lab(taxrate1), attr_rate_10k_35k = lab(taxrate2), attr_rate_35k_85k = lab(taxrate3),
  attr_rate_85k_175k = lab(taxrate4), attr_rate_175k_375k = lab(taxrate5), attr_rate_over_375k = lab(taxrate6),
  attr_revenue = fifelse(saw_revenue == 1, lab(taxrev), "(not shown)"),
  cov_survey_weight = weight, cov_birth_year = as.integer(birthyr), cov_age = as.integer(age),
  cov_gender = c(Male = "male", Female = "female")[lab(gender)], cov_education = lab(educ),
  cov_party_id = lab(pid3), cov_party_id7 = lab(pid7), cov_race = lab(race), cov_ideology = lab(conservative_ideology),
  cov_hh_income = lab(hh_income), cov_attention_pass = as.integer(attentioncheck_pass),
  cov_duration_sec = as.numeric(length), trial_saw_revenue = as.integer(saw_revenue))]
d[cov_hh_income %in% c("Skipped", "Not Asked"), cov_hh_income := NA]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), all(d$cov_gender %in% c("male", "female")))
stopifnot(all(d$cov_age == 2014 - d$cov_birth_year))
stopifnot(d[, uniqueN(paste(attr_rate_under_10k, attr_rate_over_375k))] == 24)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ballardrosa_2017_income_tax.csv"))
