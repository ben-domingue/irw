##PAC-contribution candidate vignette (CCES 2020, UC Riverside module) from
##Landgrave, M., Jenkins, N. R., & Hardesty, A. J. (2025). Do congressional candidates benefit
##from rejecting PAC contributions? Evidence from a pre-registered candidate evaluation survey
##experiment. Research & Politics, 12(3). https://doi.org/10.1177/20531680251383284
##Replication data: Harvard Dataverse doi:10.7910/DVN/HEVWIG, CC0 1.0, no restricted files, no
##terms. File read (inside the deposit's zip): CCES20_UCR_OUTPUT.DTA (the raw module data; the
##authors' Analysis.DTA only adds recodes). Level text, outcome labels and covariate codes are
##the value labels of the .dta, identical to CCES20_UCR_OUTPUT_codebook.txt (deposited).
##Usage: Rscript landgrave_2025.R <dir holding CCES20_UCR_OUTPUT.DTA> <output dir>
##
##1,000 YouGov respondents (2020 CCES team module, fielded 2020-09-29 to 11-02), one candidate
##vignette each (task = profile = 1). Three attributes randomized (the authors' "pre-registered
##candidate evaluation survey experiment", 2 x 3 x 2):
##  attr_pac_contributions  "Campaign doesn't accept contributions from political action
##                          committees" / "Campaign accepts contributions from political action
##                          committees" (CCP_con)
##  attr_prior_experience   "No prior experience in elected office" / "Previously Elected
##                          Councilmember" / "Previously Elected Mayor" (PEO_con)
##  attr_gender             Male / Female (CG_con)
##The candidate's party (UCR325_con, Democratic/Republican) is NOT randomized for partisans: it
##equals the respondent's pid3 for every Democrat and Republican (checked below) and varies only
##for independents/other/not sure. It is kept as trial_candidate_party (displayed, but
##respondent-assigned), not as an attribute.
##The vignette text and the question wording are not deposited, and the article (Sage) could
##not be read: level text is the value-label text, which may be a short form of the prose shown;
##presentation is unknown. Outcomes (codebook variable descriptions only, so wording is a
##paraphrase), 7-point, stored RAW as in the source, where LOWER = more favourable:
##  rating_vote   UCR326 "Vote likelihood": 1 Very Likely .. 4 Neither Unlikely nor Likely ..
##                7 Very Unlikely
##  rating_donate UCR327 "Donation likelihood": same labels
##  rating_trust  UCR328 "Candidate trustworthiness": 1 Very Trustworthy .. 4 Neither
##                Untrustworthy nor Trustworthy .. 7 Very Untrustworthy (code 5 is labelled
##                "Slightly Unlikely" in the source, evidently for "Slightly Untrustworthy")
##The authors reverse all three (Clean Up.do: DV_* = 8 - code). Code 98 "skipped" -> NA (2, 5, 3
##respondents); no respondent skipped all three, so all 1,000 are kept. No opt-out (ratings).
##Covariates: cov_survey_weight = teamweight (CCES team-module weight); cov_gender (gender 1 Male
##= male, 2 Female = female); cov_birth_year (birthyr); cov_education (educ label text); cov_race
##(race label text); cov_party_id (pid3 label text; "Not sure" kept as text); cov_party_id7 (pid7
##label text); cov_state (inputstate label text). Everything else in the module file is dropped,
##including zip codes (inputzip, regzip: PII), CCES panel ids (caseid; re-keyed to 1..1000),
##free-text verbatims and the other CCES common-content items. No attention check, no repeat.
##N = 1,000 (998/995/997 non-missing for vote/donate/trust; authors' log the same). Spot check:
##OLS of 8 - rating_vote on the three attributes gives accepts PAC -0.631, councilmember 0.606,
##mayor 0.483, female 0.338 = the authors' Replication.smcl (Figure 1, Vote).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "CCES20_UCR_OUTPUT.DTA"))
lab <- function(x) { l <- attr(x, "labels"); v <- as.numeric(zap_labels(x)); stopifnot(all(v %in% l | is.na(v))); unname(names(l)[match(v, l)]) }
stopifnot(all(k$CCP_con %in% 1:2), all(k$PEO_con %in% 1:3), all(k$CG_con %in% 1:2), all(k$UCR325_con %in% 1:2))
# partisans always see their own party
stopifnot(all(zap_labels(k$UCR325_con)[k$pid3 %in% 1:2] == zap_labels(k$pid3)[k$pid3 %in% 1:2]))
rat <- function(x) { x <- as.integer(zap_labels(x)); stopifnot(all(x %in% c(1:7, 98, NA))); fifelse(x %in% 98L, NA_integer_, x) }
d <- data.table(id = as.integer(rank(k$caseid)), task = 1L, profile = 1L,
                rating_vote = rat(k$UCR326), rating_donate = rat(k$UCR327), rating_trust = rat(k$UCR328),
                attr_pac_contributions = c("Campaign doesn’t accept contributions from political action committees",
                                           "Campaign accepts contributions from political action committees")[as.integer(k$CCP_con)],
                attr_prior_experience = c("No prior experience in elected office", "Previously Elected Councilmember",
                                          "Previously Elected Mayor")[as.integer(k$PEO_con)],
                attr_gender = c("Male", "Female")[as.integer(k$CG_con)],
                trial_candidate_party = c("Democratic", "Republican")[as.integer(k$UCR325_con)])
stopifnot(uniqueN(d$id) == nrow(d), d[, all(!(is.na(rating_vote) & is.na(rating_donate) & is.na(rating_trust)))])
stopifnot(all(k$gender %in% 1:2))
d[, `:=`(cov_survey_weight = as.numeric(k$teamweight), cov_gender = c("male", "female")[as.integer(k$gender)],
         cov_birth_year = as.integer(k$birthyr), cov_education = lab(k$educ), cov_race = lab(k$race),
         cov_party_id = lab(k$pid3), cov_party_id7 = lab(k$pid7), cov_state = lab(k$inputstate))]
for (v in c("cov_education", "cov_race", "cov_party_id", "cov_party_id7", "cov_state"))
  d[get(v) %in% c("skipped", "not asked"), (v) := NA_character_]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "landgrave_2025_pac_contributions.csv"))
