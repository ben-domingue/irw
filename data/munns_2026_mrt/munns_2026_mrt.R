## Munns, M. E., & Hegarty, M. (2026). Measurement of spatial ability:
## Reevaluating and revising measures of mental rotation. Intelligence, 117,
## 102040. doi:10.1016/j.intell.2026.102040
## Data: OSF https://osf.io/uec93 ("Mental Rotation Tests IRT"), one zip per
## study. Licence: CC BY 4.0 (granted by Mitch Munns by email 2026-11-25 and
## set on the OSF project the same day; copy in irw/licenseinfo/emails/).
## Mental rotation collection.
##
## Four online tests (Pavlovia + Qualtrics, 2023), each from the authors'
## cleaned analysis file, i.e. after their attention-check exclusions:
##   munns_2026_flags        Flags_Clean_Sp23.csv      21 items
##   munns_2026_vk_mrt       VK_clean_F23.csv          20 items (Vandenberg & Kuse MRT)
##   munns_2026_psvtr        PSVT_clean_S23.csv        30 items (PSVT:R)
##   munns_2026_mrt_battery  MRT_battery_clean.csv     36 items (hybrid: 10 F, 10 V, 16 P)
##
## Layout (one row per person x item):
##   resp = the authors' score_<item>. Flags items show six figures each and
##     are scored -6..6 (the authors' graded model uses this score; their 2PL
##     uses score == 6). V&K and PSVT:R items are 0/1.
##   resp_raw = the selected options (the authors' answers_<item> list, ";"-joined)
##   rt = rt_<item>, seconds
##   cov_age; cov_gender = the Qualtrics code 1-4 (value labels are not in
##     the deposit; the authors compare codes 1 and 2)
##   battery only: itemcov_source_test (flags/vk_mrt/psvtr) and, for P items,
##     itemcov_psvtr_item = the original PSVT:R item number, from the
##     authors' note in PSVT_analysis.R (battery P8..P16 = 12,13,14,-,18,21,
##     24,26,28; battery P11 has no mapping and the authors drop it).
##     F items keep their original numbers; V items are numbered V1..V10 in
##     the battery file.
## Prolific ids are remapped to integers, separately per table. Free-text
## demographics, other demographics without value labels, and the battery's
## 15-word vocabulary block are not included.
##
## Usage: Rscript munns_2026_mrt.R <dir with the four unzipped study folders> <out_dir>

args <- commandArgs(trailingOnly = TRUE)
src <- if (length(args) >= 1) args[1] else "."
out_dir <- if (length(args) >= 2) args[2] else "out"
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

files <- c(
  munns_2026_flags = "study_1_flags/flags_analysis_script/Flags_Clean_Sp23.csv",
  munns_2026_vk_mrt = "study_2_vk_mrt/VK_analysis_script/VK_clean_F23.csv",
  munns_2026_psvtr = "study_3_PSVT/PSVT_clean_S23.csv",
  munns_2026_mrt_battery = "study_4_hybrid_test/MRT_battery_clean.csv")
n_items <- c(munns_2026_flags = 21, munns_2026_vk_mrt = 20, munns_2026_psvtr = 30,
             munns_2026_mrt_battery = 36)

clean_answers <- function(a) gsub('[]["[:space:]]', "", gsub(",", ";", a))
item_order <- function(it) it[order(substr(it, 1, 1) != "F", substr(it, 1, 1) != "V",
                                    as.integer(substring(it, 2)))]
psvtr_map <- c(P1 = 1, P2 = 2, P3 = 3, P4 = 4, P5 = 5, P6 = 6, P7 = 7, P8 = 12, P9 = 13,
               P10 = 14, P11 = NA, P12 = 18, P13 = 21, P14 = 24, P15 = 26, P16 = 28)

for (table in names(files)) {
  x <- read.csv(file.path(src, files[[table]]), stringsAsFactors = FALSE, check.names = FALSE)
  stopifnot(!anyDuplicated(x$id))
  items <- item_order(sub("^score_", "", grep("^score_", names(x), value = TRUE)))
  stopifnot(length(items) == n_items[[table]])
  ids <- sort(unique(x$id))
  d <- do.call(rbind, lapply(items, function(it) data.frame(
    id = match(x$id, ids),
    item = it,
    resp = as.integer(x[[paste0("score_", it)]]),
    resp_raw = clean_answers(x[[paste0("answers_", it)]]),
    rt = as.numeric(x[[paste0("rt_", it)]]),
    cov_age = as.integer(x$age),
    cov_gender = suppressWarnings(as.integer(x$gender)),
    stringsAsFactors = FALSE)))
  if (table == "munns_2026_mrt_battery") {
    d$itemcov_source_test <- c(F = "flags", V = "vk_mrt", P = "psvtr")[substr(d$item, 1, 1)]
    d$itemcov_psvtr_item <- ifelse(substr(d$item, 1, 1) == "P", psvtr_map[d$item], NA)
  }
  d <- d[order(d$id, match(d$item, items)), ]
  write.csv(d, file.path(out_dir, paste0(table, ".csv")), row.names = FALSE, na = "")
  cat(sprintf("%s rows=%d ids=%d items=%d resp_na=%d resp_range=%s..%s median_rt=%.1f\n",
              table, nrow(d), length(ids), length(items), sum(is.na(d$resp)),
              min(d$resp, na.rm = TRUE), max(d$resp, na.rm = TRUE), median(d$rt, na.rm = TRUE)))
}
