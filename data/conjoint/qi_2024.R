##Welfare-program conjoint (US, MTurk) from
##Qi, H., & Haselswerdt, J. (2024). Ideology, information, and social welfare preferences.
##American Politics Research, 52(1), 41-51. https://doi.org/10.1177/1532673X231206151
##Replication data: Qi Hang & Haselswerdt Jake (2023), Harvard Dataverse doi:10.7910/DVN/NE1WLH,
##CC0 1.0, no restricted files. File read: conjoint_all.tab (Dataverse "original format" .dta,
##saved as conjoint_all.dta). Read as text only: conjointanalysis.do, conjointanalysis.log,
##CCES_analyses.do (the paper's CCES experiments are single-factor, not conjoints; CCES.tab and
##CCES_expanded.tab are not used). No questionnaire or codebook ships; the article was not reachable.
##Usage: Rscript qi_2024.R <dir holding conjoint_all.dta> <output dir>
##
##2,177 MTurk respondents (October 2021), 8 paired tasks of hypothetical federal/state welfare
##programs, 7 attributes. The file has no task column: each respondent has 16 rows numbered by
##`expand` (the authors' "Profile identifier" 1-16); task = ceiling(expand / 2), profile = 1 for
##odd expand, 2 for even. INFERRED from that numbering (every pair has exactly one chosen
##profile; checked), so task order/position as shown is not certain (task_source/profile_source
##inferred).
##ATTRIBUTE TEXT IS THE AUTHORS' VALUE LABELS, not the text shown. Policy description, problem 1
##and problem 2 were presumably prose about the EITC or TANF; only the labels survive (e.g.
##"EITC basic description", "TANF inadequacy most don't qualify", "EITC fraud paid preparers",
##"None"). Funding (Federal / State / Federal and state), total cost per year (19/27/53/70
##billion), participant population (5/8/17/25 million people) and time limit (No time limit / 2
##/ 4 / 8 years) are stored as labelled; the authors' figure labels say "$19 billion".
##RESTRICTION (yes): the authors' conjoint call constrains cat_a_desc#cat_a_prob1#cat_a_prob2,
##and the data show it: an EITC description appears only with EITC problems or "None", a TANF
##description only with TANF problems or "None". Levels "EITC's inadequacy & fraud problems" and
##"TANF's inadequacy & fraud problems" are value labels that never occur.
##Outcomes (one table, same tasks):
##  choice = program_choice ("Program choice": 1 = "Chose this program", 0 = "Chose other
##    program"); forced, no opt-out in the data. Question wording not deposited.
##  rating = program_support ("Program support"), 1-7, per profile, as stored; wording and end
##    labels not deposited (the authors treat higher as more support).
##Covariates (answer text as stored): cov_gender (Female/Male -> female/male), cov_age (whole
##numbers 18-100 only; the typed field has values like 4455642), cov_education (educ),
##cov_race, cov_faminc, cov_employ, cov_news_attention ("attention": follows public affairs ...,
##answer text), cov_ideology (ideo), cov_party_id (party: Democrat / Independent / Republican /
##Other / No preference), cov_party_id7 (the authors' pid_7 value label, built from party, strength
##and lean), cov_attention_pass_1..4 (the authors' pass flags: most-important-problem, newspaper,
##WWI/WWII and "neither" screeners), cov_duration_sec (whole survey, durationinseconds). Blank
##answer text -> NA.
##DROPPED / PII FOUND: ipaddress (IP addresses), responseid and the value labels of `id`
##(Qualtrics ResponseIds), randomid, start/end/recorded dates, raw screener answers, all dummy
##codings (a_*, eitc_tanf, workself, libcon, ...). id = the authors' integer `id` (codes 1-2177).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s0 <- read_dta(file.path(raw, "conjoint_all.dta"))
at <- c(description = "cat_a_desc", problem_1 = "cat_a_prob1", problem_2 = "cat_a_prob2", funding = "cat_a_funding",
        cost = "cat_a_cost", participants = "cat_a_number", time_limit = "cat_a_time")
s <- as.data.table(lapply(s0[, c("id", "expand", "program_choice", "program_support", at)], function(x) as.numeric(zap_labels(x))))
for (n in names(at)) set(s, j = paste0("attr_", n), value = as.character(as_factor(s0[[at[[n]]]], levels = "labels")))
p7 <- as.character(as_factor(s0$pid_7, levels = "labels"))
cvs <- as.data.table(s0[, c("gender", "age", "educ", "race", "faminc", "employ", "attention", "ideo", "party",
                            "mipscreener_pass", "newspaperscreener_pass", "wwiscreener_pass", "neitherscreener_pass",
                            "durationinseconds")])
rm(s0)
stopifnot(nrow(s) == 34832, uniqueN(s$id) == 2177, s[, .N, id][, all(N == 16)], s[, all(sort(expand) == 1:16), id][, all(V1)])
s[, task := as.integer(ceiling(expand / 2))][, profile := as.integer(2L - expand %% 2)]
stopifnot(s[, sum(program_choice), .(id, task)][, all(V1 == 1)], s[, all(program_support %in% 1:7)],
          !anyNA(s[, paste0("attr_", names(at)), with = FALSE]))
# restriction: description family matches problem family (or "None")
fam <- function(x) fifelse(x == "None", "none", fifelse(grepl("^EITC", x), "eitc", "tanf"))
stopifnot(s[, all(fam(attr_problem_1) %in% c("none", fam(attr_description))) && all(fam(attr_problem_2) %in% c("none", fam(attr_description)))])
nz <- function(x) { x <- trimws(as.character(x)); fifelse(x == "", NA_character_, x) }
age_ok <- function(x) { x <- suppressWarnings(as.numeric(x)); fifelse(!is.na(x) & x %% 1 == 0 & x >= 18 & x <= 100, as.integer(x), NA_integer_) }
stopifnot(all(cvs$gender %in% c("Female", "Male")))
cv <- cvs[, .(cov_gender = c(Female = "female", Male = "male")[gender], cov_age = age_ok(age), cov_education = nz(educ),
              cov_race = nz(race), cov_faminc = nz(faminc), cov_employ = nz(employ), cov_news_attention = nz(attention),
              cov_ideology = nz(ideo), cov_party_id = nz(party), cov_party_id7 = p7,
              cov_attention_pass_1 = as.integer(mipscreener_pass), cov_attention_pass_2 = as.integer(newspaperscreener_pass),
              cov_attention_pass_3 = as.integer(wwiscreener_pass), cov_attention_pass_4 = as.integer(neitherscreener_pass),
              cov_duration_sec = suppressWarnings(as.integer(durationinseconds)))]
d <- cbind(s[, .(id = as.integer(id), task, profile, choice = as.integer(program_choice), rating = as.integer(program_support))],
           s[, paste0("attr_", names(at)), with = FALSE], cv)
stopifnot(d[, uniqueN(.SD), id, .SDcols = names(cv)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "qi_2024_welfare_programs.csv"))
