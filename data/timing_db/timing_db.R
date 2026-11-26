## The Timing Database (Aydogan et al., 2023, Behavior Research Methods 56,
## 290-300, doi:10.3758/s13428-022-02050-9). OSF: https://osf.io/vrwjz
## (archive Datasets/datasets.rar_06_09_2025). Licence: CC BY 4.0, granted
## by Fuat Balci by email 2026-11-25 (the OSF project sets none; copy in
## irw/licenseinfo/emails/balci_timing_database_2026-11-25.txt).
## Psychophysics collection, irw#3686.
##
## The database pools interval-timing studies in one trial-level layout
## (Species, Subj_idx, Session, Block, Trial, Stim, Procedure, ...) with a
## codebook per study. This script builds the human datasets with at least
## 50 people (the psychophysics floor). One table per dataset; each cites
## the original study and the database.
##
## Item = the physical stimulus (target duration, or SOA for temporal order)
## crossed with any within-person condition; between-person conditions go in
## cov_ columns. Durations and SOAs are in seconds, as in the source.
##   Bisection (TB):        resp = 1 if judged "long" (Response L), 0 short.
##   Estimation (TE):       resp = estimated duration (seconds).
##   Reproduction (TR):     resp = reproduced duration (seconds).
##   Temporal order (TOJ):  resp = accuracy.
## Training trials are dropped where the source marks them.
##
## Built:
##   baccarani_2020_bisection    TB_Baccarani_2020
##   tipples_2019_bisection      TB_Tipples_2019
##   damsma_2021_reproduction    TE_Damsma_2019_Exp1 (motor block only)
##   suarezpinilla_2019_videos   TE_Suarez-Pinilla_2019
##   williams_2019_estimation    TE_Williams_2018_exp1
##   matthews_2018_toj           TOJ_Matthews_2018
##   bratzke_2019_reproduction_e1  TR_Bratzke_2019_Exp1
##   bratzke_2019_reproduction_e2  TR_Bratzke_2019_Exp2
##   hallez_2019_reproduction    TR_Hallez_2019
##   maass_2019_reproduction     TR_Maass_2019
##   maass_2019_mci_reproduction TR_Maass_2019_Exp2
##
## Left out:
##   Non-human datasets (FI, PI, DRL: rats, mice, pigeons) and human datasets
##     with fewer than 50 people (deJong_2021 has 49).
##   RT_Balci_2023 -- one retrospective duration judgement per person
##     (24,494 people), so no repeated items to model.
##   TOJ_Poole_2020 -- Choice (1/2) does not track which tone came first
##     (about 88% "1" for both orders), so it is neither the raw choice nor
##     clearly accuracy; held until the coding is confirmed.
##   TOJ_Williams_2018_Exp1 -- filed as temporal order but holds adaptive
##     duration-difference staircases on the same 52 people as
##     williams_2019_estimation; held for a closer look.
##
## Usage: Rscript timing_db.R <extracted datasets/ dir> <out_dir>

suppressMessages(library(data.table))
args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "datasets"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

files <- list.files(raw_dir, "^dataset_.*\\.csv$", recursive = TRUE, full.names = TRUE)
rd <- function(name) {
  f <- files[basename(files) == paste0("dataset_", name, ".csv")]
  stopifnot(length(f) == 1)
  x <- fread(f, showProgress = FALSE, encoding = "Latin-1")
  stopifnot(all(tolower(x$Species) %in% c("human", "bissolf")))
  x
}
## duration / SOA label: 0.208 -> "0.208", 1 -> "1"
lv <- function(v) sub("\\.?0+$", "", formatC(round(v, 3), format = "f", digits = 3))

finish <- function(d, table) {
  d <- as.data.frame(d)
  d <- d[!is.na(d$resp), ]
  front <- c("id", "item", "resp", "rt")
  trial <- sort(grep("^trial_", names(d), value = TRUE))
  covs <- sort(grep("^cov_", names(d), value = TRUE))
  icov <- sort(grep("^itemcov_", names(d), value = TRUE))
  d <- d[, c(intersect(front, names(d)), trial, covs, icov)]
  key <- c("id", "item", intersect(c("trial_session", "trial_block", "trial_number"), names(d)))
  stopifnot(!anyDuplicated(d[, key]))
  ord <- do.call(order, d[, c("id", intersect(c("trial_session", "trial_block", "trial_number"), names(d)))])
  d <- d[ord, ]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-30s rows=%6d ids=%4d items=%3d mean_resp=%.3f\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
  invisible(d)
}

