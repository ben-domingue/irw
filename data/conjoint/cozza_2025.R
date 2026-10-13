##Party-leader conjoint (United Kingdom) from
##Cozza, J. F., Di Landro, G., Aldrich, A., & Somer-Topcu, Z. (2025). A rainbow ceiling? Sexual
##orientation and party leader evaluations. British Journal of Political Science, 55, e152.
##https://doi.org/10.1017/S0007123425100823
##Replication data: Harvard Dataverse doi:10.7910/DVN/GT6VQT, CC0 1.0, no restricted files.
##Files read: final_data.RData (data.frame `final_data`, tasks 1-4) and task5.RData (data.frame
##`task5`, the repeated task), each loaded into its own environment. Read as text only: the
##authors' "A Rainbow Ceiling ... .R" and "Online Appendix - A Rainbow Ceiling.pdf" (pdftotext;
##Table A2 attributes, Figure A2 sample task, section E.1 repeated task). bes_rps_2019_1.3.0.dta
##(British Election Study) and own_shape_IRR_labs.tab are not used.
##Usage: Rscript cozza_2025.R <dir holding the two .RData files> <output dir>
##
##1,198 UK adults (Bilendi online panel, September 2023, quotas on gender, age, region), five
##paired tasks of hypothetical parties and their newly elected leaders ("Party A" / "Party B"
##columns, attributes in rows: appendix Figure A2), 8 attributes, levels as stored in the factor
##labels, which match appendix Table A2 and Figure A2: who selects the leader, number of
##candidates in the leadership election, party's polling standing before the election, leader's
##gender, sexual orientation, age, previous experience, and the margin by which the leader won.
##Randomization: "for most of the attributes, levels were randomized uniformly", with one
##restriction (appendix C, footnote 3): 23 years as MP never with leader age 38 or 46 (the data
##show exactly these two empty cells). Attribute order is not documented (unknown).
##task/profile: recorded in final_data (tasks 1-4, profile 1 = Party A). TASK 5 REPEATS TASK 1
##WITH THE PROFILES SWAPPED (appendix E.1): task5.RData holds only its outcomes, with profile =
##the displayed position in task 5 (the authors' code flips it back to match task 1); its
##attributes are therefore copied from task 1, profile 3 - p. trial_repeat_of = 1 on task 5.
##Outcomes (all asked of every pair; answers were not forced, so some are NA):
##  choice_earned: "Which of these leaders earned their position?" (subsleg1)
##  choice_legislation: "Which of these leaders would be more effective in passing legislation?" (subsleg2)
##  choice_party_work: "Which of these leaders will work harder on behalf of their party?" (subsleg3)
##  choice_unify: "Which of these leaders would be more effective in unifying the party?" (subsleg4)
##  choice_seats: "Which of these leaders would help their party win more seats in the next
##    election?" (subsleg5). Wording from the article/appendix Table A9.
##  choice_vote: source column `vote` (1/2 = which profile); its wording is in no source in the
##    deposit or article (the authors do not analyse it).
##  rating_lr: source column `lr`, 0-10, rated separately for each profile; the authors use it as
##    the perceived left-right position of the party (appendix E.6: higher = further right).
##    Wording and end labels are not in any source.
##  Choices are the authors' own 0/1 *_y columns (stored = 1 for the profile named in the 1/2
##    source column; checked). Forced choices: every answered task has exactly one chosen profile.
##DROPPED: `trust` (per-profile trust, answer text only -- "Do not trust at all" .. "Trust
##completely" -- with no numeric coding or wording in the deposit), the authors' derived
##subsleg_index, start/end/recorded dates, attention_check (all "Brown": everyone passed the
##screen, kept as cov_attention_pass = 1). Rows with every outcome NA are omitted.
##Covariates: cov_gender (gender: Female -> female, Male -> male, "In another way" -> other),
##cov_age (age as typed, whole numbers 18-100 only), cov_education (edlevel answer text),
##cov_education_age (edlevel_60_text: age when full-time education ended, typed; values > 100,
##e.g. calendar years, set NA), cov_region, cov_lr_self (lrself, 0-10), cov_duration_sec (whole
##survey), cov_manipulation_check (mancheck1: "In which office were the politicians in the
##examples elected?", answer text; correct = "The position of party leader"),
##cov_most_important_char, cov_bias_1..6 (the six-item bias battery, agreement text; items in
##appendix E.4), cov_bias_timing (group: A = battery before the conjoint, 2/3 of the sample; B =
##after, per appendix Figure A3 and the group shares). Task-level page timers: trial_time_*.
##N: 1,198 respondents x 4 tasks = 9,584 rows (appendix B.2 "maximum of 9584 observations").
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
e <- new.env(); load(file.path(raw, "final_data.RData"), envir = e)
f <- new.env(); load(file.path(raw, "task5.RData"), envir = f)
s <- as.data.table(e$final_data); r <- as.data.table(f$task5)
s[, id := as.integer(as.character(id))][, profile := as.integer(as.character(profile))]
r[, id := as.integer(id)][, profile := as.integer(profile)]
stopifnot(nrow(s) == 9584, uniqueN(s$id) == 1198, s[, .N, id][, all(N == 8)], all(r$task == 5))
attrs <- c(selectorate = "selectorate", candidates = "candidates", polling = "polling", gender = "lsex",
           orientation = "lorientation", age = "lage", experience = "lexperience", margin = "lperformance")
