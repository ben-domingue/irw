## Tsukahara, J. S., Harrison, T. L., Draheim, C., Martin, J. D., & Engle, R. W.
## (2020). Attention control: The missing link between sensory discrimination
## and intelligence. Attention, Perception, & Psychophysics, 82, 3445-3478.
## doi:10.3758/s13414-020-02044-9
## Data: OSF https://osf.io/hsqru, "Study 1/Data Files/Raw Data" and
## "Study 2/Data Files/Raw Data": RAPM_raw.csv, LetterSets_raw.csv,
## NumberSeries_raw.csv. The OSF project sets no licence; permission asked of
## Randall Engle by email 2026-11-27 (do not release before the grant is in
## irw/licenseinfo/emails/).
##
## Three timed multiple-choice reasoning tests, given in both studies with the
## same items and keys (checked below):
##   RAPM          Raven's Advanced Progressive Matrices, 18 items, options A-H
##   LetterSets    letter sets, 30 items, options A-E
##   NumberSeries  number series, 15 items, options A-E
## One table per test, both studies stacked:
##   tsukahara_2020_rapm, tsukahara_2020_lettersets, tsukahara_2020_numberseries
##
## Layout:
##   id   = the lab's subject number, as in tsukahara_2020_discrimination and
##          pillai_2026_auditory, so people link across these tables
##          (Study 1 = 12xxx, Study 2 = 14xxx; Study 2 is the Pillai sample)
##   item = test and position, e.g. rapm_01 (items are given in a fixed order)
##   resp = 1 if correct (`Accuracy`); resp_raw = the option chosen
##   rt   = response time in seconds (source in ms)
##   cov_study = 1 or 2
##   itemcov_key = the keyed option
## The tests are timed: items a person did not reach have no row. A person's
## last row is dropped when the time ran out on it (no response recorded,
## `TimeLeft` missing): 14 rows, all in Study 2.
##
## Usage: Rscript tsukahara_2020_reasoning.R <hsqru dir> <out_dir>
##   <hsqru dir> holds the "Study 1" and "Study 2" folders as downloaded.

args <- commandArgs(trailingOnly = TRUE)
src <- if (length(args) >= 1) args[1] else "hsqru"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

tests <- c(rapm = "RAPM", lettersets = "LetterSets", numberseries = "NumberSeries")
n_items <- c(rapm = 18, lettersets = 30, numberseries = 15)

for (t in names(tests)) {
  x <- do.call(rbind, lapply(1:2, function(s) {
    f <- file.path(src, paste("Study", s), "Data Files", "Raw Data",
                   paste0(tests[[t]], "_raw.csv"))
    y <- read.csv(f, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM",
                  na.strings = c("NA", ""))
    y$study <- s
    y
  }))
  stopifnot(!any(duplicated(x[, c("Subject", "Trial")])),
            all(x$Trial %in% seq_len(n_items[[t]])),
            all(x$Accuracy %in% 0:1))
  ## one key per item, the same in both studies
  keys <- unique(x[, c("Trial", "Answer")])
  stopifnot(!any(duplicated(keys$Trial)))
  ## drop the item the time ran out on
  timed_out <- is.na(x$Response)
  stopifnot(all(is.na(x$TimeLeft[timed_out])))
  x <- x[!timed_out, ]
  stopifnot(all((x$Response == x$Answer) == (x$Accuracy == 1)))
  ## items are reached in order: no gaps
  stopifnot(all(tapply(x$Trial, x$Subject, function(z) all(sort(z) == seq_along(z)))))

  d <- data.frame(
    id = as.integer(x$Subject),
    item = sprintf("%s_%02d", t, as.integer(x$Trial)),
    resp = as.integer(x$Accuracy),
    resp_raw = x$Response,
    rt = round(as.numeric(x$RT) / 1000, 3),
    cov_study = x$study,
    itemcov_key = x$Answer,
    stringsAsFactors = FALSE)
  stopifnot(all(tapply(d$cov_study, d$id, function(z) length(unique(z)) == 1)))
  d <- d[order(d$id, d$item), ]
  table <- paste0("tsukahara_2020_", t)
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%s rows=%d ids=%d (study 1: %d, study 2: %d) items=%d timed_out=%d accuracy=%.3f\n",
              table, nrow(d), length(unique(d$id)),
              length(unique(d$id[d$cov_study == 1])), length(unique(d$id[d$cov_study == 2])),
              length(unique(d$item)), sum(timed_out), mean(d$resp)))
}
