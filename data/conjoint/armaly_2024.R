##Supreme Court nominee conjoint (US, March 2022, Black oversample) from
##Armaly, M. T., Krewson, C. N., & Lane, E. A. (2024). The influence of descriptive representation on
##support for judicial nominees and the US Supreme Court. Political Behavior, 47(2), 661-687.
##https://doi.org/10.1007/s11109-024-09966-2 (CC BY 4.0 article; read via a publisher mirror)
##Replication data: Harvard Dataverse doi:10.7910/DVN/H8RIBF, CC0 1.0, no restricted files, no terms.
##File read: dat_long71524.RData (one data.table `master`, loaded into its own environment).
##replication_file.R read as text, not run. dat71524.RData (non-stacked survey items) and
##external_validity_data.RData (ratings of a fixed Ketanji Brown Jackson profile) not used.
##Usage: Rscript armaly_2024.R <dir holding dat_long71524.RData> <output dir>
##
##1,223 Black and white US adults (Lucid, March 2022, quotas on sex, age and education, Black
##respondents oversampled), fielded after Jackson's nomination and before her hearings. Each rated
##FOUR single hypothetical Supreme Court nominee profiles (4,892 rows = 1,223 x 4): one profile per
##task, task = the deposit's `profile` column (1-4; that it is the display sequence is not stated).
##Eight attributes, level text as stored: sex, age (45-65), race (White/Black/Asian/Hispanic),
##religion, ideology, judicial philosophy ("Meaning of the Constitution can change." / "... is
##fixed."), legal education (Top 5/25 public/private law school), party of the appointing president
##(attr_appointing_party). Attribute row order randomized once per respondent (the same for all four
##profiles of a respondent) and recorded (<attr>_order -> attrpos_).
##The article analyses only the 2,409 Black/white-nominee rows; all four races are kept here.
##Outcomes, asked after each profile (article; only short item descriptions are published, so the
##questions below are paraphrases):
##  rating               support for the nominee, 1 (weak) - 6 (strong)
##  rating_trust         trust in the nominee to reach impartial decisions, 1-6
##  rating_quality       qualifications to be a US Supreme Court justice, 1-6
##  rating_court_approval  approval of the Supreme Court if the nominee became a member,
##                       1 strongly disapprove - 5 strongly approve (SCOTUS_App)
##  rating_court_legal   the Court seen as more of a legal institution, 1 strongly disagree -
##                       5 strongly agree (SCOTUS_leg)
##  rating_court_agree   the Court seen as more likely to make decisions I agree with, 1-5 (SCOTUS_agr)
##A few ratings are missing (3-8 per item), kept as NA.
##Covariates (codes mapped from the authors' replication_file.R): cov_race (ethnicity: 2 = "Black",
##1 = "White"; the Figure 1 code labels ethnicity==2 "Black Respondent"), cov_gender (gender: 2 =
##female, 1 = male; Figure A7 legend), cov_party_id (political_party3: 1 Democrat, 2 Republican,
##3 Independent, 4 Other; from the authors' dummies rep = 2, ind = 3, oth = 4 with Democrat the
##omitted category). Dropped: the Lucid/Qualtrics response id (rid, re-keyed 1..N), the authors'
##0-1 rescaled age and income, racial-resentment and thermometer scores, derived dummies (Black,
##black, Asian, Hispa, rep, ind, oth, shared_p) and the JudgeScores/CourtScores indices. No survey
##weight in the deposit.
##N: 1,223 respondents x 4 = 4,892, as in the article. Spot check: the authors' Figure A4 means of
##JudgeScores ((Support + Trust + Quality - 3) / 15) by respondent race x nominee race, Black/white
##nominees only, reproduce: Black resp. 0.548 white nominee / 0.624 Black nominee; white resp.
##0.586 / 0.565 (this table, rounded: 0.55 / 0.62 / 0.59 / 0.57).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "dat_long71524.RData"), envir = e)
m <- as.data.table(e$master)
stopifnot(nrow(m) == 4892, m[, .N, rid][, all(N == 4)], m[, uniqueN(profile), rid][, all(V1 == 4)])
ids <- unique(m$rid)
at <- c(Sex = "sex", Age = "age", Race = "race", Religion = "religion", Ideology = "ideology",
        Philosophy = "philosophy", Education = "legal_education", Party = "appointing_party")
d <- m[, .(id = match(rid, ids), task = as.integer(profile), profile = 1L,
           rating = as.integer(Support), rating_trust = as.integer(Trust), rating_quality = as.integer(Quality),
           rating_court_approval = as.integer(SCOTUS_App), rating_court_legal = as.integer(SCOTUS_leg),
           rating_court_agree = as.integer(SCOTUS_agr))]
for (k in names(at)) {
  d[, paste0("attr_", at[[k]]) := as.character(m[[k]])]
  d[, paste0("attrpos_", at[[k]]) := as.integer(m[[paste0(k, "_order")]])]
}
stopifnot(!anyNA(d[, grep("^attr", names(d)), with = FALSE]))
stopifnot(all(d$rating %in% c(1:6, NA)), all(d$rating_court_approval %in% c(1:5, NA)))
eth <- as.character(m$ethnicity); gen <- as.character(m$gender); pp <- as.integer(m$political_party3)
stopifnot(all(eth %in% c("1", "2", NA)), all((eth == "2") == (m$black == 1), na.rm = TRUE))
stopifnot(all(pp %in% c(1:4, NA)), all((pp == 2) == (m$rep == 1), na.rm = TRUE), all((pp == 3) == (m$ind == 1), na.rm = TRUE))
d[, cov_race := c(`1` = "White", `2` = "Black")[eth]]
d[, cov_gender := c(`1` = "male", `2` = "female")[gen]]
d[, cov_party_id := c("Democrat", "Republican", "Independent", "Other")[pp]]
d <- d[!(is.na(rating) & is.na(rating_trust) & is.na(rating_quality) & is.na(rating_court_approval) &
         is.na(rating_court_legal) & is.na(rating_court_agree))]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "armaly_2024_scotus_nominees.csv"))