# per-profile check that *_y = 1 exactly on the profile the 1/2 source code names
for (k in c(paste0("subsleg", 1:5), "vote")) {
  stopifnot(s[!is.na(get(k)), all(get(paste0(k, "_y")) == as.integer(get(k) == profile))])
  stopifnot(r[!is.na(get(paste0("rep_", k))), all(get(paste0("rep_", k, "_y")) == as.integer(get(paste0("rep_", k)) == profile))])
}
oc <- c(choice_earned = "subsleg1_y", choice_legislation = "subsleg2_y", choice_party_work = "subsleg3_y",
        choice_unify = "subsleg4_y", choice_seats = "subsleg5_y", choice_vote = "vote_y", rating_lr = "lr")
tim <- c(trial_time_first_click = "time_first_click", trial_time_last_click = "time_last_click",
         trial_time_page_submit = "time_page_submit", trial_time_click_count = "time_click_count")
main <- s[, c("id", "task", "profile", oc, tim, attrs), with = FALSE]
setnames(main, c("id", "task", "profile", names(oc), names(tim), paste0("attr_", names(attrs))))
for (k in paste0("attr_", names(attrs))) set(main, j = k, value = as.character(main[[k]]))
t1 <- main[task == 1L, c("id", "profile", paste0("attr_", names(attrs))), with = FALSE][, profile := 3L - profile]
rep <- r[, c("id", "task", "profile", paste0("rep_", oc), paste0("rep_", tim)), with = FALSE]
setnames(rep, c("id", "task", "profile", names(oc), names(tim)))
rep <- merge(rep, t1, by = c("id", "profile"))
stopifnot(nrow(rep) == nrow(r))
main[, trial_repeat_of := NA_integer_]; rep[, trial_repeat_of := 1L]
d <- rbind(main, rep, use.names = TRUE)
d <- d[!d[, Reduce(`&`, lapply(.SD, is.na)), .SDcols = names(oc)]]
age_ok <- function(x) { x <- suppressWarnings(as.numeric(x)); fifelse(!is.na(x) & x %% 1 == 0 & x >= 18 & x <= 100, as.integer(x), NA_integer_) }
ed_ok <- function(x) { x <- suppressWarnings(as.numeric(x)); fifelse(!is.na(x) & x %% 1 == 0 & x <= 100, as.integer(x), NA_integer_) }
cv <- unique(s[, .(id, cov_gender = c(Female = "female", Male = "male", `In another way` = "other")[gender],
                   cov_age = age_ok(age), cov_education = edlevel, cov_education_age = ed_ok(edlevel_60_text),
                   cov_region = region, cov_lr_self = as.integer(lrself), cov_duration_sec = duration_seconds,
                   cov_attention_pass = 1L, cov_manipulation_check = mancheck1,
                   cov_most_important_char = most_important_char,
                   cov_bias_1 = bias_battery_1, cov_bias_2 = bias_battery_2, cov_bias_3 = bias_battery_3,
                   cov_bias_4 = bias_battery_4, cov_bias_5 = bias_battery_5, cov_bias_6 = bias_battery_6,
                   cov_bias_timing = c(A = "before conjoint", B = "after conjoint")[group])])
stopifnot(nrow(cv) == 1198, all(s$gender %in% c("Female", "Male", "In another way")))
d <- merge(d, cv, by = "id")
for (k in grep("^choice_", names(d), value = TRUE)) set(d, j = k, value = as.integer(d[[k]]))
for (k in grep("^choice_", names(d), value = TRUE))
  stopifnot(d[, .(n = sum(!is.na(get(k))), c = sum(get(k), na.rm = TRUE)), .(id, task)][n > 0, all(n == 2 & c == 1)])
stopifnot(d[attr_experience == "Member of Parliament for 23 years", !any(attr_age %in% c("38", "46"))])
setcolorder(d, c("id", "task", "profile", names(oc), paste0("attr_", names(attrs)), "trial_repeat_of", names(tim)))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "cozza_2025_party_leaders.csv"))
