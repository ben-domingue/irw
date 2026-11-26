## Confidence Database (Rahnev et al., 2020, Nature Human Behaviour,
## doi:10.1038/s41562-019-0813-1). OSF: https://osf.io/s46pr  Licence: CC0 1.0.
## Second tranche for the psychophysics collection (irw#3686): perception
## datasets with 50-99 subjects, under the floor of 50 people Ben set for
## psychophysics on 2026-11-23. The >= 100 tranche is confidence_db_perception.R,
## whose conventions this script follows (item = stimulus class x level, resp =
## accuracy, confidence and its RT in trial_ columns, itemcov_level = level).
##
## Left out of this tranche:
##   Hainguerlot_2018, Hainguerlot_unpub -- level fixed per person after
##     calibration and not recorded, so 2 items (stimulus class) only.
##   Haddara_2022_Expt2 -- one task, two classes, 7 days: 2 items.
##   Faivre_2018_JN -- pools three experiments whose `Ease` is in different
##     units, with no column saying which experiment a row is from.
##
## Usage: Rscript confidence_db_perception_n50.R <raw_dir> <out_dir>

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


## ---- Bocheva & Rahnev (2025), PsyArXiv, Expt 2 ----------------------------
## Gabor orientation (1 left, 2 right tilt); contrast 1 low, 2 high; the cued
## response hand varies by trial.
x <- rd("Bocheva_unpub_Expt2")
d <- std2afc(x, c("1" = "left", "2" = "right"),
             extra = paste0(sub(" hand", "hand", x$Condition), "_",
                            c("lowcon", "highcon")[x$Contrast]))
finish(d, "bocheva_2025_gabor")

## ---- Desender, Boldt & Yeung (2018), Psych Science, Expt 2 ----------------
## average colour of eight elements: red vs blue. Practice rows (Training = 1)
## and 189 rows with no stimulus (mean = 0) are dropped. Stimulus 0/1 is kept
## as s0/s1. Level = distance of the mean from 0.5 (0.00-0.03) x element
## variance (sd 0.0333 low, 0.1 high). trial_condition: 0 forced to respond,
## 1 chose to respond, 3 chose to see the stimulus again (free choice).
## One RT covers decision and confidence. Confidence is stored 0-50 (distance
## from "guess"; the readme describes the same scale as 50-100).
x <- rd("Desender_2018_Exp2")
x <- x[x$Training == 0 & x$sd > 0, ]
x$Accuracy <- as.integer(x$Stimulus == x$Response)
x$dist <- round(abs(x$mean - 0.5), 2)
d <- std2afc(x, c("0" = "s0", "1" = "s1"), level = "dist", levprefix = "d",
             extra = ifelse(x$sd < 0.05, "lowvar", "highvar"),
             rt = "RT_decConf", rtconf = NULL)
d$trial_condition <- x$Condition
d$trial_mean <- x$mean
finish(d, "desender_2018_colour")

## ---- Desender, Vermeylen & Verguts (2022), Nat Commun, Expt 2B ------------
## dot-number discrimination online; Difficulty = dot difference (staircase).
x <- rd("Desender_2022_Exp2B")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
d <- std2afc(x, c("0" = "s0", "1" = "s1"), level = "Difficulty", levprefix = "dd")
finish(d, "desender_2022_dots_e2b")

## ---- Konishi et al. (2019), PsyArXiv --------------------------------------
## RDK dual task: motion direction (up 1 / down -1) and colour majority
## (red 1 / blue -1), single- or dual-task blocks, three experiments. A dual
## trial gives two decisions, so two rows sharing a trial_number. Coherence
## and colour difficulty are staircased and continuous: trial_stim_level.
x <- rd("Konishi_2019")
ex <- c("long/staircase" = "longstair", "short/staircase" = "shortstair",
        "short/staircase 2" = "shortstair2", "short/constant" = "shortconst")[x$exp]
mk <- function(tk, lab) {
  S <- x[[paste0("Stimulus_", tk)]]; ok <- !is.na(x[[paste0("Accuracy_", tk)]])
  data.frame(id = x$Subj_idx, item = paste0(ex, "_", x$condition, "_", lab, "_",
                                            ifelse(S == 1, c(Motion = "up", Color = "red")[tk],
                                                   c(Motion = "down", Color = "blue")[tk])),
             resp = x[[paste0("Accuracy_", tk)]], rt = num(x[[paste0("RT_dec_", tk)]]),
             trial_confidence = num(x[[paste0("Confidence_", tk)]]),
             trial_response = x[[paste0("Response_", tk)]],
             trial_stim_level = num(x[[ifelse(tk == "Motion", "Coherence_Motion", "Difficulty_Color")]]),
             trial_number = x$Trial_Number)[ok, ]
}
d <- rbind(mk("Motion", "motion"), mk("Color", "colour"))
finish(d, "konishi_2019_dualtask")

