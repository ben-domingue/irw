## Confidence Database (Rahnev et al., 2020, Nature Human Behaviour,
## doi:10.1038/s41562-019-0813-1). OSF: https://osf.io/s46pr  Licence: CC0 1.0.
## The database PI agreed to IRW inclusion (irw#719); scoping in irw#3686.
##
## This script converts the perception datasets with >= 100 subjects (the
## current core floor) into IRW tables. Mazancieux_2018 is left out: its
## perception block has two stimulus classes and no stimulus level, so it
## cannot reach the 3-item floor.
##
## Shared conventions (all tables):
##   id              = Subj_idx (Lebreton 22XX folded into 21XX: same people)
##   item            = stimulus class x stimulus level (x task / condition where
##                     the design has them). Many of these studies adjust the
##                     level per subject with a staircase, so items are sparse:
##                     each person sees a subset of levels.
##   resp            = decision accuracy (1 correct, 0 error); Xiang_2021 is an
##                     estimation task, so resp there is the typed estimate.
##   rt              = decision RT in seconds
##   trial_confidence= confidence rating on the source's own scale (scale
##                     differs by table; see each table's notes)
##   trial_rt_conf   = confidence RT in seconds, where recorded
##   trial_response  = the alternative chosen, as coded in the source
##   trial_number    = order of the trial within person, from the source's row
##                     order (Confidence Database files are stored in trial
##                     order) unless the source carries its own index
##   itemcov_level   = the numeric stimulus level that the item label encodes
##
## Usage: Rscript confidence_db_perception.R <raw_dir> <out_dir>
##   raw_dir holds data_<Name>.csv files from the OSF "Confidence Database"
##   folder (downloaded as-is).

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

rd <- function(name) {
  x <- read.csv(file.path(raw_dir, paste0("data_", name, ".csv")),
                fileEncoding = "UTF-8-BOM", check.names = FALSE)
  names(x) <- sub("^﻿", "", names(x))
  x
}
lv <- function(v) formatC(signif(v, 4), format = "fg", digits = 4, flag = "#") |>
  trimws() |> sub(pattern = "\\.?0+$", replacement = "") |>
  (\(s) ifelse(grepl("^\\.", s), paste0("0", s), s))()
trialno <- function(id) ave(seq_along(id), id, FUN = seq_along)
num <- function(v) { v <- suppressWarnings(as.numeric(v)); v[is.nan(v)] <- NA; v }

finish <- function(d, table) {
  d$resp <- num(d$resp)
  d <- d[!is.na(d$resp), ]
  front <- c("id", "item", "resp", "rt", "treat")
  trial <- sort(grep("^trial_", names(d), value = TRUE))
  covs <- sort(grep("^cov_", names(d), value = TRUE))
  icov <- sort(grep("^itemcov_", names(d), value = TRUE))
  cols <- c(intersect(front, names(d)), trial, covs, icov)
  d <- d[order(d$id, d$trial_number), cols]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-24s rows=%7d ids=%4d items=%4d\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item))))
  invisible(d)
}

## 2AFC tables that share the standard column layout.
std2afc <- function(x, stimlab, level = NULL, levprefix = "", extra = NULL,
                    rt = "RT_dec", rtconf = "RT_conf", rt_scale = 1) {
  sl <- stimlab[as.character(x$Stimulus)]
  if (!is.null(level)) {
    item <- paste0(sl, "_", levprefix, lv(x[[level]]))
  } else item <- sl
  if (!is.null(extra)) item <- paste0(extra, "_", item)
  d <- data.frame(id = x$Subj_idx, item = item, resp = x$Accuracy,
                  rt = num(x[[rt]]) / rt_scale,
                  trial_confidence = num(x$Confidence),
                  trial_response = x$Response)
  if (!is.null(rtconf) && rtconf %in% names(x)) d$trial_rt_conf <- num(x[[rtconf]]) / rt_scale
  if (!is.null(level)) d$itemcov_level <- num(x[[level]])
  d$trial_number <- trialno(d$id)
  d
}

## ---- Rouault, Seow, Gillan & Fleming (2018), Biol Psychiatry -------------
## dot-number discrimination; DotDiff = dot difference (Expt 2: log, staircase)
for (e in 1:2) {
  x <- rd(sprintf("Rouault_2018_Expt%d", e))
  d <- std2afc(x, c("0" = "s0", "1" = "s1"), level = "DotDiff", levprefix = "dd")
  finish(d, sprintf("rouault_2018_dots_e%d", e))
}

