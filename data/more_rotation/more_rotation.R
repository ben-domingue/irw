## Two chronometric mental rotation datasets for the mental rotation and
## psychophysics collections (irw#3686 follow-up; vignette datapages/irw#460).
##
## 1. ganis_kievit_2015_mr
##    Ganis, G., & Kievit, R. A. (2015). A new set of three-dimensional shapes
##    for investigating mental rotation processes: validation data and
##    stimulus set. Journal of Open Psychology Data, 3(1), e3.
##    doi:10.5334/jopd.ai. Data: Figshare doi:10.6084/m9.figshare.1045385
##    (Behavioural_data.zip, file 3702010; demographics.xlsx), CC BY 4.0.
##    54 adults, one workbook per person (sub<N>.xlsx). Trials are rows 5-100
##    (96 trials); rows 101-106 hold the depositors' per-angle summaries and
##    are not read. Each stimulus file is a 3D shape pair: a leading "R" marks
##    a mirror-image pair, the trailing number is the angular disparity
##    (0/50/100/150). Every participant sees all 96 stimuli once.
##    item = stimulus file name without extension (96 items);
##    resp = 1 if correct (column G); trials with no response within the time
##    limit (response "[N/A]", scored incorrect in the source) are dropped;
##    rt in seconds (source ms); trial_number = trial order (column A);
##    itemcov_angle, itemcov_mirror; cov_age, cov_female (demographics.xlsx).
##
## 2. liu_lourenco_2026_mr
##    Liu, Y., & Lourenco, S. F. (2026). Time pressure amplifies gender
##    differences in mental rotation through shifts in evidence accumulation
##    and response caution. OSF https://osf.io/zy6p3 (licence CC BY 4.0).
##    File: Data/"combined_trial_by_trial-old version.csv", which holds all
##    four angular differences (0/50/100/150); the cleaned_data_for_DDM.csv
##    file keeps only 0 and 100 for the paper's diffusion models. 164 adults,
##    up to 96 trials each, instructed for speed or for accuracy (between
##    people). The file does not identify the stimulus figure.
##    item = same/mirror x angular difference (8 items, repeated, e.g.
##    mirror_d100); resp = `response` (1 correct); rt in seconds as given;
##    trial_number = row order within person in the source file (no order
##    column is given); cov_female; cov_speed_condition (1 = speed
##    instructions, 0 = accuracy); itemcov_angle, itemcov_mirror.
##
## Ids are remapped to integers.
## Usage: Rscript more_rotation.R <ganis Behavioural_data dir> <liu old-version csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
gdir <- args[1]; lfile <- args[2]
out_dir <- if (length(args) >= 3) args[3] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

finish <- function(d, table) {
  cols <- c("id", "item", "resp", "rt", sort(grep("^trial_", names(d), value = TRUE)),
            sort(grep("^cov_", names(d), value = TRUE)), sort(grep("^itemcov_", names(d), value = TRUE)))
  d <- d[order(d$id, d$trial_number), cols]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-24s rows=%5d ids=%3d items=%2d accuracy=%.3f\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)), mean(d$resp)))
  ok <- d$resp == 1
  print(round(tapply(d$rt[ok], d$itemcov_angle[ok], median), 2))
}

## 1. Ganis & Kievit
fs <- list.files(gdir, pattern = "^sub[0-9]+\\.xlsx$", full.names = TRUE)
stopifnot(length(fs) == 54)
g <- do.call(rbind, lapply(fs, function(f) {
  hdr <- as.character(unlist(suppressMessages(readxl::read_excel(f, col_names = FALSE,
           .name_repair = "minimal", range = "A4:G4"))))
  stopifnot(identical(hdr, c("Trial", "Condition", "Time", "response", "correct", "angle", "correct/incorrect")))
  s <- as.data.frame(suppressMessages(readxl::read_excel(f, col_names = FALSE,
           .name_repair = "minimal", range = "A5:G100")))
  names(s) <- c("trial", "cond", "rt", "response", "desired", "angle", "acc")
  s$sub <- as.integer(gsub("\\D", "", basename(f)))
  s
}))
stopifnot(all(table(g$sub) == 96), length(unique(g$cond)) == 96,
          all(g$angle %in% c(0, 50, 100, 150)),
          all(as.numeric(sub(".*Y([0-9]+)\\.pct$", "\\1", g$cond)) == g$angle))
g <- g[g$response != "[N/A]", ]
stopifnot(all((g$response == g$desired) == (g$acc == 1)))
demo <- as.data.frame(readxl::read_excel(file.path(gdir, "demographics.xlsx")))
m <- match(g$sub, demo$Subject)
stopifnot(!any(is.na(m)))
subs <- sort(unique(g$sub))
finish(data.frame(
  id = match(g$sub, subs),
  item = sub("\\.pct$", "", g$cond),
  resp = as.integer(g$acc),
  rt = as.numeric(g$rt) / 1000,
  trial_number = as.integer(g$trial),
  cov_age = as.integer(demo$Age[m]),
  cov_female = c(F = 1L, M = 0L)[demo$Gender[m]],
  itemcov_angle = as.numeric(g$angle),
  itemcov_mirror = as.integer(grepl("^R", g$cond))), "ganis_kievit_2015_mr")

## 2. Liu & Lourenco
l <- read.csv(lfile, stringsAsFactors = FALSE)
stopifnot(all(l$type %in% c("same", "mirror")), all(l$response %in% 0:1),
          all(l$Angular_difference %in% c(0, 50, 100, 150)),
          all(tapply(l$condition, l$subj_idx, function(v) length(unique(v))) == 1))
subs <- sort(unique(l$subj_idx))
finish(data.frame(
  id = match(l$subj_idx, subs),
  item = sprintf("%s_d%03d", l$type, l$Angular_difference),
  resp = as.integer(l$response),
  rt = as.numeric(l$rt),
  trial_number = ave(seq_len(nrow(l)), l$subj_idx, FUN = seq_along),
  cov_female = as.integer(l$gender == "Female"),
  cov_speed_condition = as.integer(tolower(l$condition) == "speed"),
  itemcov_angle = as.numeric(l$Angular_difference),
  itemcov_mirror = as.integer(l$type == "mirror")), "liu_lourenco_2026_mr")
