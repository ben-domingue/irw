##Paired candidate self-description experiments from
##Karpowitz, C. F., Monson, J. Q., Preece, J. R., & Aldridge, A. (2023). Selecting for masculinity:
##Women's under-representation in the Republican Party. American Political Science Review.
##https://doi.org/10.1017/S0003055423000783
##Replication data: Harvard Dataverse doi:10.7910/DVN/Z0IGLS, CC0 1.0. Files read:
##2016_Caucus_Survey_replication.tab (Study 3), 2018_Caucus_Survey_replication.tab (Study 4), Study 3 and
##Study 4 codebooks (PDF), Supporting Information Appendix (Tables A4-A7, B.5). Not built (held): the merged
##2016-18 CCES file (Studies 1-2: only the woman candidate's profile is randomized, four levels, the man candidate is
##fixed, so there is a single manipulated factor) and the Study 5 candidate-observer file (observational).
##Usage: Rscript karpowitz_2023.R <dir holding the two caucus .tab files> <output dir>
##
##Respondents (Republican caucus attenders, Qualtrics, recruited by email from the state party list; the state is
##redacted in the paper) saw two state-delegate candidates, Julie Baker (the woman) and Steven Hall (the man), each
##with a short self-description, and chose between them. One task per respondent, 2 profiles. The screen order of
##the candidates was randomized but not saved, so profile 1 = Julie Baker (woman), 2 = Steven Hall (man), an
##outcome-independent key (profile_source unknown); task_source recorded (single task).
##  choice  = vote_julie: "If these two candidates were running for state delegate in your precinct this year,
##            who would you vote for? Julie Baker / Steven Hall" (SI B.5.2); 1 on the profile voted for. Forced choice,
##            no opt-out. Respondents with a missing vote are dropped (Study 3: 0, Study 4: 559).
##  rating_likeable / rating_competent = like_*/comp_* for each candidate: "how well do these words describe
##            [candidate]: likeable / competent?  Extremely well, Quite well, Not too well, Not well at all"
##            (SI B.5.1), stored 1-4. Direction is not in the codebook: the authors' difference scores
##            (diff_like = like_julie - like_steven, verified exactly) are read as "higher favors the woman", so
##            4 = extremely well (the modal answer is 3 = quite well). Not recoded. The deposit's rep_*/trust_* items
##            have no documented wording and are dropped.
##Attributes (levels are the authors' condition labels; the instrument texts are in the SI Table A6 and, for Study 3,
##in the data):
##  attr_candidate   = "Julie Baker" or "Steven Hall" (fixed by position, not randomized)
##  attr_profile_type = the self-presentation condition: Masculine (a Vice President at a local bank / an engineer at a
##    local software firm, tax or deficit concern), Masculine + Mom/Dad (the same plus "a mom/dad who volunteers at my
##    kids' school"), Feminine (a teacher at a local school / a nurse at a local hospital, education concern),
##    Feminine + Mom/Dad, and (Study 3 woman only) Mom Only ("I'm a mom who volunteers at my kids' school ...").
##    The man's Study 3 profile is always Masculine; labels are shown with Mom for the woman and Dad for the man
##    as one level "+ Parent" in Study 4 (the A6 template uses mom/dad); Study 3 keeps the authors' "+Mom".
##  Study 3 only: attr_bio = the displayed self-description, exact text (profile1 = man, profile2 + "." = woman, the
##    deposit stores the woman text without its final period because the appeal sentence is appended after it);
##    attr_gender_appeal = the woman's added sentence "I believe that women like me have a lot to add to our party."
##    or "(not shown)" (the man never gets one; the woman gets it in half the cases).
##  Study 4: man and woman profile types are crossed 4 x 4 (treat 1-16 = 4*(man-1)+woman, labels "Masc v. Masc+ ..."
##    where the first label is the man; SI Table A7 note). The A6 template has bracketed random wordings
##    (occupation, conservative phrasing) that were not saved, so no exact text exists; cell sizes are unequal
##    (the eight same-type-or-fem cells hold about 480, the others about 970: level_weights nonuniform in effect).
##Trial: trial_equality_prime (Study 3, respondent-level message treatment before the candidates: "No Equality
##Prime" / "Equality Prime", not an attribute).
##Covariates: cov_gender (female: 1 = female, 0 = male, codebook "Woman"), cov_age, cov_religiosity (0-1 index as
##recorded), cov_married, cov_income_code (9 categories, no labels), cov_education (codebook value labels: Some high
##school or less, High school graduate, Some college, college graduate, Post-graduate), cov_nonwhite,
##cov_strong_conservative. ResponseId/ResponseID dropped; ids re-keyed. No survey weight in these files.
##Counts: Study 3 10,210 respondents in the experiment (10,771 rows, 561 without a profile); Study 4 11,048 voted
##(11,607 randomized, 13,928 rows). Paper N not checked (behind the SI).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
edu <- c("Some high school or less", "High school graduate", "Some college", "college graduate", "Post-graduate")
cov <- function(k) list(cov_gender = ifelse(k$female == 1, "female", "male"), cov_age = as.integer(k$age),
  cov_religiosity = k$relig, cov_married = as.integer(k$married), cov_income_code = as.integer(k$income),
  cov_education = edu[k$educ], cov_nonwhite = as.integer(k$nonwhite), cov_strong_conservative = as.integer(k$strong_con))
