##Candidate-choice conjoint from
##Ferrari, D., & Smith, B. (2025). Status threat, partisanship, and voters' conservative
##shift toward right-wing candidates. Journal of Experimental Political Science, 12(3),
##324-338. https://doi.org/10.1017/xps.2025.10006
##Replication data: Harvard Dataverse doi:10.7910/DVN/AUMLXM, CC0 1.0. File read:
##survey.csv (semicolon-delimited). Wording from the OSF pre-registration (osf.io/q5cha,
##questionnaire.pdf and revised-manuscript.pdf); no code from the deposit was run.
##Usage: Rscript ferrari_2025.R <dir holding survey.csv> <output dir>
##
##ferrari_2025_status_threat: 2,042 white US-born Prolific respondents (the paper reports
##  2,080 interviews collected; the deposit has 2,042, all with 6 complete tasks, which is
##  the analysis sample in the authors' model.log: 510 in the no-party arm), 6 pairs
##  of hypothetical candidates for an open seat in the respondent's district. 7 attributes:
##  party affiliation ("Democratic Party", "Republican Party", or "Independent" in the
##  no-party arm: about a quarter of respondents saw "Independent" on every profile) and
##  one campaign statement on each of 6 issues (affirmative action, abortion, LGBT rights,
##  immigration, redistribution, trade with China). Each issue's liberal/conservative side
##  was drawn with equal probability and then one of 5 statements of that side was shown;
##  attr_* hold the statement TEXT as displayed. The authors' liberal/conservative codes
##  (c_aff_ac etc.) and the count of conservative positions (c_ncons) are derived and
##  dropped: the side of each statement is recoverable from the 60 statements listed in
##  the questionnaire. Issue order was randomized per task (same order for both
##  candidates) but is NOT recorded, so there are no attrpos_ columns.
##  Outcomes: choice = chc_stack, "If you have to choose between these candidates, which
##  one would you choose?" (forced, no opt-out; one chosen per task). rating = chr,
##  "On a scale from 1 to 7, where 1 indicates that you definitely would NOT vote for this
##  type of candidate and 7 indicates that you definitely would vote...", per candidate;
##  higher = more favourable, raw scale kept. profile = 1 for Candidate A, 2 for B.
##  trial_status_threat is the between-respondent vignette arm read before the conjoint
##  (Status reassuring / Racial threat / Nationality threat / Racial and nationality threat).
##  Covariates: cov_gender_code (source `male`, 0/1, kept as codes: the questionnaire
##    (OSF questionnaire.pdf, section B) codes its gender item Male 0 / Female 1 /
##    Neither-other 0, the opposite of the deposit's column name, and 0 would merge female
##    and other, so no source fixes the mapping), cov_party_id (source `pid`, answer text
##    "Democratic voter" / "Republican voter": the partisanship quota, independents
##    excluded; manuscript m.txt L686-689), cov_education (source `educ` 1-5, mapped to
##    the category text of the deposit's us-census.xlsx sheet educ-census, which the
##    authors' model.py census_vs_survey() joins on that code: 1 Less than high school
##    graduate, 2 Complete high school (or equivalent, including GED), 3 Some college or
##    associates degree, 4 Bachelors degree, 5 Graduate or professional degree; collapsed
##    by the authors from the questionnaire's 7 options), cov_inc (1-10, the deposit's
##    codes, higher = more), cov_attention_pass (source chk2_passed: 1 = passed the
##    post-conjoint instructed-response check "Select <random option> in this line",
##    questionnaire section J; the paper keeps failures in its main analysis).
##  Dropped: rid2 (Prolific ID), the deposit's undocumented age and state codes, survey
##  duration, standardized and derived scales, and the attitude batteries.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "survey.csv"), sep = ";")
d <- data.table(id = as.integer(s$rid) + 1L, task = as.integer(s$task), profile = match(s$cand, c("A", "B")),
                choice = as.integer(s$chc_stack), rating = as.integer(s$chr))
stopifnot(all(d$choice == as.integer(s$chc == d$profile)))
d[, attr_party := s$c_party_affiliation]
iss <- c(aff_ac = "affirmative_action", abortion = "abortion", lgbt = "lgbt_rights", immig = "immigration",
         red = "redistribution", trade = "trade_china")
for (v in names(iss)) d[, paste0("attr_", iss[[v]]) := s[[paste0("c_", v, "_s")]]]
stopifnot(all(s$pid %in% c("Democratic voter", "Republican voter")), all(s$educ %in% 1:5), all(s$chk2_passed %in% 0:1))
educ <- c("Less than high school graduate", "Complete high school (or equivalent, including GED)",
          "Some college or associates degree", "Bachelors degree", "Graduate or professional degree")
d[, cov_gender_code := as.integer(s$male)][, cov_party_id := s$pid]
d[, cov_education := educ[as.integer(s$educ)]][, cov_inc := as.integer(s$inc)][, cov_attention_pass := as.integer(s$chk2_passed)]
d[, trial_status_threat := s$status_threat]
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "ferrari_2025_status_threat.csv"))
