##Policy discounting conjoint (UK, qualitative-delay version only) from
##Barnfield, M. (2026). Policy discounting across and beyond the lifespan. [Research note,
##Cambridge University Press; article DOI not verified, so left blank in the dictionary row.]
##Replication data: UK Data Service ReShare SN 856886, doi:10.5255/UKDA-SN-856886. Licence: the
##catalogue page marks the data file 856886_data.zip as CC BY 4.0 (the page's Terms and
##conditions text is generic; this licence was read from the licence icon beside the data file).
##Files read: 856886_data_ukds.csv (from 856886_data.zip), codebook_ukds.csv, the UKDS readme.
##Usage: Rscript barnfield_2023_policy_discounting.R <dir holding 856886_data_ukds.csv> <output dir>
##
##2,405 UK adults on Prolific (17 April 2023), blocked by age group (20-34, 35-54, 55+, ~800
##each); each saw 8 pairs of policies "focused on saving lives" and chose one (wording per the
##paper; the deposit gives none: "which would you choose if you had the choice", paraphrase).
##Forced choice, no opt-out. Four attributes: lives saved (500 / 1,000 / 5,000 / 10,000 /
##100,000), policy area (healthcare, security, environmental protection, natural disaster
##prevention), total cost (GBP 10 / 50 / 100 / 500 million), delay of payoff. No restrictions
##stated in the paper; level_weights uniform is NOT claimed.
##VERSIONS. Each respondent saw one of two versions (column `version`, constant within
##respondent). Qualitative: the delay is a statement of whether benefits arrive within,
##shortly beyond or far beyond the respondent's lifetime (qualdelay = those three categories).
##Quantitative: the delay is a NUMBER OF YEARS (paper: 10, 30, 50, 65, 100 ...); the deposit
##stores only the category in `qualdelay` for them, not the years shown. Only the QUALITATIVE
##version is built here, because there the stored category is the displayed statement; the
##quantitative rows (displayed text not recoverable) are dropped. This leaves
##the respondents of the qualitative version (count in the validator line).
##Task and profile are recorded (task 1-8; profile A/B -> 1/2); `choice` 1/2 agrees with the
##`chosen` flag on every row. 38 respondents have 7 tasks and 1 has 4 (skipped tasks; 116
##missing observations in the paper), kept as is.
##Covariates: cov_age (years; 112 rows NA), cov_age_group (blocking group text), cov_gender_code
##(0/1 undocumented in the codebook). Dropped: ib, tf, lr and their tercile categories (derived
##scales), pair id, version after filtering.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "856886_data_ukds.csv"), encoding = "UTF-8")
stopifnot(nrow(s) == 38396, uniqueN(s$id) == 2405, s[, uniqueN(version), id][, all(V1 == 1)],
          s[, all(((profile == "A" & choice == 1) | (profile == "B" & choice == 2)) == (chosen == 1))])
s <- s[version == "qualitative"]
stopifnot(s[, sum(chosen), .(id, task)][, all(V1 == 1)], !anyNA(s[, .(task, profile, lives, policy, cost, qualdelay)]))
d <- s[, .(id = as.integer(id), task = as.integer(task), profile = match(profile, c("A", "B")), choice = as.integer(chosen),
  attr_lives_saved = lives, attr_policy_area = policy, attr_cost = cost, attr_delay = qualdelay,
  cov_age = as.integer(age), cov_age_group = age_grp, cov_gender_code = as.integer(gender))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnfield_2023_policy_discounting.csv"))
