##Australian candidate-choice conjoint from
##Snagovsky, F., Kang, W. C., Sheppard, J., & Biddle, N. (2020). Does descriptive
##representation increase perceptions of legitimacy? Evidence from Australia. Australian
##Journal of Political Science, 55(4), 378-398. https://doi.org/10.1080/10361146.2020.1804834
##Replication data: Harvard Dataverse doi:10.7910/DVN/LFY8O9, CC0 1.0, no restricted files.
##Files read: combined_Q2.tab (Dataverse "original format" download, combined_Q2.dta, with
##Stata value labels) and "Replication Code.do" (read as text only). No codebook or
##questionnaire is deposited, and the article was not accessible (paywalled).
##Usage: Rscript snagovsky_2020.R <raw dir> <output dir>
##
##943 respondents (srcid), 5 contests (task = contest) of 2 hypothetical candidates
##(profile = candidate Can1/Can2), 9,430 rows. The W7_ variables (wave 7 weight and party
##question) suggest the ANU / Life in Australia panel; 78 respondents have no W7 data (the
##file is "combined"; the deposit does not say from what).
##Attributes (Stata value-label text, 13 columns): gender, age, party, currently seated,
##political_id, left_right, marital status, children, country of birth, cultural background,
##other language, previous occupation, highest education.
##Ideology: the source stores it as two labelled variables, Political_id ("Centre left/right" /
##"Hard left/right") and left_right ("left" / "right"), with left_right fully determined by
##party (Labor = left, Liberal = right in all 9,430 rows). Both are kept verbatim as
##attr_political_id and attr_left_right; how they were combined on screen is not deposited.
##Restrictions (observed in the data, not documented): other language is tied to cultural
##background (Chinese -> Mandarin, Indian -> Hindi, Middle Eastern -> Arabic; Anglo-Caucasian
##-> any of None/Mandarin/Hindi/Arabic), and left_right to party. Level weights look
##unequal for other language as a result (None appears only with Anglo-Caucasian).
##Outcome: choice = Q2 (Candidate 1 / Candidate 2; the do file's `chosen`). Question wording
##is not deposited. Q2 also has "Don't know" (2,154 rows = 1,077 tasks): kept, choice = 0 on
##both profiles (opt-out). "Refused" (176 tasks) is no answer: those tasks are dropped, which
##removes 18 respondents who refused all 5; the table has 925 respondents, 9,078 rows.
##Covariates: cov_age_group (p_age_group value-label text; "Unknown" -> NA), cov_party_id
##(W7_Q9 "Generally speaking, do you usually think of yourself as...?" value-label text;
##"Prefer not to say" -> NA), cov_survey_weight (W7_weight), cov_gender_code (the source's
##0/1 `male` as cov_gender_code; its question is not deposited, so it is not mapped to cov_gender),
##cov_cob_group (pcob: Australian / ESB / NESB), cov_culture_group (pculture:
##White-Anglo/European / Asian / Other), cov_linked_fate (fate_yes, 0/1; "linked fate" per
##the do file). Dropped: the authors' derived dummies (cand_*, rparty, rculture, RCOB,
##two_party, rminority, same_party_Loop, chosen2, seifa_high, position_yes, lote_yes,
##ethno_anglo_yes).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- read_dta(file.path(raw, "combined_Q2.dta"))
lab <- function(v) as.character(as_factor(k[[v]], levels = "labels"))
q2 <- lab("Q2")
stopifnot(all(q2 %in% c("Candidate 1", "Candidate 2", "Don't know", "Refused")))
d <- data.table(id = as.integer(k$srcid), task = as.integer(k$contest),
                profile = match(k$candidate, c("Can1", "Can2")),
                choice = ifelse(q2 == "Refused", NA_integer_, as.integer(k$chosen)),
                attr_gender = lab("Gender"), attr_age = lab("Age"), attr_party = lab("Party"),
                attr_currently_seated = lab("Currently_se"),
                attr_political_id = lab("Political_id"), attr_left_right = lab("left_right"),
                attr_marital_status = lab("Marital_stat"), attr_children = lab("Children"),
                attr_country_of_birth = lab("COB"), attr_cultural_background = lab("Cul_bg"),
                attr_other_language = lab("Oth_lang"), attr_previous_occupation = lab("Prev_occ"),
                attr_education = lab("Highest_edu"))
stopifnot(!anyNA(d$profile), d[, all(attr_political_id %in% c("Centre left/right", "Hard left/right"))],
          d[, all((attr_party == "Labor") == (attr_left_right == "left"))],
          d[, !anyNA(.SD), .SDcols = patterns("^attr_")])
pid <- lab("W7_Q9"); pid[pid == "Prefer not to say"] <- NA
ag <- lab("p_age_group"); ag[ag == "Unknown"] <- NA
d[, `:=`(cov_age_group = ag, cov_party_id = pid, cov_survey_weight = as.numeric(k$W7_weight),
         cov_gender_code = as.integer(k$male), cov_cob_group = ifelse(k$pcob == "", NA, k$pcob),
         cov_culture_group = k$pculture, cov_linked_fate = as.integer(k$fate_yes))]
d <- d[!is.na(choice)]
stopifnot(d[, .N, .(id, task)][, all(N == 2)], d[, sum(choice), .(id, task)][, all(V1 <= 1)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "snagovsky_2020_candidates_australia.csv"))
