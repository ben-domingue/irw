##Candidate-classification conjoints (US, CCES team modules) from
##Goggin, S. N., Henderson, J. A., & Theodoridis, A. G. (2020). What goes with red and blue?
##Mapping partisan and ideological associations in the minds of voters. Political Behavior,
##42(4), 985-1013. https://doi.org/10.1007/s11109-018-09525-6 (online January 2019)
##Replication data: Harvard Dataverse doi:10.7910/DVN/RDQZUM, CC0 1.0, no restricted files,
##no terms. Files read: party_conjoint.csv, ideology_conjoint.csv (one row per respondent x
##profile, labels as text), Red_Blue_Appendix.pdf (Table I: factors and levels); the authors'
##WhatGoesWithRedAndBlueAnalyses.R read as text. The article (paywalled) was NOT read: question
##wording and the CCES year are not documented here.
##Usage: Rscript goggin_2020.R <raw dir> <output dir>
##
##Respondents saw one hypothetical candidate at a time (single-profile tasks, profile = 1),
##described by gender, family, religion, military service, occupation and three issue
##priorities (appendix Table I; the three priorities drawn from 17 issues WITHOUT replacement),
##and were asked to guess the candidate's party (or ideology), how sure they were, and to rate
##the candidate. Two experiments, two tables:
##  goggin_2020_party_guess: party_conjoint.csv, 2,000 respondents from two CCES team modules
##    ("AGT - N=1000", "JAH - N=1000"; pooled by the authors; cov_cces_module), 4 profiles each,
##    task = Conjoint_CandTrialNum (recorded).
##  goggin_2020_ideology_guess: ideology_conjoint.csv, the JAH module's 1,000 respondents (the
##    same people as the JAH half of the party table, same V101); 177 of them have no attribute
##    values on any of their 4 rows (no ideology profiles saved) and are dropped: 823
##    respondents. No task column: task = row order within respondent (INFERRED).
##Outcomes (wording not in the deposit; paraphrased in the design record):
##  rating_republican (party table): the party guess, 1 = "Republican", 0 = "Democrat"
##    (ConjointDV_a); rating_conservative (ideology table): 1 = "Conservative", 0 = "Liberal"
##    (iconjointDV_a). A classification of a single profile: a rating, not a choice.
##  rating_sure: sureness of the guess, the four answer texts coded 1 = "Very unsure",
##    2 = "Somewhat unsure", 3 = "Somewhat sure", 4 = "Very sure" (order of the labels).
##  rating_favorability: 0 = "Very Unfavorable" to 10 = "Very Favorable" (DV_c; the end labels
##    stripped from "0 - Very Unfavorable" / "10 - Very Favorable").
##  Rows with all three outcomes missing are omitted (party: 3 rows; ideology: 2 rows among
##  the profiles with attributes).
##attr_ text: the deposited labels (= appendix Table I). attr_religion "None Listed" is a level
##  of Table I and is kept as text (whether the religion line read "None Listed" or was left
##  off is not documented). attr_issue1-3 are the 1st/2nd/3rd priorities.
##Randomization: restriction = issue priorities without replacement (Table I; no profile repeats
##  an issue); otherwise not documented. Attribute order not documented.
##Covariates (CCES text as deposited): cov_birth_year, cov_gender (Male/Female -> male/female),
##  cov_education (educ), cov_race, cov_hispanic, cov_marital_status, cov_party_id7 (pid7; "Not
##  sure" kept), cov_state (inputstate), cov_region, cov_registered (votereg), cov_cces_module,
##  cov_survey_weight (weight, the CCES weight).
##Dropped: CCES case id V101 (re-keyed), inputzip and regzip (ZIP codes), race_other (free
##  text), StateAbbr/CCEStake/add_confirm/votereg_f, the authors' dummy codings of the
##  attributes (g1, f1-f6, r1-r4, m1-m3, o1-o9, i1_*, i2_*, i3_*, ia_*), pid3withlean,
##  guess_rep and derived scores, knowledge items and indices, ideology3.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
sure <- c("Very unsure" = 1L, "Somewhat unsure" = 2L, "Somewhat sure" = 3L, "Very sure" = 4L)
fav <- function(v) as.integer(sub("^([0-9]+).*$", "\\1", v))
covs <- function(x) x[, .(cov_birth_year = as.integer(birthyr), cov_gender = c(Male = "male", Female = "female")[gender],
                          cov_education = educ, cov_race = race, cov_hispanic = hispanic, cov_marital_status = marstat,
                          cov_party_id7 = pid7, cov_state = inputstate, cov_region = region, cov_registered = votereg,
                          cov_cces_module = trimws(ccesmodule), cov_survey_weight = weight)]
## party
x <- fread(file.path(raw, "party_conjoint.csv"), na.strings = c("", "NA"))
stopifnot(uniqueN(x$V101) == 2000, x[, .N, V101][, all(N == 4)])
d <- x[, .(src = V101, task = as.integer(Conjoint_CandTrialNum), profile = 1L,
           rating_republican = c(Democrat = 0L, Republican = 1L)[ConjointDV_a],
           rating_sure = sure[ConjointDV_b], rating_favorability = fav(ConjointDV_c),
           attr_gender = ConjointIV_gender, attr_family = ConjointIV_family, attr_religion = ConjointIV_religion,
           attr_military = ConjointIV_military, attr_occupation = ConjointIV_job,
           attr_issue1 = ConjointIV_Issue1, attr_issue2 = ConjointIV_Issue2, attr_issue3 = ConjointIV_Issue3)]
d <- cbind(d, covs(x))
stopifnot(d[, uniqueN(task), src][, all(V1 == 4)], !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, all(attr_issue1 != attr_issue2 & attr_issue1 != attr_issue3 & attr_issue2 != attr_issue3)],
          all(d$rating_favorability %in% c(0:10, NA)))
d <- d[!(is.na(rating_republican) & is.na(rating_sure) & is.na(rating_favorability))]
d[, id := match(src, sort(unique(src)))][, src := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "goggin_2020_party_guess.csv"))
## ideology
y <- fread(file.path(raw, "ideology_conjoint.csv"), na.strings = c("", "NA"))
stopifnot(uniqueN(y$V101) == 1000, y[, .N, V101][, all(N == 4)])
y[, task := seq_len(.N), V101]
y <- y[!is.na(iconjoint_gender)]
e <- y[, .(src = V101, task, profile = 1L,
           rating_conservative = c(Liberal = 0L, Conservative = 1L)[iconjointDV_a],
           rating_sure = sure[iconjointDV_b], rating_favorability = fav(iconjointDV_c),
           attr_gender = iconjoint_gender, attr_family = iconjoint_family, attr_religion = iconjoint_religion,
           attr_military = iconjoint_military, attr_occupation = iconjoint_job,
           attr_issue1 = iconjoint_issue1, attr_issue2 = iconjoint_issue2, attr_issue3 = iconjoint_issue3)]
e <- cbind(e, covs(y))
stopifnot(uniqueN(e$src) == 823, e[, .N, src][, all(N == 4)], !anyNA(e[, .SD, .SDcols = patterns("^attr_")]),
          e[, all(attr_issue1 != attr_issue2 & attr_issue1 != attr_issue3 & attr_issue2 != attr_issue3)])
e <- e[!(is.na(rating_conservative) & is.na(rating_sure) & is.na(rating_favorability))]
e[, id := match(src, sort(unique(src)))][, src := NULL]
setcolorder(e, c("id", "task", "profile"))
setorder(e, id, task, profile)
fwrite(e, file.path(out, "goggin_2020_ideology_guess.csv"))
