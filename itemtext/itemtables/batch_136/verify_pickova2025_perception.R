# verify_pickova2025_perception.R
#
# CLAIM UNDER TEST: item codes perc_1..perc_7 correspond, in order, to columns
# 13..19 (0-based 12..18) of the deposit's raw Google-Forms export
# "DATA - Attitude-Behavior Gap on TEMU and SHEIN (Odpovedi).xlsx"
# (figshare article 30576341, file 59422829, CC BY 4.0) -- i.e. to the seven
# bracketed statements under the grid question "How do you perceive
# SHEIN/TEMU?".  No processing script for this table exists in the repo, so the
# code->column tie is POSITIONAL and must be shown, not assumed.
#
# FALSIFIABLE PREDICTION: for each item, the count of respondents at each of the
# seven scale points in the live IRW table must equal the count for the claimed
# raw column, cell for cell.  The seven raw frequency vectors are mutually
# distinct, so any permutation of the seven codes breaks at least one cell; the
# script enumerates all 5039 non-identity permutations to show that.
#
# The raw counts are hard-coded from the deposit file (fixed, published data).

suppressMessages(library(irw))

TABLE <- "pickova2025_perception"

# Raw-file counts of resp values 1..7, per claimed source column.
RAW <- rbind(
  perc_1 = c( 1,  5,  6, 10, 25, 45, 41), # col 13: "I believe SHEIN/TEMU offers good value for money."
  perc_2 = c( 2,  4,  9, 10, 28, 45, 35), # col 14: "...products ... acceptable quality for their price."
  perc_3 = c( 2,  9,  7, 14, 23, 38, 40), # col 15: "...innovative in its business model and use of technology."
  perc_4 = c( 2,  4,  4,  8, 24, 40, 50), # col 16: "...makes trendy fashion accessible to people like me."
  perc_5 = c(41, 19,  6, 12, 12, 20, 22), # col 17: "...business practices are harmful to the environment."
  perc_6 = c( 9,  8,  9, 16, 23, 41, 27), # col 18: "I am aware of the ethical concerns regarding labor practices..."
  perc_7 = c(22, 17, 11, 24, 16, 25, 18)  # col 19: "...lacks transparency about its supply chain."
)
colnames(RAW) <- 1:7

d <- irw::irw_fetch(TABLE)
LIVE <- matrix(0L, nrow = 7, ncol = 7,
               dimnames = list(paste0("perc_", 1:7), 1:7))
tab <- table(d$item, d$resp)
for (i in rownames(LIVE))
  for (j in colnames(LIVE))
    if (i %in% rownames(tab) && j %in% colnames(tab)) LIVE[i, j] <- tab[i, j]

cat("Per-item response-frequency match (raw deposit column vs live IRW table)\n")
cat(sprintf("%-8s %-26s %-26s %s\n", "item", "raw counts 1..7", "live counts 1..7", "match"))
ok_item <- logical(7); names(ok_item) <- rownames(RAW)
for (i in rownames(RAW)) {
  same <- all(RAW[i, ] == LIVE[i, ])
  ok_item[i] <- same
  cat(sprintf("%-8s %-26s %-26s %s\n", i,
              paste(RAW[i, ], collapse = ","),
              paste(LIVE[i, ], collapse = ","),
              if (same) "OK" else "MISMATCH"))
}

# Permutation sensitivity: no other assignment of the seven codes to the seven
# raw columns may also reproduce the live counts.
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(k)
    lapply(perms(v[-k]), function(p) c(v[k], p))))
P <- perms(1:7)
n_alt <- 0
for (p in P) {
  if (identical(as.integer(p), 1:7)) next
  if (all(RAW[p, ] == LIVE)) { n_alt <- n_alt + 1; cat("  ALT:", paste(p, collapse = "-"), "\n") }
}
cat(sprintf("\n%d of the %d non-identity permutations of the 7 codes reproduce the live counts\n",
            n_alt, length(P) - 1L))

cat("\nMeans, for readability:\n")
for (i in rownames(RAW))
  cat(sprintf("  %-8s raw %.4f   live %.4f\n", i,
              sum(RAW[i, ] * 1:7) / sum(RAW[i, ]),
              sum(LIVE[i, ] * 1:7) / sum(LIVE[i, ])))

cat("\nWhat this does NOT establish: the resp <-> option_text axis. The deposit\n",
    "publishes no anchor labels for the 1-7 scale points (checked: the main\n",
    "export's headers, the article description, the analysis workbooks and the\n",
    "deposited Tableau screenshot), so option_text ships blank and the scale\n",
    "direction is not verified here. It also does not test the instructions or\n",
    "instrument text -- only the item <-> code tie.\n", sep = "")

cat(if (all(ok_item) && n_alt == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
