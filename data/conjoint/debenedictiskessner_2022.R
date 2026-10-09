##Opioid-user news-story factorial vignette from
##de Benedictis-Kessner, J., & Hankinson, M. (2022). How the identity of substance users shapes
##public opinion on opioid policy. Political Behavior, 46(1), 609-629 (2024).
##https://doi.org/10.1007/s11109-022-09845-8
##Replication data: Harvard Dataverse doi:10.7910/DVN/QMVU0Z, CC0 1.0. File read:
##opioids_identity_recoded.rds. Wording from the article's Online Appendix A-B
##(11109_2022_9845_MOESM1_ESM.pdf, Springer ESM); the authors' opioids_identity_analysis.R read as text.
##Usage: Rscript debenedictiskessner_2022.R <dir holding the .rds> <output dir>
##
##NORC AmeriSpeak, June 2019, web, n = 3,112 US adults (as in the paper). Each respondent read ONE
##news story (task = 1, profile = 1) about a recovering opioid user with a photo of a hand holding
##pills or a needle, and five randomized attributes ("full randomization that allowed each attribute
##to take one value with no restrictions based on other attribute values", Appendix B):
##  attr_race      Black / White: shown by the name and a dark- or light-skinned hand in the photo
##                 (authors' coding, from P_VIG "Black woman" etc.)
##  attr_gender    woman / man: shown by the name and he/she pronouns throughout (authors' coding, P_VIG)
##  attr_location  P_GEO, the CONTEXT slot as displayed: a rural farm / a quiet suburb / an urban downtown center
##  attr_pathway   the PATHWAY sentence. The deposit stores it truncated at 120 characters (P_PATHA); the
##                 full text is taken from Appendix B, in its his/her form (respondents saw the pronouns
##                 of their randomized gender). The photo showed pills for the two OxyContin pathways and
##                 a needle for heroin (Appendix B), so it adds no separate attribute.
##  attr_insurance the INSURANCE slot (P_PATHI, as stored; Appendix B prints it lower-case)
##The name itself is not in the deposit. Appendix B lists two names per race x gender cell, one from the
##lowest and one from the highest education quartile (Gaddis 2017); P_RNAME (High/Low) appears to record
##that draw and is kept as trial_name_quartile without mapping it to names (the pairing is not documented).
##Outcomes (Appendix A; order of Q1 and Q2 randomized, trial_question_order = DOV_ORDER):
##  rating_treatment   Q1 "If you were making up the budget for the federal government this year, would you
##                     increase, decrease, or keep spending the same for treatment for those addicted to opioids?"
##  rating_enforcement Q2, same stem, "... for law enforcement to arrest and prosecute those addicted to opioids?"
##                     both 1 Increase a lot, 2 Increase a little, 3 Keep the same, 4 Decrease a little,
##                     5 Decrease a lot (the source factor's code order; higher = less spending)
##  rating_blame       Q4 "Would you agree or disagree that individuals addicted to opioids are to blame for
##                     their own addiction?" 1 Strongly agree .. 5 Strongly disagree (factor code order;
##                     higher = less blame)
##"SKIPPED ON WEB" is NA (DON'T KNOW / REFUSED never occur). Q3 (a favourable/unfavourable item the authors
##call aca_support) is dropped: its wording is not in the appendix or the deposit. Manipulation checks M1-M5
##(two random checks per respondent) and the authors' recodes (*_bi, 0-1 rescalings, matches, dummies) are
##dropped, as are P_BLOCK / P_039 (combinations of the attributes), RND_01 and the start/end timestamps.
##Covariates: cov_survey_weight = WEIGHT (NORC panel weight); cov_gender from GENDER (Female/Male; NORC label
##text); cov_age = age; cov_education = EDUC (NORC label text); cov_party_id7 = P_PARTYID (NORC 7-point text);
##others keep the NORC label text. Q5_1..Q5_5 = "Do you personally know anyone who has ever been addicted to
##opioids...": Yes, me / a family member / a close friend / an acquaintance / No (Appendix A; order assumed to
##follow the listed options, so kept as cov_know_addict_1..5). CaseId (NORC case number) re-keyed to 1..n.
##Rows with none of the three outcomes answered are omitted.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(readRDS(file.path(raw, "opioids_identity_recoded.rds")))
stopifnot(nrow(k) == 3112L, !anyDuplicated(k$CaseId))
setorder(k, CaseId)
lik <- function(x, lev) { x <- as.character(x); r <- match(x, lev); stopifnot(all(!is.na(r) | x %in% c("SKIPPED ON WEB", NA))); r }
spend <- c("Increase a lot", "Increase a little", "Keep the same", "Decrease a little", "Decrease a lot")
agree <- c("Strongly agree", "Somewhat agree", "Neither agree nor disagree", "Somewhat disagree", "Strongly disagree")
stopifnot(identical(levels(k$Q1)[1:5], spend), identical(levels(k$Q2)[1:5], spend), identical(levels(k$Q4)[1:5], agree))
vig <- tstrsplit(as.character(k$P_VIG), " ")
path_full <- c("Injured his/her knee and needed surgery. His/her doctor prescribed him/her OxyContin pills for the pain during his/her recovery.",
               "His/her friend illegally gave him/her OxyContin pain pills at a party.",
               "His/her friend gave him/her heroin at a party.")
pa <- as.character(k$P_PATHA)
pth <- ifelse(startsWith(pa, "He/She injured his/her knee"), path_full[1], pa)
stopifnot(all(pth %in% path_full))
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L,
                rating_treatment = lik(k$Q1, spend), rating_enforcement = lik(k$Q2, spend), rating_blame = lik(k$Q4, agree),
                attr_race = vig[[1]], attr_gender = vig[[2]], attr_location = as.character(k$P_GEO),
                attr_pathway = pth, attr_insurance = as.character(k$P_PATHI),
                trial_name_quartile = as.character(k$P_RNAME), trial_question_order = as.character(k$DOV_ORDER))
stopifnot(all(d$attr_race %in% c("Black", "White")), all(d$attr_gender %in% c("man", "woman")),
          all(d$attr_race == k$condition_race), all(d[, ifelse(attr_gender == "woman", "Female", "Male")] == k$condition_gender))
cv <- function(x) { x <- as.character(x); x[x %in% c("SKIPPED ON WEB", "REFUSED")] <- NA; x }
d[, `:=`(cov_survey_weight = k$WEIGHT,
         cov_gender = c(Female = "female", Male = "male")[as.character(k$GENDER)],
         cov_age = as.integer(k$age), cov_education = cv(k$EDUC), cov_race_ethnicity = cv(k$RACETHNICITY),
         cov_party_id7 = cv(k$P_PARTYID), cov_ideology = cv(k$P_IDEO), cov_religion = cv(k$P_RELIG),
         cov_attendance = cv(k$P_ATTEND), cov_income = cv(k$INCOME), cov_marital = cv(k$MARITAL),
         cov_employment = cv(k$EMPLOY), cov_housing = cv(k$HOUSING), cov_metro = cv(k$METRO),
         cov_urbanicity = cv(k$URBAN39), cov_region4 = cv(k$REGION4), cov_state = cv(k$STATE),
         cov_device = trimws(cv(k$Device)))]
for (j in 1:5) d[, paste0("cov_know_addict_", j) := cv(k[[paste0("Q5_", j)]])]
d <- d[!(is.na(rating_treatment) & is.na(rating_enforcement) & is.na(rating_blame))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "debenedictiskessner_2022_opioid_identity.csv"))
