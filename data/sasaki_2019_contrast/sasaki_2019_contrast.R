## Sasaki & Yamada (2019). Crowdsourcing visual perception experiments: a case
## of contrast threshold. PeerJ 7:e8339. doi:10.7717/peerj.8339
## Data: Figshare doi:10.6084/m9.figshare.9767057 ("Online experiment of
## contrast thresholds"), file data.zip. Licence: CC BY 4.0 (Figshare record).
## Psychophysics collection, irw#3686 (floor of 50 people, Ben 2026-11-23).
##
## Task: Gabor patch tilted 45 deg clockwise or counterclockwise; 2AFC
## orientation judgement with the arrow keys. Method of constant stimuli:
## 4 spatial frequencies x 7 Michelson contrasts per frequency (paper, Methods):
##   cpd code 1 = 0.02 cycles/pixel: 3, 8, 13, 18, 23, 28, 33 %
##   cpd code 2 = 0.05 cycles/pixel: 1, 6, 11, 16, 21, 26, 31 %
##   cpd code 3 = 0.09 cycles/pixel: 1, 6, 11, 16, 21, 26, 31 %
##   cpd code 4 = 0.38 cycles/pixel: 5, 10, ..., 35 %
## (0.5, 1, 2 and 8 cycles/degree under the lab viewing distance; online the
## viewing distance was not controlled, so the cycles/pixel value is the one
## that was actually fixed.) One spatial frequency per session (`phase`), four
## sessions, order randomised.
##
## Two online samples (Yahoo! Crowdsourcing, Japan), one table each:
##   sasaki_2019_contrast_online      onlinenonrep.csv, 285 people, each cell
##                                    once per tilt (56 trials per person)
##   sasaki_2019_contrast_online_rep  onlinerep.csv, 166 people, each cell 10
##                                    times per tilt (560 trials per person)
## The two samples share no ids. The laboratory sample (24 people, one csv per
## person) is under the floor of 50 and is left out.
##
## Layout (follows data/confidence_db/confidence_db_perception.R):
##   item  = tilt x spatial frequency x contrast, e.g. left_sf0.05_c16
##           (stimulus class x level; 56 items)
##   resp  = 1 if the reported tilt was correct (`seikai`)
##   rt    = response time in seconds (source: ms)
##   trial_number  = order of the trial within person (jsPsych trial_index)
##   trial_session = session 1-4 (`phase`); trial_repeat = 0-9 iteration
##   cov_female    = 1 female, 0 male, NA no answer (source gender 3/2/1;
##                   checked against the paper's counts for the analysed sample)
##   cov_age
##   cov_acq_correct = attention-check questions answered correctly (of 4).
##                   Four arithmetic questions, one per session (survey-likert
##                   rows); they are not perceptual items and are not in `item`.
##   cov_excluded_in_paper = 1 if the paper dropped the person: any wrong ACQ
##                   (both tables), or, in the repetition sample only, a
##                   negative probit slope or a threshold outside 0-100%
##                   (taken from the analysed-sample file alldata_online_rep.csv).
##   itemcov_contrast = Michelson contrast in %; itemcov_sf_cpp = cycles/pixel
## Dropped: jsPsych bookkeeping, the stimulus HTML, the session timestamp
## (`nichiji`) and the platform's random string id (remapped to integers).
##
## Usage: Rscript sasaki_2019_contrast.R <unzipped data dir> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "data"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

sf_cpp <- c(`1` = 0.02, `2` = 0.05, `3` = 0.09, `4` = 0.38)
contrasts <- list(`1` = c(3, 8, 13, 18, 23, 28, 33),
                  `2` = c(1, 6, 11, 16, 21, 26, 31),
                  `3` = c(1, 6, 11, 16, 21, 26, 31),
                  `4` = c(5, 10, 15, 20, 25, 30, 35))

