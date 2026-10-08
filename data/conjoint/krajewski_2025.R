##Criminal-opportunity choice conjoint (US) from
##Krajewski, A. T., Pickett, J. T., & Jacobs, B. A. (2025). How people choose between criminal
##opportunities. Criminology, 63(3), 639-660. https://doi.org/10.1111/1745-9125.70006
##Replication data: Harvard Dataverse doi:10.7910/DVN/8DCXQF, CC0 1.0. File read:
##CrimeOpportunitiesConj-ReplicationData.dta (Dataverse "original format" download). The
##authors' .do file (CrimeOpportunitiesConj-Analysis.do) was read as text, not run. The article is
##paywalled and was not read; no codebook or questionnaire ships.
##Usage: Rscript krajewski_2025.R <dir holding the .dta> <output dir>
##
##1,000 respondents ("national sample" per the abstract; country not stated in the deposit, payouts in dollars), 5 tasks of 2 hypothetical criminal opportunities,
##7 attributes. The article's abstract reports N = 1,023; the deposit holds 1,000 (gap not
##explained in the deposit; not fixed here). The file has NO task or profile column: each
##respondent has exactly 10 contiguous rows, and consecutive row pairs form a task (in all
##4,982 answered pairs exactly one profile is chosen, and the 18 unanswered pairs are missing
##on both rows), so task and profile are INFERRED from row order. The 18 unanswered tasks
##(36 rows) are omitted.
##Outcome: choice = cj1_chosen, Stata label "Criminal opportunity chosen"; the question wording
##is not in the deposit. Forced choice between the two opportunities: no opt-out in the data.
##Attribute text = the Stata value labels (victim; number of people involved; completion time;
##your payout; time until payout; chance of arrest; possible punishment), e.g. "Takes minutes",
##"$500", "Less than 1%". Whether these are the exact displayed strings is not verifiable
##from the deposit. Randomization restrictions and attribute order are not documented; every
##pair of attribute levels co-occurs and level shares look uniform.
##Covariates kept (the underlying items are not deposited): cov_selfcontrol_avg (mean of the
##self-control items, 0-4), cov_prior_offending (offenderD, 1 = prior offending),
##cov_attention_passed (1 = passed all attention checks; the authors do not filter on it).
##Dropped: the authors' derived attribute dummies (victimD, victim_indiv, victim_biz,
##peopleinvolvedD, peopleinvolved_group, timeuntilpayoutD, possiblepunishmentD).
##The id column is a Stata-generated respondent number (not a platform id).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "CrimeOpportunitiesConj-ReplicationData.dta"))
r <- rle(as.vector(k$id)); stopifnot(all(r$lengths == 10), !anyDuplicated(r$values))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
d <- data.table(id = as.integer(k$id))
d[, r := seq_len(.N), id][, task := (r + 1L) %/% 2L][, profile := 2L - r %% 2L][, r := NULL]
d[, choice := as.integer(k$cj1_chosen)]
for (v in c("victim", "peopleinvolved", "completiontime", "yourpayout", "timeuntilpayout", "chanceofarrest", "possiblepunishment"))
  d[, paste0("attr_", v) := lab(v)]
d[, `:=`(cov_selfcontrol_avg = as.numeric(k$selfcontrol_avg), cov_prior_offending = as.integer(k$offenderD),
         cov_attention_passed = as.integer(k$attentioncheck))]
stopifnot(d[, .(n = sum(is.na(choice))), .(id, task)][, all(n %in% c(0L, 2L))])
d <- d[!is.na(choice)]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "krajewski_2025_criminal_opportunities.csv"))
