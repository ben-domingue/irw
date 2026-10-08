##Uncivil-tweet candidate conjoint (United States) from
##Vargiu, C., Nai, A., & Garzia, D. (2026). Incivility does not exist: An experimental assessment
##on the drivers of incivility perceptions and their effects on candidate evaluations. The Journal
##of Politics, 88(2), 867-881. https://doi.org/10.1086/735437 (registered report; deposit 2024).
##Replication data: Harvard Dataverse doi:10.7910/DVN/SJL3S8, CC0 1.0, no restricted files.
##File read: IncivilityDoesNotExist_data.Rdata (one data.frame, 2,122 rows, one per respondent,
##loaded into its own environment). Read as text: the codebook (.html), the analysis code (.R),
##Appendix A (conjoint task), Appendix D (questionnaire), the Stage 2 report (.pdf).
##Usage: Rscript vargiu_2026.R <dir holding the .Rdata> <output dir>
##
##US adults (CloudResearch, February 2024; 2,122 recruited), 3 tasks of 2 hypothetical
##Congressional candidates side by side, each shown as a Twitter profile (name, AI-generated photo,
##election) with four tweets carrying the attributes; the last tweet is always an uncivil attack
##on the opponents. 8 attributes, stored with the authors' level labels (codebook / Appendix A),
##not the tweet text: the displayed text is in Appendix A Table A1; it is the same across tasks,
##but profile A and profile B show slightly different wordings of each level (report fn 6).
##  attr_party: Democrat / Republican / Unknown (displayed "Democratic Party" / "Republican Party"
##    / "Not Disclosed").
##  attr_gender: Female / Male, conveyed ONLY by the first name and photo (e.g. Danielle vs
##    Daniel Miller; names per task and profile in Appendix A Table A2).
##  attr_traits: "High agency, low communion" / "High communion, low agency".
##  attr_insider: Insider / Outsider.
##  attr_attack_type: Attack / Counterattack (the codebook labels; Appendix A calls them
##    Non-Retaliatory / Retaliatory: "...in response to the attacks launched today by my opponents").
##  attr_issue: the issue named in the attack tweet (Abortion, GunOwnership,
##    IndividualRights&Liberties, theEconomy, TaxReform, Inflation; the hashtags displayed). The
##    authors' moral/economic dummy (ATT_ISSUE_*) is derived from it and dropped.
##  attr_incivility_type: Insult / Ridicule. Each was one of three texts (Appendix A); WHICH of
##    the three was shown is not in the data, only the type.
##  attr_setting: High incivility context / Low incivility context (news-agency retweet).
##Tweet order was randomized between tasks and respondents (attack always last); not recorded.
##Randomization restrictions: none documented.
##Outcomes, all 0-100 sliders about each profile (report pp. 16-17; codebook anchors). The exact
##question text is not deposited (Appendix D stops at the task intro), so the wording below is the
##report's paraphrase. Kept in the asked direction, NOT recoded: for the four perception items
##higher = more uncivil (less favourable).
##  rating_impolite:   attack polite (0) - impolite (100)
##  rating_unacceptable: acceptable (0) - unacceptable (100)
##  rating_notnormal:  normal (0) - not normal (100)
##  rating_wrong:      right (0) - wrong (100)
##  rating:            feeling thermometer toward the candidate, 0 cold/not favourable - 100
##                     warm/favourable (the authors' candidate evaluation)
##No choice question. Rows with all five outcomes missing are omitted: this drops the 26
##respondents whose attributes were not saved and 44 more with no ratings (2,052 kept).
##cov_in_authors_sample = 1 for the authors' analytic sample (passed attention check, not a
##straight-liner on the 6 authority items, duration >= half the median; dplyr::filter also drops
##missing attention check / missing SD), as in their code: 1,884 respondents, the report's n.
##1,843 of them have ratings and are in this table.
##Covariates. Reserved names (codebook .html; questionnaire = Appendix D):
##  cov_gender (SEX "Respondent's sex", factor Female/Male, lowercased; Appendix D Q2.2 "What is
##    your gender?" also offered "Other, non-binary" and "I prefer not to answer", which the
##    deposit holds only as NA, 29 respondents).
##  cov_age (AGE, "Respondent's age in number", years; Q2.3).
##  cov_education (EDU_NUM, the answer text of Appendix D Q3.6 "What is the highest level of
##    school you have completed or the highest degree you have received?" for codes 1-16; codes
##    match the codebook's EDU_CAT1 collapse, e.g. 9 = High school diploma, 10 = Some college).
##    The authors' collapsed EDU_CAT1 keeps its name (cov_edu_cat1).
##  cov_party_id (PID_DIR "partisan identification (direction)": Democrat / Republican; the
##    authors' coding from Q5.1-Q5.4 with leaners counted as partisans, so pure independents
##    and "Neither" are NA).
##  cov_party_id7 (PID_STR "partisan identification (strength)", the authors' 7 labels: Strong
##    Democrat, Democrat, Weak Democrat, Independent, Weak Republican, Republican, Strong
##    Republican).
##Kept as in the source: race, political interest, left-right and liberal-conservative
##self-placement (0-10), issue importance (6), populism (7), authoritarian aggression (6),
##status loss/gain, Dirty Dozen (12) and aggression (12) items. Dropped: RESPID (re-keyed 1..n in file order),
##DURATION, ATTENTIONCHECK (folded into cov_in_authors_sample).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "IncivilityDoesNotExist_data.Rdata"), envir = e)
s <- as.data.table(e$IncivilityDoesNotExist_data)
s[, id := .I]
auth <- s[, as.numeric(sd(c(POLATT_AUTHORITY_1, POLATT_AUTHORITY_2, POLATT_AUTHORITY_3, POLATT_AUTHORITY_4,
                            POLATT_AUTHORITY_5, POLATT_AUTHORITY_6))), by = id]$V1
