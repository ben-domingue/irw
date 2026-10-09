##Undemocratic-candidate conjoint (Study 1, second experiment; MTurk, USA) from
##Frederiksen, K. V. S., & Laustsen, L. (2025). Interstate conflict increases the appeal of
##undemocratic candidates. British Journal of Political Science. https://doi.org/10.1017/S0007123425101014
##Replication data: Harvard Dataverse doi:10.7910/DVN/MQBORA, CC0 1.0, no restricted files, no terms.
##File read: study1.dta (both Study 1 conjoint experiments, long: respondent x candidate). Read as
##text: Readme.txt, conjoint.do. Design and wording: the article (Study 1 section) and its
##Supplementary Appendix A (Table A1, attributes and probabilities).
##Usage: Rscript frederiksen_2025.R <dir holding study1.dta> <output dir>
##
##ONE TABLE, the SECOND Study 1 conjoint experiment only (conjointstudy == 2): 1,795 US MTurk
##respondents (2021), 10 pairs of hypothetical gubernatorial candidates (task; profile 1 =
##Candidate 1 = odd source `candid`, 2 = Candidate 2), 7 attributes. The FIRST experiment
##(conjointstudy == 1, 2,022 respondents) is NOT built: Table A1 lists different behaviour statements
##for it (fighting opponents in the streets, polling stations, court rulings by judges appointed by
##the other party, harassing journalists), but the .dta carries only the second experiment's value
##labels for `candem`, so experiment 1's codes cannot be mapped to text. (The two experiments are
##separate fieldings with separate respondents; `respondentid` restarts within each and is
##re-keyed here.)
##Attributes (.dta value-label text; Table A1 gives the same levels and probabilities):
##  attr_age (canage, years, drawn from 5 equally likely bands 40-49 ... 67-75), attr_gender
##  (Female 1/5, Male 4/5), attr_background (Company Founder 4/10, Lawyer 3/10, Civil Servant,
##  Self-employed, Political Career 1/10 each), attr_party (Democrat / Republican),
##  attr_economic_position (one of six redistribution positions), attr_social_position (one of six
##  morality/immigration positions), attr_behavior (eight democratic / undemocratic statements,
##  1/8 each; the PDF ligature "ﬃ" in the labels is written "ffi").
##Outcomes: each respondent was randomly assigned ONE outcome for all tasks (Appendix A), so each row
##has exactly one of four ratings (the others NA):
##  rating_dominance  "Candidate 1 (2) is aggressive, threatening, and intimidating"
##  rating_warmth     "... warm, reliable, and friendly"
##  rating_competence "... competent, knowledgeable, and skillful"
##    (seven-point Strongly disagree (1) ... Strongly agree (7))
##  rating_vote       "How likely is it that you would vote for candidate 1 (2)?" (seven points;
##    anchors not reported)
##The deposit stores all four RESCALED to 0-1 by the authors ((k - 1) / 6); they are kept as stored.
##"Don't know" was coded missing by the authors; candidates with no answer are omitted (rows with
##no outcome). Higher = more dominant / warm / competent / likely to vote.
##Covariates (answer text as stored): cov_age (ageres), cov_gender (Female/Male/Non-binary / Other
##-> female/male/other; blank -> NA), cov_education (edures), cov_income (incomeres), cov_party_id7
##(PIDres value-label text, ANES 7-point built by the authors from Q6-Q9), cov_state (stateres
##labels), cov_duration_sec. Dropped: Qualtrics ResponseId (PII), respondent number `resp`, the raw
##party items, countryres (all "The United States"), the authors' recodes (candemmg, item*,
##aggressives, cantax..., partymatch, socleft, redileft).
##Counts: 1,795 respondents in the file, 1,788 with at least one answer; 8,798 dominance
##observations here + 9,597 in experiment 1 = the article's 18,395. Spot check: undemocratic minus
##democratic behaviour = +0.157 on dominance, -0.100 warmth, -0.087 competence, -0.084 vote (the
##article pools both experiments: +0.20 dominance, -0.11 to -0.12 on the others).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x0 <- read_dta(file.path(raw, "study1.dta"))
lab <- function(v) gsub("ﬃ", "ffi", as.character(as_factor(x0[[v]], levels = "labels")))
keep <- zap_labels(x0$conjointstudy) == 2
x <- as.data.table(zap_labels(x0))
d <- x[, .(src = respondentid, task = as.integer(task), candid = as.integer(candid),
           rating_dominance = dominance, rating_warmth = warmth, rating_competence = competence, rating_vote = vote)]
d[, profile := 2L - candid %% 2L]
stopifnot(all(d$task == (d$candid + 1L) %/% 2L))
d[, `:=`(attr_age = as.character(x$canage), attr_gender = lab("cangender"), attr_background = lab("canbackground"),
         attr_party = lab("canparty"), attr_economic_position = lab("canredi"), attr_social_position = lab("cansoc"),
         attr_behavior = lab("candem"))]
g <- x$genderres; g <- c(Female = "female", Male = "male", "Non-binary / Other" = "other")[g]
d[, `:=`(cov_age = as.integer(x$ageres), cov_gender = unname(g), cov_education = fifelse(x$edures == "", NA_character_, x$edures),
         cov_income = fifelse(x$incomeres == "", NA_character_, x$incomeres), cov_party_id7 = lab("PIDres"),
         cov_state = lab("stateres"), cov_duration_sec = as.integer(x$durationinseconds))]
d <- d[keep]
stopifnot(d[, .N, src][, all(N == 20)], uniqueN(d$src) == 1795, !anyNA(d[, .SD, .SDcols = patterns("^attr_")]),
          d[, uniqueN(attr_behavior)] == 8, all(d$cov_age %in% 18:99),
          d[, sum(!is.na(c(rating_dominance, rating_warmth, rating_competence, rating_vote))), .(src)][, all(V1 >= 0)])
nout <- d[, (!is.na(rating_dominance)) + (!is.na(rating_warmth)) + (!is.na(rating_competence)) + (!is.na(rating_vote))]
stopifnot(all(nout <= 1))
d <- d[nout == 1]
d[, id := match(src, sort(unique(src)))][, c("src", "candid") := NULL]
setcolorder(d, c("id", "task", "profile"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "frederiksen_2025_undemocratic_dominance.csv"))
