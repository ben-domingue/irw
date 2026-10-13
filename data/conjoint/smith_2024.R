##Supply-chain disclosure law conjoint, 15 countries, from
##Smith, E. K., Kolcava, D., & Bernauer, T. (2024). Stringent sustainability regulations for global
##supply chains are supported across middle-income democracies. Nature Communications, 15, 1049.
##https://doi.org/10.1038/s41467-024-45399-5
##Replication data: Zenodo doi:10.5281/zenodo.18256903 (concept DOI; resolves to 10.5281/zenodo.18256904), CC BY 4.0,
##open access. File read: Smith_Kolcava_Bernauer_DATA.dta (36 MB). Read as text only:
##Smith_Kolcava_Bernauer_Questionnaire.pdf (English instrument, India version), Smith_Kolcava_Bernauer_ANALYSIS.do
##(authors' code, not run).
##Usage: Rscript smith_2024.R <dir holding the .dta> <output dir>
##
##30,004 online respondents in 15 countries (Brazil, Indonesia, India = middle-income; Belgium, Canada, Switzerland,
##Germany, Spain, France, Italy, Japan, South Korea, Netherlands, UK, US = large OECD importers), about 2,000 each.
##INDONESIA EXCLUDED (2,000 respondents; table = 28,004 respondents, 14 countries). In the Indonesian rows, policy_oppose
##(asked only if a respondent opposes both proposals) is 1 exactly when policy_support = 1 on both proposals of the pair
##(1,993 of 10,000 pairs) and policy_support = 0 on both with policy_oppose = 0 in 1,819 more pairs; in the other 14
##countries a pair with policy_oppose = 1 always has policy_support = 0 on both rows and there is no such pair. So
##policy_support looks inverted for a part of the Indonesian sample (Indonesian-language and English versions both affected),
##and the inversion cannot be located for pairs with exactly one proposal supported (those look consistent either way).
##Rather than store an outcome known to be partly reversed, all Indonesian rows are left out; flagged for the authors/Ben.
##Each respondent saw 5 pairs of proposals for a new supply-chain disclosure law (profile 1/2 = the two proposals of
##a pair) with 3 attributes: attr_size (which companies the law applies to, 4 levels), attr_strict (reporting
##requirements, 3 levels), attr_action (what government can do if companies violate them, 3 levels).
##TASK/PROFILE ARE INFERRED: the file has 10 consecutive rows per respondent (300,040 rows = 30,004 x 10 before the exclusion) and no task or
##profile column; task = ceiling(row / 2), profile = 1 or 2 by row order. Row order within a respondent is checked only for
##consistency: policy_oppose (asked per pair) is identical on the two rows of every pair and 1 only when both rows have
##policy_support = 0. Which row was displayed as Proposal A cannot be verified (row order is outcome-independent here).
##TABLE: ONE table with cov_country: the authors pool the 12 OECD countries and analyse BR, ID and IN (ANALYSIS.do
##Fig. 1-3, north_south) on the same design and the same questionnaire, and the attribute levels are one set in the
##English master instrument. Level text = the English instrument's option text (labels in the .dta are short:
##size 1-4, strict 1-3, action 1-3 -> the instrument's options in the order listed). The instrument in the deposit is the
##India version ("India", "$XXX billion" exports are country-adapted); the thresholds (25'000 / 2'500 / 250 / 25
##employees) are stated once and assumed identical in all countries; respondents saw the survey in 12 languages
##(not stored; cov_language is NOT kept).
##Outcome: rating = policy_support, the per-proposal "If you were presented Proposal A [B] today, would you be opposed or
##in favour of it?" (instrument Q9.2/Q9.3), stored 1 = in favour, 0 = opposed (the instrument codes In favour = 0,
##Opposed = 1; the .dta policy_support is 1 for "Yes", and 1 never co-occurs with policy_oppose = 1, so it is "in favour").
##Both proposals can be favoured or both opposed. The forced choice Q9.4 ("Would you rather support
##Proposal A or Proposal B?") is NOT in the deposit, so there is no choice column. 0/1 per proposal that does not pick
##among profiles = a rating (README rule).
##Dropped: policy_oppose, policy_oppose_str, policy_oppose_res (why-opposed-both follow-ups, per pair), cj_pack_treat
##(authors' derived Low/Medium/High package of the profile, used for probe analyses), cj_treat, probe_* , enviro_att_s,
##glob_job_thr_m, ins_trust_m, north_south (derived from country), language, ResponseId (Qualtrics id; ids re-keyed).
##Covariates: cov_country (ISO alpha-2; deposit codes JA, KO, UK -> JP, KR, GB); cov_gender (female, .dta labels
##Male/Female); cov_age_group (the .dta value-label text, e.g. "18-24 years"); cov_educ_years (years of education 0-20,
##as recorded); cov_income_decile (income decile within country, 1-10, missing for about half); cov_left_right (Q13.1,
##1 left - 11 right); cov_enviro_impact (.dta label "Environmental Impacted", 1 strongly disagree - 7 strongly agree;
##the instrument item is Q6.3, "most products in India are made under worse working and environmental conditions
##than ... in Europe or North America", country-adapted; mapping of the label to that item is by position, not stated).
##No survey weight in the file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "Smith_Kolcava_Bernauer_DATA.dta")))
stopifnot(nrow(k) == 300040, uniqueN(k$ResponseId) == 30004)
k[, rid := .GRP, ResponseId]; k[, row := seq_len(.N), rid]
stopifnot(k[, .N, rid][, all(N == 10)], k[, all(diff(rid) >= 0)])
szs <- c("Very large companies - 25'000 employees or more", "Large and very large companies - 2'500 employees or more",
         "Medium sized, large, and very large companies - 250 employees or more", "All companies with 25 employees or more")
