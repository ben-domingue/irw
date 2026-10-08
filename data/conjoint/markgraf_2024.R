##Credit-and-welfare policy conjoint (England) from
##Markgraf, J., & Rosas, G. (2024). Borrowing to self-insure? Credit access and support for
##welfare. The Journal of Politics, 86(2), 642-655. https://doi.org/10.1086/726924
##Replication data: Harvard Dataverse doi:10.7910/DVN/UMBLQS, CC0 1.0, no restricted files,
##no terms. File read: cleanedConjointData.csv, which is an R serialized data frame (gzip RDS)
##despite its name; read with readRDS. CODEBOOK.html and the authors' analyze-conjoint_data.R /
##pap_analysis.R were read as text. The article (paywalled) was NOT read: question wording,
##profile labels, survey firm and dates are not documented here.
##Usage: Rscript markgraf_2024.R <raw dir> <output dir>
##
##Codebook: "an original survey with a conjoint experiment on credit access in England",
##1,286 respondents (ResponseID), paired tasks. Each profile is a policy package of five
##attributes, three levels each (codebook names; levels as deposited):
##  attr_mortgage_rate: "Mortgage loans (average interest rate)" 2% / 6% / 10%
##  attr_credit_card_rate: "Credit card loans (average interest rate)" 5% / 15% / 25%
##  attr_social_assistance: "Social assistance for low income families" None / 33% of average
##    income / 66% of average income
##  attr_unemployment_insurance: "Unemployment insurance" 0 months / Up to 12 months / Up to 24
##    months
##  attr_income_tax: "Fiscal burden (average income tax)" 15% tax / 25% tax / 35% tax
##choice: forcedChoice (1 = the package chosen), one chosen per pair (checked); the authors
##  call it a forced choice: no opt-out. Wording not in the deposit (paraphrase in the record).
##task = the round suffix of taskId (".r1".."r6"), 6 paired tasks per respondent (recorded).
##  The numeric part of taskId collides across respondents for 60 ids, so tasks are keyed by
##  respondent x round. profile is INFERRED: the source has no profile/position column and the
##  rows of a pair are not adjacent (the file is shuffled), so profile 1/2 = order of appearance
##  in the file and carries NO screen-position information.
##Randomization: not documented in the deposit; every pair of levels occurs, with near-equal
##  counts.
##Covariates (the authors' coded respondent variables, codebook definitions): cov_lr_self (0-10
##  left-right self-placement), cov_income_group (income.cat: High Income > 32,824 GBP net
##  household income, Low Income < 15,392, Middle Class otherwise), cov_higher_education
##  (educ.cat text), cov_unemployment_risk (unempRisk3.cat: Low Risk = 1-2, High Risk = 4-5 on
##  the 1-5 job-loss likelihood question; as deposited, no NA), cov_welfare_benefit (wlfrBenefit
##  1 = ever relied on government support), cov_precarious_employment (precEmpl 1 = not employed
##  full-time), cov_homeowner (howner), cov_credit_experience (expLoan.cat text),
##  cov_credit_access (crdtAccess 1-5, the "how difficult or easy has it been for you to obtain a
##  loan" answer as stored; the codebook's crdtAccess2 calls 1-2 "Easy"; NA = no credit
##  experience), cov_crisis_losses (expFinCrisis.cat text), cov_high_unemployment_sector
##  (highUnemp, Rehm 2009 occupational rates).
##Dropped: Qualtrics ResponseId (re-keyed to integers), duplicate/combined recodes
##  (unempRisk.cat, incomeRisk.cat, lr.cat, round.cat), the per-profile flag atypicalProfile.
##N = 1,286 respondents, 15,432 rows, as in the codebook (article not read).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x <- as.data.table(readRDS(file.path(raw, "cleanedConjointData.csv")))
stopifnot(uniqueN(x$ResponseId) == 1286)
x[, task := as.integer(sub("^.*\\.r", "", taskId))]
x[, profile := seq_len(.N), .(ResponseId, task)]
stopifnot(x[, .N, .(ResponseId, task)][, all(N == 2)], x[, sum(forcedChoice), .(ResponseId, task)][, all(V1 == 1)],
          x[, uniqueN(task), ResponseId][, all(V1 == 6)])
ids <- sort(unique(x$ResponseId))
d <- x[, .(id = match(ResponseId, ids), task, profile, choice = as.integer(forcedChoice),
           attr_mortgage_rate = as.character(mrtg.crdt), attr_credit_card_rate = as.character(consum.crdt),
           attr_social_assistance = as.character(welfare), attr_unemployment_insurance = as.character(unempl),
           attr_income_tax = as.character(tax),
           cov_lr_self = as.integer(lrscale), cov_income_group = income.cat, cov_higher_education = educ.cat,
           cov_unemployment_risk = unempRisk3.cat, cov_welfare_benefit = as.integer(wlfrBenefit),
           cov_precarious_employment = as.integer(precEmpl), cov_homeowner = as.integer(howner),
           cov_credit_experience = expLoan.cat, cov_credit_access = as.integer(crdtAccess),
           cov_crisis_losses = expFinCrisis.cat, cov_high_unemployment_sector = highUnemp)]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "markgraf_2024_credit_welfare.csv"))
