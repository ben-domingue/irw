##Four news-story conjoints from
##Darr, J. P., & Robinson, S. (2026). Assessing civic journalism training: A mixed-method applied
##research study. Political Communication. https://doi.org/10.1080/10584609.2026.2715698
##Replication data: Harvard Dataverse doi:10.7910/DVN/WBOZEL, CC0 1.0, no restricted files, no terms.
##Files read (Dataverse "original format" .dta downloads): engagement_conjoint.dta,
##solutions_conjoint.dta, goodconflict_conjoint.dta, transparency_conjoint.dta. Also read as text:
##the README and "PolComm Replication - Assessing Civic Journalism Training.do" (value labels and
##the authors' -conjoint- calls). The article is paywalled and was not read; the deposit has no
##questionnaire or codebook.
##Usage: Rscript darr_2026.R <raw dir> <output dir>
##
##Four separate Qualtrics Conjoint (CBCONJOINT) experiments on US Prolific samples, each with its
##own attribute set and fielding date, so FOUR TABLES (the authors analyse each on its own):
##  darr_2026_engagement_news   2024-08-15, 700 respondents, 6 tasks x 2 stories
##  darr_2026_good_conflict_news 2024-08-12, 701 respondents, 6 tasks x 2
##  darr_2026_solutions_news    2024-08-09, 702 respondents, 6 tasks x 2
##  darr_2026_transparency_news 2025-01-30, 607 respondents (600 finished), 8 tasks x 2
##The same Prolific worker can appear in several experiments; IDs are re-keyed per table, so
##respondents cannot be linked across tables.
##Task = choice_set (1-6 or 1-8); the source's `choice` (1..12 / 1..16) numbers the profiles
##within respondent, odd = first profile of the task (profile 1), even = second (profile 2).
##Outcome: choice = the authors' `chosen` (their -conjoint chosen ... id(prolific_id)- model), a
##forced pick of one of the two stories; every completed task has exactly one chosen story. The
##question wording is not in the deposit (design record: unknown). No rating.
##Attributes (feature display names in the data: Headline, Source, Editor's Note / Note, Pledge,
##Photo). Level text, per experiment:
##  - source: displayed text as stored (USA Today / Largest in-state newspaper / Largest in-state
##    nonprofit news / State AP wire).
##  - photo: a photograph; the stored text is the authors' description of the photo (Gov't
##    meeting / Journalist listening / Blue donkey vs. red elephant).
##  - engagement: note is the full displayed text; headline is the authors' SHORT LABEL as stored
##    (e.g. "Engagement: Your questions answered"); the headline wording is not in the deposit.
##  - solutions: headline and note are the full displayed text. The headline piped in the
##    respondent's state (${q://QID8/ChoiceGroup/SelectedAnswers/1}); the state answer is not
##    labelled in the deposit, so the pipe is stored as "[your state]".
##  - good conflict: headline is stored as codes (GC1, GC2, GC bad 1, GC bad 2) and note as short
##    labels; both are mapped to the authors' Stata value labels of headline_n / note_n (e.g.
##    "Good: Eye to Eye", "Bad: Corruption"). Not the displayed wording.
##  - transparency: headline, note and pledge are the authors' short labels as stored.
##  So most headline/note/pledge levels are the authors' labels, not the wording respondents read.
##Randomization: Qualtrics Conjoint with 260 design versions (vers_CBCONJOINT, kept as
##trial_design_version); no source documents restrictions or level probabilities. Identical
##profiles within a task occur (8 transparency tasks). Attribute order not recorded.
##Dropped: Prolific IDs (prolific_id, PROLIFIC_PID), Qualtrics ResponseId, LocationLatitude/
##Longitude (GPS), dates, consent/status/progress/finished, state_1..3 (unlabelled codes), the
##wide copies of the choices (c1..c8, chosen1..8), pid_5_TEXT (free text), debrief, cq/revision,
##and the authors' derived variables (age_n, rep2p, res_new, res_longer, hi_polint, most_polint,
##*_n codes, note_stub, hed). Transparency: 39 tasks of 7 respondents who left the survey early
##(finished = 0) have no choice and are dropped.
##Covariates: cov_birth_year (source `age`, a typed year of birth; the authors' age_n is 2024 -
##age); non-numeric entries (some respondents typed their Prolific ID) and values outside
##1900-2010 (a few typed an age instead) are NA. cov_gender: `sex`, value labels of
##engagement_wide.dta 1 Male, 2 Female, 3 Other -> male/female/other; code 4 (unlabelled, 1-2
##respondents per table) -> NA. cov_party_id: the authors' pid3 "Party ID (w/ leaners)" value
##labels Democrat/Independent/Republican (leaners counted with their party). Kept as codes with no
##labels in the deposit: cov_pid_code (raw pid; codes 1-5 unlabelled), cov_pid_strength, cov_pid_lean, cov_residence, cov_pol_interest,
##cov_hisp, cov_hisp_type, cov_race (multi-select, comma-joined codes). cov_duration_sec = whole
##survey duration. No survey weight.
##N: respondents per table as above; the article's Ns were not checked (paywalled).
##Spot check: the stored choice reproduces exactly one chosen story per completed task in all
##four experiments.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
lab <- function(v) { l <- attr(v, "labels"); stopifnot(all(zap_labels(v) %in% l)); names(l)[match(zap_labels(v), l)] }
build <- function(file, tab, attrs) {
  x <- as.data.table(read_dta(file.path(raw, file)))
  x <- x[x[, .(ok = sum(chosen) == 1), .(prolific_id, choice_set)], on = .(prolific_id, choice_set)][ok == TRUE]
  stopifnot(x[, .(s = sum(chosen), n = .N), .(prolific_id, choice_set)][, all(s == 1 & n == 2)])
  ids <- unique(x$prolific_id)
  d <- data.table(id = match(x$prolific_id, ids), task = as.integer(x$choice_set),
                  profile = 2L - as.integer(x$choice) %% 2L, choice = as.integer(x$chosen))
  stopifnot(all((as.integer(x$choice) + 1L) %/% 2L == d$task))
  for (n in names(attrs)) d[, paste0("attr_", n) := attrs[[n]](x)]
  d[, trial_design_version := as.integer(x$vers_cbconjoint)]
  by <- suppressWarnings(as.integer(x$age)); by[!is.na(by) & (by < 1900 | by > 2010)] <- NA
  d[, cov_birth_year := by]
  sx <- as.integer(x$sex); stopifnot(all(sx %in% c(1:4, NA)))
  d[, cov_gender := c("male", "female", "other", NA)[sx]]
  stopifnot(all(attr(x$pid3, "labels") == 1:3), names(attr(x$pid3, "labels")) == c("Democrat", "Independent", "Republican"))
  d[, cov_party_id := c("Democrat", "Independent", "Republican")[as.integer(x$pid3)]]
  d[, `:=`(cov_pid_code = as.integer(x$pid), cov_pid_strength = as.integer(x$pid_strength), cov_pid_lean = as.integer(x$pid_lean),
           cov_residence = as.integer(x$residence), cov_pol_interest = as.integer(x$pol_interest),
           cov_hisp = as.integer(x$hisp), cov_hisp_type = as.integer(x$hisp_type), cov_race = as.character(x$race),
           cov_duration_sec = as.integer(x$durationinseconds))]
  d[cov_race == "", cov_race := NA]
  for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(nzchar(d[[v]])))
  setorder(d, id, task, profile)
  fwrite(d, file.path(out, paste0(tab, ".csv")))
  cat(tab, nrow(d), uniqueN(d$id), "\n")
}
src <- function(x) as.character(x$source)
pho <- function(x) as.character(x$photo)
build("engagement_conjoint.dta", "darr_2026_engagement_news",
      list(headline = function(x) as.character(x$headline), source = src, note = function(x) as.character(x$note), photo = pho))
build("solutions_conjoint.dta", "darr_2026_solutions_news",
      list(headline = function(x) gsub("${q://QID8/ChoiceGroup/SelectedAnswers/1}", "[your state]", x$headline, fixed = TRUE),
           source = src, note = function(x) as.character(x$note), photo = pho))
build("goodconflict_conjoint.dta", "darr_2026_good_conflict_news",
      list(headline = function(x) { h <- lab(x$headline_n)
             stopifnot(all(paste(x$headline, h) %in% c("GC bad 1 Bad: Binary groups", "GC bad 2 Bad: Humiliation", "GC1 Good: Eye to Eye", "GC2 Good: Identity pride"))); h },
           source = src, note = function(x) { h <- lab(x$note_n); stopifnot(all(mapply(grepl, x$note, h, fixed = TRUE))); h }, photo = pho))
build("transparency_conjoint.dta", "darr_2026_transparency_news",
      list(headline = function(x) as.character(x$headline), source = src, note = function(x) as.character(x$note),
           pledge = function(x) as.character(x$pledge), photo = pho))
