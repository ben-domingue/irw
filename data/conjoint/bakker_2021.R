##Populist-message candidate conjoint (US; Study 2) from
##Bakker, B. N., Schumacher, G., & Rooduijn, M. (2021). The populist appeal: Personality and
##antiestablishment communication. The Journal of Politics, 83(2), 589-601.
##https://doi.org/10.1086/710014 (preprint read: PsyArXiv doi:10.31234/osf.io/n3je2, Study 2
##section and Table 2)
##Replication data: Harvard Dataverse doi:10.7910/DVN/HJSQNL, CC0 1.0. File read: Study2_data.csv
##(a raw Qualtrics export: header row, then a question-text row, then 1,209 responses). Also read
##as text: "1. ReadMe.pdf", Study2_coding.R and Study2_Analyses.R (the authors' code, not run).
##Usage: Rscript bakker_2021.R <dir holding Study2_data.csv> <output dir>
##
##PII IN THE SOURCE FILE (all dropped): IPAddress (V6), LocationLatitude/LocationLongitude,
##postalcode, city, PID (panel respondent id), ResponseID (V1), Q30 (free-text comments).
##NOT BUILT: Study 1 (observational surveys) and the other experiments fielded in the same SSI
##survey (food irradiation, brand/movie items, TTIP framing: columns Q15 onward): separate
##experiments, not examined further.
##SSI US online sample, July 2016. 869 respondents answered the round-1 choice (the preprint:
##869 assigned to the experiment, 868 completed, 1,736 choices); 2 rounds ("election rounds") x
##2 fictitious House candidates (A = profile 1, B = profile 2), 6 attributes per candidate,
##stored as the displayed text in Rd_<round>_<A|B>_<attribute>. Tasks with no choice answered
##are omitted. Tasks WITH a choice but all 12 attribute cells empty (round 1: 6, round 2: 7; the
##profiles shown were not saved) are DROPPED. Result: 863 round-1 and 861 round-2 tasks, 865
##respondents (the preprint reports 868 completing and 1,736 choices; 1,724 tasks here plus the 13
##unsaved ones is 1,737; the one-task difference is not resolved).
##Outcomes (question-text row of the export; scale from the preprint):
##  choice: Popchoice1 / Q159, "Which candidate do you prefer?" (1 = Candidate A, 2 = B), forced
##          choice: exactly one per task (checked).
##  rating_feeling: Pop1_feeling_1/_2 and Pop2_feelings_1/_2, "We would like to know how you
##          feel about the two candidates using something we call the feeling t[hermometer]..."
##          (the export truncates the text), per candidate; "very unfavorable (0) to very
##          favorable (100)" (preprint). Missing feeling stays NA.
##Attributes (exact displayed text; the authors' coding script matches the same strings):
##anti-establishment (Washington), people-centrism (Representation), conflict (House),
##immigration, taxation, background. The preprint's Table 2 paraphrases some of them (e.g.
##"mostly full of Washington insiders who only care about themselves"); the stored text is what
##the export recorded. Curly apostrophes in the taxation texts are kept as stored. Attribute
##order: the variable names do not record a position; not documented. Restrictions: none
##documented; the preprint's randomization check (Appendix B.2) is not in the deposit.
##Covariates (codes as stored; the export has no value labels, hence _code suffixes):
##cov_gender_code (Q110, "What is your gender?", 1/2; the authors recode 1 -> 0 and 2 -> 1 as
##`sex` without labels), cov_birth_year (Q116, "In what year were you born?"; only 1900-2000
##kept), cov_education_code (hs, 1-8), cov_income_code (Q114), cov_race_code (race),
##cov_hispanic_code (hispanic), cov_pid1_code..cov_pid4_code (party-ID branching items; the
##authors build a 7-point scale from them, Study2_coding.R L90-98), cov_agree_1..cov_agree_10
##(Q150_1..10, the 10 Goldberg Agreeableness items, raw 1-5; items 2,4,6,8,10 are reverse
##keyed in the authors' code), cov_auth_1..cov_auth_4 (auth1-4, child-rearing authoritarianism
##items, raw 1/2). No survey weight in the deposit. id re-keyed to integers in file order.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- fread(file.path(raw, "Study2_data.csv"), encoding = "UTF-8", header = TRUE, colClasses = "character")
stopifnot(s$Popchoice1[1] == "Which candidate do you prefer?", s$Q159[1] == "Which candidate do you prefer?")
s <- s[-1]
stopifnot(nrow(s) == 1209)
s[, rid := .I]
at <- c(Washington = "antiestablishment", Representation = "people_centrism", House = "conflict",
        Immigration = "immigration", Taxation = "taxation", Background = "background")
task <- function(r, chv, fv) {
  rows <- lapply(c(A = 1L, B = 2L), function(p) {
    lt <- c("A", "B")[p]
    x <- data.table(rid = s$rid, task = r, profile = p, ch = s[[chv]],
                    rating_feeling = suppressWarnings(as.numeric(s[[paste0(fv, p)]])))
    for (k in names(at)) x[, paste0("attr_", at[[k]]) := trimws(s[[sprintf("Rd_%d_%s_%s", r, lt, k)]])]
    x
  })
  x <- rbindlist(rows)
  x <- x[ch %in% c("1", "2")]
  blank <- x[, .(b = any(.SD == "")), .(rid), .SDcols = patterns("^attr_")][b == TRUE, rid]
  x <- x[!rid %in% blank]
  x[, choice := as.integer(as.integer(ch) == profile)][, ch := NULL]
  x
}
d <- rbind(task(1L, "Popchoice1", "Pop1_feeling_"), task(2L, "Q159", "Pop2_feelings_"))
stopifnot(!anyNA(d[, .SD, .SDcols = patterns("^attr_")]), d[, all(sapply(.SD, function(z) all(z != ""))), .SDcols = patterns("^attr_")],
          d[, sum(choice), .(rid, task)][, all(V1 == 1)], d[, all(rating_feeling %in% c(0:100, NA))])
n <- function(v) suppressWarnings(as.integer(s[[v]]))
cv <- data.table(rid = s$rid, cov_gender_code = n("Q110"), cov_birth_year = n("Q116"), cov_education_code = n("hs"),
                 cov_income_code = n("Q114"), cov_race_code = n("race"), cov_hispanic_code = n("hispanic"),
                 cov_pid1_code = n("pid1"), cov_pid2_code = n("pid2"), cov_pid3_code = n("pid3"), cov_pid4_code = n("pid4"))
cv[!(cov_birth_year >= 1900 & cov_birth_year <= 2000), cov_birth_year := NA_integer_]
for (i in 1:10) cv[, paste0("cov_agree_", i) := n(paste0("Q150_", i))]
for (i in 1:4) cv[, paste0("cov_auth_", i) := n(paste0("auth", i))]
d <- merge(d, cv, by = "rid")
d[, id := match(rid, sort(unique(rid)))][, rid := NULL]
setcolorder(d, c("id", "task", "profile", "choice", "rating_feeling"))
stopifnot(d[task == 1, uniqueN(id)] == 863, d[task == 2, uniqueN(id)] == 861, !anyDuplicated(d[, .(id, task, profile)]))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "bakker_2021_populist_appeal.csv"))
