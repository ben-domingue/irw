## Ebert, W. M., Jost, L., Jansen, P., & Stevanovski, B. (2024/2025). Visual
## working memory as the substrate for mental rotation: A replication.
## Psychonomic Bulletin & Review, 32, 1204-1216. doi:10.3758/s13423-024-02602-4
## Data: OSF https://osf.io/7x4rd, Data/DataMR.csv. Licence: CC BY 4.0
## (granted by Miro Ebert by email 2026-11-25 and set on the OSF project the
## same day; copy in irw/licenseinfo/emails/).
## Mental rotation and psychophysics collections.
##
## Task: chronometric letter rotation (10 letters, normal or mirrored; the
## file does not record which), judged alone (block "MR") or while holding a
## visual working-memory load (block "Dual"); two experiments with object
## (OWM) or spatial (SWM) working-memory tasks, between people. 213 adults.
##
## The depositors scaled rotation as (degrees - 72) / 72 (WMMR_preparation.R),
## so -1/0/1 are 0/72/144 degrees; restored here as itemcov_angle. They also
## removed mental rotation trials with RT below 100 ms or above 3,000 ms
## before publishing the file, so those trials are absent.
##
## Layout:
##   item = letter x angle, e.g. G_d072 (30 items, repeated)
##   resp = MR_correct; rt in seconds (source ms)
##   trial_condition = "MR" (rotation alone) or "Dual" (with WM load);
##   trial_wm_correct = the concurrent WM response in Dual trials;
##   trial_number = row order within person (the file's order)
##   cov_female (Weiblich/Maennlich; blank = NA), cov_age,
##   cov_wm_task = OWM (object) or SWM (spatial) experiment
##   itemcov_angle
## The depositors' random ids ("id149") are remapped to integers.
##
## Usage: Rscript ebert_2024_letter_mr.R <DataMR.csv> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
raw <- if (length(args) >= 1) args[1] else "DataMR.csv"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- read.csv2(raw, dec = ".", stringsAsFactors = FALSE)
stopifnot(all(x$rotation %in% c(-1, 0, 1)), all(x$MR_correct %in% 0:1),
          all(x$block %in% c("MR", "Dual")), length(unique(x$id)) == 213)
x$angle <- 72 * x$rotation + 72
ids <- unique(x$id); ids <- ids[order(as.integer(sub("id", "", ids)))]
d <- data.frame(
  id = match(x$id, ids),
  item = sprintf("%s_d%03d", x$stimulus, x$angle),
  resp = as.integer(x$MR_correct),
  rt = as.numeric(x$rt) / 1000,
  trial_condition = x$block,
  trial_number = ave(seq_len(nrow(x)), x$id, FUN = seq_along),
  trial_wm_correct = ifelse(x$block == "Dual", as.integer(x$WM_correct), NA),
  cov_age = suppressWarnings(as.integer(x$age)),
  cov_female = ifelse(x$gender == "Weiblich", 1L, ifelse(x$gender %in% c("Männlich", "Maennlich"), 0L, NA)),
  cov_wm_task = x$experiment,
  itemcov_angle = x$angle,
  stringsAsFactors = FALSE)
d <- d[order(d$id, d$trial_number), ]
table <- "ebert_2024_letter_mr"
write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
cat(sprintf("%s rows=%d ids=%d items=%d accuracy=%.3f female=%d male=%d\n", table, nrow(d),
            length(unique(d$id)), length(unique(d$item)), mean(d$resp),
            sum(d$cov_female[!duplicated(d$id)] == 1, na.rm = TRUE), sum(d$cov_female[!duplicated(d$id)] == 0, na.rm = TRUE)))
ok <- d$resp == 1
print(round(tapply(d$rt[ok], list(d$itemcov_angle[ok], d$trial_condition[ok]), median), 3))
