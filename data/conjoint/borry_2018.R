##Factorial vignette experiment (Study 2) on rule formalization x rule consistency and rule following from
##Borry, E. L., DeHart-Davis, L., Kaufmann, W., Merritt, C. C., Mohr, Z., & Tummers, L. (2018). Formalization and consistency
##heighten organizational rule following: Experimental and survey evidence. Public Administration, 96(2), 368-385.
##https://doi.org/10.1111/padm.12407
##Replication data: Harvard Dataverse doi:10.7910/DVN/V7SULP, CC0 1.0. Files read: "Study 2 data" (Stata original, saved locally as s2.dta)
##and "Study 2 do-file" (s2.do; text, not run). Study 1 (N = 75, below the 100-respondent minimum) and Study 3 (a survey, N = 713) are not built.
##Usage: Rscript borry_2018.R <dir holding s2.dta> <output dir>
##
##150 respondents (Study 2), one vignette each, 2 x 2 between-subject (37-38 per cell): Written (Unwritten / Written) x Consistent
##(Inconsistent / Consistent), the rule's formalization and how consistently it is enforced. Attribute level text is the Stata VALUE
##LABEL stored in the deposit; the vignette wording is NOT in the deposit and the article (Wiley, 403) could not be retrieved, so
##the level text is the labels only (LABELS: tags only; flag for Ben, ruling 10-13). The Four_Groups_Green_Tape variable agrees with Written x Consistent.
##Outcome: Rulebreaking, 0 = "Rule following", 1 = "Rulebending" (the value labels). It is a 0/1 judgement of what the respondent would do
##under the vignette rule, not a pick among profiles, so it is stored as rating_rulebending (raw, 1 = rule bending; higher = more rule bending).
##No opt-out. Question wording not in the deposit.
##Covariates: cov_gender (Male/Female per the labels), cov_age (years; 1 missing). Dropped: Number (the authors' respondent number; re-keyed to
##row order), Year_born (two-digit), WC1_Wi0, WC1_UC0, WC_UI (the authors' contrast dummies), Four_Groups_Green_Tape (derived).
##Sample: not described in the deposit (ages 28-66).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- as.data.table(read_dta(file.path(raw, "s2.dta")))
stopifnot(nrow(d) == 150, all(d$Rulebreaking %in% 0:1), all(d$Written %in% 0:1), all(d$Consistent %in% 0:1))
stopifnot(all(d$Four_Groups_Green_Tape == 1 + d$Consistent + 2 * d$Written))
r <- d[, .(id = .I, task = 1L, profile = 1L, rating_rulebending = as.integer(Rulebreaking),
  attr_formalization = c("Unwritten", "Written")[Written + 1L], attr_consistency = c("Inconsistent", "Consistent")[Consistent + 1L],
  cov_gender = c("male", "female")[Gender + 1L], cov_age = as.integer(Age))]
setorder(r, id, task, profile)
fwrite(r, file.path(out, "borry_2018_rule_following.csv"))
