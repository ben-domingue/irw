##Birth-scenario discrete choice experiment (US MTurk, 2016 + 2018) from
##Clarke, D., Oreffice, S., & Quintana-Domeque, C. (2021). On the value of birth weight.
##Oxford Bulletin of Economics and Statistics, 83(5), 1130-1159. https://doi.org/10.1111/obes.12429
##Replication data: Harvard Dataverse doi:10.7910/DVN/IWINJN, CC0 1.0, no restricted files.
##File read: data/conjointBW_20162018.dta, extracted from data.7z (the archive also holds ACS and
##natality files, not read). Sources for wording and design: OBES-20-065-article.pdf (Section 2-3)
##and OBES-20-065-appendix.pdf Figure A5 (screenshot of a task); source/dceAnalysis.do read as text.
##Usage: Rscript clarke_2021.R <dir holding conjointBW_20162018.dta> <output dir>
##
##2,005 US MTurk workers (two HITs with an identical experiment, September 2016 and May 2018; trial_wave = survey year), 7 paired
##tasks each (round 1-7 = task, option 1-2 = profile = Scenario 1 / Scenario 2, both recorded).
##Every task has exactly one chosen profile (forced choice: "In order to move forward in the
##experiment a choice must be made for each pair"), so opt-out = no.
##  choice: "Which of these two birth scenarios would you choose?" (appendix Figure A5).
##Scenarios: a hospital birth of the first child with no complications (article). Attributes, text
##as stored (= as displayed in Figure A5): attr_gender (Boy / Girl), attr_cost ("Out of Pocket
##Expenses", $250 ... $10,000, 10 levels), attr_birth_weight ("5 pounds 8 ounces" ... "8 pounds 13
##ounces", 11 levels), attr_season ("Season of Birth": Winter/Spring/Summer/Fall).
##Design: article: "main-effects, orthogonal (all attribute levels vary independently) and balanced
##(each level of an attribute occurs the same number of times)" -> restrictions none, level weights
##uniform. Attribute row order randomized once per respondent and fixed across the 7 tasks
##(article); recorded as attrpos_* (the deposit's *_position, 1-4; constant within respondent, checked).
##Sample: all 2,005 completed responses are kept. The article's analysis sample (1,894) drops
##respondents located outside the US by IP (72), failing a repeated education question (26) and
##finishing in under 2 minutes (16); the authors' flag is kept as cov_main_sample (1 = in the 1,894;
##it equals _mergeMTQT==3 & notUSA==0 & surveyTime>=2 & RespEduc==RespEducCheck, checked).
##Weight: cov_survey_weight = the deposit's `weight` (state population share / sample share, defined
##for the 1,894 only, NA otherwise), used by the authors in their re-weighted robustness table
##(dceAnalysis.do L1030 [pw=weight] if mainSample==1).
##Covariates (Qualtrics answer text as stored): cov_gender (RespSex Female/Male -> female/male),
##cov_birth_year (RespYOB, year of birth; age is not stored), cov_education (RespEduc),
##cov_race (RespRace), cov_state (RespState), cov_pregnant (RespPregnant), cov_plans_kids
##(RespPlansKids; blank = not asked/answered -> NA), cov_child_birth_year (RespKidBYear: a year, or
##"I don't have biological children"; the export's mis-encoded apostrophe repaired),
##cov_survey_minutes (surveyTime, the authors' completion time in minutes), cov_main_sample.
##Dropped: latitude/longitude and their Mercator copies (IP geolocation with noise added),
##answersurveycodeO (MTurk completion code), status, Qualtrics duration (2018 only), the repeated
##education check and all derived dummies/demeaned/merge variables.
##N: 2,005 respondents (the article's 2,005 valid responses); 1,894 with cov_main_sample = 1 (matches the
##article; 26,516 rows = Table 2 N). Spot check: a linear probability model on the 1,894 reproduces
##Table 2's logit average marginal effects (7lbs 3oz 0.181 vs 0.181, Spring 0.034 vs 0.034, Girl
##0.002 vs 0.002). The same authors' "The demand for season of birth" (J. Applied Econometrics 2019)
##is a different MTurk experiment as far as the deposit shows (not checked further).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(haven::zap_labels(haven::read_dta(file.path(raw, "conjointBW_20162018.dta"))))
stopifnot(nrow(s) == 28070, uniqueN(s$ID) == 2005, s[, .N, .(ID, round, option)][, all(N == 1)],
          all(s$round %in% 1:7), all(s$option %in% 1:2), s[, sum(chosen), .(ID, round)][, all(V1 == 1)])
ok <- with(s, `_mergeMTQT` == 3 & notUSA == 0 & surveyTime >= 2 & RespEduc == RespEducCheck)
stopifnot(all(ok == (s$mainSample == 1)), s[!duplicated(ID), sum(mainSample)] == 1894)
pos <- c("cost_position", "birthweight_position", "gender_position", "sob_position")
stopifnot(s[, lapply(.SD, uniqueN), ID, .SDcols = pos][, all(unlist(.SD) == 1), .SDcols = pos])
stopifnot(all(s$RespSex %in% c("Female", "Male")))
na <- function(x) fifelse(x == "", NA_character_, x)
d <- s[, .(id = as.integer(ID), task = as.integer(round), profile = as.integer(option), choice = as.integer(chosen),
           attr_gender = gender, attr_cost = cost, attr_birth_weight = birthweight, attr_season = sob,
           attrpos_gender = as.integer(gender_position), attrpos_cost = as.integer(cost_position),
           attrpos_birth_weight = as.integer(birthweight_position), attrpos_season = as.integer(sob_position),
           trial_wave = as.integer(surveyYear),
           cov_gender = c(Female = "female", Male = "male")[RespSex], cov_birth_year = as.integer(RespYOB),
           cov_education = na(RespEduc), cov_race = na(RespRace), cov_state = na(RespState),
           cov_pregnant = na(RespPregnant), cov_plans_kids = na(RespPlansKids),
           cov_child_birth_year = na(gsub("â€™", "'", RespKidBYear, fixed = TRUE)),
           cov_survey_minutes = round(surveyTime, 2), cov_main_sample = as.integer(mainSample),
           cov_survey_weight = weight)]
stopifnot(d[, uniqueN(attr_birth_weight)] == 11, d[, uniqueN(attr_cost)] == 10, d[, uniqueN(attr_season)] == 4,
          !anyNA(d[, .(attr_gender, attr_cost, attr_birth_weight, attr_season)]),
          d[cov_main_sample == 0, all(is.na(cov_survey_weight))], d[cov_main_sample == 1, !anyNA(cov_survey_weight)],
          d[, all(cov_birth_year %between% c(1900L, 2005L))])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "clarke_2021_birth_weight.csv"))
