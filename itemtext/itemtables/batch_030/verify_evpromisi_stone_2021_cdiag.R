# verify_evpromisi_stone_2021_cdiag.R -- Step 5b, route 9 (response-frequency matching).
#
# CLAIM UNDER TEST: each live item code cdiagNN carries the item stem the study's own
# codebook attaches to the source variable cdiagNN (e.g. cdiag06 = "lung disease",
# not "kidney disease"), and resp 1/2/3 carry the codebook's 1=No, never diagnosed /
# 2=No, but diagnosed in the past / 3=Yes, currently diagnosed.
#
# FALSIFIABLE PREDICTION: the per-item x per-level response counts in the five
# CC0 source files must reproduce the live table cell for cell. Swapping the text of
# any two items, or permuting the response levels, breaks it -- see the uniqueness
# check below, which establishes that no two items share a count triple, so the
# match distinguishes every item from every other rather than only as a set.
#
# SOURCE COUNTS: pooled over the five *_demos.sas7bdat files of Harvard Dataverse
# doi:10.7910/DVN/G4E2SR (CC0), read column-by-column BY NAME (cs 100 + hs 100 +
# oa 100 + pms 100 + bc 86 = 486 participants). Hard-coded per template rule 4.

suppressMessages(library(irw))

TABLE <- "evpromisi_stone_2021_cdiag"

SRC <- rbind(
  cdiag01 = c(439,  25,  21),
  cdiag02 = c(393,  41,  50),
  cdiag03 = c(437,  10,  38),
  cdiag04 = c(369,  31,  85),
  cdiag05 = c(454,  27,   4),
  cdiag06 = c(457,   3,  25),
  cdiag07 = c(469,   9,   6),
  cdiag08 = c(466,   5,  14),
  cdiag09 = c(426,  33,  26),
  cdiag10 = c(408,  52,  24),
  cdiag11 = c(329,  39, 117),
  cdiag12 = c(331,   9, 145)
)
colnames(SRC) <- c("1", "2", "3")

d <- irw::irw_fetch(TABLE)
LIVE <- table(factor(d$item, levels = rownames(SRC)),
              factor(d$resp, levels = colnames(SRC)))
LIVE <- matrix(as.integer(LIVE), nrow = nrow(SRC),
               dimnames = dimnames(SRC))

cat(sprintf("%-8s %-18s %-18s %s\n", "item", "source (1/2/3)", "live (1/2/3)", "match"))
ok <- TRUE
for (i in rownames(SRC)) {
  s <- SRC[i, ]; l <- LIVE[i, ]
  m <- all(s == l); ok <- ok && m
  cat(sprintf("%-8s %-18s %-18s %s\n", i,
              paste(s, collapse = "/"), paste(l, collapse = "/"),
              if (m) "yes" else "NO"))
}
cat(sprintf("\ntotal cells compared: %d ; mismatched: %d\n",
            length(SRC), sum(SRC != LIVE)))

# Does the route distinguish EVERY item from EVERY other item?
trip <- apply(SRC, 1, paste, collapse = "/")
ndup <- length(trip) - length(unique(trip))
cat(sprintf("distinct source count-triples: %d of %d (duplicate triples: %d)\n",
            length(unique(trip)), length(trip), ndup))

# Would a permuted response coding survive? Compare live against reversed source.
rev_mis <- sum(SRC[, c(3, 2, 1)] != LIVE)
cat(sprintf("cells mismatched under a reversed 3/2/1 coding: %d (control)\n", rev_mis))

cat("Note: this pins item<->text and resp<->option_text for all 12 items and all 3\n",
    "levels. It does NOT independently confirm the codebook's own stem wording --\n",
    "the stems are transcribed from that codebook and there is no second source.\n", sep = "")

cat(if (ok && ndup == 0 && rev_mis > 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
