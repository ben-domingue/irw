##MP-choice conjoint on local roots (UK) from
##Campbell, R., Cowley, P., Vivyan, N., & Wagner, M. (2019). Why friends and neighbors?
##Explaining the electoral appeal of local roots. The Journal of Politics, 81(3), 937-951.
##https://doi.org/10.1086/703131
##Replication data: Harvard Dataverse doi:10.7910/DVN/C15VOD, CC0 1.0, no restricted files.
##File read: study2data_wide.rds (Study 2). Design facts and wording from the accepted
##manuscript (Wagner's prepublication full text, CCVW_localism_fulltext_prepub.pdf, via the
##Internet Archive): Study 2 section and Figure 2 (screenshot of a task).
##Usage: Rscript campbell_2019.R <raw dir> <output dir>
##
##Study 2 only: 1,719 YouGov respondents (4-5 February 2015), 5 comparisons (task 1-5, "Comparison
##1".."5") of two hypothetical MPs (profile 1 = MP 1, the source's "a" columns; profile 2 = MP 2,
##"b"), six attributes, "assigned randomly and independently" (article; the 768 profile ids are
##the full 4x4x4x3x2x2 factorial). Intro: "Please carefully read the description of these two
##MPs, both of whom were first elected in 2010." Each MP was shown as a bullet list:
##  "MP 1 is a <party> MP." / "<He/She> <position>." / "<He/She> <local roots>." / "<He/She>
##  spends on average <n> days of a 5-day week reviewing and working on national policies in
##  Parliament, and the remaining <5-n> days working on local constituency issues." / "When
##  considering policy matters, <he/she> mainly thinks about <his/her> <influence> views." /
##  "<His/Her> political interests include <policy>."
##attr_ text is the deposited display text (the wide file's HTML fragments, <b> tags removed):
##  attr_gender He/She (the pronoun is the only gender cue); attr_party_position e.g. "is
##  generally considered to be on the left-wing of the Labour party" (the party line "is a
##  Labour MP" always agrees; one randomized attribute in the article, 4 levels);
##  attr_local_roots (4 levels, e.g. "lives in another part of the country"); attr_time: the
##  parliament/constituency split as a sentence built from the template above with the
##  deposited day counts ("4 days ... and the remaining 1 day ..."; the source's consttime and
##  parltime always sum to 5); attr_influence "constituents'", "party's", "own personal"
##  (followed by "views"); attr_policy "economic policy and taxation"/"education and health
##  policy".
##choice: "Based on this information, which ONE of these two MPs would you prefer to have as
##  your MP?" (MP 1 / MP 2; a response was required, no opt-out).
##Covariates: cov_gender ("female"/"male", lowercased from the deposited factor gender
##  Female/Male), cov_age (years), cov_region (GOR), cov_education (qual, the deposit's
##  highest-qualification variable as stored: "None/Other/Unknown", "Level 1/2", "Level 3",
##  "Level 4"; the deposit has no finer version), cov_socialgrade (ABC1/C2DE), cov_party_id
##  (partyid, the deposited answer text, e.g. "Yes - Labour", "NoneDK"; the same answers as
##  the abbreviated pidfull used before), cov_interest, cov_lr_self, cov_lr_con, cov_lr_lab
##  (left-right placements as deposited), cov_local_years, cov_local_feel, cov_local_care
##  (numeric, as deposited), cov_survey_weight (W8, YouGov weight). No attention check or
##  duration in the deposit.
##Dropped: parliamentary constituency (quasi-identifier), YouGov refno, response date, web
##  browser / operating system / device, the authors' derived recodes (age/qualification/
##  social-grade groupings, lr* comparisons, local* categorisations).
##Study 1 (study1data.rds) is not built: a between-subjects 2x3 vignette (one MP's local roots
##  x behavioral information), one task, no profile pairs varying on both sides.
##N = 1,719 and 17,190 profile rows match the article.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
w <- as.data.table(readRDS(file.path(raw, "study2data_wide.rds")))
stopifnot(uniqueN(w$ID) == nrow(w))
untag <- function(x) trimws(gsub("<[^>]+>", "", as.character(x)))
rows <- list()
for (t in 1:5) for (p in 1:2) {
  s <- paste0("_", t, c("a", "b")[p])
  g <- function(v) untag(w[[paste0(v, s)]])
  ct <- g("consttime"); pt <- g("parltime")
  stopifnot(as.integer(sub(" .*", "", ct)) + as.integer(sub(" .*", "", pt)) == 5L)
  pos <- g("position"); pty <- g("party")
  stopifnot(all(mapply(grepl, sub("is a (.*) MP", "\\1", pty), pos)))
  rows[[length(rows) + 1]] <- data.table(
    id = as.integer(w$ID), task = t, profile = p,
    choice = as.integer(as.character(w[[paste0("choice", t)]]) == paste("MP", p)),
    attr_gender = g("gender"), attr_party_position = pos, attr_local_roots = g("local"),
    attr_time = paste0("spends on average ", pt, " of a 5-day week reviewing and working on national policies in Parliament, and the remaining ",
                       ct, " working on local constituency issues"),
    attr_influence = g("influence"), attr_policy = g("policy"))
}
d <- rbindlist(rows)
cv <- c(gender = "gender", age = "age", region = "region_GOR", education = "qual", socialgrade = "socialgrade", party_id = "partyid",
        interest = "interest", lr_self = "lrself", lr_con = "lrcon", lr_lab = "lrlab", local_years = "localyears",
        local_feel = "localfeel.num", local_care = "localcare.num", survey_weight = "W8")
cvd <- w[, c("ID", cv), with = FALSE]; setnames(cvd, c("id", paste0("cov_", names(cv))))
for (v in names(cvd)) if (is.factor(cvd[[v]])) set(cvd, j = v, value = as.character(cvd[[v]]))
cvd[, id := as.integer(id)][, cov_gender := tolower(cov_gender)]
stopifnot(all(cvd$cov_gender %in% c("female", "male")))
d <- merge(d, cvd, by = "id")
stopifnot(d[, sum(choice), .(id, task)][, all(V1 == 1)], nrow(d) == 17190L)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "campbell_2019_local_roots.csv"))