s[, cov_in_authors_sample := as.integer(ATTENTIONCHECK %in% "Passed" & !is.na(auth) & auth != 0 &
                                          !(DURATION < median(DURATION) / 2))]
am <- c(party = "PARTY", gender = "GENDR", traits = "TRAIT", insider = "POPUL", attack_type = "ATTAK",
        issue = "ISSUEALL", incivility_type = "IMPOL", setting = "SETTG")
om <- c(rating_impolite = "IMPOLITE", rating_unacceptable = "UNACCEPT", rating_notnormal = "NOTNORMAL",
        rating_wrong = "WRONG", rating = "FEELING")
d <- rbindlist(lapply(1:3, function(t) rbindlist(lapply(1:2, function(p) {
  x <- data.table(id = s$id, task = t, profile = p)
  for (k in names(om)) x[, (k) := as.integer(s[[sprintf("DV_%s_T%d_P%d", om[[k]], t, p)]])]
  for (k in names(am)) x[, paste0("attr_", k) := as.character(s[[sprintf("ATT_%s_T%d_P%d", am[[k]], t, p)]])]
  x
}))))
d <- d[!(is.na(rating_impolite) & is.na(rating_unacceptable) & is.na(rating_notnormal) & is.na(rating_wrong) & is.na(rating))]
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]))
cv <- c("SEX", "AGE", "EDU_NUM", "EDU_CAT1", "RACE", "POLINT", "LR_SELF", "LC_SELF", "PID_DIR", "PID_STR",
        grep("^(ISSUEIMP|POLATT|SOCEXP|PERSONL)_", names(s), value = TRUE))
for (v in cv) {
  x <- s[[v]]; x <- if (is.factor(x)) as.character(x) else as.numeric(x)
  d[, paste0("cov_", tolower(v)) := x[id]]
}
## reserved names and codings (header)
q36 <- c("Less than 1st grade", "1st, 2nd, 3rd or 4th grade", "5th or 6th grade", "7th or 8th grade", "9th grade",
         "10th grade", "11th grade", "12th grade no diploma",
         "High school graduate - high school diploma or equivalent (for example: GED)", "Some college but no degree",
         "Associate degree in college - Occupational/vocational program", "Associate degree in college - Academic program",
         "Bachelor's degree (For example: BA, AB, BS)", "Master's degree (For example: MA, MS, MEng, MEd, MSW, MBA)",
         "Professional School Degree (For example: MD,DDS,DVM,LLB,JD)", "Doctorate degree (For example: PhD, EdD)")
stopifnot(all(d$cov_edu_num %in% c(1:16, NA)), all(d$cov_sex %in% c("Female", "Male", NA)))
d[, cov_edu_num := q36[cov_edu_num]][, cov_sex := tolower(cov_sex)]
setnames(d, c("cov_sex", "cov_edu_num", "cov_pid_dir", "cov_pid_str"),
         c("cov_gender", "cov_education", "cov_party_id", "cov_party_id7"))
d[, cov_in_authors_sample := s$cov_in_authors_sample[id]]
d[, id := frank(id, ties.method = "dense")]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "vargiu_2026_incivility_tweets.csv"))
