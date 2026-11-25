## Jost, L. (2022). Mental Rotation - The Test Design, Sex Differences, and the
## Link to Physical Activity [Dissertation, University of Regensburg].
## doi:10.5283/epub.51432. Data and code: github.com/LeonardoJost/MCMR
## (multiple-choice mental rotation tests), licence GPL-3.0 (repository).
## Preregistrations: Exp 1 https://osf.io/b78yx ; Exp 2
## https://doi.org/10.23668/psycharchives.5394
## Mental rotation and psychophysics collections (irw#3686 follow-up).
##
## Task: chronometric mental rotation with 3D cube figures (12 models) shown as
## a target plus 2, 4 or 8 alternatives; the participant selects the
## alternatives that are rotated (not mirrored) copies. Blocks differ in the
## number of alternatives and in whether distractors are mirrored copies of
## the same figure ("paired") or of mixed figures ("mixed"). In the
## 2-alternative blocks the rotation angle is 45, 90, 135 or 180 degrees.
##
## ONLY the 2-alternative blocks are used (Ben, 2026-11-25). There each screen
## yields exactly one row: one choice, one RT, one angle. In 4- and
## 8-alternative blocks the rows are alternatives on a multi-figure screen
## (selections and misses, with correct rejections not recorded), which does
## not give a usable item; those blocks are left out.
##
## Tables:
##   jost_2022_mcmr_e1  Exp 1, dataset/Exp1/dataset.csv: 253 people
##   jost_2022_mcmr_e2  Exp 2, dataset/datasetFull.csv: 1,250 people (all
##                      recorded); cov_excluded = 1 for the 412 people not in
##                      the authors' cleaned dataset/dataset.csv
## Layout:
##   item = model x distractor type, e.g. m07_paired (24 items, each seen
##          about twice per person)
##   resp = 1 if the chosen alternative was the rotated copy (`type` hit),
##          0 if the mirrored one (`incorrect`). A `miss` is a screen left
##          unanswered before the time limit (no RT); those rows are dropped.
##   rt   = response time in seconds; non-positive source values set NA
##   trial_angle = rotation angle of the screen in degrees (45/90/135/180;
##          it varies within item, so it is a trial column)
##   trial_block = block label (main1-main6); trial_number = order within
##          person (block, then the source's within-block position)
##   trial_rt_outlier (Exp 1) = the source's trial outlier flag
##   cov_female; cov_education (Exp 2, German school/degree labels as
##   given); cov_experience (prior mental rotation test experience,
##   yes/no as given); cov_stem (Exp 1, STEM / nonSTEM / none as given)
## IDs ("id92") are remapped to integers.
##
## Usage: Rscript jost_2022_mcmr.R <dir with exp1.csv, full2.csv, exp2.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

rd <- function(f) read.csv2(file.path(raw_dir, f), stringsAsFactors = FALSE, dec = ".")

build <- function(x, table, extra) {
  x <- x[x$nStimuli == 2, ]
  stopifnot(all(x$type %in% c("hit", "incorrect", "miss")),
            all(is.na(x$reactionTime[x$type == "miss"]) | x$type[x$type == "miss"] == "miss"))
  x <- x[x$type != "miss", ]
  x <- x[order(x$ID, x$block, x$trialNumber), ]
  ids <- unique(x$ID); ids <- ids[order(as.integer(sub("id", "", ids)))]
  rt <- as.numeric(x$reactionTime)
  d <- data.frame(
    id = match(x$ID, ids),
    item = sprintf("m%02d_%s", as.integer(sub("m", "", x$modelNumber)), x$typeOfAlternatives),
    resp = as.integer(x$type == "hit"),
    rt = ifelse(rt > 0, rt / 1000, NA),
    trial_angle = as.numeric(x$deg),
    trial_block = x$block,
    trial_number = ave(seq_len(nrow(x)), x$ID, FUN = seq_along),
    cov_female = ifelse(is.na(x$sex), NA, as.integer(x$sex == "female")),
    stringsAsFactors = FALSE)
  d <- cbind(d, extra(x))
  cols <- c("id", "item", "resp", "rt", sort(grep("^trial_", names(d), value = TRUE)),
            sort(grep("^cov_", names(d), value = TRUE)))
  d <- d[, cols]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-20s rows=%6d ids=%5d items=%2d accuracy=%.3f\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
  ok <- d$resp == 1 & !is.na(d$rt)
  stopifnot(all(d$trial_angle %in% c(45, 90, 135, 180)))
  print(round(tapply(d$rt[ok], d$trial_angle[ok], median), 2))
}

e1 <- rd("exp1.csv")
build(e1, "jost_2022_mcmr_e1", function(x) data.frame(
  trial_rt_outlier = as.integer(x$outlier),
  cov_experience = x$Experience,
  cov_stem = x$STEM, stringsAsFactors = FALSE))

e2 <- rd("full2.csv")
kept <- unique(rd("exp2.csv")$ID)
build(e2, "jost_2022_mcmr_e2", function(x) data.frame(
  cov_education = x$education,
  cov_excluded = as.integer(!x$ID %in% kept),
  cov_experience = x$experience, stringsAsFactors = FALSE))
