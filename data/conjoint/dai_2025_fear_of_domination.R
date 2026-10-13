##International-organisation (IO) paired conjoint, US MTurk, Dec 2020, from the
##figshare deposit "How Fear of Domination Affects Public Support for International
##Organizations: A Conjoint Experiment Approach", doi:10.6084/m9.figshare.29857265, CC BY 4.0.
##Deposit author: Shih-chan Dai. File read: conjoint.dta (one file; no codebook, no README, no article linked in the
##deposit). Usage:
##  Rscript dai_2025_fear_of_domination.R <dir holding data.dta (conjoint.dta renamed)> <output dir>
##
##1,633 US adults (Amazon Mechanical Turk, December 2020 per the deposit description), 9 paired
##tasks each (stimulus 1-18 per respondent; stimuli 2k-1 and 2k form task k). Verified: in every
##one of the 14,697 pairs exactly one stimulus has binarychoice = 1, so forced choice, no opt-out.
##Position is recorded: the per-pair columns io_ab, io_cd, ... name the chosen IO as
##"International Organization A/B, C/D, ..."; stimulus 2k-1 = first IO of the pair (A, C, ...)
##and the choice flags agree (binarychoicea ... binarychoicer mark the chosen stimulus).
##Outcome wording is NOT in the deposit (the description speaks of "support for an IO").
##Attributes (level text = the source's own short labels; the deposit has no codebook, and the
##full wording the respondents saw is not recoverable; the description names the aspects as the
##actor that mainly funds the IO, the issue focus, US financial contributions and the decision
##rule): top_donor (China / EU / Equal), issue (Development / Migration / No Issue),
##us_involvement (Yes / No), decision (Majority / A Few). Derived dummies (chinatop, eutop, ...)
##and numeric recodes dropped.
##Randomization: usinvolve and decision are NOT independent in the data (No x A Few 4,899
##rows, No x Majority 9,798, Yes x A Few 9,798, Yes x Majority 4,899), top_donor x issue is
##exactly balanced (3,266 each): restrictions 'observed'.
##Covariates (the control_* text columns): cov_gender, cov_age_group, cov_education, cov_party_id
##(Democrat/Republican/Independent/Other), cov_income (text band), cov_race, cov_region,
##cov_ideology (control_poliview), cov_duration_sec (survey duration).
##Dropped: dates, consent/acknowledgement items, attention-like text items (e2test), threat and
##party-feeling items. The respondent column is a plain 1..1633 index, kept as id.
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(s) == 29394, s[, .N, respondent][, all(N == 18)], s[, all(stimulus == seq_len(.N)), respondent][, all(V1)])
s[, `:=`(task = (stimulus + 1L) %/% 2L, profile = 2L - stimulus %% 2L)]
stopifnot(s[, sum(binarychoice), .(respondent, task)][, all(V1 == 1)])
d <- s[, .(id = as.integer(respondent), task = as.integer(task), profile = as.integer(profile), choice = as.integer(binarychoice),
  attr_top_donor = topdonor, attr_issue = issue, attr_us_involvement = usinvolve, attr_decision = decision,
  cov_gender = c(Female = "female", Male = "male")[control_gender], cov_age_group = control_age,
  cov_education = control_education, cov_party_id = control_partyid, cov_income = control_income,
  cov_race = control_race, cov_region = control_location, cov_ideology = control_poliview,
  cov_duration_sec = as.integer(durationinseconds))]
stopifnot(!anyNA(d[, 1:8]), d[, uniqueN(attr_top_donor)] == 3, !anyNA(d$cov_gender))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "dai_2025_fear_of_domination.csv"))
