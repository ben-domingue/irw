# verify_pedroso_2021_ifsq_laissezfaire.R
#
# CLAIM UNDER TEST (Step 5b, route 1 -- published per-item statistics):
#   each IRW item code LF1..LF11 carries the IFSQ-Br wording that Pedroso &
#   Gubert (2021) S1 Table prints against that same code, AND the option_text
#   shipped for resp 1..5 runs in the direction the live data actually stores
#   -- i.e. mirrored for the four "recoded" columns, unmirrored for the rest.
#
# FALSIFIABLE PREDICTION: PLOS ONE 10.1371/journal.pone.0257991 Table 4 prints,
# for every laissez-faire item, the number of respondents at the LOWEST and at
# the HIGHEST score of the 5-point scale, computed listwise within each
# sub-construct (n = 404 attention, n = 464 diet quality). Those 22 counts are
# item-specific and nowhere near each other, so they distinguish every item from
# every other item. If item_text for two items were swapped, the pair of counts
# would land on the wrong item. If the recode direction were wrong, the
# low/high counts of LF6-LF9 would fail to mirror.
#
# This uses the study's own S1 Dataset (the file data/pedroso_2021_ifsq.py reads
# to build the IRW table) rather than irw_fetch(), which would export the whole
# table against the shared 200GB/30-day Redivis quota. irw_table_sets() is used
# to confirm the live per-item n matches the source file item for item, so the
# numbers below are about the table that actually shipped.

suppressMessages({library(irw); library(readxl); library(httr)})

TABLE <- "pedroso_2021_ifsq_laissezfaire"
SRC   <- "https://doi.org/10.1371/journal.pone.0257991.s002"

# --- Published values, PLOS ONE 10.1371/journal.pone.0257991 Table 4 ----------
# item = the paper's code; lo/hi = n at lowest / highest score, IN THE PAPER'S
# (original, un-recoded) DIRECTION.  Paper prints LF5 lo as "219 (72.0%)"; 72.0%
# of n=404 is 291, and 219 is a typographical error in the paper -- the percent
# is what is compared here for that one cell (flagged, not silently fixed).
PUB <- data.frame(
  paper_code = c("LF 1","LF 2","LF 3","LF 4","LF 5",
                 "LF 6","LF 7","LF 8","LF 9","LF 10","LF 11"),
  irw_item   = c("LF1","LF2","LF3","LF4","LF5",
                 "LF6recoded","LF7recoded","LF8recoded","LF9recoded","LF10","LF11"),
  lo  = c(161, 242, 197, 38, 291, 4, 38, 11, 6, 457, 434),
  hi  = c(155,  45,  60, 319, 80, 420, 363, 401, 419, 6, 10),
  # TRUE where data/pedroso_2021_ifsq.py's source column is the "recoded"
  # (reverse-scored) one, so the live 1 corresponds to the paper's highest score
  recoded = c(FALSE,FALSE,FALSE,FALSE,FALSE, TRUE,TRUE,TRUE,TRUE, FALSE,FALSE),
  stringsAsFactors = FALSE)

ATT <- c("LF1","LF2","LF3","LF4","LF5")
DQ  <- c("LF6recoded","LF7recoded","LF8recoded","LF9recoded","LF10","LF11")

tmp <- tempfile(fileext = ".xlsx")
r <- httr::GET(SRC, httr::write_disk(tmp, overwrite = TRUE),
               httr::user_agent("IRW-itemtext/1.0"))
stopifnot(httr::status_code(r) == 200)
raw <- as.data.frame(readxl::read_excel(tmp))
num <- function(x) suppressWarnings(as.numeric(gsub(",", ".", as.character(x), fixed = TRUE)))
for (cc in c(ATT, DQ)) raw[[cc]] <- num(raw[[cc]])

blk <- function(cols) { d <- raw[, cols, drop = FALSE]; d[complete.cases(d), , drop = FALSE] }
A <- blk(ATT); D <- blk(DQ)
cat(sprintf("listwise n: attention %d (paper 404), diet quality %d (paper 464)\n\n",
            nrow(A), nrow(D)))

# --- tie the source file to the live table (per-item n, no export) -----------
live <- tryCatch(irw::irw_table_sets(TABLE, source = "core", per_item = TRUE),
                 error = function(e) NULL)
if (!is.null(live) && !is.null(live$per_item)) {
  pi <- as.data.frame(live$per_item)
  src_n <- sapply(c(ATT, DQ), function(cc) sum(!is.na(raw[[cc]])))
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
  d   <- if (it %in% ATT) A else D
  n1  <- sum(d[[it]] == 1); n5 <- sum(d[[it]] == 5)
  # in the paper's direction: a recoded column's live 1 is the paper's HIGHest
  obsLO <- if (PUB$recoded[i]) n5 else n1
  obsHI <- if (PUB$recoded[i]) n1 else n5
  good  <- obsLO == PUB$lo[i] && obsHI == PUB$hi[i]
  ok    <- ok && good
  cat(sprintf("%-6s %-11s %-9s %6d %6d %6d %6d %s\n",
              PUB$paper_code[i], it, ifelse(PUB$recoded[i], "yes", "no"),
              PUB$lo[i], obsLO, PUB$hi[i], obsHI, ifelse(good, "ok", "MISMATCH")))
}
cat("* obs is stated in the PAPER's direction: for the four recoded columns the\n",
    "  live resp=1 count is printed under pubHI and vice versa, which is exactly\n",
    "  the mirroring the shipped option_text encodes.\n\n", sep = "")

# --- corroboration: published sub-construct mean (Table 2) --------------------
dqm <- mean(rowMeans(D)); dqs <- sd(rowMeans(D))
cat(sprintf("Laissez-faire (diet quality) composite: observed M=%.2f SD=%.2f  vs published M=1.24 SD=0.41\n",
            dqm, dqs))
cat("  -> confirms the six diet-quality items are the RECODED values, and that\n")
cat("     LF6-LF9 sit in the same direction as LF10/LF11 once recoded.\n\n")

cat("What this does NOT establish: the belief-vs-behaviour ANCHOR WORDING split\n",
    "(disagree..agree for LF4, LF5, LF10, LF11; never..always for LF1-LF3 and the\n",
    "recoded LF6-LF9) is read from the paper's Methods sentence and the item\n",
    "content, not from any per-item statistic -- the floor/ceiling counts pin the\n",
    "DIRECTION of each item's scale but not which of the two 5-point label sets\n",
    "it carried. Nor does it establish the Portuguese anchor wording, which the\n",
    "study never published.\n\n", sep = "")

cat(if (ok && abs(dqm - 1.24) < 0.01) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