## ---- Haddara & Rahnev (2022), Psych Science, Expt 1 -----------------------
## Task 1 = X vs O majority; Task 2 = red vs blue majority. treat = assigned to
## the trial-by-trial feedback group (Task 2 had no feedback for either group).
x <- rd("Haddara_2022_Expt1")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
lab <- ifelse(x$Task == 1, c("x", "o")[x$Stimulus], c("red", "blue")[x$Stimulus])
d <- data.frame(id = x$Subj_idx, item = paste0(ifelse(x$Task == 1, "letter_", "colour_"), lab),
                resp = x$Accuracy, rt = num(x$RT_dec),
                trial_confidence = num(x$Confidence), trial_rt_conf = num(x$RT_conf),
                trial_response = x$Response)
d$treat <- ave(x$Feedback, x$Subj_idx, FUN = max)
d$trial_number <- trialno(d$id)
## only 4 items: task x majority class; the grid composition was not exported.
finish(d, "haddara_2022_majority")

## ---- Jaquiery & Yeung (unpublished; collected 2018) -----------------------
## dot discrimination; Difficulty = dots moved from one box to the other.
## Decision and confidence given together on one slider (RT_decConf).
x <- rd("Jaquiery_unpub")
d <- std2afc(x, c("0" = "left", "1" = "right"), level = "Difficulty", levprefix = "diff",
             rt = "RT_decConf", rtconf = NULL)
d$trial_in_block <- x$Trial_in_block
finish(d, "jaquiery_2018_dots")

## ---- Mazor, Moran & Fleming (2021), Neurosci Conscious, Expts 1-7 ---------
## masked discrimination; level = SOA in ms (staircased); confidence 0-1 continuous
## Stimulus codes 1/2 are kept as s1/s2: the readmes name the two classes
## (e.g. Q and O) but not which code is which.
mz <- c(`1` = "qo", `2` = "co", `3` = "tilt", `4` = "curve", `5` = "cube",
        `6` = "mirror_n", `7` = "grating")
for (e in names(mz)) {
  x <- rd(paste0("Mazor_2021_Expt", e))
  d <- std2afc(x, c("1" = "s1", "2" = "s2"), level = "SOA", levprefix = "soa")
  d$trial_number <- x$Trial
  finish(d, sprintf("mazor_2021_%s", mz[[e]]))
}

## ---- Prieto, Reyes & Silva (unpublished) ----------------------------------
## two-scene contrast discrimination (Fleming et al., 2010 task), staircased
## contrast; RT >= 2 s not recorded (NA). Confidence continuous 1-6.
x <- rd("Prieto_unpub")
## contrast sits on a 0.01 grid; round away float noise (-5e-16) and drop the
## two rows recorded at a negative contrast, which cannot occur.
x$Contrast <- round(x$Contrast, 2)
x <- x[x$Contrast >= 0, ]
d <- std2afc(x, c("1" = "first", "2" = "second"), level = "Contrast", levprefix = "c")
finish(d, "prieto_unpub_contrast")

## ---- Bang, Shekhar & Rahnev (2019), JEP:General, Expt 2 -------------------
## Task 1 = coarse (45 deg, Gabor in noise; level = contrast); Task 2 = fine
## (~1 deg tilt; level = tilt). Level was fixed per batch of subjects, so it is
## kept per trial, not on the item. Subjects 179-201 were excluded in the paper.
x <- rd("Bang_2019_Exp2")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
d <- std2afc(x, c("0" = "s0", "1" = "s1"),
             extra = paste0(ifelse(x$Task == 1, "coarse", "fine"),
                            ifelse(x$Catch_trial == 1, "_catch", "")))
d$trial_stim_level <- num(x$ContrastOrTilt)
d$cov_excluded_in_paper <- as.integer(x$Subj_idx >= 179)
finish(d, "bang_2019_gabor")

## ---- Wierzchon et al. (2014), Consc Cogn ----------------------------------
## masked face-sex identification; Difficulty 1-12 = 192 down to 16 ms.
## Awareness scale (CR, PAS, PDW, FOW) and rating order are between-subject.
x <- rd("Wierzchon_2014")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
d <- std2afc(x, c("1" = "s1", "2" = "s2"), level = "Difficulty", levprefix = "d")
d$trial_block <- x$Block
## source codes C, O, P, PAS; readme names CR, PAS, PDW, FOW without a key
d$cov_scale <- x$Scale
d$cov_order <- x$Order
finish(d, "wierzchon_2014_faces")

