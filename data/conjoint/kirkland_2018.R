##Candidate choice conjoints with and without party labels, from
##Kirkland, P. A., & Coppock, A. (2018). Candidate choice without party labels: New insights
##from conjoint survey experiments. Political Behavior, 40(3), 571-591.
##https://doi.org/10.1007/s11109-017-9414-8
##Replication data: Harvard Dataverse doi:10.7910/DVN/WSUHI3, CC0 1.0. Files read (original
##format, both are .rdata despite the Dataverse extensions): mturk_replication.rdata
##(object mturk_clean), yougov_replication.rdata (object yougov_clean). Codebooks:
##mturk_codebook.txt, yougov_codebook.txt.
##Usage: Rscript kirkland_2018.R <raw dir> <output dir>
##
##Two tables, one per sample, because the YouGov version added levels (School Board President;
##Electrician, Stay-at-Home Dad/Mom) and the paper analyses the two samples separately:
##  kirkland_2018_candidates_mturk   MTurk convenience sample
##  kirkland_2018_candidates_yougov  YouGov nationally representative sample (weights kept)
##Design (paper pp. 578-580, Table 2, Figs 1-2): 5 "elections" per respondent, 2 candidates each,
##attributes race, gender, age, political experience, career experience, and party. All levels
##"fully randomized so that every possible candidate profile is equally likely"; attribute order
##randomized (not recorded). Whether party is shown is randomized per election: in nonpartisan
##elections the party row is absent, stored as blank attr_party (trial_election = nonpartisan).
##Level text = the codebook/factor labels (e.g. "Stay-at-Home Dad/Mom"); the stimuli are only
##shown as images in the paper, so capitalisation as displayed is not verified.
##Outcomes (paper p. 580):
##  choice = win, "Which of these two candidates do you prefer?", forced choice, no opt-out.
##  rating = comp, "On a scale from 0 to 100, how competent do you think these candidates would
##           be as mayor?" (0-100, higher = more competent; endpoint labels not reported).
##           YouGov: comp is NA for some candidates (127 respondents never rated); kept as NA.
##task = contest_no (recorded). profile = row order within contest (inferred; the deposit has
##no left/right column); each contest has exactly one winner (checked).
##MTurk: the MTurk worker ID is dropped and respondents re-keyed (mturk_clean); one worker
##ID appears with two sets of 5 contests (20 rows) and is dropped; contests left with one row
##by the authors' na.omit (4 contests) are dropped. Dropped as derived: democrat, republican,
##same_party, policy_index and valence_index (indices built from follow-up items not deposited).
##Covariates: cov_pid7 (respondent 7-point party ID, 1 = strong Democrat), cov_pid3 (text),
##cov_survey_weight (YouGov only). Respondent N is not given in the paper's main text.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ld <- function(f, o) { e <- new.env(); load(file.path(raw, f), envir = e); as.data.table(get(o, e)) }
build <- function(x, idcol) {
  x <- copy(x)
  x[, rid := get(idcol)]
  x[, n := .N, .(rid, contest_no)]
  x <- x[n == 2]
  x[, profile := seq_len(.N), .(rid, contest_no)]
  d <- data.table(rid = x$rid, task = as.integer(x$contest_no), profile = x$profile,
                  choice = as.integer(x$win), rating = as.integer(x$comp))
  for (v in c("Gender", "Age", "Race", "Job", "Political")) d[, paste0("attr_", tolower(v)) := as.character(x[[v]])]
  d[, attr_party := ifelse(x$Party == "non-partisan", "", as.character(x$Party))]
  d[, trial_election := ifelse(x$Party == "non-partisan", "nonpartisan", "partisan")]
  d[, cov_pid7 := as.integer(x$resp_pid_7)]
  d[, cov_pid3 := x$resp_pid_3_text]
  if ("weight" %in% names(x)) d[, cov_survey_weight := x$weight]
  stopifnot(d[, .(s = sum(choice), u = uniqueN(trial_election)), .(rid, task)][, all(s == 1 & u == 1)])
  d[, id := as.integer(factor(rid, levels = unique(rid)))][, rid := NULL]
  setcolorder(d, c("id", "task", "profile"))
  setorder(d, id, task, profile)
  d
}
m <- ld("mturk_replication.rdata", "mturk_clean")
dup <- m[, .N, resp_mturkid][N > 10, resp_mturkid]
m <- m[!resp_mturkid %in% dup]
m[, rid0 := as.integer(mturk_clean)]
dm <- build(m, "rid0")
y <- ld("yougov_replication.rdata", "yougov_clean")
y[, rid0 := as.integer(caseid)]
dy <- build(y, "rid0")
fwrite(dm, file.path(out, "kirkland_2018_candidates_mturk.csv"))
fwrite(dy, file.path(out, "kirkland_2018_candidates_yougov.csv"))
