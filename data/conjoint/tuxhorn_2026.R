##Canadian tax-policy conjoint (vertical, horizontal and exchange equity), from the deposit "Replication package: Balancing Fairness: Public Evaluations of
##Vertical, Horizontal, and Exchange Equity in Tax Policy" (depositor Kim-Lee Tuxhorn per the Mendeley contributor record; no article DOI located 2026-11-10; deposit created 2026-10-15)
##(Mendeley Data doi:10.17632/t7dx92jmcz.1, CC BY 4.0).
##Files read: "Survey data and statistical analysis /tax_fairness_conjoint_data.dta" (long format, 10 rows per respondent), Tax_Fairness_Codebook.docx (value labels, read as text
##from the docx XML), Tax_Fairness_replication_script.do (read as text), and the survey export PDF "context_original-survey.pdf" (question wording).
##Usage: Rscript tuxhorn_2026.R <dir holding the .dta> <output dir>
##
##Canadian online sample (probability-weighted; post-stratification weight wgt1), 1,573 respondent ids in the file; 5 paired comparisons of two tax policies, each profile with
##three randomized attributes shown as sentences: vertical equity (poor pays 20% of income in taxes, rich pays 16/20/24/28/32%), horizontal equity (one pays 20% of income, the
##other pays 20/16/12/8/4%), exchange equity (a taxpayer receives $60/$80/$100/$120/$140 in government benefits and services). Level text = the Stata value labels / codebook
##(attr_vertical_equity, attr_horizontal_equity, attr_exchange_equity). Fully crossed 5 x 5 x 5, levels drawn from a Qualtrics CBC design (feature0-2 fields in the survey export).
##Outcomes on the same pairs (forced, exactly one per pair, no opt-out): choice = fair_policy "Which tax policy do you think is more fair?" (DC24-DC27, DC46; Tax Policy 1 / Tax Policy 2; the
##authors' main outcome) and choice_preferred = preferred_policy_profile "Would you prefer Canada to adopt Tax Policy 1 or Tax Policy 2?" (C1-C5). Respondents' answers to the two questions
##differ in 322 of 6,126 tasks.
##Missing data: 309 respondents (3,090 rows) have no attribute levels and no weight (they did not reach the conjoint) and are omitted; for 194 further tasks both outcomes are 0 on both
##profiles (neither question answered) and these tasks are dropped (the authors' fair_policy_limited is NA there); 20 respondents with no answered task are omitted. Result: 1,244
##respondents with 6,126 tasks x 2 profiles (the authors' main regression sample uses these 6,126 tasks, n = 12,252 rows).
##Attribute order: the codebook says `flipped` (1 = survey version with the order of the three dimensions reversed, 0 = original); which order is the original is not documented in the deposit and
##the assignment of version is not documented, so attr_order is unknown, there are no attrpos_ columns, and flipped is kept as trial_flipped.
##Authors' analysis sample: weighted regressions on all rows with attributes and weight (no duration cut, no attention check: `long_duration` is only a subgroup indicator; the codebook
##notes survey duration runs 10 to 489,331 seconds); no respondent beyond the structural drops above is removed. cov_duration_sec is kept.
##Covariates: cov_survey_weight (wgt1, post-stratification, mean about 1), cov_province (value labels), cov_age (years, age_years), cov_woman (1 = self-identified woman, 0 otherwise; the codebook
##does not label the gender codes, so cov_gender is not used), cov_education_code (codes 1-6, no labels in the file), cov_party_id_code (1 Liberal, 2 Conservative, 3 NDP per the codebook; 4-7 unlabeled),
##cov_ideology (0 left .. 10 right), cov_income_code (1-8, higher = higher household income, 8 = nonresponse per the codebook), cov_trust_others and cov_trust_federal (1 Never, 2 Once in a while, 3 Most
##of the time, 4 Always -> text), cov_success_is_luck (Hard work / Luck), cov_duration_sec. Dropped: responseid (platform response id, re-keyed), free-text and language fields, derived dummies and subgroup
##indicators (trust/ideology/age/income groups, knowledge flags), ISCED regrouping, Stata province dummies. PII FOUND: none (anonymous case_id; responseid dropped).
##Respondent count vs paper: not checked (paper not located); 1,573 ids in the file, 1,264 with a conjoint, 1,244 with an answer.
suppressMessages({library(data.table); library(haven)})
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "tax_fairness_conjoint_data.dta")))
stopifnot(nrow(d) == 15730, d[, uniqueN(case_id)] == 1573)
d[, has := !is.na(vertical) & !is.na(horizontal) & !is.na(exchange)]
stopifnot(d[, all(is.na(wgt1) == !has)])
d <- d[has == TRUE]
d[, `:=`(f = as.integer(fair_policy), p = as.integer(preferred_policy_profile))]
tk <- d[, .(nf = sum(f), np = sum(p), n = .N), .(case_id, contest)]
stopifnot(all(tk$n == 2), all(tk$nf %in% 0:1), all(tk$np == tk$nf))
d <- merge(d, tk[nf == 1, .(case_id, contest)], by = c("case_id", "contest"))
stopifnot(nrow(d) == 12252)
lab <- function(v) as.character(as_factor(d[[v]]))
tr <- function(v, m) unname(m[as.character(as.integer(d[[v]]))])
d[, `:=`(attr_vertical_equity = lab("vertical"), attr_horizontal_equity = lab("horizontal"), attr_exchange_equity = lab("exchange"))]
stopifnot(!anyNA(d$attr_vertical_equity), !anyNA(d$attr_horizontal_equity), !anyNA(d$attr_exchange_equity))
d[, `:=`(id = as.integer(factor(case_id)), task = as.integer(contest), profile = as.integer(profile_num), choice = f, choice_preferred = p)]
trustl <- c("1" = "Never", "2" = "Once in a while", "3" = "Most of the time", "4" = "Always")
d[, `:=`(cov_survey_weight = round(as.numeric(wgt1), 6), cov_province = lab("province"), cov_age = fifelse(age_years >= 18 & age_years <= 100, as.integer(age_years), NA_integer_),
         cov_woman = as.integer(Woman), cov_education_code = as.integer(education), cov_party_id_code = as.integer(party), cov_ideology = as.integer(ideology_1),
         cov_income_code = as.integer(income), cov_trust_others = tr("trust_others", trustl), cov_trust_federal = tr("trust_federal", trustl),
         cov_success_is_luck = tr("luckvhardwork", c("0" = "Hard work", "1" = "Luck")), cov_duration_sec = as.integer(round(durationinseconds)), trial_flipped = as.integer(flipped))]
nm <- c("id", "task", "profile", "choice", "choice_preferred", "attr_vertical_equity", "attr_horizontal_equity", "attr_exchange_equity", grep("^cov_", names(d), value = TRUE), "trial_flipped")
d <- d[, ..nm]; setorder(d, id, task, profile)
fwrite(d, file.path(out, "tuxhorn_2026_tax_equity.csv"))
cat(nrow(d), d[, uniqueN(id)], d[, .N, .(task)][, N], "\n")