## ---- Lebreton et al. (2018), Science Advances -----------------------------
## two-Gabor contrast comparison under monetary incentives; 4 experiments,
## incentive codes differ by experiment so the item carries the experiment.
## Subjects 21XX and 22XX are the same people (Expt 2, two incentive schemes).
x <- rd("Lebreton_2018")
x$Subj_idx <- ifelse(x$Subj_idx %/% 100 == 22, x$Subj_idx - 100, x$Subj_idx)
ex <- c("10" = "e1", "21" = "e2conf", "22" = "e2perf", "30" = "e3", "40" = "e4")
ok <- c(`1` = "G1E", `2` = "N", `3` = "L1E")
inc <- list(e1 = ok, e2conf = ok, e2perf = ok,
            e3 = c(`1` = "G1E", `2` = "G10c", `3` = "L1E", `4` = "L10c"),
            e4 = c(`1` = "G2E", `2` = "G1E", `3` = "G10c", `4` = "L2E", `5` = "L1E", `6` = "L10c"))
raw_id <- rd("Lebreton_2018")$Subj_idx
e <- ex[as.character(raw_id %/% 100)]
il <- mapply(function(a, b) inc[[a]][as.character(b)], e, x$incentive)
d <- data.frame(id = x$Subj_idx,
                item = paste0(e, "_", il, "_", ifelse(x$Stimulus == 1, "left", "right")),
                resp = x$accuracy, rt = num(x$RT_dec) / 1000,
                trial_confidence = num(x$Confidence), trial_response = x$Response,
                trial_contrast_left = x$stim1, trial_contrast_right = x$stim2,
                trial_block = x$block, trial_in_block = x$trial_in_block,
                trial_feedback_performance = x$feeback_performance,
                trial_feedback_lottery = x$feedback_lottery)
d$cov_experiment <- sub("e2.*", "e2", e)
d$trial_number <- trialno(d$id)
finish(d, "lebreton_2018_gabor")

## ---- Massoni & Roux (2017), J Math Psych ----------------------------------
## dot-number discrimination; Difficulty = exposure (1 850, 2 700, 3 550 ms).
## Study 1 had trial feedback, Study 2 none (not randomised: separate samples).
x <- rd("Massoni_2017")
d <- std2afc(x, c("1" = "s1", "2" = "s2"), level = "Difficulty", levprefix = "d")
d$cov_study <- x$Study
d$cov_feedback <- x$Feedback
finish(d, "massoni_2017_dots")

## ---- Zheng, Xue, Shekhar & Rahnev (2023) ----------------------------------
## dot discrimination in a 15x15 grid. Condition 0 = confidence reported;
## 1/2 = expectation cue before/after stimulus; 3/4 = reward cue before/after.
## Cue_value 1 = neutral, 3 = 3:1; Cued_side 0 left, 1 right. RTs in ms.
x <- rd("Zheng_2023")
cond <- c("conf", "expect_pre", "expect_post", "reward_pre", "reward_post")[x$Condition + 1]
cue <- ifelse(x$Cue_value == -10, "", ifelse(x$Cue_value == 1, "_neutral",
              paste0("_cue", c(`0` = "left", `1` = "right")[as.character(x$Cued_side)])))
d <- data.frame(id = x$Subj_idx,
                item = paste0(cond, cue, "_", c("left", "right")[x$Stimulus + 1]),
                resp = x$Accuracy, rt = num(x$RT_dec) / 1000,
                trial_confidence = ifelse(x$Confidence == -1, NA, x$Confidence),
                trial_rt_conf = ifelse(x$RT_conf == -1, NA, x$RT_conf / 1000),
                trial_response = x$Response,
                cov_sex = ifelse(x$sex == "NR", NA, x$sex))
d$trial_number <- trialno(d$id)
finish(d, "zheng_2023_dots")

## ---- Xiang, Graeber, Enke & Gershman (2021), AP&P -------------------------
## numerosity ESTIMATION: 15-65 dots, typed estimate; duration 100 or 2000 ms.
## resp = the estimate (continuous). Missing = no answer in 10 s. One negative
## estimate (a typing error) is dropped.
x <- rd("Xiang_2021")
r <- num(x$Response); r[!is.na(r) & r < 0] <- NA
d <- data.frame(id = x$Subj_idx,
                item = paste0("n", x$Stimulus, "_", x$Duration, "ms"),
                resp = r, rt = num(x$RT_dec),
                trial_confidence = num(x$Confidence), trial_rt_conf = num(x$RT_conf),
                trial_block = x$Block, trial_block_mean = x$AveStim,
                itemcov_level = x$Stimulus)
d$trial_number <- trialno(d$id)
finish(d, "xiang_2021_numerosity")
