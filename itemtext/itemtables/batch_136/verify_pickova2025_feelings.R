# verify_pickova2025_feelings.R
#
# CLAIM UNDER TEST: item codes feel_1..feel_5 correspond, in order, to columns
# 20..24 (1-based) of the deposit's raw Google-Forms export
# "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# (figshare article 30576341, file 59422829, CC BY 4.0) -- i.e. to the five
# bracketed statements under the grid question
# "How do you feel about shopping on these platforms?".
# No processing script for this table exists in the IRW repo, so the
# code->column tie is POSITIONAL and has to be shown, not assumed.
#
# FALSIFIABLE PREDICTION: for each item, the count of respondents at each of the
# seven scale points in the live IRW table must equal the count for the claimed
# raw column, cell for cell. The five raw frequency vectors below are mutually
# distinct in several cells each, so ANY permutation of the five codes breaks at
# least two comparisons; the script enumerates all 119 non-identity permutations
# and shows that none reproduces the live data.
#
# The raw counts are hard-coded from the deposit file (fixed, published data),
# computed over non-empty cells only (two items have one blank response).

suppressMessages(library(irw))

TABLE <- "pickova2025_feelings"

RAW <- rbind(
  feel_1 = c( 4,  6,  6, 14, 15, 37, 51), # col 20: "I feel excited when I browse new arrivals on SHEIN/TEMU."
  feel_2 = c( 2,  3,  2,  8, 15, 48, 55), # col 21: "I feel satisfied when I receive a package from SHEIN/TEMU."
  feel_3 = c(41, 26, 16, 13, 18, 12,  7), # col 22: "I feel guilty after making a purchase from SHEIN/TEMU."
  feel_4 = c(19, 13, 13, 15, 39, 21, 12), # col 23: "I feel anxious about the product quality when I order from SHEIN/TEMU."
  feel_5 = c(32, 26, 14, 23, 16, 14,  7)  # col 24: "I feel frustrated by the environmental impact of my consumption on these platforms."
)
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
LIVE <- matrix(0L, nrow = 5, ncol = 7,
               dimnames = list(paste0("feel_", 1:5), 1:7))
tab <- table(d$item, d$resp)
for (i in rownames(LIVE))
  for (j in colnames(LIVE))
    if (i %in% rownames(tab) && j %in% colnames(tab)) LIVE[i, j] <- tab[i, j]

cat("Per-item response-frequency match (raw deposit column vs live IRW table)\n")
cat(sprintf("%-8s %-24s %-24s %s\n", "item", "raw counts 1..7", "live counts 1..7", "match"))
ok_item <- logical(5); names(ok_item) <- rownames(RAW)
for (i in rownames(RAW)) {
  same <- all(RAW[i, ] == LIVE[i, ])
  ok_item[i] <- same
  cat(sprintf("%-8s %-24s %-24s %s\n", i,
              paste(RAW[i, ], collapse = ","),
              paste(LIVE[i, ], collapse = ","),
              if (same) "OK" else "MISMATCH"))
}

# Permutation sensitivity: no other assignment of the five codes to the five
# raw columns reproduces the live counts.
perms <- as.matrix(expand.grid(1:5, 1:5, 1:5, 1:5, 1:5))
perms <- perms[apply(perms, 1, function(r) length(unique(r)) == 5L), , drop = FALSE]
n_alt <- 0
for (k in seq_len(nrow(perms))) {
  p <- as.integer(perms[k, ])
  if (identical(p, 1:5)) next
  if (all(RAW[p, ] == LIVE)) { n_alt <- n_alt + 1; cat("  ALT: ", paste(p, collapse = "-"), "\n") }
}
cat(sprintf("\n%d of the %d non-identity permutations of the 5 codes reproduce the live counts\n",
            n_alt, nrow(perms) - 1L))

cat("\nMeans and n, for readability:\n")
for (i in rownames(RAW))
  cat(sprintf("  %-8s n raw %3d live %3d   mean raw %.4f live %.4f\n", i,
              sum(RAW[i, ]), sum(LIVE[i, ]),
              sum(RAW[i, ] * 1:7) / sum(RAW[i, ]),
              sum(LIVE[i, ] * 1:7) / sum(LIVE[i, ])))

cat("\nWhat this does NOT establish: the resp<->option_text axis. The deposit\n",
    "publishes no labels for the seven scale points, so option_text is shipped\n",
    "blank and the scale direction is not verified here. It also does not test\n",
    "the instructions text, only the item<->code mapping.\n", sep = "")

cat(if (all(ok_item) && n_alt == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
