## Wong, M. S., & Wong, T. T.-Y. (2025). Supporting data for "The Roles of
## Spatial Ability and Visuospatial Working Memory Capacity on Cognitive
## Mapping Performance" [Data set]. The University of Hong Kong (Figshare).
## doi:10.25442/hku.29633990.v1. Licence: CC BY-NC 4.0 (Figshare record).
## File: ThesisDataset_SpatialAbility_VSWM_CogMapping_202507.sav, with
## README.txt (variable list). 201 adults in Hong Kong.
##
## One table per instrument (item-level columns in the deposit):
##   wong_2025_mental_rotation     MR1-MR10, mental rotation test; item
##                                 scores -4..3 as scored by the depositors
##                                 (they sum to the deposit's MR total; the
##                                 penalty scoring is not documented, so the
##                                 values are kept as given)
##   wong_2025_embedded_figures    EF1-EF14, item scores -3..4, as above
##   wong_2025_spatial_scaling     SS1-SS24, 0/1
##   wong_2025_perspective_taking  SPT1-SPT18, 0/1
##   wong_2025_vswm                VSWM1-VSWM14, visuospatial working memory, 0/1
##   wong_2025_vwm                 VWM1-VWM14, verbal working memory, 0/1
##   wong_2025_raven12             Raven1-Raven12, Raven short form, 0/1
##   wong_2025_sbsod               SOD1-SOD15, Santa Barbara Sense of
##                                 Direction, 1-7 as recorded (negatively
##                                 worded items not reversed)
## Covariates (all tables): cov_age, cov_male (deposit gender: 0 = female,
## 1 = male), cov_education (1-7), cov_language (1 English, 2 Cantonese and
## traditional Chinese, 3 Mandarin and simplified Chinese), cov_order
## (0 = paper tasks first, 1 = laptop first).
## Left out: totals, standardised and winsorised scores, interaction terms,
## and the navigation outcomes (route repetition, landmark placement,
## wayfinding), which are composite scores rather than item responses.
## ID is remapped to integers.
##
## Usage: Rscript wong_2025_spatial.R <ThesisDataset_...sav> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
sav <- if (length(args) >= 1) args[1] else "ThesisDataset_SpatialAbility_VSWM_CogMapping_202507.sav"
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

x <- haven::zap_labels(haven::read_sav(sav))
stopifnot(nrow(x) == 201, !any(duplicated(x$ID)))
ids <- sort(unique(x$ID))

blocks <- list(
  wong_2025_mental_rotation = "MR", wong_2025_embedded_figures = "EF",
  wong_2025_spatial_scaling = "SS", wong_2025_perspective_taking = "SPT",
  wong_2025_vswm = "VSWM", wong_2025_vwm = "VWM",
  wong_2025_raven12 = "Raven", wong_2025_sbsod = "SOD")
n_items <- c(MR = 10, EF = 14, SS = 24, SPT = 18, VSWM = 14, VWM = 14, Raven = 12, SOD = 15)

for (table in names(blocks)) {
  p <- blocks[[table]]
  cols <- paste0(p, seq_len(n_items[[p]]))
  stopifnot(all(cols %in% names(x)))
  if (p %in% c("MR", "SPT")) stopifnot(all(rowSums(x[, cols]) == x[[p]]))
  rows <- lapply(cols, function(cc) data.frame(
    id = match(x$ID, ids), item = cc, resp = as.numeric(x[[cc]]),
    cov_age = as.integer(x$age), cov_education = as.integer(x$education),
    cov_language = as.integer(x$Language), cov_male = as.integer(x$gender),
    cov_order = as.integer(x$order)))
  d <- do.call(rbind, rows)
  d <- d[!is.na(d$resp), ]
  d <- d[order(d$id, match(d$item, cols)), ]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%-30s rows=%5d ids=%3d items=%2d resp %s\n", table, nrow(d),
              length(unique(d$id)), length(unique(d$item)),
              paste(range(d$resp), collapse = "..")))
}
