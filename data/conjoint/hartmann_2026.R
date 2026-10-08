##Disaster-policy candidate conjoint (Malawi) from
##Hartmann, F. (2026). Do voters value relief over preparedness? Evidence from disaster
##policies in Malawi. The Journal of Politics. https://doi.org/10.1086/736446
##Replication data: Harvard Dataverse doi:10.7910/DVN/ECUDW4, CC0 1.0. Files read:
##conjoint.rds (long conjoint data) and covariates.rds (one row per respondent, joined by
##CaseID); 0_replication.qmd read as text. The deposit's Afrobarometer, EM-DAT, ND-GAIN and
##EUSpeech files are other inputs to the paper, not read.
##Usage: Rscript hartmann_2026.R <dir holding the two .rds files> <output dir>
##
##805 respondents in Malawi, 6 contests of 2 hypothetical candidates each, 7 attributes.
##task = source `contest`, profile = `candidate` (both recorded). Survey mode, language and
##date are not documented in the deposit, and the article was not read: the respondents
##probably saw Chichewa (or English) wording, but the deposit ships only the author's short
##English factor labels, which are stored as is: prevention effort (No Prevention Effort /
##Prevention Effort), relief effort, prevention effectiveness (Prevention Not Effective /
##Prevention Effective), relief effectiveness (No Relief / Relief Effective), whether the
##candidate asked for relief (Not Ask Relief / Ask Relief), visits (EQ: No Visits / Visits)
##and honesty (No Corruption / Corruption / Vote Buying). Effort and effectiveness were
##crossed freely (e.g. "No Prevention Effort" with "Prevention Effective" occurs 2,270
##times); restrictions and attribute order are not documented. In 30 of 4,830 contests the
##two profiles are identical.
##Outcome: choice = `Choice`, the candidate the respondent supported (qmd axis label:
##"Effect on Probability of Support for Candidate"); exact wording not in the deposit.
##Exactly one profile chosen in every contest (checked); no opt-out.
##Check: OLS of choice on the 7 attributes, SEs clustered by id, reproduces the deposit's
##tab_A4_main_results.tex (effort 0.05/0.09, effective 0.11/0.12, ask 0.12, visits 0.16,
##corruption -0.24, vote buying -0.17; N = 9,660).
##trial_disaster_prime: the respondent's arm in a disaster prime shown before the conjoint
##(control/treatment, covariates.rds). cov_age is age in years. Not kept: gender (0/1 with
##no label; the qmd's own Female/Male recode is commented out), education and income codes
##(no labels), village (location), interview duration, and the other survey items.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(readRDS(file.path(raw, "conjoint.rds")))
cv <- as.data.table(readRDS(file.path(raw, "covariates.rds")))
stopifnot(uniqueN(s$CaseID) == 805, s[, .N, .(CaseID, contest, candidate)][, all(N == 1)],
          s[, .N, CaseID][, all(N == 12)], all(s$Choice == (s$Choosen_Candidate == s$candidate)),
          s[, sum(Choice), .(CaseID, contest)][, all(V1 == 1)], all(s$CaseID %in% cv$CaseID), !anyDuplicated(cv$CaseID))
key <- sort(unique(s$CaseID))
s <- merge(s, cv[, .(CaseID, disaster_prime, age)], by = "CaseID")
d <- s[, .(id = match(CaseID, key), task = as.integer(contest), profile = as.integer(candidate), choice = as.integer(Choice),
           attr_prevention_effort = as.character(Effort_prevention), attr_relief_effort = as.character(Effort_relief),
           attr_prevention_effective = as.character(Effective_prevention), attr_relief_effective = as.character(Effective_relief),
           attr_ask_relief = as.character(Ask), attr_visits = as.character(EQ), attr_honesty = as.character(Honesty),
           trial_disaster_prime = disaster_prime, cov_age = as.integer(age))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "hartmann_2026_disaster_relief.csv"))
