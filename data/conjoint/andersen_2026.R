##Party/no-party candidate conjoint (US, MTurk) from
##Andersen, S. C., & Hjortskov, M. (2026). Masking or lexicographic preferences? Using conjoint
##experiments to distinguish between two fundamental theories of choice. Political Science
##Research and Methods (Dataverse PSRM; article DOI not found as of 2026-10-07).
##Replication data: Harvard Dataverse doi:10.7910/DVN/NA3YBS, CC0 1.0, no restricted files.
##File read: candidateconj_masking.dta (Stata value labels give the level text).
##Lexicographic_codebook.pdf (deposit) documents the variables; the authors' R log
##(masking_lexicographic_preferences_replication.html) was read as text for counts.
##Usage: Rscript andersen_2026.R <dir holding the .dta> <output dir>
##
##1,363 MTurk respondents (ResponseId in the source), each 5 tasks (scenario) of 2 candidate
##profiles (candidate 1/2): task and profile are recorded. Between-subject arms
##(trial_party_info, source experiment1): "Party information" (662) shows the candidate's party;
##"No party information" (683) does not (attr_party "(not shown)"). 18 respondents have no arm, no
##attributes and no answers and are dropped with the other rows lacking any outcome.
##The party arm is the same MTurk sample as Hjortskov & Andersen (2024, BJPolS,
##doi:10.1017/S0007123424000048; data doi:10.7910/DVN/F53FQ1, party arm only); this deposit
##adds the no-party arm.
##Outcomes:
##  choice: candidate chosen (source `choice`, "Candidate choice (yes/no)"); forced choice of
##     two, no opt-out. Question wording is not in the deposit.
##  rating_guess_democrat: no-party arm, task 5 only: the respondent's guess of each candidate's
##     party (source `guess`, "Guess about party affiliation (condition A, scenario 5)"),
##     coded 1 = Democrat, 0 = Republican (source 2/1). Not an evaluation; direction arbitrary.
##Attributes (Stata labels; codebook Table 1): party Democrat/Republican, gender Male/Female,
##race Black/White, age 35/45/55/65, job Business executive/Factory worker, experience
##None/1/2/3+. How the profiles were laid out and whether attribute order was randomized are
##not documented. Randomization restrictions are not documented.
##Covariate: cov_party_id7, "Generally speaking, do you usually think of yourself as a
##republican, a democrat or as an independent?" (source partyc), stored as the label text:
##Strong Democrat, Weak Democrat, Independent-Democrat, Independent, Independent-Republican,
##Weak Republican, Strong Republican (Stata value labels of partyc, codes 1-7; codebook partyc).
##No 3-category party ID in the deposit. No survey weight in the deposit or codebook.
##Dropped: ResponseId (Qualtrics/MTurk response ID; re-keyed to integers in source order).
##N: 1,363 ids, arms 683/662 match the authors' log; 1,326 respondents (679 no-party, 647 party)
##have >= 1 answer and are kept; rows with no answer are omitted (1 task keeps one profile).
##Spot check: the authors' feols of choice on attributes + task in the no-party arm (log,
##6,350 obs) gives Race Black 0.083, Experience 3+ 0.270; reproduced exactly (all coefficients).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- as.data.table(read_dta(file.path(raw, "candidateconj_masking.dta")))
lab <- function(x) { stopifnot(!is.null(attr(x, "labels"))); as.character(as_factor(x, levels = "labels")) }
stopifnot(s[, .N, ResponseId][, all(N == 10)])
s[, id := match(ResponseId, unique(ResponseId))]
d <- data.table(id = as.integer(s$id), task = as.integer(s$scenario), profile = as.integer(s$candidate),
                choice = as.integer(zap_labels(s$choice)),
                rating_guess_democrat = c(0L, 1L)[as.integer(zap_labels(s$guess))],
                attr_party = lab(s$party), attr_gender = lab(s$gen), attr_race = lab(s$race), attr_age = lab(s$age),
                attr_job = lab(s$job), attr_experience = lab(s$exp),
                trial_party_info = ifelse(zap_labels(s$experiment1) == 1, "Party information", "No party information"),
                cov_party_id7 = lab(s$partyc))
d <- d[!(is.na(choice) & is.na(rating_guess_democrat))]
stopifnot(d[trial_party_info == "No party information", all(is.na(attr_party))],
          d[trial_party_info == "Party information", !anyNA(attr_party)],
          d[!is.na(rating_guess_democrat), all(task == 5 & trial_party_info == "No party information")])
d[trial_party_info == "No party information", attr_party := "(not shown)"]
stopifnot(!anyNA(d[, grep("^attr_", names(d)), with = FALSE]))
stopifnot(!anyNA(d$attr_gender), !anyNA(d$trial_party_info), d[!is.na(choice), sum(choice), .(id, task)][, all(V1 == 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "andersen_2026_party_masking.csv"))
