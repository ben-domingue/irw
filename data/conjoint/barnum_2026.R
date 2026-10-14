##Video vignette 2x2 (offender race x victim race) bystander experiment from
##Barnum, T. C., Herman, S., Nagin, D. S., & Pickett, J. T. (2026). Understanding bystander decision-making:
##Experimental evidence on when and how people respond to crime. Criminology. https://doi.org/10.1111/1745-9125.70048
##Replication data: Harvard Dataverse doi:10.7910/DVN/FFLIHT, CC0 1.0. File read: WhoIntervenesData_Dataverse.tab
##("original format" download = Stata .dta, value labels used). WhoInterveneStataCode_Dataverse.do read as text
##(not run). The example video file is not used.
##Usage: Rscript barnum_2026.R <dir holding data.dta> <output dir>
##
##2,033 US adults (national online sample) each watched ONE video of a crime in progress and then answered
##questions about what they would do. Two randomized factors, set by the Qualtrics block randomizer
##(FL_18_DO_* display-order columns; 4 arms of 505-513 respondents each, equal allocation):
##  attr_offender_race: "Black offenders" / "White offenders" (authors' labels "Black Offender"/"White Offender",
##                      .do file lines 33-36; the offenders are a group of men in their 20s per the manipulation check Q91)
##  attr_victim_race:   "Black victim" / "White victim" (authors' labels "Black Victim"/"White Victim")
##The videos themselves are not deposited (only an example); level text is the authors' label of the video condition
##(there is no displayed text). One vignette per respondent: id = row number of the deposit (no respondent id in
##the file; the .do file's own `gen ID = _n`), task = 1, profile = 1. Presentation recorded as image (video).
##Outcomes (ratings, stored raw as in the deposit; 1 = Very likely ... 5 = Very unlikely: LOWER = MORE LIKELY;
##the authors reverse them with revrs for analysis):
##  rating_call_police, rating_find_witnesses, rating_take_picture, rating_follow_offender, rating_confront_offender,
##  rating_detain_offender = Q69_1..Q69_6, "If you saw this crime happen, how likely or unlikely is it that YOU would
##  do each of the following" (item texts are truncated in the deposit's labels; the six items are named by the
##  authors' renvars call int_call int_witns int_pic int_foll int_conft int_detn, so wording is a paraphrase);
##  rating_unsafe_to_intervene = Q71 "Thinking again about the incident you just witnessed: How safe or unsafe do you
##  [think physical intervention would be]" (authors' label "Perceived Danger of Physical Intervention"; 1 = Very safe
##  ... 5 = Very unsafe; HIGHER = MORE UNSAFE).
##Not kept: Q68_1-5 (beliefs about what the police would do if called: item texts truncated and not recoverable), Q73
##(worry about police harm), Q76, manipulation checks Q91/Q92, fitness, gun, height/weight and other respondent items.
##Covariates: cov_gender (Q22 Male/Female), cov_birth_year (Q23, free-typed: kept only as a whole number between
##1920 and 2007, else NA; the authors' typo corrections are not applied), cov_education (Q78 value-label text),
##cov_race (Q77 text), cov_hispanic (Q48 text).
##Respondent n = 2,033; the paper's analytic sample is 1,901 (complete cases on all variables used in its models,
##.do file "n = 1,901"). Not filtered here: missing outcomes stay NA.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
k <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(all(k$Status == 0))
lab <- function(x) as.character(as_factor(x, levels = "labels"))
arm <- k[, .(a1 = FL_18_DO_BP_BV_T, a2 = FL_18_DO_BP_WV_T, a3 = FL_18_DO_WP_BV_T, a4 = FL_18_DO_WP_WV_T)]
n_arm <- rowSums(!is.na(arm)); stopifnot(all(n_arm == 1))
vc <- max.col(!is.na(as.matrix(arm)), ties.method = "first")
d <- data.table(id = seq_len(nrow(k)), task = 1L, profile = 1L)
for (v in c("Q69_1", "Q69_2", "Q69_3", "Q69_4", "Q69_5", "Q69_6", "Q71")) {
  nm <- c(Q69_1 = "call_police", Q69_2 = "find_witnesses", Q69_3 = "take_picture", Q69_4 = "follow_offender",
          Q69_5 = "confront_offender", Q69_6 = "detain_offender", Q71 = "unsafe_to_intervene")[v]
  d[, paste0("rating_", nm) := as.integer(zap_labels(k[[v]]))]
}
d[, attr_offender_race := c("Black offenders", "Black offenders", "White offenders", "White offenders")[vc]]
d[, attr_victim_race := c("Black victim", "White victim", "Black victim", "White victim")[vc]]
d[, cov_gender := c("male", "female")[as.integer(zap_labels(k$Q22))]]
by <- suppressWarnings(as.integer(k$Q23)); by[!(by >= 1920 & by <= 2007)] <- NA
d[, cov_birth_year := by]
d[, cov_education := lab(k$Q78)][, cov_race := lab(k$Q77)][, cov_hispanic := lab(k$Q48)]
for (v in c("cov_education", "cov_race", "cov_hispanic")) d[get(v) %in% c("", "NA"), (v) := NA]
rc <- grep("^rating_", names(d), value = TRUE)
d <- d[rowSums(!is.na(d[, ..rc])) > 0]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "barnum_2026_bystander_video.csv"))
