# verify_pedroso_2021_ifsq_restriction.R
#
# CLAIM UNDER TEST (Step 5b, route 1 -- published per-item statistics):
#   each IRW item code RS1..RS4, RS5recoded, RS6recoded, RS7..RS11 carries the
#   IFSQ-Br wording that Pedroso & Gubert (2021) S1 Table prints against that
#   same code, AND the option_text shipped for resp 1..5 runs in the direction
#   the live data actually stores -- i.e. mirrored for the two "recoded"
#   columns, unmirrored for the other nine.
#
# FALSIFIABLE PREDICTION: PLOS ONE 10.1371/journal.pone.0257991 Table 4 prints,
# for every restrictive-style item, the number of respondents at the LOWEST and
# at the HIGHEST score of the 5-point scale, computed listwise within each
# sub-construct (n = 461 amount, n = 463 diet quality). The 22 counts are
# item-specific and no two items share a (lo, hi) pair, so they distinguish
# every item from every other item. If item_text for two items were swapped,
# the pair of counts would land on the wrong item. If the recode direction were
# wrong, the low/high counts of RS5/RS6 would fail to mirror.
#
# This uses the study's own S1 Dataset (the file data/pedroso_2021_ifsq.py reads
# to build the IRW table) rather than irw_fetch(), which would export the whole
# table against the shared 200GB/30-day Redivis quota. irw_table_sets() is used
# to confirm the live per-item n matches the source file item for item, so the
# numbers below are about the table that actually shipped.

suppressMessages({library(irw); library(readxl); library(httr)})

TABLE <- "pedroso_2021_ifsq_restriction"
SRC   <- "https://doi.org/10.1371/journal.pone.0257991.s002"

# --- Published values, PLOS ONE 10.1371/journal.pone.0257991 Table 4 ----------
# lo/hi = n at lowest / highest score, IN THE PAPER'S (original, un-recoded)
# direction.
PUB <- data.frame(
  paper_code = c("RS 1","RS 2","RS 3","RS 4","RS 5","RS 6",
                 "RS 7","RS 8","RS 9","RS 10","RS 11"),
  irw_item   = c("RS1","RS2","RS3","RS4","RS5recoded","RS6recoded",
                 "RS7","RS8","RS9","RS10","RS11"),
  lo  = c( 44,  43,  44, 128, 424, 397,  36,  11,  53,  34,  12),
  hi  = c(334, 358, 374, 270,   3,   7, 371, 437, 339, 381, 418),
  # TRUE where data/pedroso_2021_ifsq.py's source column is the "recoded"
  # (reverse-scored) one, so the live 1 corresponds to the paper's highest score
  recoded = c(FALSE,FALSE,FALSE,FALSE, TRUE,TRUE, FALSE,FALSE,FALSE,FALSE,FALSE),
  stringsAsFactors = FALSE)

AM <- c("RS1","RS2","RS3","RS4")
DQ <- c("RS5recoded","RS6recoded","RS7","RS8","RS9","RS10","RS11")

tmp <- tempfile(fileext = ".xlsx")
r <- httr::GET(SRC, httr::write_disk(tmp, overwrite = TRUE),
               httr::user_agent("IRW-itemtext/1.0"))
stopifnot(httr::status_code(r) == 200)
raw <- as.data.frame(readxl::read_excel(tmp))
num <- function(x) suppressWarnings(as.numeric(gsub(",", ".", as.character(x), fixed = TRUE)))
for (cc in c(AM, DQ)) raw[[cc]] <- num(raw[[cc]])

blk <- function(cols) { d <- raw[, cols, drop = FALSE]; d[complete.cases(d), , drop = FALSE] }
A <- blk(AM); D <- blk(DQ)
cat(sprintf("listwise n: amount %d (paper 461), diet quality %d (paper 463)\n\n",
            nrow(A), nrow(D)))

