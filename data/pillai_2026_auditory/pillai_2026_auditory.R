## Pillai, M. G., Mashburn, C. A., Tsukahara, J. S., Leroux, A., & Engle, R. W.
## (2026). Task-evoked pupillary responses reveal a role for attentional
## intensity in auditory discrimination. Journal of Experimental Psychology:
## General, 155, 2870-2887. doi:10.1037/xge0001982
## Psychophysics collection, irw#3686.
##
## Two sources for the same sample (Engle lab, 2017-2018):
##  (a) OSF https://osf.io/f38ks, combined_rt.csv (Pillai et al.). Permission to
##      reformat and share under CC BY 4.0 given by email by Randall Engle,
##      2026-11-25 (copy in irw/licenseinfo/emails/).
##  (b) OSF https://osf.io/hsqru, "Study 2/Data Files/Raw Data" (Tsukahara et
##      al. 2020, doi:10.3758/s13414-020-02044-9): {Pitch,Loud,Duration}
##      Discrimination_raw.csv and the retest files *_2_raw.csv. Permission
##      asked of Randall Engle by email 2026-11-27; do not release this version
##      before that grant is in irw/licenseinfo/emails/.
## (a) holds only the trials kept for the pupil analyses: about 10% of trials
## are missing, and they are not missing at random (accuracy .60 on the
## missing trials). The first version of this table (built from (a) alone)
## had that gap. (b) holds every trial, so this version takes trials from (b),
## the response time from (a) where (a) has the trial, and adds the retest.
## Every trial present in both agrees on tones and accuracy (checked below).
##
## Task: three adaptive two-tone discrimination tasks (pitch, duration,
## loudness): two tones are played and the participant judges which is
## higher / longer / louder. The difference between the tones is adapted to
## performance; the base tone is jittered from trial to trial.
##
## Layout:
##   id   = the lab's subject number (14xxx), shared with tsukahara_2020_rapm,
##          _lettersets and _numberseries (Study 2 of those tables)
##   item = task x tone difference, e.g. pitch_d07, duration_d040, loudness_d03
##          (staircased, so items are uneven)
##   resp = 1 if correct (`Accuracy`)
##   wave = 1 for the main session (2017-2018); 2 for the retest, which 63
##          people took in 2018 (*_2_raw.csv in (b))
##   rt   = response time in seconds, from (a); empty for trials (a) lacks,
##          for the people only in (b), and for the retest
##   trial_number = order within the task and session (1-64)
##   trial_tone1, trial_tone2 = the two tone values in the source's units
##          (pitch in Hz, duration in ms, loudness on the source's scale)
##   itemcov_difference = |tone2 - tone1| as in the source `Difference`
##   cov_ac = the lab's attention-control composite; cov_antisaccade,
##   cov_va4, cov_sact (attention-control tasks), cov_ospan, cov_symspan,
##   cov_rotspan (complex spans), cov_rapm, cov_lettersets,
##   cov_numberseries (reasoning), as given in (a); empty for people not in (a).
## Not included: pupil measures (combined_thesis.csv). combined_rt.csv repeats
## each trial once per pupil-analysis phase; one row per trial is kept.
## The paper analyses 336 people after its own exclusions, which neither
## source flags.
##
## Usage: Rscript pillai_2026_auditory.R <combined_rt.csv> <Study 2 Raw Data dir> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_a <- if (length(args) >= 1) args[1] else "combined_rt.csv"
dir_b <- if (length(args) >= 2) args[2] else "Study 2/Data Files/Raw Data"
out_dir <- if (length(args) >= 3) args[3] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

