## Makowski, D., Te, A.-S., Zhang, J., Kirk, S., & Ngoi, Z. L. (2024).
## IllusionGameEEG_data. OpenNeuro ds004587 v1.0.0.
## doi:10.18112/openneuro.ds004587.v1.0.0. Licence: CC0 (dataset_description.json).
## Psychophysics collection, irw#3686 (floor of 50 people, Ben 2026-11-23).
##
## Task (README): the Illusion Game. Stimuli made with Pyllusion for three
## illusions (Ebbinghaus, Mueller-Lyer, Vertical-Horizontal); on each trial the
## participant judges which target is bigger/longer as fast as possible,
## ignoring the context. Two parameters are manipulated:
##   illusion_strength   size of the biasing context (sign = direction:
##                       context that pushes towards vs against the right
##                       answer; 0 = no illusion). In these data positive
##                       strength is the incongruent, harder context: mean
##                       accuracy 0.52-0.76 by illusion, against 0.90-0.98
##                       for negative strength.
##   illusion_difference true difference between the targets (sign = which
##                       target is bigger; magnitude = task difficulty)
## Each illusion: 2 blocks of 64 trials, 128 strength x difference cells, each
## seen once by every participant -- a fixed, fully crossed grid of 384 items.
##
## Behaviour files: sub-*/ses-01/beh/sub-*_task-IG_run-01_beh.tsv (jsPsych).
## 103 participants; 3 have no illusion-game behaviour (README), so 100.
##
## Layout (follows data/confidence_db/confidence_db_perception.R):
##   item  = illusion x strength x difference, e.g. ebbinghaus_s0.36_dneg0.159
##           (a negative value is spelled "neg" so that sign is not read as
##           punctuation by item-variant checks)
##   resp  = 1 if the judgement was correct (`correct`)
##   rt    = response time in seconds (source: ms)
##   trial_number = order of the trial within person (jsPsych trial_index)
##   trial_block  = block 1-6 (`block_number`)
##   cov_age, cov_female (participants.tsv: sex F/M)
##   itemcov_strength, itemcov_difference = the two stimulus parameters
## Dropped: the 18 practice trials at the start (6 per illusion, strength 0 or
## an extreme +/-1e10 placeholder at the largest difference); jsPsych
## bookkeeping; browser, screen and OS fields; the session date and time; and
## jsPsych's random participant string. BIDS subject labels are remapped to
## integers.
##
## Usage: Rscript makowski_2024_illusion.R <raw_dir with beh/ and participants.tsv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

fs <- sort(Sys.glob(file.path(raw_dir, "beh", "sub-*_task-IG_run-01_beh.tsv")))
stopifnot(length(fs) == 100)
x <- do.call(rbind, lapply(fs, function(f) {
  d <- read.delim(f, na.strings = c("n/a", "NULL"), stringsAsFactors = FALSE)
  d <- d[!is.na(d$illusion_strength), ]
  d$sub <- sub("_ses-01.*", "", basename(f))
  d[, c("sub", "trial_index", "rt", "correct", "block", "illusion_strength",
        "illusion_difference", "block_number", "trial_number")]
}))

## Practice: the first 18 trials of block 1 (6 per illusion).
practice <- x$block_number == 1 & x$trial_number <= 18
stopifnot(sum(practice) == 18 * 100,
          all(abs(x$illusion_strength[!practice]) < 1e9))
x <- x[!practice, ]
stopifnot(all(table(x$sub) == 384))

lab <- c(Ebbinghaus = "ebbinghaus", MullerLyer = "mullerlyer",
         VerticalHorizontal = "verticalhorizontal")
num <- function(v) paste0(ifelse(v < 0, "neg", ""),
                          sub("\\.?0+$", "", formatC(abs(v), format = "f", digits = 3)))
x$item <- sprintf("%s_s%s_d%s", lab[x$block], num(x$illusion_strength),
                  num(x$illusion_difference))
## every person sees every item exactly once
stopifnot(length(unique(x$item)) == 384, !any(duplicated(x[, c("sub", "item")])))

p <- read.delim(file.path(raw_dir, "participants.tsv"), stringsAsFactors = FALSE)
subs <- sort(unique(x$sub))
idmap <- setNames(seq_along(subs), subs)
m <- match(x$sub, p$participant_id)
stopifnot(!any(is.na(m)), all(x$correct %in% c("TRUE", "FALSE", TRUE, FALSE)))

d <- data.frame(
  id = unname(idmap[x$sub]),
  item = x$item,
  resp = as.integer(as.logical(x$correct)),
  rt = as.numeric(x$rt) / 1000,
  trial_block = as.integer(x$block_number),
  trial_number = as.integer(x$trial_index),
  cov_age = as.integer(p$age[m]),
  cov_female = c(F = 1L, M = 0L)[p$sex[m]],
  itemcov_difference = as.numeric(x$illusion_difference),
  itemcov_strength = as.numeric(x$illusion_strength),
  stringsAsFactors = FALSE)
d <- d[order(d$id, d$trial_number), ]
table <- "makowski_2024_illusion"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
pp <- d[!duplicated(d$id), ]
cat(sprintf("%s rows=%d ids=%d items=%d female=%d male=%d na=%d mean_resp=%.3f\n",
            table, nrow(d), length(unique(d$id)), length(unique(d$item)),
            sum(pp$cov_female == 1, na.rm = TRUE), sum(pp$cov_female == 0, na.rm = TRUE),
            sum(is.na(pp$cov_female)), mean(d$resp)))
