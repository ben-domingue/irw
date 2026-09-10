# verify_pickova2025_behavioral_intent.R
#
# CLAIM UNDER TEST: item codes int_1..int_4 correspond, in order, to columns
# 25..28 (0-based 24..27) of the deposit's raw Google-Forms export
# "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# (figshare article 30576341, file 59422829) -- i.e. to the four bracketed
# statements under the grid question "What are your plans regarding these
# platforms?".  The processing script is not in this repo, so the code->column
# tie is positional and must be shown, not assumed.
#
# FALSIFIABLE PREDICTION: for each item, the count of respondents at each of the
# seven scale points in the live IRW table must equal the count for the claimed
# raw column, cell for cell.  The four frequency vectors below are mutually
# distinct at multiple levels, so ANY permutation of the four item codes breaks
# at least two of the four comparisons.  This is a stronger test than means.
#
# The raw counts are hard-coded from the deposit file (fixed, published data).

suppressMessages(library(irw))

TABLE <- "pickova2025_behavioral_intent"

# Raw-file counts of resp values 1..7, per claimed source column.
RAW <- rbind(
  int_1 = c(4, 6, 5, 11, 21, 34, 52),   # col 25: "I intend to continue shopping on SHEIN/TEMU in the future."
  int_2 = c(26, 18, 15, 25, 19, 18, 12),# col 26: "I plan to reduce my spending on SHEIN/TEMU."
  int_3 = c(27, 28, 18, 18, 17, 17, 8), # col 27: "I am actively looking for alternatives to SHEIN/TEMU."
  int_4 = c(24, 14, 14, 25, 17, 17, 22) # col 28: "I would stop using SHEIN/TEMU if I found a similarly priced alternative."
)
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
LIVE <- matrix(0L, nrow = 4, ncol = 7,
               dimnames = list(paste0("int_", 1:4), 1:7))
tab <- table(d$item, d$resp)
for (i in rownames(LIVE))
  for (j in colnames(LIVE))
    if (i %in% rownames(tab) && j %in% colnames(tab)) LIVE[i, j] <- tab[i, j]

cat("Per-item response-frequency match (raw deposit column vs live IRW table)\n")
cat(sprintf("%-7s %-22s %-22s %s\n", "item", "raw counts 1..7", "live counts 1..7", "match"))
ok_item <- logical(4); names(ok_item) <- rownames(RAW)
for (i in rownames(RAW)) {
  same <- all(RAW[i, ] == LIVE[i, ])
  ok_item[i] <- same
  cat(sprintf("%-7s %-22s %-22s %s\n", i,
              paste(RAW[i, ], collapse = ","),
              paste(LIVE[i, ], collapse = ","),
              if (same) "OK" else "MISMATCH"))
}

# Permutation sensitivity: show that no other assignment of the four codes to
# the four raw columns also reproduces the live counts.
perms <- as.matrix(expand.grid(1:4, 1:4, 1:4, 1:4))
perms <- perms[apply(perms, 1, function(r) length(unique(r)) == 4L), , drop = FALSE]
cat("\nAlternative code->column assignments that also reproduce the live counts:\n")
n_alt <- 0
for (k in seq_len(nrow(perms))) {
  p <- as.integer(perms[k, ])
  if (identical(p, 1:4)) next
  if (all(RAW[p, ] == LIVE)) { n_alt <- n_alt + 1; cat("  ", paste(p, collapse = "-"), "\n") }
}
cat(sprintf("  %d of the %d non-identity permutations of the 4 codes reproduce the data\n",
            n_alt, nrow(perms) - 1L))

cat("\nMeans, for readability:\n")
for (i in rownames(RAW))
  cat(sprintf("  %-7s raw %.4f   live %.4f\n", i,
              sum(RAW[i, ] * 1:7) / sum(RAW[i, ]),
              sum(LIVE[i, ] * 1:7) / sum(LIVE[i, ])))

cat("\nWhat this does NOT establish: the response-option ANCHOR wording. The\n",
    "deposit publishes no labels for the 1-7 scale points, so option_text is\n",
    "shipped blank; the direction of the scale is not verified by this check.\n",
    "It also does not test instructions/section text, only item<->code.\n", sep = "")

cat(if (all(ok_item) && n_alt == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