sts <- c("Slightly stricter - annual confidential report, no mandatory information",
         "Somewhat stricter - annual confidential report with mandatory summary information",
         "Much stricter - annual public report with mandatory detailed information")
acs <- c("Not take any action - only remind companies of their responsibility",
         "Take somewhat stronger action - put company on public list, moderate financial penalty",
         "Take much stronger action - put company on public list, severe financial penalty, stop buying supplies, press legal charges")
stopifnot(all(k$size %in% 1:4), all(k$strict %in% 1:3), all(k$action %in% 1:3), all(k$policy_support %in% 0:1))
# the .dta value labels must be the short forms of the instrument options, in this order
stopifnot(names(attr(k$size, "labels")) == c("Very large companies", "Large and very large companies",
          "Medium sized, large, and very large companies", "All companies with 25 employees or more"),
          names(attr(k$strict, "labels")) == c("Slightly stricter", "Somewhat stricter", "Much stricter"),
          names(attr(k$action, "labels")) == c("Not change this", "Allow for some government action", "Allow for strong government action"))
k[, pr := (row + 1L) %/% 2L]
stopifnot(k[, uniqueN(policy_oppose), .(rid, pr)][, all(V1 == 1)])
k <- k[country != "ID"]
stopifnot(k[policy_oppose == 1, all(policy_support == 0)], k[, uniqueN(rid)] == 28004)
cc <- c(BE = "BE", BR = "BR", CA = "CA", CH = "CH", DE = "DE", ES = "ES", FR = "FR", ID = "ID", IN = "IN", IT = "IT",
        JA = "JP", KO = "KR", NL = "NL", UK = "GB", US = "US")
k[, rid := match(rid, sort(unique(rid)))]
o <- k[, .(id = as.integer(rid), task = as.integer(pr), profile = as.integer((row - 1L) %% 2L + 1L),
           rating = as.integer(policy_support),
           attr_size = szs[as.integer(size)], attr_strict = sts[as.integer(strict)], attr_action = acs[as.integer(action)],
           cov_country = unname(cc[country]),
           cov_gender = c("male", "female")[as.integer(female) + 1L],
           cov_age_group = as.character(as_factor(age)),
           cov_educ_years = as.integer(educ_years), cov_income_decile = as.integer(income_dec),
           cov_left_right = as.integer(poli_ori), cov_enviro_impact = as.integer(enviro_impact))]
o[cov_age_group == "", cov_age_group := NA]
stopifnot(!anyNA(o$cov_country), !anyNA(o[, .(attr_size, attr_strict, attr_action, rating)]))
setorder(o, id, task, profile)
fwrite(o, file.path(out, "smith_2024_supply_chain.csv"))
