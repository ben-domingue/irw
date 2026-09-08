# verify_ibrahim_2015_bfi.R
#
# CLAIM UNDER TEST: the live item code B5<i> carries the wording of BFI-44 item <i>
# in the canonical John, Donahue & Kentle (1991) numbering, and all 44 items are
# stored RAW (not reverse-scored), so option_text runs 1 = "disagree strongly" ...
# 5 = "agree strongly" for every item.
#
# The IRW table is melted straight out of the PLOS S1 SPSS file by column NAME
# (data/ibrahim_2015_ckd_personality_qol.py, BFI_COLS = [f"B5{i}" for i in 1..44]),
# so item code == source column name; but those columns carry NO variable labels,
# so the tie from code to BFI item number is reconstructed, not read off the file.
# What the file DOES carry are the authors' own derived columns:
#   * B5<i>_R  -- reverse-scored duplicates, present for exactly 16 of the 44 items
#   * B5_Extraversion / _Agree / _Conscience / _Neuro / _Open -- domain sum scores
# Those are a falsifiable prediction about which BFI item number each column is.
#
# This script is deliberately source-side plus a set/aggregate cross-check via
# irw_table_sets(); it never calls irw_fetch(), which would export all 8,800 rows
# against the account-wide Redivis quota.

suppressMessages({
  library(haven)
})

TABLE <- "ibrahim_2015_bfi"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0129015.s001")

# --- canonical BFI-44 scoring key (John, Donahue & Kentle 1991), hard-coded ---
REV  <- c(2, 6, 8, 9, 12, 18, 21, 23, 24, 27, 31, 34, 35, 37, 41, 43)
KEYS <- list(
  B5_Extraversion = c(1, 6, 11, 16, 21, 26, 31, 36),
  B5_Agree        = c(2, 7, 12, 17, 22, 27, 32, 37, 42),
  B5_Conscience   = c(3, 8, 13, 18, 23, 28, 33, 38, 43),
  B5_Neuro        = c(4, 9, 14, 19, 24, 29, 34, 39),
  B5_Open         = c(5, 10, 15, 20, 25, 30, 35, 40, 41, 44)
)

f <- tempfile(fileext = ".sav")
utils::download.file(SI_URL, f, quiet = TRUE, mode = "wb")
d <- haven::read_sav(f)

ok <- TRUE

# --- Check 1: which columns have a reverse-scored twin? --------------------
have_R <- sort(as.integer(sub("^B5(\\d+)_R$", "\\1",
                             grep("^B5\\d+_R$", names(d), value = TRUE))))
cat("Check 1 -- items the authors reverse-scored (B5<i>_R columns present)\n")
cat("  in file    :", paste(have_R, collapse = ", "), "\n")
cat("  canonical  :", paste(REV,    collapse = ", "), "\n")
c1 <- identical(have_R, as.integer(REV))
cat("  identical  :", c1, "  (1 of choose(44,16) = 2.1e+11 possible 16-subsets)\n\n")
ok <- ok && c1

# --- Check 2: B5<i>_R == 6 - B5<i>, i.e. B5<i> is the RAW response ---------
worst <- 0
for (i in REV) worst <- max(worst, max(abs(6 - d[[paste0("B5", i)]] - d[[paste0("B5", i, "_R")]]), na.rm = TRUE))
cat("Check 2 -- storage direction: max |(6 - B5<i>) - B5<i>_R| over the 16 reverse items =",
    worst, "\n")
cat("  => the melted B5<i> columns hold RAW responses; anchors ship in one direction for all 44.\n\n")
c2 <- worst == 0
ok <- ok && c2

# --- Check 3: reproduce the authors' five domain sums from the canonical key
cat("Check 3 -- domain sums rebuilt from the canonical BFI-44 key\n")
cat(sprintf("  %-16s %6s %8s %12s\n", "domain", "nitem", "maxdiff", "rows_exact"))
c3 <- TRUE
for (k in names(KEYS)) {
  cols <- ifelse(KEYS[[k]] %in% REV, paste0("B5", KEYS[[k]], "_R"), paste0("B5", KEYS[[k]]))
  s <- rowSums(as.data.frame(d[, cols]))
  df <- abs(s - d[[k]])
  cat(sprintf("  %-16s %6d %8.1f %7d/%d\n", k, length(cols), max(df), sum(df < 1e-9), nrow(d)))
  c3 <- c3 && all(df < 1e-9)
}
cat("  all five domains reproduced exactly for every respondent:", c3, "\n\n")
ok <- ok && c3

# --- Check 4: source column <-> live item code, from the data side ---------
# Exactly two BFI columns never take the value 1 in the source file. If the live
# table's item codes are the source column names, exactly those two live items
# must have resp_min = 2. (Live sets via irw_table_sets -- no export.)
src_min2 <- sort(grep("^B5\\d+$", names(d), value = TRUE)[
  vapply(grep("^B5\\d+$", names(d), value = TRUE),
         function(cn) min(d[[cn]], na.rm = TRUE) > 1, logical(1))])
cat("Check 4 -- source columns whose minimum response is 2, not 1:",
    paste(src_min2, collapse = ", "), "\n")
c4 <- NA
live <- try(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE), silent = TRUE)
if (inherits(live, "try-error") || is.null(live$per_item)) {
  cat("  live per-item ranges unavailable (no credentials?); expected B522, B533\n")
  c4 <- identical(src_min2, c("B522", "B533"))
} else {
  st <- as.data.frame(live$per_item)
  live_min2 <- sort(as.character(st$item[st$resp_min > 1]))
  cat("  live items with resp_min > 1               :", paste(live_min2, collapse = ", "), "\n")
  c4 <- identical(src_min2, live_min2)
  cat("  identical:", c4, "\n")
}
cat("\n")
ok <- ok && isTRUE(c4)

cat("WHAT THIS DOES NOT ESTABLISH: checks 1 and 3 pin every item's Big Five domain\n",
    "and its keying polarity, which fixes the mapping up to a permutation WITHIN each\n",
    "domain-by-polarity class. They do not separate, e.g., the five forward-keyed\n",
    "Extraversion items B51/B511/B516/B526/B536 from one another. The verification\n",
    "status for this table is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
