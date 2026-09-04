# verify_contreras_valdez_2022_bsq.R
#
# STATUS: this table is BLOCKED on the item-text rights rule (irw#1891); no
# __items.csv was written. This script therefore does not verify a shipped
# mapping -- it re-runs, so a later attempt does not have to rebuild it, the
# evidence that the IRW item codes bsq_i01..bsq_i16 correspond to items 1..16
# of the BSQ-16B (Evans & Dolan 1993) as reproduced in Spanish in the
# administered Mexican adaptation (Amaya Hernandez 2013, UNAM, Apendice A).
#
# THE CLAIM UNDER TEST
#   bsq_iNN  ==  position NN of BSQ-16B, i.e. the ascending list of BSQ-34
#   items {2,4,6,12,13,14,16,18,19,23,24,27,29,30,31,33}.
#
# THE FALSIFIABLE PREDICTION
#   The study's own S1 spreadsheet carries bsq8_overall, described in its Keys
#   sheet as the "8-item BSQ overall score", and the paper says the eight-item
#   one-factor model of Evans & Dolan was used. BSQ-8C is BSQ-34 items
#   {4,6,13,16,19,23,29,33}. Under the claim those are BSQ-16B positions
#   {2,3,5,7,9,10,13,16}. So the columns whose row sums reproduce bsq8_overall
#   must be exactly bsq_i02, i03, i05, i07, i09, i10, i13, i16 -- 1 of
#   choose(16,8) = 12870 possible subsets.
#
# Data: the PLOS ONE S1 file, which is the source the IRW table was built from
# (data/contreras_valdez_2022_edeq_battery.py). No Redivis export needed.

suppressMessages({library(readxl); library(utils)})

SI <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0266507.s001")
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(SI, tmp, quiet = TRUE, mode = "wb")
d <- as.data.frame(readxl::read_excel(tmp, sheet = "Data"))
d <- d[d$study == 1, ]

b <- sprintf("bsq_i%02d", 1:16)
X <- as.matrix(d[, b]); tot <- d$bsq8_overall

# BSQ-16B, ascending BSQ-34 item numbers -> positions 1..16
BSQ16B   <- c(2,4,6,12,13,14,16,18,19,23,24,27,29,30,31,33)
BSQ8C    <- c(4,6,13,16,19,23,29,33)          # Evans & Dolan (1993)
PREDICTED <- which(BSQ16B %in% BSQ8C)          # -> 2 3 5 7 9 10 13 16

cat(sprintf("Study 1 rows: %d\n", nrow(X)))
cat("predicted 8-item subset (BSQ-8C under the claimed mapping):",
    paste(sprintf("bsq_i%02d", PREDICTED), collapse = " "), "\n\n")

cmb <- utils::combn(16, 8)
hit <- which(apply(cmb, 2, function(cc)
    isTRUE(all.equal(as.numeric(rowSums(X[, cc, drop = FALSE])), as.numeric(tot)))))
cat(sprintf("subsets of 8 columns whose row sums equal bsq8_overall exactly: %d of %d\n",
            length(hit), ncol(cmb)))
observed <- if (length(hit) == 1) sort(cmb[, hit]) else integer(0)
cat("observed subset:", if (length(observed)) paste(sprintf("bsq_i%02d", observed),
    collapse = " ") else "(not unique)", "\n\n")

# Secondary, weaker: content plausibility of the extremes.
m <- colMeans(X)
cat(sprintf("%-9s %6s\n", "item", "mean"))
for (i in 1:16) cat(sprintf("%-9s %6.3f\n", b[i], m[i]))
cat(sprintf("\nlowest-mean item: %s (%.3f) -- BSQ-34 #%d, the avoidance-of-social-occasions item\n",
            b[which.min(m)], min(m), BSQ16B[which.min(m)]))
cat(sprintf("highest-mean item: %s (%.3f) -- BSQ-34 #%d, the fear-of-becoming-fat item\n",
            b[which.max(m)], max(m), BSQ16B[which.max(m)]))

# Independent-sample EFA loadings, Amaya Hernandez (2013) Apendice A, items 1..16.
LOAD <- c(.665,.617,.691,.634,.628,.538,.461,.541,.730,.618,.698,.571,.745,.622,.537,.677)
tt <- rowSums(X)
itc <- sapply(1:16, function(i) cor(X[, i], tt - X[, i]))
rho <- suppressWarnings(cor(LOAD, itc, method = "spearman"))
cat(sprintf("\nSpearman(dissertation EFA loading, corrected item-total r here) = %.3f over 16 items\n", rho))

cat("\nWhat this does NOT establish: the subset test pins WHICH EIGHT positions are\n",
    "the BSQ-8C members; it does not order items within the 8C half or within the\n",
    "8D half, so it is PARTIAL, not per-item. The loading correlation is supporting\n",
    "only (independent sample, adolescents). Nothing here bears on the rights block.\n", sep = "")

ok <- length(observed) == 8 && all(observed == PREDICTED)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
