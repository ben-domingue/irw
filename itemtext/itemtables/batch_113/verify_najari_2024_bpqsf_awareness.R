# verify_najari_2024_bpqsf_awareness.R
#
# CLAIM UNDER TEST: the item_text shipped for q1..q46 is the text printed against
# those very codes in Table 2 of Najari et al. (2024), PLOS ONE 19(9):e0306348.
#
# Falsifiable prediction: Table 2's final column, "CICs" (corrected item-total
# correlations), is a per-item number. If item_text for, say, q13 and q18 were
# swapped, the shipped text would sit against the wrong published CIC. So
# recompute each item's corrected item-total correlation from the study's own
# raw data and line it up against the published column.
#
# DATA SOURCE. The live IRW table is a straight melt of S1 Data's q1..q46
# columns (data/najari_2024_bpqsf.py), so this script reads S1 Data rather than
# calling irw_fetch(), which would export the whole table against the 200GB/30d
# account cap. The code identity between source and live table is confirmed
# server-side with irw_table_sets(), which exports nothing.
#
# Also checks the resp axis: option_text is anchored 1=Never .. 5=Always, so the
# subdiaphragmatic subscale sum must reproduce the published BPQSUBR mean/SD
# (Table 6) in the raw direction and not in the reversed one.

suppressMessages({library(irw); library(readxl)})

TABLE <- "najari_2024_bpqsf_awareness"
SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0306348.s001")

# ---- Table 2, "CICs" column, in printed order q1..q46 -----------------------
PUB <- c(0.34,0.47,0.48,0.55,0.51,0.46,0.53,0.54,0.54,0.55,0.50,0.51,0.59,
         0.47,0.38,0.35,0.50,0.31,0.50,0.36,0.51,0.47,0.52,0.56,0.58,0.47,
         0.52,0.48,0.52,0.53,0.60,0.58,0.53,0.49,0.40,0.52,0.80,0.53,0.57,
         0.49,0.48,0.46,0.44,0.56,0.37,0.55)
names(PUB) <- paste0("q", 1:46)
# q37 is printed as 0.80 in a column where every other value is 0.31-0.60 and its
# own factor loading is the second smallest in the table; treated as a print
# error (see provenance note) and excluded from the tolerance test.
DROP <- "q37"
TOL <- 0.05          # per item
TOL_MAD <- 0.02      # mean absolute deviation over the 45 tested items

# ---- code identity: source column names == live item codes ------------------
live <- irw::irw_table_sets(TABLE)
live_items <- sort(unlist(live$item, use.names = FALSE))
cat("live item codes (irw_table_sets, no export): n =", length(live_items), "\n")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SI, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
qcols <- paste0("q", 1:46)
stopifnot(all(qcols %in% names(raw)))
cat("S1 Data q-columns present:", sum(qcols %in% names(raw)), "of 46;",
    "identical to live item set:", identical(sort(qcols), live_items), "\n\n")

X <- raw[, qcols]
X[] <- lapply(X, function(z) suppressWarnings(as.numeric(z)))
X <- X[stats::complete.cases(X), ]
cat("n respondents with complete BPQ-SF:", nrow(X), "\n\n")

# ---- route 1: corrected item-total correlations -----------------------------
tot <- rowSums(X)
obs <- sapply(qcols, function(c) stats::cor(X[[c]], tot - X[[c]]))

cat(sprintf("%-5s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (c in qcols)
    cat(sprintf("%-5s %10.2f %10.3f %8.3f%s\n", c, PUB[[c]], obs[[c]],
                obs[[c]] - PUB[[c]], if (c %in% DROP) "   <- excluded" else ""))

keep <- setdiff(qcols, DROP)
diffs <- abs(obs[keep] - PUB[keep])
mad <- mean(diffs); worst <- max(diffs)
r <- stats::cor(obs[keep], PUB[keep])
cat(sprintf("\n%d items tested; r(published, observed) = %.4f; MAD = %.4f; worst = %.3f (%s)\n",
            length(keep), r, mad, worst, keep[which.max(diffs)]))

ok1 <- (worst <= TOL) && (mad <= TOL_MAD) && (r >= 0.95)

# ---- route 3 / resp axis: BPQSUBR total vs Table 6 ---------------------------
sub <- paste0("q", 41:46)
s_raw <- rowSums(X[, sub]); s_rev <- rowSums(6 - X[, sub])
cat(sprintf("\nBPQSUBR (q41-q46) published mean/SD = 11.01 / 3.72\n"))
cat(sprintf("  as shipped (1=Never..5=Always): %.2f / %.2f\n", mean(s_raw), sd(s_raw)))
cat(sprintf("  if anchors were reversed:       %.2f / %.2f\n", mean(s_rev), sd(s_rev)))
ok2 <- abs(mean(s_raw) - 11.01) < 0.15 && abs(sd(s_raw) - 3.72) < 0.15

cat("\nWhat this does NOT establish: the CIC route on its own could not separate\n",
    "items whose published CICs coincide (e.g. q11/q17/q19 all print 0.50) -- what\n",
    "distinguishes every item from every other here is that Table 2 prefixes each\n",
    "item's text with the literal code ('q1.', 'q2.', ...) that S1 Data uses as a\n",
    "column name and the live table uses as `item`. The numbers above corroborate\n",
    "that label match; they do not carry it alone. Nor does this check the\n",
    "section_prompt wording, which comes from the BPQ manual, not from the paper.\n",
    sep = "")

cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
