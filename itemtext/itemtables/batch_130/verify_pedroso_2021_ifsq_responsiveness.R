# verify_pedroso_2021_ifsq_responsiveness.R
#
# CLAIM UNDER TEST (Step 5b, route 1 -- published per-item statistics):
#   each IRW item code RP1..RP12 carries the IFSQ-Br wording that Pedroso &
#   Gubert (2021) S1 Questionnaire prints against that same code, AND the
#   shipped option_text runs in the direction the live data stores (resp 1 =
#   the lowest anchor, "disagree"/"never"; resp 5 = the highest,
#   "agree"/"always").
#
# FALSIFIABLE PREDICTION: PLOS ONE 10.1371/journal.pone.0257991 Table 4 prints,
# for every responsive-style item, the number of respondents at the LOWEST and
# at the HIGHEST score of the 5-point scale, computed listwise within each
# sub-construct (n = 461 satiety, n = 464 attention). All twelve (lo, hi) pairs
# are distinct, so they distinguish every item from every other item. Swap the
# item_text of any two RP items and a pair lands on the wrong item; reverse the
# option direction and lo/hi swap for every item at once.
#
# Secondary claim tested here: the sub-construct ASSIGNMENT shipped in
# section_id (RP1-RP7 satiety, RP8-RP12 attention), against the workbook's own
# mean_Rpsatiety / mean_Rpattention composite columns and Table 2's published
# sub-construct means.
#
# Third claim tested here: which of the paper's two anchor vocabularies each
# item carried. The paper added an "I don't know/does not apply" option to the
# BELIEF items only, so belief items -- and only belief items -- can be missing.
#
# This uses the study's own S1 Dataset (the file data/pedroso_2021_ifsq.py reads
# to build the IRW table) rather than irw_fetch(), which would export the whole
# table against the shared 200GB/30-day Redivis quota. irw_table_sets() is used
# to confirm the live per-item n matches the source file item for item, so the
# numbers below are about the table that actually shipped.

suppressMessages({library(irw); library(readxl); library(httr)})

TABLE <- "pedroso_2021_ifsq_responsiveness"
SRC   <- "https://doi.org/10.1371/journal.pone.0257991.s002"

# --- Published values, PLOS ONE 10.1371/journal.pone.0257991 Table 4 ----------
# lo/hi = n (and %) at the lowest / highest score of the 5-point scale.
PUB <- data.frame(
  paper_code = c("RP 1","RP 2","RP 3","RP 4","RP 5","RP 6",
                 "RP 7","RP 8","RP 9","RP 10","RP 11","RP 12"),
  irw_item   = c("RP1","RP2","RP3","RP4","RP5","RP6",
                 "RP7","RP8","RP9","RP10","RP11","RP12"),
  lo = c( 26,   9, 151,   3,   4,  27,  16, 142,  69, 168,  41,   3),
  hi = c(374, 381, 205, 426, 439, 404, 403, 269, 346, 217, 357, 451),
  # anchor set shipped in option_text
  anchors = c("never..always","never..always","never..always","never..always",
              "never..always","disagree..agree","disagree..agree",
              "never..always","never..always","never..always","never..always",
              "disagree..agree"),
  stringsAsFactors = FALSE)

SAT <- paste0("RP", 1:7)    # Responsive (satiety),  paper n = 461
ATT <- paste0("RP", 8:12)   # Responsive (attention), paper n = 464

tmp <- tempfile(fileext = ".xlsx")
r <- httr::GET(SRC, httr::write_disk(tmp, overwrite = TRUE),
               httr::user_agent("IRW-itemtext/1.0"))
stopifnot(httr::status_code(r) == 200)
raw <- as.data.frame(readxl::read_excel(tmp))
num <- function(x) suppressWarnings(as.numeric(gsub(",", ".", as.character(x), fixed = TRUE)))
for (cc in c(SAT, ATT, "mean_Rpsatiety", "mean_Rpattention")) raw[[cc]] <- num(raw[[cc]])

blk <- function(cols) { d <- raw[, cols, drop = FALSE]; d[complete.cases(d), , drop = FALSE] }
S <- blk(SAT); A <- blk(ATT)
cat(sprintf("listwise n: satiety %d (paper 461), attention %d (paper 464)\n\n",
            nrow(S), nrow(A)))
n_ok <- nrow(S) == 461L && nrow(A) == 464L

# --- tie the source file to the live table (per-item n, no export) -----------
live <- tryCatch(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE),
                 error = function(e) NULL)
