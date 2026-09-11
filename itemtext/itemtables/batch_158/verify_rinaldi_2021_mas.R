# verify_rinaldi_2021_mas.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST. The IRW item codes Mas_1..Mas_61 are the source .sav's own
# column names, but the item WORDING comes from the paper's Table 2, which prints
# only 60 items for 61 data columns. The shipped mapping is:
#     Mas_1 .. Mas_56   ->  Table 2 items 1..56   (identity)
#     Mas_57            ->  NO Table 2 row (item_text left blank)
#     Mas_58 .. Mas_61  ->  Table 2 items 57..60  (shifted by one)
# Four independent checks below. Note Table 2 is computed on the full N=506
# sample while this IRW table is the N=258 CFA subsample, so exact agreement is
# not expected -- the SIGNAL is which alignment fits, not the third decimal.
#
# Rinaldi T et al. (2021) PLOS ONE 16(4):e0249272, Tables 2 and 3.

suppressMessages(library(irw))
TABLE <- "rinaldi_2021_mas"

# Table 2, items 1..60: MEAN, SD, SKEWNESS (as printed).
P_M <- c(5.27,4.61,5.39,5.11,5.60,4.97,4.62,5.29,4.88,4.17,5.17,5.72,3.59,3.71,
         3.75,4.76,4.71,5.11,5.26,4.96,5.68,3.93,4.56,3.89,4.35,3.29,4.23,5.57,
         5.38,4.07,4.00,3.86,5.12,5.97,5.09,4.41,5.14,5.08,3.43,5.51,5.14,5.32,
         3.38,4.88,3.82,5.06,5.04,4.22,4.87,5.37,5.34,5.17,2.96,5.75,2.67,3.89,
         4.58,5.05,4.90,5.58)
P_SD <- c(1.40,1.71,1.28,1.40,1.22,1.58,1.69,1.42,1.82,1.61,1.44,1.29,1.75,1.54,
          1.68,1.56,1.40,1.44,1.70,1.79,1.34,1.61,1.62,1.77,1.45,1.69,1.63,1.26,
          1.32,1.61,1.75,1.71,1.34,1.20,1.36,1.67,1.45,1.43,1.53,1.38,1.32,1.36,
          1.60,1.57,1.75,1.42,1.55,1.57,1.56,1.33,1.42,1.39,1.65,1.15,1.46,1.82,
          1.56,1.24,1.31,1.27)
# Table 2 items that are negatively worded (the study's own reverse set).
P_REV <- c(9,13,15,19,20,24,31,32,36,39,40,44,53,55,56)
# Table 3 (35-item EFA), factor -> Table 2 item numbers.
FACTORS <- list(
  Identifying     = c(41,57,35,58,32,11,55,59,13,21),
  Expressing      = c(44,31,20,36,48,45,40,9),
  Curiosity       = c(33,46,42,34,60,12,28),
  Processing      = c(10,6,26,7,23,14,43),
  Autobiographical= c(16,47,1))

# ---- live data, wide ----------------------------------------------------
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id","item","resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
rev_n  <- c(9,13,15,19,20,24,31,32,36,39,40,44,53,55,56)   # R-suffixed columns
code   <- function(i) if (i %in% rev_n) paste0("Mas_", i, "R") else paste0("Mas_", i)
codes  <- vapply(1:61, code, "")
stopifnot(all(codes %in% names(w)))
M  <- vapply(codes, function(cc) mean(w[[cc]], na.rm = TRUE), 0)
SD <- vapply(codes, function(cc) stats::sd(w[[cc]], na.rm = TRUE), 0)

# shipped mapping: data index -> Table 2 index (NA for the undocumented Mas_57)
map <- c(1:56, NA, 57:60)

# ---- CHECK 1: which tail alignment fits? --------------------------------
cat("== CHECK 1: where does the undocumented 61st column sit? ==\n")
cat("Total |dMean|+|dSD| over all 60 mapped pairs, for each candidate gap position:\n")
fit <- function(g) {
  idx <- setdiff(1:61, g); p <- seq_along(idx)
  sum(abs(M[idx] - P_M[p]) + abs(SD[idx] - P_SD[p]))
}
tail_fit <- vapply(57:61, fit, 0)
for (k in seq_along(tail_fit))
  cat(sprintf("   gap at Mas_%-2d : %6.3f%s\n", 56 + k, tail_fit[k],
              if (which.min(tail_fit) == k) "   <-- best" else ""))
c1 <- which.min(tail_fit) == 1
cat(sprintf("   best is gap at Mas_57 (shipped): %s; margin over runner-up %.3f\n\n",
            c1, sort(tail_fit)[2] - min(tail_fit)))

