##Naturalization conjoint and vignette experiments (Switzerland), six design arms, from
##Hainmueller, J., Hangartner, D., & Yamamoto, T. (2015). Validating vignette and conjoint
##survey experiments against real-world behavior. PNAS, 112(8), 2395-2400.
##https://doi.org/10.1073/pnas.1416587112
##Replication data: Harvard Dataverse doi:10.7910/DVN/27793 ("Do Survey Experiments Capture
##Real-World Behavior? ..."), CC0 1.0, no restricted files, no terms. File read: repdata.dta
##(Dataverse "original format" download; its Stata value labels are the only source of the level
##text). repcode.do read as text. The SI Appendix (attribute list, question wording, design
##details) could not be retrieved, so wording below is the article's main-text description.
##Usage: Rscript hainmueller_2015.R <dir holding repdata.dta> <output dir>
##
##Main sample: 1,979 Swiss citizens sampled from the voting-age population of municipalities
##that used naturalization referendums before 2004, recruited by telephone, survey online. Each
##respondent was randomly assigned one of five designs and did 10 tasks; a later sample of 652
##students and staff of a Zurich university did only the forced-choice paired conjoint (5 tasks).
##Applicant profiles vary on 7 attributes: gender, origin, age, years since arrival, education,
##integration status, German proficiency. Level text = the value labels of repdata.dta, i.e. the
##authors' short English labels (e.g. integration "Traditions" / "Assimilated" / "Integrated" /
##"Indistinguishable", language "Adequate" / "Good" / "Perfect", origin "form. Yugoslavia"), not
##the wording respondents saw (not deposited; the survey language is not stated in the article).
##One table per design arm (the article estimates and benchmarks each design separately, and
##the arms differ in layout and question):
##  hainmueller_2015_natur_forced          mode 2 paired conjoint, forced choice (394 resp)
##  hainmueller_2015_natur_paired          mode 3 paired conjoint, accept/reject each (403)
##  hainmueller_2015_natur_paired_vignette mode 4 paired vignettes, accept/reject each (394)
##  hainmueller_2015_natur_single          mode 5 single conjoint, accept/reject (396)
##  hainmueller_2015_natur_single_vignette mode 6 single vignette, accept/reject (392)
##  hainmueller_2015_natur_students        mode 7 forced choice, student sample (652)
##Mode 1 (the behavioural referendum benchmark, municipality-level rejection shares) is not
##survey data and is not built.
##Outcome. The source variable Y is "rejected" (1 = rejected). Stored as:
##  forced arms: choice = 1 - Y, the profile preferred for naturalization ("respondents are forced
##    to choose which of the two immigrant profiles they prefer for naturalization"; paraphrase);
##    every kept task has exactly one rejected profile. No opt-out.
##  single arms: choice = 1 - Y (accept); single-profile accept/reject, so opt_out = yes.
##  paired accept/reject arms: rating_reject = Y raw (1 = reject, 0 = accept), a 0/1 judgement of
##    each profile that does not pick between them (both or neither may be rejected).
##Dropped: the "irregular" tasks (regular == 0; the authors' repcode.do keeps regular == 1 only).
##They are always task 10, cover about 75% of main-sample respondents, are undocumented in the
##deposit, and in the forced arm 111 of them have BOTH profiles rejected, so they were not the
##regular forced-choice task. All missing outcomes are in those tasks. No other rows dropped.
##Task = taskno (recorded). PROFILE POSITION IS NOT RECORDED: rows are shuffled within respondent
##(the two rows of a pair are seldom adjacent), so profile 1/2 is file order within the task,
##not screen position (profile_source unknown); do not use it for position effects.
##Randomization: no source read documents restrictions; OBSERVED: German and Austrian applicants
##never have "Adequate" German, and 21-year-olds are never "29 Years" since arrival. Level
##weights OBSERVED unequal: origin Italy and Turkey ~26% each vs ~6-9% for the others; language
##Perfect 52%; age 21 Years 20%; residency 29 Years 20% (others ~27%).
##Covariates (main arms): cov_survey_weight = wgt (entropy-balancing weight to the Swiss post-
##referendum study margins; NA for the 8 respondents with voted NA), cov_voted_target = voted
##(1 = aged over 30 and reports voting in naturalization referendums, the authors' target
##population; the article's estimates use voted == 1 only), cov_survey_complicated and
##cov_survey_toolong ("survey complicated/too long", 1 strongly disagree .. 5 strongly agree).
##trial_submit_sec = tasktime_submit (submit time for the task, seconds as stored). In the
##student table wgt = 1 and voted = 1 throughout, so neither is kept. munic/period (benchmark
##cluster codes, constant 99 in the survey) and originR (aggregated origin, derived) dropped.
##IDs are the deposit's integer respondent IDs (not platform IDs).
##N: 394+403+394+396+392 = 1,979 = article's main sample; student 652 (article gives no N in the
##main text).
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
h <- read_dta(file.path(raw, "repdata.dta"))
lab <- function(x) { l <- attr(x, "labels"); names(l)[match(as.numeric(x), l)] }
attrs <- c(gender = "gender", origin = "origin", age = "age", ysince = "years_since_arrival",
           educ = "education", integ = "integration", lang = "language")
x <- as.data.table(zap_labels(h))
for (v in names(attrs)) x[, paste0("attr_", attrs[[v]]) := lab(h[[v]])]
x <- x[mode > 1 & regular == 1]
stopifnot(!anyNA(x$Y), all(x$Y %in% 0:1), x[, !anyNA(.SD), .SDcols = patterns("^attr_")])
x[, id := as.integer(ID)][, task := as.integer(taskno)]
x[, profile := seq_len(.N), .(id, task)]
x[, trial_submit_sec := tasktime_submit]
stopifnot(x[, uniqueN(mode), id][, all(V1 == 1)])
ac <- paste0("attr_", attrs)
covs <- function(d, keep) if (keep) d[, `:=`(cov_survey_weight = wgt, cov_voted_target = as.integer(voted),
                                              cov_survey_complicated = as.integer(resp_complicated),
                                              cov_survey_toolong = as.integer(resp_toolong))] else d
build <- function(m, name, kind) {
  d <- copy(x[mode == m])
  np <- if (kind %in% c("single")) 1L else 2L
  stopifnot(d[, .N, .(id, task)][, all(N == np)])
  if (kind == "forced") { stopifnot(d[, sum(Y), .(id, task)][, all(V1 == 1)]); d[, choice := 1L - as.integer(Y)] }
  if (kind == "single") d[, choice := 1L - as.integer(Y)]
  if (kind == "paired") d[, rating_reject := as.integer(Y)]
  d <- covs(d, m != 7)
  oc <- intersect(c("choice", "rating_reject"), names(d))
  cc <- grep("^cov_", names(d), value = TRUE)
  d <- d[, c("id", "task", "profile", oc, ac, cc, "trial_submit_sec"), with = FALSE]
  setorder(d, id, task, profile)
  cat(name, nrow(d), uniqueN(d$id), "\n")
  fwrite(d, file.path(out, paste0(name, ".csv")))
}
build(2, "hainmueller_2015_natur_forced", "forced")
build(3, "hainmueller_2015_natur_paired", "paired")
build(4, "hainmueller_2015_natur_paired_vignette", "paired")
build(5, "hainmueller_2015_natur_single", "single")
build(6, "hainmueller_2015_natur_single_vignette", "single")
build(7, "hainmueller_2015_natur_students", "forced")
