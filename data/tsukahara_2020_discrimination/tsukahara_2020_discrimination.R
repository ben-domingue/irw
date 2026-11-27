## Tsukahara, J. S., Harrison, T. L., Draheim, C., Martin, J. D., & Engle, R. W.
## (2020). Attention control: The missing link between sensory discrimination
## and intelligence. Attention, Perception, & Psychophysics, 82, 3445-3478.
## doi:10.3758/s13414-020-02044-9
## Data: OSF https://osf.io/hsqru, folder "Study 1/Data Files": the four
## *Discrimination_raw.csv files and Data_Study1.csv. The OSF project sets no
## licence; permission asked of Randall Engle by email 2026-11-27 (Ben is
## proceeding on the assumption it is granted; do not release before the grant
## is in irw/licenseinfo/emails/). Psychophysics collection, irw#3686.
##
## Study 1 only. Study 2's pitch, loudness and duration trials are the same
## people and trials as pillai_2026_auditory (391 of 399 subjects shared,
## 22,602 of 25,536 pitch trials identical), so they are not rebuilt here.
## Study 1 shares no subjects with pillai_2026_auditory.
##
## Task: four adaptive two-alternative discrimination tasks, 64 trials each.
## Two stimuli are presented and the participant judges which is higher
## (pitch), louder (loudness), longer (line length) or larger (circle size).
## The difference between them is adapted to performance (staircase); the base
## stimulus is jittered from trial to trial.
##
## Layout (one table, as pillai_2026_auditory):
##   item = task x stimulus difference, e.g. pitch_d07, loudness_d03,
##          line_d25, circle_d10 (staircased, so items are uneven)
##   resp = 1 if correct (`Accuracy`)
##   trial_number = the source `Trial`: order within the task (1-64)
##   trial_task   = pitch, loudness, line or circle
##   trial_stim1, trial_stim2 = the two stimulus values in the source's units
##          (pitch in Hz, loudness on the source's scale, line length and
##          circle size in the source's display units)
##   itemcov_difference = |stim2 - stim1| as in the source `Difference`
##   cov_rapm, cov_lettersets, cov_numberseries (reasoning), cov_ospan,
##   cov_symspan, cov_rotspan (complex spans), cov_antisaccade,
##   cov_flankereffect, cov_stroopeffect (attention control): task scores as
##   given in Data_Study1.csv. That file lists only the 331 people kept after
##   the paper's exclusions; the other 21 people have these covariates empty.
## No response times in the source. Demographics.csv (date of birth, etc.) is
## not used. id is the lab subject number (12xxx), shared with
## tsukahara_2020_rapm, _lettersets and _numberseries.
## Subject 12256 appears twice in LineDiscrimination_raw.csv with identical
## trials; the copy is dropped. The paper's accuracy-based exclusions
## (Scored Data/removed/*_removed.csv) are not applied: every person is kept.
##
## Usage: Rscript tsukahara_2020_discrimination.R <Study 1/Data Files dir> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
src <- if (length(args) >= 1) args[1] else "Study 1/Data Files"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

tasks <- list(
  pitch    = list(file = "PitchDiscrimination_raw.csv",  s = c("Tone1", "Tone2"),     w = 2),
  loudness = list(file = "LoudDiscrimination_raw.csv",   s = c("Tone1", "Tone2"),     w = 2),
  line     = list(file = "LineDiscrimination_raw.csv",   s = c("Line1", "Line2"),     w = 2),
  circle   = list(file = "CircleDiscrimination_raw.csv", s = c("Circle1", "Circle2"), w = 2))

parts <- lapply(names(tasks), function(t) {
  k <- tasks[[t]]
  x <- read.csv(file.path(src, "Raw Data", k$file), stringsAsFactors = FALSE,
                fileEncoding = "UTF-8-BOM")
  x <- x[!duplicated(x[, c("Subject", "Trial", k$s, "Accuracy")]), ]
  stopifnot(!any(duplicated(x[, c("Subject", "Trial")])),
            all(x$Accuracy %in% 0:1),
            all(x$Difference == abs(x[[k$s[2]]] - x[[k$s[1]]])))
  data.frame(Subject = x$Subject, task = t, Trial = as.integer(x$Trial),
             s1 = as.numeric(x[[k$s[1]]]), s2 = as.numeric(x[[k$s[2]]]),
             Difference = as.numeric(x$Difference),
             Accuracy = as.integer(x$Accuracy), w = k$w,
             stringsAsFactors = FALSE)
})
x <- do.call(rbind, parts)
stopifnot(all(x$Difference == round(x$Difference)), max(x$Difference) < 100)

cv <- read.csv(file.path(src, "Data_Study1.csv"), stringsAsFactors = FALSE)
covs <- c(rapm = "RAPM", lettersets = "LetterSets", numberseries = "NumberSeries",
          ospan = "OSpan", symspan = "SymSpan", rotspan = "RotSpan",
          antisaccade = "Antisaccade", flankereffect = "FlankerEffect",
          stroopeffect = "StroopEffect")
stopifnot(!any(duplicated(cv$Subject)), all(cv$Subject %in% x$Subject))


m <- match(x$Subject, cv$Subject)
d <- data.frame(
  id = as.integer(x$Subject),
  item = sprintf("%s_d%0*d", x$task, x$w, as.integer(x$Difference)),
  resp = x$Accuracy,
  trial_number = x$Trial,
  trial_task = x$task,
  trial_stim1 = x$s1,
  trial_stim2 = x$s2,
  stringsAsFactors = FALSE)
for (v in names(covs)) d[[paste0("cov_", v)]] <- round(as.numeric(cv[[covs[[v]]]][m]), 5)
d$itemcov_difference <- x$Difference

## person covariates must be constant within person
for (v in grep("^cov_", names(d), value = TRUE))
  stopifnot(all(tapply(d[[v]], d$id, function(z) length(unique(z[!is.na(z)])) <= 1)))
d <- d[order(d$id, d$trial_task, d$trial_number), ]

table <- "tsukahara_2020_discrimination"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
## sanity: accuracy should rise with the stimulus difference within each task
for (t in names(tasks)) {
  s <- d[d$trial_task == t, ]
  cat(t, "\n"); print(round(tapply(s$resp, cut(s$itemcov_difference, 4), mean), 2))
}
