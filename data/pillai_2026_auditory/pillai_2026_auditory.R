## Pillai, M. G., Mashburn, C. A., Tsukahara, J. S., Leroux, A., & Engle, R. W.
## (2026). Task-evoked pupillary responses reveal a role for attentional
## intensity in auditory discrimination. Journal of Experimental Psychology:
## General, 155, 2870-2887. doi:10.1037/xge0001982
## Data: OSF https://osf.io/f38ks, file combined_rt.csv. The OSF project sets
## no licence; permission to reformat and share under CC BY 4.0 given by
## email by Randall Engle, 2026-11-25 (copy in irw/licenseinfo/emails/).
## Psychophysics collection, irw#3686.
##
## Task: three adaptive two-tone discrimination tasks (pitch, duration,
## loudness): two tones are played and the participant judges which is
## higher / longer / louder. The difference between the tones is adapted to
## performance; the base tone is jittered from trial to trial.
##
## Layout:
##   item = task x tone difference, e.g. pitch_d07, duration_d040,
##          loudness_d03 (52 items; staircased, so items are uneven)
##   resp = 1 if correct (`Accuracy`)
##   rt   = response time in seconds (source already in seconds)
##   trial_number = the source `Trial`: order within the task (1-64).
##          combined_rt.csv repeats each trial once per pupil-analysis phase
##          (rows identical in Subject, Task, Trial, tones, accuracy and RT);
##          the script keeps one row per trial and checks that this leaves
##          Subject x Task x Trial unique.
##   trial_tone1, trial_tone2 = the two tone values in the source's units
##          (pitch in Hz, duration in ms, loudness on the source's scale)
##   itemcov_difference = |tone2 - tone1| as in the source `Difference`
##   cov_ac = the lab's attention-control composite; cov_antisaccade,
##   cov_va4, cov_sact (attention-control tasks), cov_ospan, cov_symspan,
##   cov_rotspan (complex spans), cov_rapm, cov_lettersets,
##   cov_numberseries (reasoning), as given in the file.
## Not included: pupil measures (combined_thesis.csv). Subject numbers are
## remapped to integers. The file holds 392 people; the paper analyses 336
## after its own exclusions, which the file does not flag.
##
## Usage: Rscript pillai_2026_auditory.R <combined_rt.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw <- if (length(args) >= 1) args[1] else "combined_rt.csv"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- read.csv(raw, stringsAsFactors = FALSE)
key <- c("Subject", "Task", "Trial", "Tone1", "Tone2", "Accuracy", "RT")
x <- x[!duplicated(x[, key]), ]
stopifnot(!any(duplicated(x[, c("Subject", "Task", "Trial")])))
stopifnot(all(x$Task %in% c("Pitch", "Duration", "Loudness")),
          all(x$Accuracy %in% 0:1),
          all(x$Difference == abs(x$Tone2 - x$Tone1)))

width <- c(Pitch = 2, Duration = 3, Loudness = 2)
subs <- sort(unique(x$Subject))
d <- data.frame(
  id = match(x$Subject, subs),
  item = sprintf("%s_d%0*d", tolower(x$Task), width[x$Task], as.integer(x$Difference)),
  resp = as.integer(x$Accuracy),
  rt = as.numeric(x$RT),
  trial_number = as.integer(x$Trial),
  trial_task = tolower(x$Task),
  trial_tone1 = as.numeric(x$Tone1),
  trial_tone2 = as.numeric(x$Tone2),
  cov_ac = round(as.numeric(x$AC), 5),
  cov_antisaccade = round(as.numeric(x$Antisaccade), 5),
  cov_lettersets = as.numeric(x$LetterSets),
  cov_numberseries = as.numeric(x$NumberSeries),
  cov_ospan = as.numeric(x$OSpan),
  cov_rapm = as.numeric(x$RAPM),
  cov_rotspan = as.numeric(x$RotSpan),
  cov_sact = round(as.numeric(x$SACT), 5),
  cov_symspan = as.numeric(x$SymSpan),
  cov_va4 = as.numeric(x$VA4),
  itemcov_difference = as.numeric(x$Difference),
  stringsAsFactors = FALSE)
## person covariates must be constant within person
for (v in grep("^cov_", names(d), value = TRUE))
  stopifnot(all(tapply(d[[v]], d$id, function(z) length(unique(z[!is.na(z)])) <= 1)))
d <- d[order(d$id, d$trial_task, d$trial_number), ]
table <- "pillai_2026_auditory"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
for (t in c("pitch", "duration", "loudness")) {
  s <- d[startsWith(d$item, t), ]
  print(round(tapply(s$resp, cut(s$itemcov_difference, 4), mean), 2))
}
