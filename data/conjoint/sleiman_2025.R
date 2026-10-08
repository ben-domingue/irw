##Online-dating profile conjoint (UK) from
##Sleiman, Y., Melios, G., & Dolan, P. (2025). "Sleeping with the enemy": Partisanship and
##tolerance in online dating. Political Science Research and Methods.
##https://doi.org/10.1017/psrm.2025.10011
##Replication data: Harvard Dataverse doi:10.7910/DVN/G1H0UA, CC0 1.0, no restricted files.
##(The article cites G1H0UA. A second Dataverse deposit of the same paper, doi:10.7910/DVN/8HAWA3,
##also exists: if it comes up, it is a duplicate of this table.)
##Files read: DATA/cjoint_raw.dta (the Qualtrics export, one row per respondent: set1-set16 =
##profile chosen (1/2) in choice set 1-16, wset*/mset* = the same split by female/male sets,
##survey answers). The authors' DO/1.cleaning.do and DO/2.reshape.do were read as text (not run):
##2.reshape.do gives each set's attribute levels ("Define the attribute and levels as they appear
##in the questionnaire", task x alternative lists) and 1.cleaning.do the covariate value labels.
##Level text and design facts from the article (LSE Research Online accepted version, Table 2).
##Usage: Rscript sleiman_2025.R <dir holding cjoint_raw.dta> <output dir>
##
##2,993 Prolific respondents (UK, non-married, aged 18-40, July 1-6 2023; article Table 1 has the
##same 2,993), 16 paired choice sets each, 95,776 rows. Respondents saw the female or the male
##sets by stated orientation (no preference: assigned at random); trial_profile_gender = "Woman"
##for the wset sets, "Man" for the mset sets (constant within respondent, so not an attr_).
##Outcome: choice = the profile chosen in the set (wording not in the deposit: select a date,
##paraphrase from the article: "probability of being selected for a date"); forced choice, no
##opt-out (one chosen per set, checked).
##Design: a fixed D-optimal fractional design (R skpr) of 16 choice sets with 8 binary attributes,
##the SAME 16 pairs for every respondent (one design for both set genders, per 2.reshape.do); the
##ORDER of the sets was randomized and is not recorded, so `task` is the choice-set number (1-16),
##not the position shown. profile = alternative 1/2 (the recorded answer 1/2).
##Attributes (article Table 2 wording): party (Labor / Tory), tolerance ("Open to match with
##anyone" / "No Tories!" on Labor profiles and "No Lefties!" on Tory profiles: the article's
##"No Tories/Lefties!" is contingent on the profile's party), ideology (Traditional /
##Progressive), race (White / Black: shown only by the profile photo; level = the authors' coding
##of the photo), education (Degree / No degree), diet ("Vegetarian, trying to be vegan" / "No
##dietary limitations"), attractiveness (High / Low: shown only by the photo, coded from a
##500-person pretest rating), height (tall/short shown as 5'8"/5'4" on women's and 6'/5'8" on
##men's profiles). Profile pictures make presentation = image.
##Covariates (codes -> text from 1.cleaning.do label define; 99 = refused/prefer not -> NA, blank
##-> NA): cov_gender (1 Male, 2 Female, 3 Non-binary -> male/female/other), cov_age (years),
##cov_relationship (1 Single, never married .. 6 Widowed; raw code, before the authors' recode of
##4 -> 3), cov_orientation (1 Men, 2 Women, 5 No preference), cov_education (1 None .. 6
##Post-graduate), cov_ethnic (1 White .. 5 Other), cov_diet (1 Vegan, 2 Vegetarian, 3 Meat-eater),
##cov_vote (2019 general election vote, 1 "I did not vote" .. 11 Other), cov_beauty (self-rated
##attractiveness 0-10), cov_labour_therm / cov_tory_therm (party_therm_1/_2), cov_labour_like /
##cov_tory_like, cov_ideology (0-10, as stored), cov_st_<trait> (which party's supporters the
##trait fits: 1 Conservatives, 2 Labour, 3 Neither), cov_duration_sec (Qualtrics survey duration).
##Not reserved and not mapped: cov_attention_set_code (answer 1/2 to the attention-check pair,
##check_w1/check_m1; the correct answer is not documented) and cov_check_4_code (check_4, likely
##an instructed slider; undocumented). The article excludes respondents failing two checks;
##failed_checks is empty and all 2,993 are in Table 1.
##Dropped: IP address, latitude/longitude, Prolific pid, ResponseId, reCAPTCHA score, free-text
##feedback (q326) and height (free text; the authors' cleaned version is derived); the authors'
##derived party_id, matches and dummies. id = row number of the export.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "cjoint_raw.dta")))
k[, id := .I]
## per-set attribute levels, 2.reshape.do: tasks (sets) where alternative 1 / 2 has level 1
des <- list(
  race      = list(c(2, 3, 8, 10, 11, 13, 14, 15, 16), c(3, 6, 9, 11, 12, 15, 16), "White", "Black"),
  party     = list(c(1, 3, 4, 6, 10, 11, 13, 15), c(1, 5, 6, 8, 10, 11, 13, 16), "Labor", "Tory"),
  tolerance = list(c(1, 2, 6, 10, 11, 12, 15), c(1, 3, 4, 8, 12, 14, 16), "Open to match with anyone", NA),
  education = list(c(3, 4, 6, 7, 14, 15, 16), c(1, 3, 4, 6, 7, 9, 13, 14, 16), "Degree", "No degree"),
  attractiveness = list(c(5, 6, 11, 13, 15), c(1, 2, 3, 5, 6, 7, 9, 10, 12, 14, 15), "High", "Low"),
  height    = list(c(1, 2, 3, 4, 8, 9, 10, 13, 15, 16), c(1, 2, 3, 7, 10, 14), "Tall", "Short"),
  diet      = list(c(4, 9, 10, 12, 14, 15, 16), c(2, 3, 5, 6, 8, 10, 14, 15, 16), "Vegetarian, trying to be vegan", "No dietary limitations"),
  ideology  = list(c(1, 2, 3, 5, 6, 7, 14, 15, 16), c(2, 5, 10, 11, 12, 14, 16), "Progressive", "Traditional"))
