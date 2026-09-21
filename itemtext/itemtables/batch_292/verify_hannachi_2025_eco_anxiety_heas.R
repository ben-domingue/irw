# Step 5b mapping verification for hannachi_2025_eco_anxiety_heas.
#
# CLAIM: item code heasN carries the French wording the preprint's Appendix indexes
# as "HEAS N" (and, for heas8/9/10, the shared CCAS2/HEAS8, CCAS9/HEAS9, CCAS11/HEAS10
# rows). The falsifiable prediction: Supplementary S5 Table S5.1 publishes M, SD and
# the full 0-4 response-category frequency table for each of those source codes
# (N = 534). If any two items' text were swapped, the live per-item frequency vectors
# would no longer line up with the published rows.
#
# The 13 published frequency vectors are pairwise distinct, so a match pins every item
# individually, not just a block or a polarity class.

suppressMessages(library(irw))

TABLE <- "hannachi_2025_eco_anxiety_heas"

# Supplementary_Materials.docx, Table S5.1 (osf.io/djcex). Columns: M, SD, n at resp 0..4.
PUB <- rbind(
  heas1  = c(1.91, 1.40, 125,  92, 110, 122,  85),
  heas2  = c(1.14, 1.22, 224, 132,  86,  66,  26),
  heas3  = c(2.44, 1.28,  48,  86, 122, 137, 141),
  heas4  = c(2.36, 1.31,  62,  86, 110, 152, 124),
  heas5  = c(1.22, 1.26, 211, 130,  95,  62,  36),
  heas6  = c(0.88, 1.14, 278, 130,  59,  48,  19),
  heas7  = c(1.40, 1.30, 169, 149, 103,  60,  53),
  heas8  = c(0.85, 1.19, 303, 102,  66,  33,  30),   # source col CCAS2/HEAS8
  heas9  = c(0.65, 0.99, 329, 109,  56,  32,   8),   # source col CCAS9/HEAS9
  heas10 = c(0.61, 0.99, 344, 106,  46,  26,  12),   # source col CCAS11/HEAS10
  heas11 = c(1.88, 1.26,  92, 124, 136, 120,  62),
  heas12 = c(1.63, 1.28, 127, 139, 122,  95,  51),
  heas13 = c(1.73, 1.33, 121, 134, 116,  95,  68)
)
colnames(PUB) <- c("M", "SD", "n0", "n1", "n2", "n3", "n4")

d <- irw::irw_fetch(TABLE)
items <- rownames(PUB)

cat(sprintf("%-7s %6s %6s | %s\n", "item", "M.pub", "M.obs",
            "counts published -> observed at resp 0,1,2,3,4"))
ok_counts <- TRUE; worst_m <- 0
for (it in items) {
  r <- d$resp[d$item == it]
  obs <- as.integer(table(factor(r, levels = 0:4)))
  m   <- mean(r)
  worst_m <- max(worst_m, abs(round(m, 2) - PUB[it, "M"]))
  same <- identical(obs, as.integer(PUB[it, 3:7]))
  ok_counts <- ok_counts && same
  cat(sprintf("%-7s %6.2f %6.2f | %-24s -> %-24s %s\n", it, PUB[it, "M"], m,
              paste(PUB[it, 3:7], collapse = ","), paste(obs, collapse = ","),
              if (same) "match" else "MISMATCH"))
}
cat(sprintf("\nlargest |round(M.obs,2) - M.pub| = %.4f (Table S5.1 is rounded to 2 dp)\n", worst_m))

# The route's discriminating power, stated rather than assumed.
dup <- anyDuplicated(apply(PUB[, 3:7], 1, paste, collapse = ","))
cat("Note: heas2's published M (1.14) differs by .01 from the 1.1348 implied by its own\n",
    "published frequencies, so M is checked to 0.01; the 65 category counts, which are the\n",
    "discriminating evidence, match exactly with no tolerance.\n", sep = "")
cat(sprintf("pairwise-distinct published frequency vectors: %s\n",
            if (dup == 0) "yes (all 13 distinct -- every item is individually pinned)"
            else "NO -- route is only partial"))

cat(if (ok_counts && worst_m <= 0.0101 && dup == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