build <- function(file, table, analysed_ids = NULL) {
  x <- read.csv(file.path(raw_dir, file), stringsAsFactors = FALSE,
                check.names = FALSE, na.strings = c("NULL", "NA", ""))
  acq <- x[x$trial_type == "survey-likert", ]
  acq_n <- tapply(acq$seikai, acq$randomID, sum)
  stopifnot(all(table(acq$randomID) == 4))

  t <- x[x$trial_type == "html-keyboard-response", ]
  t$cpd <- as.character(t$cpd)
  stopifnot(all(t$cpd %in% names(sf_cpp)),
            all(mapply(function(c, k) c %in% contrasts[[k]], t$contrast, t$cpd)),
            all(t$LR %in% 1:2), all(t$seikai %in% 0:1),
            all(t$key_press %in% c(37, 39)))
  ## LR == 1 is answered correctly with the left arrow (37), LR == 2 with the
  ## right arrow (39). The paper says the patch was tilted 45 deg clockwise or
  ## counterclockwise but not which key stood for which, so the tilt is named
  ## by its response key (left/right) rather than guessed.
  stopifnot(all((t$LR == 1 & t$key_press == 37) | (t$LR == 2 & t$key_press == 39)
                  == (t$seikai == 1)))
  tilt <- c(`1` = "left", `2` = "right")[as.character(t$LR)]

  ids <- unique(x$randomID)
  idmap <- setNames(seq_along(ids), ids)
  g <- x[!duplicated(x$randomID), c("randomID", "gender", "age")]
  g$cov_female <- c(`1` = NA, `2` = 0L, `3` = 1L)[as.character(g$gender)]

  d <- data.frame(
    id = unname(idmap[t$randomID]),
    item = sprintf("%s_sf%s_c%d", tilt, format(sf_cpp[t$cpd]), as.integer(t$contrast)),
    resp = as.integer(t$seikai),
    rt = as.numeric(t$rt) / 1000,
    trial_number = as.integer(t$trial_index),
    trial_session = as.integer(t$phase),
    trial_repeat = as.integer(t[["repeat"]]),
    itemcov_contrast = as.numeric(t$contrast),
    itemcov_sf_cpp = unname(sf_cpp[t$cpd]),
    stringsAsFactors = FALSE)
  m <- match(t$randomID, g$randomID)
  d$cov_female <- g$cov_female[m]
  d$cov_age <- as.integer(g$age[m])
  d$cov_acq_correct <- as.integer(acq_n[t$randomID])
  excl <- d$cov_acq_correct < 4
  if (!is.null(analysed_ids)) excl <- excl | !(t$randomID %in% analysed_ids)
  d$cov_excluded_in_paper <- as.integer(excl)

  if (all(d$trial_repeat == 0)) d$trial_repeat <- NULL
  cols <- c("id", "item", "resp", "rt",
            sort(grep("^trial_", names(d), value = TRUE)),
            sort(grep("^cov_", names(d), value = TRUE)),
            sort(grep("^itemcov_", names(d), value = TRUE)))
  d <- d[order(d$id, d$trial_number), cols]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  pp <- d[!duplicated(d$id), ]
  cat(sprintf("%-32s rows=%6d ids=%4d items=%3d excluded_in_paper=%d female=%d male=%d na=%d\n",
              table, nrow(d), length(unique(d$id)), length(unique(d$item)),
              sum(pp$cov_excluded_in_paper), sum(pp$cov_female == 1, na.rm = TRUE),
              sum(pp$cov_female == 0, na.rm = TRUE), sum(is.na(pp$cov_female))))
  invisible(d)
}

build("online_nonrepetition/onlinenonrep.csv", "sasaki_2019_contrast_online")

## The analysed repetition sample: ids in the authors' per-person summary file.
## The file's last row has no trailing newline, so read it with readLines.
rep_lines <- readLines(file.path(raw_dir, "online_repetition/alldata_online_rep.csv"), warn = FALSE)
rep_ids <- sub(",.*", "", rep_lines[-1])
build("online_repetition/onlinerep.csv", "sasaki_2019_contrast_online_rep",
      analysed_ids = rep_ids)
