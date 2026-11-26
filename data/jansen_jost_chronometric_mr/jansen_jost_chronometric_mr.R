## Three chronometric mental rotation datasets from Petra Jansen's and
## Leonardo Jost's group (Regensburg). Mental rotation and psychophysics
## collections (irw#3686 follow-up; vignette idea datapages/irw#460).
## Each trial shows figures rotated by a recorded angle; the participant judges
## same vs mirrored (or which of two matches). Every table keeps rt and the
## angle, so response time can be modelled against rotation angle.
##
## 1. bauer_2021_mr_pupil
##    Bauer, R., Jost, L., & Jansen, P. (2021). The effect of mindfulness and
##    stereotype threat in mental rotation: a pupillometry study. Journal of
##    Cognitive Psychology, 33, 861-876. doi:10.1080/20445911.2021.1967366
##    Data: Zenodo 4081753 (dataset.csv), CC BY 4.0. 107 adults, 3D cube
##    figures (10 models), same/mirror, pre and post a mindfulness or control
##    induction crossed with stereotype threat (2 x 2 between).
##    item = model x angle x same/mirror (e.g. m01_d090_mirror; 100 cells,
##    several repeated within a session); wave 1 = pre, 2 = post;
##    cov_mindfulness, cov_stereotype_threat (the two manipulations),
##    cov_tms (Toronto Mindfulness Scale score). The source's `sex` is coded
##    1/2 without labels and is left out; pupil and fixation columns are left
##    out.
##
## 2. ebert_2024_animal_mr
##    Ebert, W. M., Jost, L., & Jansen, P. (2024). Gender stereotypes in
##    preschoolers' mental rotation. Frontiers in Psychology, 15, 1284314.
##    doi:10.3389/fpsyg.2024.1284314
##    Data: Zenodo 14275869 (MR_anonymous.csv, readme.rtf), CC BY 4.0. 98
##    children aged 4-6, animal figures (12), angles 0/90/180/270,
##    same/mirror; each cell once.
##    item = animal x angle x same/mirror (e.g. a07_d180_same; 96 items);
##    cluster_id = kindergarten (random number in the source);
##    cov_female, cov_age_months, cov_iat_d (gender-stereotype IAT D score),
##    cov_stereotype_q (explicit stereotype questionnaire), cov_ses.
##    trial_number = row order within child in the source file (no order
##    column is given); trial_outlier_code = source `outlier` (0 none, 1 RT
##    outlier, 2 mirrored item, 3/4 undocumented).
##
## 3. jost_2023_mr_visualization
##    Jost, L., & Siebertz, M. (2023). InternalExternalVisualizationOfRotation
##    [data and code]. github.com/LeonardoJost/InternalExternalVisualizationOfRotation
##    (dataset/datasetOS.csv), GPL-3.0. 150 adults, 3D cube figures (12
##    models), two figures per trial, the participant chooses which one is the
##    rotated (not mirrored) version; three within-person conditions (mental,
##    visual, visualStop).
##    item = model x signed rotation (source originalDegrees, 45-315; e.g.
##    m12_d135; 84 cells, repeated); trial_condition, trial_correct_side
##    (left/right), trial_number (order by block and stimulus start time).
##    No participant covariates are in the file; eye-gaze and pupil columns
##    are left out.
##
## In all three: resp = 1 if correct; rt in seconds (source ms);
## trial_rt_outlier = the depositors' RT-outlier flag (rows are kept);
## itemcov_angle = rotation angle in degrees (as recorded), itemcov_mirror =
## 1 for mirrored figures where the design has same/mirror trials.
## Ids are remapped to integers.
##
## Usage: Rscript jansen_jost_chronometric_mr.R <dir with pupil.csv sellstem.csv ie.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw_dir <- if (length(args) >= 1) args[1] else "raw"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

finish <- function(d, table) {
  front <- c("id", "item", "resp", "wave", "rt", "cluster_id")
  cols <- c(intersect(front, names(d)),
            sort(grep("^trial_", names(d), value = TRUE)),
            sort(grep("^cov_", names(d), value = TRUE)),
            sort(grep("^itemcov_", names(d), value = TRUE)))
  ord <- if ("wave" %in% names(d)) order(d$id, d$wave, d$trial_number) else order(d$id, d$trial_number)
  d <- d[ord, cols]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-28s rows=%6d ids=%4d items=%3d accuracy=%.3f\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
  print(round(tapply(d$rt[d$resp == 1], d$itemcov_angle[d$resp == 1], median), 3))
}