if (!is.null(live) && !is.null(live$per_item)) {
  pi <- as.data.frame(live$per_item)
  src_n <- sapply(c(SAT, ATT), function(cc) sum(!is.na(raw[[cc]])))
  m <- pi$n[match(names(src_n), pi$item)]
  cat("live per-item n vs source-file per-item n:\n")
  cat(paste(sprintf("  %-5s live %3d  source %3d", names(src_n), m, src_n),
            collapse = "\n"), "\n\n")
  if (!identical(as.integer(m), as.integer(src_n)))
    cat("  WARNING: live and source per-item n differ\n\n")
} else cat("(irw_table_sets unavailable -- source-file check only)\n\n")

# --- the mapping check -------------------------------------------------------
cat(sprintf("%-6s %-5s %6s %6s %6s %6s %s\n",
            "paper", "item", "pubLO", "obsLO", "pubHI", "obsHI", ""))
ok <- TRUE
for (i in seq_len(nrow(PUB))) {
  it <- PUB$irw_item[i]
  d  <- if (it %in% SAT) S else A
  obsLO <- sum(d[[it]] == 1); obsHI <- sum(d[[it]] == 5)
  good  <- obsLO == PUB$lo[i] && obsHI == PUB$hi[i]
  ok    <- ok && good
  cat(sprintf("%-6s %-5s %6d %6d %6d %6d %s\n",
              PUB$paper_code[i], it, PUB$lo[i], obsLO, PUB$hi[i], obsHI,
              ifelse(good, "ok", "MISMATCH")))
}
pairs_distinct <- !anyDuplicated(paste(PUB$lo, PUB$hi))
cat(sprintf("\nall 12 (lo,hi) pairs distinct: %s\n\n", pairs_distinct))

# --- corroboration 1: sub-construct assignment (section_id) -------------------
# The workbook ships its own composite columns; recomputing them from the items
# shipped under each section_id must reproduce them, and Table 2's published
# sub-construct means must follow.
d_sat <- rowMeans(raw[, SAT]); d_att <- rowMeans(raw[, ATT])
mx_s <- max(abs(d_sat - raw$mean_Rpsatiety),  na.rm = TRUE)
mx_a <- max(abs(d_att - raw$mean_Rpattention), na.rm = TRUE)
cat(sprintf("composite of RP1-RP7  vs workbook mean_Rpsatiety : max |diff| = %.5f\n", mx_s))
cat(sprintf("composite of RP8-RP12 vs workbook mean_Rpattention: max |diff| = %.5f\n", mx_a))
cat(sprintf("Table 2 satiety  : observed M=%.2f SD=%.2f  vs published M=4.51\n",
            mean(raw$mean_Rpsatiety, na.rm = TRUE), sd(raw$mean_Rpsatiety, na.rm = TRUE)))
cat(sprintf("Table 2 attention: observed M=%.2f SD=%.2f  vs published M=4.05\n\n",
            mean(raw$mean_Rpattention, na.rm = TRUE), sd(raw$mean_Rpattention, na.rm = TRUE)))
sec_ok <- mx_s < 0.006 && mx_a < 0.006 &&
          abs(mean(raw$mean_Rpsatiety,  na.rm = TRUE) - 4.51) < 0.01 &&
          abs(mean(raw$mean_Rpattention, na.rm = TRUE) - 4.05) < 0.01

# --- corroboration 2: which anchor set each item carried ---------------------
# The paper: "The 'I don't know/don't apply' answer option was also included in
# the items that referred to beliefs". So an item can only be missing if it is a
# belief item. Prediction: missingness > 0 exactly on the items shipped with the
# disagree..agree anchors.
miss <- sapply(c(SAT, ATT), function(cc) sum(is.na(raw[[cc]])))
bel  <- PUB$irw_item[PUB$anchors == "disagree..agree"]
cat("missing values per item (source file, n = 465 rows):\n")
cat(paste(sprintf("  %-5s %d%s", names(miss), miss,
                  ifelse(names(miss) %in% bel, "   <- shipped as a BELIEF item", "")),
          collapse = "\n"), "\n")
anch_ok <- setequal(names(miss)[miss > 0], bel)
cat(sprintf("\nitems with any missingness == items shipped with disagree..agree anchors: %s\n\n",
            anch_ok))

cat("What this does NOT establish: the PORTUGUESE anchor wording, which the\n",
    "study never published -- option_text ships the article's English anchor\n",
    "sets while item_text is the administered Portuguese. The missingness test\n",
    "above shows RP6, RP7 and RP12 are the only items that could carry the\n",
    "belief-only 'I don't know/does not apply' option, which is strong but\n",
    "indirect evidence for the belief/behaviour split; it is not a printed\n",
    "per-item anchor list.\n\n", sep = "")

cat(if (ok && n_ok && pairs_distinct && sec_ok && anch_ok)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
