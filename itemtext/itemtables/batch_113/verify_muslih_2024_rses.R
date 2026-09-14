# verify_muslih_2024_rses.R
#
# CLAIM UNDER TEST: the wording shipped for item code RSESk is the wording the
# paper's Table 2 prints on the row labelled "RSES k" (Muslih & Chung 2024,
# PLOS ONE 19(5) e0300184, t002). That table prints, alongside each item's
# words, the item's mean, SD and its correlation with every other item -- so if
# item_text for any two items had been swapped, the live per-item statistics
# would land on the wrong published row and the 45-cell correlation matrix
# would stop matching.
#
# Table 2's correlations are computed on the RAW (not reverse-scored) responses
# -- r(1,2) = -0.11 -- which is the same coding the live IRW table stores, so
# the comparison is direct.

suppressMessages(library(irw))
TABLE <- "muslih_2024_rses"

# --- published values, hard-coded from Table 2 (t002 PNG) ---
PUB_MEAN <- c(2.05, 2.39, 1.92, 1.98, 2.32, 2.30, 2.02, 2.57, 2.31, 1.97)
PUB_SD   <- c(0.94, 0.86, 0.81, 0.84, 0.86, 0.91, 0.83, 0.87, 0.83, 0.86)
PUB_R <- matrix(NA_real_, 10, 10)
PUB_R[2, 1]  <- -0.11
PUB_R[3, 1:2] <- c(0.56, -0.12)
PUB_R[4, 1:3] <- c(0.51, -0.04, 0.63)
PUB_R[5, 1:4] <- c(-0.03, 0.48, -0.13, -0.11)
PUB_R[6, 1:5] <- c(-0.00, 0.62, -0.04, -0.01, 0.48)
PUB_R[7, 1:6] <- c(0.52, -0.01, 0.64, 0.86, -0.07, 0.06)
PUB_R[8, 1:7] <- c(-0.19, 0.71, -0.22, -0.15, 0.43, 0.50, -0.15)
PUB_R[9, 1:8] <- c(-0.10, 0.85, -0.13, -0.09, 0.56, 0.63, -0.05, 0.71)
PUB_R[10, 1:9] <- c(0.55, 0.01, 0.58, 0.63, -0.01, -0.03, 0.64, -0.08, -0.04)

TOL_M <- 0.015   # published to 2dp
TOL_R <- 0.015

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, paste0("RSES", 1:10)]

obs_m <- sapply(w, mean, na.rm = TRUE)
obs_s <- sapply(w, sd,   na.rm = TRUE)
obs_r <- cor(w, use = "pairwise.complete.obs")

cat(sprintf("%-8s %9s %9s %9s %9s\n", "item", "pub.mean", "obs.mean", "pub.SD", "obs.SD"))
for (i in 1:10)
    cat(sprintf("RSES%-4d %9.2f %9.2f %9.2f %9.2f\n",
                i, PUB_MEAN[i], obs_m[i], PUB_SD[i], obs_s[i]))

cat("\nInter-item correlations, published vs observed (lower triangle, 45 cells):\n")
bad_r <- 0
for (i in 2:10) for (j in 1:(i - 1)) {
    dv <- obs_r[i, j] - PUB_R[i, j]
    flag <- if (abs(dv) > TOL_R) " <-- MISMATCH" else ""
    if (abs(dv) > TOL_R) bad_r <- bad_r + 1
    cat(sprintf("  r(%2d,%2d)  pub %6.2f  obs %6.2f  diff %6.3f%s\n",
                i, j, PUB_R[i, j], obs_r[i, j], dv, flag))
}

bad_m <- sum(abs(obs_m - PUB_MEAN) > TOL_M)
cat(sprintf("\nmeans off by >%.3f: %d/10   largest |diff| = %.3f\n",
            TOL_M, bad_m, max(abs(obs_m - PUB_MEAN))))
cat(sprintf("correlations off by >%.3f: %d/45\n", TOL_R, bad_r))

cat("\nWhat this establishes: each item code's own correlation profile against the\n",
    "other nine is a unique fingerprint, so every item is distinguished from every\n",
    "other -- a swap of any two item_texts would misalign at least 8 cells each.\n",
    "What it does NOT establish: that the English shipped here is what Indonesian\n",
    "respondents read; the administered Indonesian wording is published nowhere in\n",
    "the paper or the S1 deposit (see provenance, text_source=translated_substitute).\n", sep = "")

if (bad_m == 0 && bad_r == 0) cat("\nVERDICT: PASS\n") else cat("\nVERDICT: FAIL\n")