## 1. pupillometry
p <- read.csv2(file.path(raw_dir, "pupil.csv"), dec = ".", stringsAsFactors = FALSE)
stopifnot(length(unique(p$ID)) == 107, all(p$type %in% c("hit", "incorrect")),
          all(p$prepost %in% c("pre", "post")))
ids <- sort(unique(p$ID))
d <- data.frame(
  id = match(p$ID, ids),
  item = sprintf("m%02d_d%03d_%s", as.integer(sub("modell", "", p$model)), p$deg,
                 ifelse(p$orig, "same", "mirror")),
  resp = as.integer(p$type == "hit"),
  wave = ifelse(p$prepost == "pre", 1L, 2L),
  rt = p$reactionTime / 1000,
  trial_number = as.integer(sub("Trial", "", p$Trial)),
  trial_rt_outlier = as.integer(p$outlier),
  cov_mindfulness = as.integer(p$mf),
  cov_stereotype_threat = as.integer(p$st),
  cov_tms = as.numeric(p$tmsScore),
  itemcov_angle = as.numeric(p$deg),
  itemcov_mirror = as.integer(!p$orig))
stopifnot(!any(duplicated(d[, c("id", "wave", "trial_number")])))
finish(d, "bauer_2021_mr_pupil")

## 2. SellSTEM preschoolers
e <- read.csv(file.path(raw_dir, "sellstem.csv"), stringsAsFactors = FALSE)
stopifnot(length(unique(e$ano_id)) == 98, all(e$orientation %in% 1:2),
          all(e$correct %in% 0:1), all(e$gender %in% c("0.5", "-0.5")))
ids <- sort(unique(e$ano_id))
d <- data.frame(
  id = match(e$ano_id, ids),
  item = sprintf("a%02d_d%03d_%s", e$stimulus, e$angle, ifelse(e$orientation == 1, "same", "mirror")),
  resp = as.integer(e$correct),
  rt = e$rt / 1000,
  cluster_id = as.integer(e$institution),
  trial_number = ave(seq_len(nrow(e)), e$ano_id, FUN = seq_along),
  trial_outlier_code = as.integer(e$outlier),
  trial_rt_outlier = as.integer(e$outlier == 1),
  cov_age_months = as.integer(e$age),
  cov_female = as.integer(e$gender == "-0.5"),
  cov_iat_d = round(as.numeric(e$D_IAT), 4),
  cov_ses = as.numeric(e$SES),
  cov_stereotype_q = round(as.numeric(e$Q_score), 4),
  itemcov_angle = as.numeric(e$angle),
  itemcov_mirror = as.integer(e$orientation == 2))
stopifnot(!any(duplicated(d[, c("id", "item")])))
finish(d, "ebert_2024_animal_mr")

## 3. internal/external visualization
i <- read.csv2(file.path(raw_dir, "ie.csv"), dec = ".", stringsAsFactors = FALSE)
stopifnot(length(unique(i$ID)) == 150, all(i$correct %in% 0:1),
          all((i$orientation == i$orientationLeftBase) == (i$correctSide == "left")))
i <- i[order(i$ID, i$startTimeOfBlock, i$startTimeOfStimulus), ]
ids <- unique(i$ID); ids <- ids[order(as.integer(sub("id", "", ids)))]
d <- data.frame(
  id = match(i$ID, ids),
  item = sprintf("m%02d_d%03d", as.integer(sub("m", "", i$modelNumber)), i$originalDegrees),
  resp = as.integer(i$correct),
  rt = i$reactionTime / 1000,
  trial_condition = i$block,
  trial_correct_side = i$correctSide,
  trial_number = ave(seq_len(nrow(i)), i$ID, FUN = seq_along),
  trial_rt_outlier = as.integer(i$outlier),
  itemcov_angle = as.numeric(i$deg),
  itemcov_signed_angle = as.numeric(i$originalDegrees))
finish(d, "jost_2023_mr_visualization")