## ---- Baccarani, Grondin, Laflamme & Brochard (2020), APP 83, 448-462 ------
## Auditory temporal bisection (white noise, 0.208-0.592 s, anchors 0.208 and
## 0.592), 250 female students in two experiments; each person did one
## odour x expectancy condition (between-person). The Session code gives the
## condition and the response hands: odd codes (311, 321, ...) answered short
## with the right hand, even codes with the left. Participant 30's rows carry
## Species "BISSOLF" and no ExperimentNumber; their odour (BLANK1) places them
## in Experiment 1.
x <- rd("TB_Baccarani_2020")
stopifnot(x[, uniqueN(Session), by = Subj_idx]$V1 == 1)
x[is.na(ExperimentNumber) & Odtest == "BLANK1", ExperimentNumber := 1]
stopifnot(!anyNA(x$ExperimentNumber), x$Response %in% c("L", "S"))
d <- x[, .(id = Subj_idx, item = paste0("d", lv(Test_Duration)),
           resp = as.integer(Response == "L"), trial_number = Trial,
           cov_experiment = as.integer(ExperimentNumber),
           cov_odour = tolower(sub("[0-9]$", "", Odtest)),
           cov_expectancy = c("NO-AROUSAL" = "none", RELAXING = "relaxing",
                              STIMULATING = "stimulating")[Instruct],
           cov_short_hand = ifelse(Session %% 2 == 1, "right", "left"),
           itemcov_duration = round(Test_Duration, 3))]
finish(d, "baccarani_2020_bisection")

## ---- Tipples (2019), APP 81, 707-715 ---------------------------------------
## Visual temporal bisection (0.4-1.6 s, anchors 0.4 and 1.6) with threatening
## or neutral animal pictures (within person), 53 adults. The source drops
## the eight training trials. Codebook: participant 27 was excluded from the
## analyses -- kept, flagged in trial_excluded_by_authors. Covariates: sex,
## age, EAS Temperament Survey subscale scores (anger, distress, fearfulness,
## sociability, activity) and STAI trait score, as in the source.
x <- rd("TB_Tipples_2019")
stopifnot(x$Response %in% c("L", "S"))
d <- x[, .(id = Subj_idx, item = paste0(Condition, "_d", lv(Test_Duration)),
           resp = as.integer(Response == "L"), rt = Response_Time,
           trial_number = Trial,
           trial_excluded_by_authors = as.integer(Subj_idx == 27),
           cov_female = as.integer(Sex == "female"), cov_age = Age,
           cov_eas_anger = anger, cov_eas_distress = distress,
           cov_eas_fearfulness = fearfulness, cov_eas_sociability = sociability,
           cov_eas_activity = activity, cov_stai_trait = STAI,
           itemcov_duration = Test_Duration)]
finish(d, "tipples_2019_bisection")

