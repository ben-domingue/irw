# verify_pickova2025_fast_fashion_beliefs.R -- Step 5b route 9 (response-frequency matching).
#
# Claim under test: item codes ffb_1..ffb_5 correspond POSITIONALLY to columns
# 29..33 (1-based) of the raw Google Forms export
# "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# (figshare 30576341, file 59422829), whose headers carry the item wording
# under the shared grid stem "What are your general beliefs about the fast
# fashion industry?".
#
# Falsifiable prediction: the per-item x per-level response frequency table of
# the live IRW data must match, cell for cell, the frequency table computed
# from those raw columns. The five raw frequency vectors are mutually
# distinct, so a transposition of any two items would break at least one cell.
# Raw counts are hard-coded from the raw file so this runs offline.

suppressMessages(library(irw))

TABLE <- "pickova2025_fast_fashion_beliefs"

# counts of raw values 1..7 in the raw xlsx, columns 29..33 in header order
RAW <- rbind(
  "environmental impact of the fast fashion industry as a whole" = c(11,  9, 19, 24, 22, 27, 23),
  "social and labor ethics in the global garment industry"       = c(11,  9,  9, 13, 31, 38, 24),
  "individual consumers have a responsibility"                   = c( 4,  2,  4, 18, 23, 49, 35),
  "primarily the government's responsibility to regulate"        = c( 4,  1, 10, 18, 38, 30, 32),
  "sustainable fashion is a luxury I cannot afford"              = c(22, 15, 16, 20, 25, 21, 16))
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, paste0("ffb_", 1:5)), factor(d$resp, 1:7))

cat("shipped item_text (in ffb_1..ffb_5 order) vs raw column, counts of resp 1..7\n\n")
ok <- TRUE
for (i in 1:5) {
  r <- as.integer(RAW[i, ]); l <- as.integer(LIVE[i, ])
  cat(sprintf("%-6s %-62s raw: %-22s live: %-22s %s\n",
              paste0("ffb_", i), rownames(RAW)[i],
              paste(r, collapse = " "), paste(l, collapse = " "),
              if (identical(r, l)) "match" else "MISMATCH"))
  if (!identical(r, l)) ok <- FALSE
}

# a transposition must be detectable: no two raw rows may be identical, and no
# non-identity permutation of the five codes may reproduce the live table.
sig  <- apply(RAW, 1, paste, collapse = "-")
dupe <- any(duplicated(sig))
perms <- function(v) if (length(v) == 1) list(v) else
  do.call(c, lapply(seq_along(v), function(i)
    lapply(perms(v[-i]), function(p) c(v[i], p))))
LIVEm <- matrix(as.integer(LIVE), 5, 7)
nrep <- sum(vapply(perms(1:5), function(p)
  all(unname(RAW[p, , drop = FALSE]) == LIVEm), logical(1)))
cat(sprintf("\nany two raw frequency vectors identical? %s\n", if (dupe) "YES" else "no"))
cat(sprintf("permutations of the 5 codes reproducing the live table: %d of 120 (expect exactly 1, the identity)\n", nrep))

cat("\nNote: this pins every item's TEXT to its code (all 5 vectors distinct, all 35\n",
    "cells match, unique permutation). It does NOT establish the response-option\n",
    "anchors: the Google Forms grid publishes no labels for scale points 1-7, so\n",
    "option_text is blank by design and nothing here verifies the resp<->option_text\n",
    "axis or the scale's polarity direction.\n", sep = "")

cat(if (ok && !dupe && nrep == 1L) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