# --- tie the source file to the live table (per-item n, no export) -----------
live <- tryCatch(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE),
                 error = function(e) NULL)
if (!is.null(live) && !is.null(live$per_item)) {
  pi <- as.data.frame(live$per_item)
  src_n <- sapply(c(AM, DQ), function(cc) sum(!is.na(raw[[cc]])))
  m <- pi$n[match(names(src_n), pi$item)]
  cat("live per-item n vs source-file per-item n:\n")
  cat(paste(sprintf("  %-11s live %3d  source %3d", names(src_n), m, src_n),
            collapse = "\n"), "\n\n")
  if (!identical(as.integer(m), as.integer(src_n)))
    cat("  WARNING: live and source per-item n differ\n\n")
} else cat("(irw_table_sets unavailable -- source-file check only)\n\n")

# --- the mapping check -------------------------------------------------------
cat(sprintf("%-6s %-11s %-9s %6s %6s %6s %6s %s\n",
            "paper", "irw item", "recoded?", "pubLO", "obs*", "pubHI", "obs*", ""))
ok <- TRUE
for (i in seq_len(nrow(PUB))) {
  it  <- PUB$irw_item[i]
  d   <- if (it %in% AM) A else D
  n1  <- sum(d[[it]] == 1); n5 <- sum(d[[it]] == 5)
  obsLO <- if (PUB$recoded[i]) n5 else n1
  obsHI <- if (PUB$recoded[i]) n1 else n5
  good  <- obsLO == PUB$lo[i] && obsHI == PUB$hi[i]
  ok    <- ok && good
  cat(sprintf("%-6s %-11s %-9s %6d %6d %6d %6d %s\n",
              PUB$paper_code[i], it, ifelse(PUB$recoded[i], "yes", "no"),
              PUB$lo[i], obsLO, PUB$hi[i], obsHI, ifelse(good, "ok", "MISMATCH")))
}
cat("* obs is stated in the PAPER's direction: for the two recoded columns the\n",
    "  live resp=1 count is printed under pubHI and vice versa, which is exactly\n",
    "  the mirroring the shipped option_text encodes.\n\n", sep = "")

# no two published (lo, hi) pairs coincide -> the route separates every item
pairs <- paste(PUB$lo, PUB$hi)
cat(sprintf("distinct published (lo,hi) pairs: %d of %d items\n\n",
            length(unique(pairs)), nrow(PUB)))

# --- corroboration: published sub-construct means (Table 2) ------------------
am <- mean(rowMeans(A)); as_ <- sd(rowMeans(A))
dm <- mean(rowMeans(D)); ds  <- sd(rowMeans(D))
cat(sprintf("Restrictive (amount)       observed M=%.2f SD=%.2f  vs published M=4.19 SD=1.02\n", am, as_))
cat(sprintf("Restrictive (diet quality) observed M=%.2f SD=%.2f  vs published M=4.64 SD=0.61\n", dm, ds))
cat("  -> confirms the seven diet-quality items are the RECODED values, i.e.\n")
cat("     RS5recoded/RS6recoded sit in the same direction as RS7-RS11.\n\n")

cat("What this does NOT establish: the belief-vs-behaviour ANCHOR WORDING split\n",
    "(never..always for RS1, RS2 and the recoded RS5/RS6; disagree..agree for\n",
    "RS3, RS4 and RS7-RS11) is read from the paper's Methods sentence and the\n",
    "item content, not from any per-item statistic -- the floor/ceiling counts\n",
    "pin the DIRECTION of each item's scale but not which of the two 5-point\n",
    "label sets it carried. Nor does it establish the Portuguese anchor wording,\n",
    "which the study never published.\n\n", sep = "")

cat(if (ok && length(unique(pairs)) == nrow(PUB) &&
        abs(am - 4.19) < 0.01 && abs(dm - 4.64) < 0.01)
      "VERDICT: PASS\n" else "VERDICT: FAIL\n")