two <- function(k, wtype, mtype, extra_w, extra_m, tr) {
  n <- nrow(k); id <- seq_len(n)
  W <- data.table(id = id, task = 1L, profile = 1L, choice = as.integer(k$vote_julie == 1),
    rating_likeable = as.integer(k$like_julie), rating_competent = as.integer(k$comp_julie), attr_candidate = "Julie Baker", attr_profile_type = wtype)
  M <- data.table(id = id, task = 1L, profile = 2L, choice = as.integer(k$vote_julie == 0),
    rating_likeable = as.integer(k$like_steven), rating_competent = as.integer(k$comp_steven), attr_candidate = "Steven Hall", attr_profile_type = mtype)
  if (!is.null(extra_w)) { W <- cbind(W, extra_w); M <- cbind(M, extra_m) }
  cv <- as.data.table(cov(k)); cv[, id := id]
  d <- merge(rbind(W, M), cv, by = "id")
  if (!is.null(tr)) d[, trial_equality_prime := tr[id]]
  d
}
# Study 3 (2016)
k <- fread(file.path(raw, "2016_Caucus_Survey_replication.tab"))
k <- k[!is.na(profile) & !is.na(vote_julie)]
wl <- c("Masculine", "Masculine+Mom", "Feminine", "Feminine+Mom", "Mom Only")
app <- "I believe that women like me have a lot to add to our party."
stopifnot(all(k$profile %in% 1:5), all(k$gender_appeal %in% 0:1), all(k$women_like_me[k$gender_appeal == 1] == paste0(". ", app)))
d3 <- two(k, wl[k$profile], "Masculine",
          data.table(attr_bio = paste0(k$profile2, "."), attr_gender_appeal = ifelse(k$gender_appeal == 1, app, "(not shown)")),
          data.table(attr_bio = k$profile1, attr_gender_appeal = "(not shown)"),
          ifelse(k$treat == 1, "Equality Prime", "No Equality Prime"))
setcolorder(d3, c("id", "task", "profile", "choice", "rating_likeable", "rating_competent")); setorder(d3, id, task, profile)
stopifnot(!anyNA(d3[, .(choice, attr_bio, attr_profile_type)]), d3[, sum(choice), id][, all(V1 == 1)], d3[, uniqueN(id)] == 10210)
fwrite(d3, file.path(out, "karpowitz_2023_masculinity_2016.csv"))
# Study 4 (2018)
k <- fread(file.path(raw, "2018_Caucus_Survey_replication.tab"))
k <- k[!is.na(treat) & !is.na(vote_julie)]
lab <- c("Masculine", "Masculine + Parent", "Feminine", "Feminine + Parent")
mi <- (k$treat - 1L) %/% 4L + 1L; wi <- (k$treat - 1L) %% 4L + 1L
d4 <- two(k, lab[wi], lab[mi], NULL, NULL, NULL)
setcolorder(d4, c("id", "task", "profile", "choice", "rating_likeable", "rating_competent")); setorder(d4, id, task, profile)
stopifnot(d4[, sum(choice), id][, all(V1 == 1)], d4[, uniqueN(id)] == 11048)
fwrite(d4, file.path(out, "karpowitz_2023_masculinity_2018.csv"))