## ---- Damsma, Schlichting, van Rijn & Roseboom (2021), Collabra 7(1) -------
## Experiment 1 (preprint 2019, doi:10.31234/osf.io/pg7bs): visual intervals
## of 1-4 s judged by three methods within person (Block): verbal (digit)
## estimate, timeline (line) and motor reproduction (motor). Only the motor
## block is built. In the digit and line blocks the Response column does not
## track the target (median about 1.2-1.7 s for every target from 1 to 4 s),
## so it looks like a response time rather than the estimate; the motor
## reproductions do track it (median 1.0 s at 1 s, 3.6 s at 4 s).
## resp = reproduced duration (seconds). `version` (Calibrated /
## Uncalibrated) is constant within person and kept as cov_version.
x <- rd("TE_Damsma_2019_Exp1")
stopifnot(x[, uniqueN(version), by = Subj_idx]$V1 == 1)
x <- x[Block == "motor"]
d <- x[, .(id = Subj_idx, item = paste0("d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_number = Trial,
           cov_version = tolower(version), itemcov_duration = Target_Duration)]
finish(d, "damsma_2021_reproduction")

## ---- Suarez-Pinilla, Nikiforou, Fountas, Seth & Roseboom (2019), Collabra -
## Duration estimates for natural-scene videos of 1-64 s from three settings
## (City, Office and cafe, Campus and outside); item = setting x duration,
## resp = estimated duration (seconds). 52 adults.
x <- rd("TE_Suarez-Pinilla_2019")
vt <- c("City" = "city", "Office and cafe" = "office", "Campus and outside" = "campus")
stopifnot(x$VideoType %in% names(vt))
d <- x[, .(id = Subj_idx, item = paste0(vt[VideoType], "_d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_number = Trial,
           itemcov_duration = Target_Duration)]
finish(d, "suarezpinilla_2019_videos")

## ---- Williams, Yuksel, Stewart & Jones (2019), APP 81, 823-845, Exp 1 -----
## Verbal estimation of auditory, visual and tactile intervals (0.077-1.1 s,
## ten durations), modality within person, in three sessions; 52 adults.
## Training trials dropped. resp = estimate (seconds). Duration_Set in the
## source is garbled (a trailing per-row counter) and is not used.
x <- rd("TE_Williams_2018_exp1")
x <- x[Procedure == "TE"]
d <- x[, .(id = Subj_idx, item = paste0(tolower(Stim), "_d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_session = Session, trial_number = Trial,
           itemcov_duration = Target_Duration)]
finish(d, "williams_2019_estimation")

## ---- Matthews, Welch & Festa (2018), eNeuro 5(6) --------------------------
## Visual temporal order judgements on dynamic plaids (which component changed
## direction first), radial or rotational motion, SOA 0-0.2 s; 120 members of
## a drum corps in five sections (cov_section). resp = accuracy (the source
## gives accuracy, not the choice); at SOA 0 accuracy is chance by design.
## rt = Reaction_Time (seconds).
x <- rd("TOJ_Matthews_2018")
d <- x[, .(id = Subj_idx, item = paste0(tolower(Stim_Rotation), "_soa", lv(SOA)),
           resp = as.integer(Accuracy), rt = Reaction_Time, trial_number = Trial,
           cov_section = tolower(sub("Baritons", "baritones", Condition)),
           itemcov_soa = SOA)]
finish(d, "matthews_2018_toj")

## ---- Bratzke & Ulrich (2019), JEP:HPP 45, 1218-1235 -----------------------
## Temporal reproduction. Exp 1: visual or auditory standards (0.7-2.7 s),
## reproduced in the same modality (Congruency 1, "same") or the other
## ("cross"). Exp 2: auditory, filled vs empty, reproduction matching the
## standard (Congruency 1) or not. Each file pools three sub-experiments of
## 24 people (a, b, c: how durations were blocked), which are ids 1-24,
## 25-48 and 49-72 (checked: trial counts per person differ by sub-
## experiment). Training trials dropped. resp = reproduced duration in
## seconds. In Exp 1, 233 of 24,576 test rows hold values above 100 (up to
## 27,027) against standards of at most 2.7 s, with none between 20 and 100;
## they are not plausible in seconds or milliseconds and are dropped. Exp 2
## has no such values (maximum 133 s, one row) and is kept as recorded.
bratzke <- function(name, table) {
  x <- rd(name)
  tc <- intersect(c("Training", "Practice"), names(x))
  x <- x[get(tc) == "Testing"]
  bad <- name == "TR_Bratzke_2019_Exp1" & x$Response > 100
  cat(name, "rows dropped (resp > 100):", sum(bad), "\n")
  x <- x[!bad]
  sub_of <- cut(x$Subj_idx, c(0, 24, 48, 72), labels = c("a", "b", "c"))
  stopifnot(!anyNA(sub_of))
  d <- x[, .(id = Subj_idx,
             item = paste0(tolower(Stim), "_", ifelse(Congruency == 1, "same", "cross"),
                           "_d", lv(Target_Duration)),
             resp = as.numeric(Response), trial_block = Block, trial_number = Trial,
             cov_subexperiment = as.character(sub_of), itemcov_duration = Target_Duration)]
  finish(d, table)
}
bratzke("TR_Bratzke_2019_Exp1", "bratzke_2019_reproduction_e1")
bratzke("TR_Bratzke_2019_Exp2", "bratzke_2019_reproduction_e2")

## ---- Hallez, Damsma, Rhodes, van Rijn & Droit-Volet (2019), Acta Psych 192 -
## Visual temporal reproduction in a short (0.5-0.9 s) and a long (0.9-1.3 s)
## context, tested on different days (within person); 113 people aged 5, 6,
## 7 or adult (cov_age_group). item = context x duration (0.9 s appears in
## both). The source's Accuracy column is undocumented for a reproduction
## task and is not used.
x <- rd("TR_Hallez_2019")
d <- x[, .(id = Subj_idx, item = paste0(tolower(Range), "_d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_block = Block, trial_number = Trial,
           cov_age_group = sub(" years", "", AgeGroup), itemcov_duration = Target_Duration)]
finish(d, "hallez_2019_reproduction")

## ---- Maass, Schlichting & van Rijn (2019), Acta Psych 199, 102898 ---------
## Auditory temporal reproduction (0.625-1.296 s) in eight blocks alternating
## between a shorter and a longer duration set; 138 adults, each given one
## instruction about the sets (cov_instruction: none, pitch, short/long,
## A/B) and, in the pitch group, a pitch mapping (cov_pitch).
x <- rd("TR_Maass_2019")
stopifnot(x[, uniqueN(instruction), by = Subj_idx]$V1 == 1)
ins <- c(noLabel = "none", pitch = "pitch", "S/L" = "short_long", "A/B" = "a_b")
d <- x[, .(id = Subj_idx, item = paste0("d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_block = Session, trial_number = Trial,
           cov_instruction = ins[instruction],
           cov_pitch = c(longHigh = "long_high", shortHigh = "short_high")[pitch],
           itemcov_duration = Target_Duration)]
finish(d, "maass_2019_reproduction")

## ---- Maass, Riemer, Wolbers & van Rijn (2019), Behav Brain Res 373 --------
## Auditory temporal reproduction (1-1.68 s) in four blocks; 15 people with
## amnestic mild cognitive impairment (cov_mci = 1) and 44 healthy older
## controls.
x <- rd("TR_Maass_2019_Exp2")
x <- x[Procedure == "TR"]
d <- x[, .(id = Subj_idx, item = paste0("d", lv(Target_Duration)),
           resp = as.numeric(Response), trial_block = Session, trial_number = Trial,
           cov_mci = as.integer(MCI), itemcov_duration = Target_Duration)]
finish(d, "maass_2019_mci_reproduction")