## ---- Massoni (unpublished; collected 2018) --------------------------------
## dot-number discrimination; Difficulty 1 = twice, 2 = half the staircased
## dot difference. Study 1 no feedback (subjects 1-23), Study 2 feedback.
x <- rd("Massoni_unpub")
d <- std2afc(x, c("1" = "s1", "2" = "s2"), level = "Difficulty", levprefix = "d")
d$cov_study <- x$Study
d$cov_feedback <- x$Feedback
finish(d, "massoni_2018_dots")

## ---- Matthews et al. (2018), PsyArXiv -------------------------------------
## dual-task detection: peripheral Gabor present/absent (1) and central target
## letter T present/absent (2); attention full (single task) or diverted (dual);
## expectation = cued probability of the peripheral target. Decision and
## confidence (1-4) given together. Training blocks dropped. cov_group:
## control, functional or organic movement disorder (20 each).
x <- rd("Matthews_unpub")
x <- x[x$Training == 0, ]
att <- ifelse(x$Condition_Attention == "full_attention", "full", "diverted")
ex <- ifelse(is.na(x$Condition_Expectations), "", paste0("_p", x$Condition_Expectations))
mk <- function(k, lab) {
  S <- x[[paste0("Stimulus_", k)]]; A <- x[[paste0("Accuracy_", k)]]; ok <- !is.na(A) & !is.na(S)
  data.frame(id = x$Subj_idx,
             item = paste0(lab, "_", att, if (k == "1") ex else "", "_", ifelse(S == 1, "present", "absent")),
             resp = A, rt = if (k == "1") num(x$RT_decConf_1) else NA_real_,
             trial_confidence = num(x[[paste0("Confidence_", k)]]),
             trial_response = x[[paste0("Response_", ifelse(k == "1", "0", "2"))]],
             trial_stim_level = if (k == "1") x$Contrast_1 else x$SOA_2,
             cov_group = x$Group)[ok, ]
}
d <- rbind(mk("1", "periph"), mk("2", "central"))
d$trial_number <- ave(seq_len(nrow(d)), d$id, FUN = seq_along)
finish(d, "matthews_2018_dualtask")

## ---- Rouault, Dayan & Fleming (2019), Nat Commun --------------------------
## dot-number discrimination, DotDiff 24 (hard) or 60 (easy). Each trial gave
## either feedback or a confidence rating (50-100%): trial_feedback = 1 marks
## the feedback trials, whose confidence is missing. RT_conf is in ms.
x <- rd("Rouault_2019")
d <- std2afc(x, c("0" = "s0", "1" = "s1"), level = "DotDiff", levprefix = "dd")
d$trial_rt_conf <- num(x$RT_conf) / 1000
d$trial_feedback <- as.integer(is.na(x$Confidence))
finish(d, "rouault_2019_dots")

## ---- Sadeghi et al. (2017), Sci Rep ---------------------------------------
## two-interval odd-Gabor contrast detection, staircased contrast difference.
## cov_group: methadone-maintenance patients vs controls (all male).
x <- rd("Sadeghi_2017_perception")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
d <- std2afc(x, c("1" = "first", "2" = "second"), level = "contrast_difference", levprefix = "c")
d$cov_group <- x$group
finish(d, "sadeghi_2017_contrast")

## ---- Siedlecka, Koculak & Paulewicz (2021), PB&R --------------------------
## go/no-go dot comparison: press the space bar only when the designated side
## has more dots (designated side = Condition, 1 left / 2 right, by block).
## resp = accuracy, so a correct withhold counts as correct; trial_response =
## pressed (1) or withheld (0). Difficulty 1 = 55:45, 2 = 52:48, 3 = 51:49.
## Missing confidence = the person reported an error instead of rating.
x <- rd("Siedlecka_2021")
d <- std2afc(x, c("1" = "moreleft", "2" = "moreright"), level = "Difficulty", levprefix = "d",
             extra = ifelse(x$Condition == 1, "goleft", "goright"))
d$trial_response <- as.integer(!is.na(x$Response))
d$trial_error_report <- as.integer(is.na(x$Confidence))
d$trial_number <- x$Trial + 1 + 390 * x$Block
d$cov_gender <- x$Gender
d$cov_age <- x$Age
finish(d, "siedlecka_2021_dots")

## ---- Wierzchon et al. (2019), Consc Cogn ----------------------------------
## masked Gabor orientation (45 deg left/right), duration 32/48/64/128 ms.
## Awareness rated 0-1 on one of three scales, between subjects (cov_scale:
## pas, cs = continuous, cpas = continuous with PAS labels).
x <- rd("Wierzchon_2019")
x$Accuracy <- as.integer(x$Stimulus == x$Response)
d <- std2afc(x, c("1" = "s1", "2" = "s2"), level = "Difficulty", levprefix = "ms")
d$cov_scale <- x$Condition
finish(d, "wierzchon_2019_gabor")
