# verify_NSR-FC_Youhasan_2021.R -- Step 5b evidence, re-runnable.
#
# Claim under test: each item code Q1..Q35 in the live table carries the wording
# this extraction shipped for it.
#
# Two independent checks:
#  (A) SOURCE TIE. The deposit's own "Supplement 1. Results of the content
#      validation..." (Harvard Dataverse doi:10.7910/DVN/IKRPCP, file id 4330774)
#      prints one row per item, labelled with the very code -- Q1..Q35 -- that the
#      raw response CSVs use as column headers and that data/NSR-FC_Youhasan_2021.R
#      passes through unchanged (pivot_longer(Q1:Q35)). So the tie is a label match
#      at the source. This re-fetches that file and diffs it character-for-character
#      against the shipped item_text.
#  (B) STRUCTURAL CORROBORATION. The paper (JEEHP 2020;17:41, Table 1) publishes a
#      PCA item->factor assignment by item NUMBER. If the code->text mapping were
#      permuted, the shipped subscale membership would not reproduce in the live
#      correlation structure. Counts how many items load strongest on their
#      hypothesised factor.

suppressMessages({library(irw)})

TABLE   <- "NSR-FC_Youhasan_2021"
ITEMS   <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])),
                     paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS)) ITEMS <- paste0("itemtables/batch_120/", TABLE, "__items.csv")

## ---- (A) source tie -------------------------------------------------------
SUPP <- "https://dataverse.harvard.edu/api/access/datafile/4330774?format=original"
supp <- tryCatch(read.csv(url(SUPP), header = FALSE, stringsAsFactors = FALSE,
                          colClasses = "character"), error = function(e) NULL)
shipped <- read.csv(ITEMS, stringsAsFactors = FALSE, colClasses = "character")
shipped <- unique(shipped[, c("item", "item_text")])

if (is.null(supp)) {
  cat("Supplement 1 could not be fetched; check (A) skipped.\n")
  okA <- NA
} else {
  keep <- grepl("^Q[0-9]+$", supp[[1]])
  src  <- data.frame(item = supp[keep, 1], src_text = trimws(supp[keep, 2]),
                     stringsAsFactors = FALSE)
  m <- merge(shipped, src, by = "item", all = TRUE)
  m$match <- !is.na(m$src_text) & !is.na(m$item_text) & m$src_text == m$item_text
  cat(sprintf("(A) Supplement 1 rows labelled Q*: %d ; shipped items: %d ; exact text matches: %d\n",
              nrow(src), nrow(shipped), sum(m$match)))
  if (any(!m$match)) print(m[!m$match, ])
  cat(sprintf("    e.g. Q1  src=%s\n", src$src_text[src$item == "Q1"]))
  cat(sprintf("         Q30 src=%s\n", src$src_text[src$item == "Q30"]))
  okA <- nrow(src) == 35 && sum(m$match) == 35
}

## ---- (B) structural corroboration ----------------------------------------
GROUPS <- list(
  technological  = paste0("Q", c(6:16, 18)),
  environmental  = paste0("Q", c(20, 21, 23, 24, 25)),
  personal       = paste0("Q", c(1, 2, 3, 4, 17, 19)),
  pedagogical    = paste0("Q", c(22, 26, 27, 28, 29, 34, 35)),
  interpersonal  = paste0("Q", c(30, 31, 32, 33)))

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w$id <- NULL
R <- cor(w, use = "pairwise.complete.obs")

hits <- 0; tot <- 0
cat("\n(B) mean r with each hypothesised subscale (own subscale excludes self)\n")
for (g in names(GROUPS)) for (it in GROUPS[[g]]) {
  tot <- tot + 1
  ms <- sapply(names(GROUPS), function(h) {
    o <- setdiff(GROUPS[[h]], it); mean(R[it, o], na.rm = TRUE) })
  best <- names(which.max(ms))
  hits <- hits + (best == g)
  cat(sprintf("  %-4s own=%-14s %5.2f   best=%-14s %5.2f %s\n",
              it, g, ms[[g]], best, max(ms), ifelse(best == g, "", "<-- cross")))
}
cat(sprintf("\n(B) %d/%d items load strongest on the factor the paper assigns them.\n", hits, tot))
cat("Note: (B) alone pins subscale membership, not order within a subscale, and the\n",
    "cross-loaders are the ones the paper itself reports as weak/double-loading\n",
    "(Q16 .476/.474, Q22 .437, Q29 .506). (A) is what distinguishes every item from\n",
    "every other item; (B) only corroborates it.\n", sep = "")

pass <- isTRUE(okA) && hits >= 30
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