## (a) Pillai et al.
a <- read.csv(raw_a, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM")
key <- c("Subject", "Task", "Trial", "Tone1", "Tone2", "Accuracy", "RT")
a <- a[!duplicated(a[, key]), ]
stopifnot(!any(duplicated(a[, c("Subject", "Task", "Trial")])),
          all(a$Task %in% c("Pitch", "Duration", "Loudness")),
          all(a$Accuracy %in% 0:1),
          all(a$Difference == abs(a$Tone2 - a$Tone1)))

## (b) Tsukahara et al. Study 2, main session and retest
files <- c(Pitch = "Pitch", Duration = "Duration", Loudness = "Loud")
b <- do.call(rbind, lapply(names(files), function(t) {
  do.call(rbind, lapply(1:2, function(w) {
    f <- file.path(dir_b, sprintf("%sDiscrimination%s_raw.csv", files[[t]],
                                  if (w == 2) "_2" else ""))
    y <- read.csv(f, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM")
    data.frame(Subject = y$Subject, Task = t, Trial = as.integer(y$Trial),
               Tone1 = as.numeric(y$Tone1), Tone2 = as.numeric(y$Tone2),
               Difference = as.numeric(y$Difference),
               Accuracy = as.integer(y$Accuracy), wave = w,
               stringsAsFactors = FALSE)
  }))
}))
stopifnot(!any(duplicated(b[, c("Subject", "Task", "Trial", "wave")])),
          all(b$Accuracy %in% 0:1),
          all(b$Difference == abs(b$Tone2 - b$Tone1)))

## every main-session trial in both sources must agree
k_a <- paste(a$Subject, a$Task, a$Trial)
b1 <- b$wave == 1
k_b <- paste(b$Subject, b$Task, b$Trial)
m <- match(k_b, k_a)
both <- b1 & !is.na(m)
stopifnot(all(b$Tone1[both] == a$Tone1[m[both]]),
          all(b$Tone2[both] == a$Tone2[m[both]]),
          all(b$Accuracy[both] == a$Accuracy[m[both]]))
b$RT <- NA_real_
b$RT[both] <- as.numeric(a$RT[m[both]])

## trials in (a) for a person-task that (b) does not have at all
st_b <- unique(paste(b$Subject[b1], b$Task[b1]))
extra <- a[!paste(a$Subject, a$Task) %in% st_b, ]
stopifnot(all(paste(extra$Subject, extra$Task, extra$Trial) %in% k_a))
if (nrow(extra) > 0)
  b <- rbind(b, data.frame(Subject = extra$Subject, Task = extra$Task,
                           Trial = as.integer(extra$Trial),
                           Tone1 = extra$Tone1, Tone2 = extra$Tone2,
                           Difference = extra$Difference,
                           Accuracy = as.integer(extra$Accuracy), wave = 1,
                           RT = as.numeric(extra$RT), stringsAsFactors = FALSE))
## nothing in (a) is lost
stopifnot(all(k_a %in% paste(b$Subject, b$Task, b$Trial)[b$wave == 1]))

## person covariates from (a)
cv <- a[!duplicated(a$Subject), ]
mc <- match(b$Subject, cv$Subject)
width <- c(Pitch = 2, Duration = 3, Loudness = 2)
d <- data.frame(
  id = as.integer(b$Subject),
  item = sprintf("%s_d%0*d", tolower(b$Task), width[b$Task], as.integer(b$Difference)),
  resp = b$Accuracy,
  wave = b$wave,
  rt = b$RT,
  trial_number = b$Trial,
  trial_task = tolower(b$Task),
  trial_tone1 = b$Tone1,
  trial_tone2 = b$Tone2,
  cov_ac = round(as.numeric(cv$AC[mc]), 5),
  cov_antisaccade = round(as.numeric(cv$Antisaccade[mc]), 5),
  cov_lettersets = as.numeric(cv$LetterSets[mc]),
  cov_numberseries = as.numeric(cv$NumberSeries[mc]),
  cov_ospan = as.numeric(cv$OSpan[mc]),
  cov_rapm = as.numeric(cv$RAPM[mc]),
  cov_rotspan = as.numeric(cv$RotSpan[mc]),
  cov_sact = round(as.numeric(cv$SACT[mc]), 5),
  cov_symspan = as.numeric(cv$SymSpan[mc]),
  cov_va4 = as.numeric(cv$VA4[mc]),
  itemcov_difference = b$Difference,
  stringsAsFactors = FALSE)
## person covariates must be constant within person
for (v in grep("^cov_", names(d), value = TRUE))
  stopifnot(all(tapply(d[[v]], d$id, function(z) length(unique(z[!is.na(z)])) <= 1)))
d <- d[order(d$id, d$wave, d$trial_task, d$trial_number), ]
table <- "pillai_2026_auditory"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
cat(sprintf("wave 1: %d rows, %d ids, %d with rt, %d only in (a); wave 2: %d rows, %d ids\n",
            sum(d$wave == 1), length(unique(d$id[d$wave == 1])),
            sum(!is.na(d$rt)), nrow(extra),
            sum(d$wave == 2), length(unique(d$id[d$wave == 2]))))
