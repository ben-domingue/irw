# verify_perceived_injustice_mourin.R -- Step 5b mapping check (batch_706).
#
# Claim: live codes in_k are the study's .sav columns In_k = DRAFT item k of the 19-item
# first draft, and the 10 retained items published in S1/S2 File (final 1..10) are
# in_1, in_2, in_3, in_9, in_10, in_13, in_14, in_16, in_18, in_19 in that order.
#
# What this establishes:
#   (a) live in_k == .sav In_k (per-item means and n, all 19 items);
#   (b) the draft numbering: the paper's own statement that draft item 10 has r>=.8
#       (rounded to 1 dp) with items 4,5,6,7,8,11,12 and item 16 with 15 & 17;
#   (c) the retained SET: the shipped 10 reproduce every published statistic of the final
#       scale to 3 dp (alpha .931, corrected item-total range .543-.841, 61.95% variance,
#       r with Steel .428, experience .426, rating .441, PSS-10 .332, WHO-5 -.361), and are
#       the ONLY one of the 92,378 10-item subsets of 19 that does so;
#   (d) the format block: final items 9-10 use Never..Always anchors, final 1-8 use
#       intensity anchors; in_18 and in_19 have by far the lowest ceiling % of all 19.
# What this does NOT establish: the order of the 8 intensity items among final
# positions 1-8, or in_18 vs in_19 for final 9 vs 10. Those rest on the assumption that
# the final form kept draft order (ascending). No per-item statistic is published.
suppressMessages({library(irw); library(haven)})
TABLE <- "perceived_injustice_mourin"
SHIP  <- c(1, 2, 3, 9, 10, 13, 14, 16, 18, 19)

tmp <- tempfile(fileext = ".sav")
download.file("https://osf.io/download/37ren/", tmp, mode = "wb", quiet = TRUE)
d <- zap_labels(read_sav(tmp))
X <- as.matrix(d[, paste0("In_", 1:19)])

ok <- TRUE
# (a) live codes == .sav columns
live <- irw::irw_fetch(TABLE)
lm <- tapply(live$resp, live$item, mean, na.rm = TRUE)[paste0("in_", 1:19)]
ln <- tapply(!is.na(live$resp), live$item, sum)[paste0("in_", 1:19)]
sm <- colMeans(X, na.rm = TRUE); sn <- colSums(!is.na(X))
cat("(a) live vs .sav per-item mean (n):\n")
for (k in 1:19) cat(sprintf("  in_%-2d live %.4f (%d)  sav %.4f (%d)\n", k, lm[k], ln[k], sm[k], sn[k]))
a <- max(abs(lm - sm)) < 1e-9 && all(ln == sn)
cat("  max |diff| =", max(abs(lm - sm)), "->", a, "\n"); ok <- ok && a

# (b) draft numbering from the paper's correlation statement
R <- cor(X, use = "pairwise")
hi <- function(i) which(round(R[i, ], 1) >= 0.8 & seq_len(19) != i)
cat("(b) round(r,1)>=.8 with item 10:", hi(10), "(paper: 4 5 6 7 8 11 12)\n")
cat("    round(r,1)>=.8 with item 16:", hi(16), "(paper: 15 17)\n")
b <- identical(as.integer(hi(10)), c(4L,5L,6L,7L,8L,11L,12L)) && all(c(15, 17) %in% hi(16))
ok <- ok && b

# (c) retained set
Xc <- X[complete.cases(X), ]
alpha <- function(M) { k <- ncol(M); k/(k-1) * (1 - sum(apply(M, 2, var)) / var(rowSums(M))) }
citc <- function(M) sapply(seq_len(ncol(M)), function(j) cor(M[, j], rowSums(M[, -j])))
stats <- function(s) {
  M <- Xc[, s]; t <- rowSums(X[, s])
  c(alpha = alpha(M), citc_min = min(citc(M)), citc_max = max(citc(M)),
    var1 = eigen(cor(M))$values[1] / 10,
    steel = cor(t, d$Total_Steel_Inv, use = "c"), exper = cor(t, d$Injustice, use = "c"),
    rating = cor(t, d$Rating, use = "c"), pss = cor(t, d$Total_PSS10, use = "c"),
    who5 = cor(t, d$Total_WHO_5, use = "c"))
}
PUB <- c(alpha = .931, citc_min = .543, citc_max = .841, var1 = .6195, steel = .428,
         exper = .426, rating = .441, pss = .332, who5 = -.361)
got <- stats(SHIP)
cat("(c) 19-item alpha", sprintf("%.4f", alpha(Xc)), "(paper .971)\n")
cat(sprintf("    %-9s %9s %9s\n", "stat", "published", "observed"))
for (n in names(PUB)) cat(sprintf("    %-9s %9.4f %9.4f\n", n, PUB[n], got[n]))
dig <- ifelse(names(PUB) == "var1", 4, 3)
c1 <- all(round(got, dig) == PUB)
C <- cov(Xc); cmb <- combn(19, 10)
al <- apply(cmb, 2, function(s) { v <- C[s, s]; 10/9 * (1 - sum(diag(v)) / sum(v)) })
cand <- which(round(al, 3) == .931)
full <- Filter(function(k) all(round(stats(cmb[, k]), dig) == PUB), cand)
cat("    subsets of 19 choose 10 =", ncol(cmb), "; alpha rounds to .931:", length(cand),
    "; reproduce all 9 statistics:", length(full), "->", sapply(full, function(k) paste(cmb[, k], collapse = ",")), "\n")
c2 <- length(full) == 1 && identical(as.numeric(cmb[, full[[1]]]), SHIP)
ok <- ok && c1 && c2

# (d) format block
ceil <- colMeans(X == 4, na.rm = TRUE) * 100
cat("(d) ceiling % by item:", paste0(1:19, ":", sprintf("%.1f", ceil)), "\n")
low2 <- sort(order(ceil)[1:2])
cat("    two lowest-ceiling items:", low2, "(expected 18 19 = frequency-anchored final 9, 10)\n")
dd <- identical(as.integer(low2), c(18L, 19L)); ok <- ok && dd

cat("NOT established: order among final 1-8 (in_1,2,3,9,10,13,14,16) and in_18 vs in_19;",
    "these assume the final form kept draft order.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