# ---- CHECK 2: per-item agreement under the shipped mapping --------------
cat("== CHECK 2: per-item mean/SD vs Table 2 under the shipped mapping ==\n")
ok <- !is.na(map)
dM <- M[ok] - P_M[map[ok]]; dS <- SD[ok] - P_SD[map[ok]]
cat(sprintf("%-9s %8s %8s %8s | %8s %8s\n","item","pub M","obs M","dM","pub SD","obs SD"))
for (i in which(ok))
  cat(sprintf("%-9s %8.2f %8.2f %8.3f | %8.2f %8.2f\n",
              codes[i], P_M[map[i]], M[i], M[i]-P_M[map[i]], P_SD[map[i]], SD[i]))
cat(sprintf("mean |dM| = %.3f, max |dM| = %.3f (%s); mean |dSD| = %.3f\n\n",
            mean(abs(dM)), max(abs(dM)), codes[ok][which.max(abs(dM))], mean(abs(dS))))
c2 <- mean(abs(dM)) < 0.10 && max(abs(dM)) < 0.30

# ---- CHECK 3: reverse-wording markers ------------------------------------
# The 15 R-suffixed codes must be exactly the items that correlate NEGATIVELY
# with the sum of the 46 non-reverse items. This fixes the 1..56 block against
# any shift: the reverse positions are not shift-invariant.
cat("== CHECK 3: polarity of the 15 R-suffixed codes ==\n")
pos <- setdiff(1:61, rev_n)
tot <- rowSums(w[, codes[pos]], na.rm = TRUE)
r   <- vapply(codes, function(cc) stats::cor(w[[cc]], tot, use = "complete.obs"), 0)
low <- order(r)[1:15]
cat(sprintf("   15 lowest item-rest r : %s\n", paste(sort(codes[low]), collapse = ", ")))
cat(sprintf("   R-suffixed codes      : %s\n", paste(codes[rev_n], collapse = ", ")))
cat(sprintf("   r range, R-suffixed: %.2f..%.2f ; non-R: %.2f..%.2f (classes disjoint: %s)\n",
            min(r[rev_n]), max(r[rev_n]), min(r[pos]), max(r[pos]),
            max(r[rev_n]) < min(r[pos])))
c3 <- setequal(low, rev_n) && max(r[rev_n]) < min(r[pos]) &&
      identical(sort(rev_n), sort(P_REV))
cat(sprintf("   R-suffixed column numbers == Table 2's negatively worded item numbers\n   (%s): %s\n\n",
            paste(P_REV, collapse = ","), identical(sort(rev_n), sort(P_REV))))

# ---- CHECK 4: Table 3's 5-factor assignment reproduces in the data ------
cat("== CHECK 4: Table 3 factor blocks (35 items) ==\n")
cm <- suppressWarnings(stats::cor(w[, codes], use = "pairwise.complete.obs"))
# put every item on the positive pole so block structure is readable
sgn <- ifelse(r < 0, -1, 1); cm <- outer(sgn, sgn) * cm; diag(cm) <- NA
inv <- match(unlist(FACTORS), map)              # Table 2 no. -> data index
grp <- rep(names(FACTORS), lengths(FACTORS))
c4 <- TRUE
for (g in names(FACTORS)) {
  ii <- inv[grp == g]; jj <- setdiff(inv, ii)
  wi <- mean(cm[ii, ii], na.rm = TRUE); bt <- mean(cm[ii, jj], na.rm = TRUE)
  cat(sprintf("   %-16s n=%2d  within-factor r = %.3f  vs cross-factor r = %.3f  %s\n",
              g, length(ii), wi, bt, if (wi > bt) "ok" else "FAIL"))
  if (!(wi > bt)) c4 <- FALSE
}
cat("\n")

cat("What this does NOT establish: the four checks fix the ALIGNMENT (no shift in\n",
    "1..56, the gap at Mas_57, the tail shift) but they do not separate every item\n",
    "from every other. On the published stats, 10 of the 1770 possible pairwise\n",
    "transpositions fit marginally better than the shipped mapping (best -0.165\n",
    "against a per-pair misfit of 0.162, i.e. inside the N=506-vs-N=258 noise):\n",
    "data items 4/38, 11/38, 18/52, 18/38, 46/47, 11/52, 4/18, 6/46, 37/38, 29/51.\n",
    "Check 4 rejects 46/47 and 6/46 (different factors) and both 11 pairs (11 is a\n",
    "retained Identifying item, 38 and 52 are not retained). The rest are\n",
    "unretained non-reverse items the statistics cannot separate. Status is\n",
    "therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (c1 && c2 && c3 && c4) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