pf <- CJ(task = 1:16, profile = 1:2)
for (v in names(des)) {
  x <- des[[v]]
  hi <- (pf$profile == 1 & pf$task %in% x[[1]]) | (pf$profile == 2 & pf$task %in% x[[2]])
  set(pf, j = v, value = ifelse(hi, x[[3]], x[[4]]))
}
pf[is.na(tolerance), tolerance := fifelse(party == "Labor", "No Tories!", "No Lefties!")]
## choices
w <- !is.na(k$wset1)
stopifnot(all(xor(w, !is.na(k$mset1))))
ch <- rbindlist(lapply(1:16, function(t) data.table(id = k$id, task = t, pick = k[[paste0("set", t)]])))
stopifnot(all(ch$pick %in% 1:2), all(k$set1 == fifelse(w, k$wset1, k$mset1)))
d <- merge(ch, pf, by = "task", allow.cartesian = TRUE)
d[, choice := as.integer(pick == profile)][, pick := NULL]
d[, trial_profile_gender := c("Man", "Woman")[w[id] + 1]]
d[, height := fifelse(trial_profile_gender == "Woman", fifelse(height == "Tall", "5'8\"", "5'4\""),
                      fifelse(height == "Tall", "6'", "5'8\""))]
setnames(d, names(des), paste0("attr_", names(des)))
## covariates
num <- function(x) suppressWarnings(as.integer(x))
lab <- function(x, l) { x <- num(x); unname(l[as.character(x)]) }
cv <- k[, .(id,
  cov_gender = lab(gender, c("1" = "male", "2" = "female", "3" = "other")),
  cov_age = num(age),
  cov_relationship = lab(rel, c("1" = "Single, never married", "2" = "In a relationship", "3" = "Engaged", "4" = "Married", "5" = "Separated/divorced", "6" = "Widowed")),
  cov_orientation = lab(orientation, c("1" = "Men", "2" = "Women", "5" = "No preference")),
  cov_education = lab(edu, c("1" = "None", "2" = "Primary", "3" = "Secondary", "4" = "Higher/A-levels", "5" = "University", "6" = "Post-graduate")),
  cov_ethnic = lab(ethnic, c("1" = "White", "2" = "Black", "3" = "Asian", "4" = "Mixed", "5" = "Other")),
  cov_diet = lab(diet, c("1" = "Vegan", "2" = "Vegetarian", "3" = "Meat-eater")),
  cov_vote = lab(vote, c("1" = "I did not vote", "2" = "I was not eligible to vote", "3" = "Conservative", "4" = "Labour", "5" = "Liberal Democrat", "6" = "Scottish National Party", "7" = "Plaid Cymru", "8" = "UK Independence Party", "9" = "Green Party", "10" = "British National Party", "11" = "Other")),
  cov_beauty = num(beauty_1), cov_labour_therm = num(party_therm_1), cov_tory_therm = num(party_therm_2),
  cov_labour_like = num(labour_like_1), cov_tory_like = num(tory_like_1), cov_ideology = num(ideology_1),
  cov_duration_sec = as.numeric(durationinseconds),
  cov_attention_set_code = fifelse(is.na(check_w1), check_m1, check_w1), cov_check_4_code = check_4)]
st <- c("1" = "Conservatives", "2" = "Labour", "3" = "Neither")
for (s in c("vegan", "vegetarian", "white", "black", "progressive", "trad", "degree", "nodegree"))
  set(cv, j = paste0("cov_st_", s), value = lab(k[[paste0("st_", s)]], st))
## every non-missing source code was mapped (99 / blank -> NA only)
stopifnot(all(num(k$gender) %in% c(1:3, 99)), all(num(k$edu) %in% c(NA, 1:6, 99)), all(num(k$vote) %in% c(NA, 1:11)),
          all(num(k$rel) %in% c(1:6, 99)), all(num(k$ethnic) %in% c(NA, 1:5, 99)), all(num(k$diet) %in% c(NA, 1:3, 99)))
d <- merge(d, cv, by = "id")
stopifnot(d[, sum(choice), by = .(id, task)][, all(V1 == 1)], uniqueN(d$id) == 2993, nrow(d) == 95776,
          d[, !anyNA(.SD), .SDcols = patterns("^attr_")])
setcolorder(d, c("id", "task", "profile", "choice", paste0("attr_", names(des)), "trial_profile_gender"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "sleiman_2025_online_dating.csv"))
