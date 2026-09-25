# verify_SABFI2_Gallardo_Pujol_2018_Trust.R -- Step 5b re-runnable check (batch_404)
#
# CLAIM. The live codes Trust1..Trust5 are the five items of the General Trust Scale
# (Yamagishi et al., 2015) in the order the International Situations Project (ISP) survey
# displayed them (ISP 'Spanish ISP.pdf', osf.io/download/3vche, pp. 29-30, question 11;
# 'English ISP.pdf', osf.io/download/wft8k, p. 23; same order in the ISP translation file
# 'Trustworthiness Scale (Spanish).docx', osf.io/download/96tc3):
#   1 basically honest, 2 good-natured and kind, 3 most people TRUST OTHERS,
#   4 GENERALLY, I TRUST OTHERS (the only first-person item), 5 most people are trustworthy.
# Stored raw, 1 = "Totalmente en desacuerdo" (Disagree strongly) ... 5 = "Totalmente de acuerdo".
#
# DATA. The study's own Study 3 file on OSF kp572 ('Data/Study 3/Study 3 data.csv',
# osf.io/download/r2zhc), which data/SABFI2_Gallardo_Pujol_2018.R melts with names kept
# (select(starts_with("Trust")) + pivot_longer). Used instead of irw_fetch() to stay off the
# Redivis export cap; step (0) ties it to the live table by per-item n and mean, hard-coded
# from item_stats.R 2026-09-24. The paper publishes no trust statistics at all.
#
# ROUTE. 8 (semantic coherence of the correlation/level pattern), plus the same-export
# direction check and display-order corroboration used for the Tight sibling (batch_166).

csv <- file.path(tempdir(), "sabfi2_study3.csv")
if (!file.exists(csv)) download.file("https://osf.io/download/r2zhc/", csv, quiet = TRUE, mode = "wb")
d <- read.csv(csv)
X <- d[, paste0("Trust", 1:5)]
ok <- TRUE

# (0) the OSF file is the live table
LIVE_N    <- rep(419, 5)
LIVE_MEAN <- c(2.71, 3.25, 2.91, 3.43, 2.81)
obs_n <- colSums(!is.na(X)); obs_m <- colMeans(X, na.rm = TRUE)
cat("(0) OSF Study 3 file vs live item_stats.R\n")
for (i in 1:5) cat(sprintf("  %-7s live n=%d osf n=%d   live mean %.2f  osf mean %.4f\n",
                           names(X)[i], LIVE_N[i], obs_n[i], LIVE_MEAN[i], obs_m[i]))
if (any(obs_n != LIVE_N) || any(abs(obs_m - LIVE_MEAN) > 0.006)) { cat("  -> OSF file does NOT reproduce live table\n"); ok <- FALSE }

# (A) content predictions from the claimed wording
R <- cor(X); up <- which(upper.tri(R), arr.ind = TRUE)
pairs <- data.frame(a = rownames(R)[up[, 1]], b = colnames(R)[up[, 2]], r = R[up])
pairs <- pairs[order(-pairs$r), ]
mr <- sapply(1:5, function(k) mean(R[k, -k]))
ceil <- colMeans(X == 5) * 100
cat("\n(A) inter-item correlations:\n"); print(round(R, 3))
cat("  pairs, strongest first:\n"); for (i in seq_len(nrow(pairs))) cat(sprintf("    %s-%s  %.3f\n", pairs$a[i], pairs$b[i], pairs$r[i]))
for (k in 1:5) cat(sprintf("  Trust%d  mean r with others %.3f   mean %.3f   %% at 5 = %.1f\n", k, mr[k], obs_m[k], ceil[k]))
# P1: the only first-person item ('Generally, I trust others') is the most endorsed and the
#     only one with a non-trivial ceiling (self-description vs belief about 'most people').
if (which.max(obs_m) != 4 || which.max(ceil) != 4) { cat("  -> P1 fails: Trust4 is not the most endorsed item\n"); ok <- FALSE }
# P2: 'Most people trust others' is the only item about other people's TRUSTING rather than
#     their trustworthiness or my own trust, so it should be the weakest-linked item.
if (which.min(mr) != 3) { cat("  -> P2 fails: Trust3 is not the weakest-linked item\n"); ok <- FALSE }
# P3: 'honest' and 'good-natured and kind' (both statements about others' character) form the
#     strongest pair.
if (!(setequal(c(pairs$a[1], pairs$b[1]), c("Trust1", "Trust2")))) { cat("  -> P3 fails: Trust1-Trust2 is not the strongest pair\n"); ok <- FALSE }
cat("  -> P1 Trust4 most endorsed, P2 Trust3 weakest-linked, P3 Trust1-Trust2 strongest pair.\n")

# (B) direction of the stored 1-5 coding, from the same survey export: the IHS uses the same
# ISP five-point format, is all positively keyed, and the postprint's Table 6 publishes
# M 3.49 SD 0.54.
s <- rowMeans(d[, paste0("IntHapp", 1:9)])
cat(sprintf("\n(B) IHS as stored: M %.3f SD %.3f (published 3.49 / 0.54); reversed reading M %.3f\n", mean(s), sd(s), 6 - mean(s)))
if (abs(mean(s) - 3.49) > 0.01 || abs(sd(s) - 0.54) > 0.01) { cat("  -> IHS direction check misses\n"); ok <- FALSE }

# (C) corroboration only (not in the verdict): the export keeps survey display order for
# sibling scales whose authors' scoring keys follow the ISP website order.
chk <- function(cols, keys, label) {
  Rs <- cor(d[, cols], use = "pairwise"); p <- outer(keys, keys); u <- upper.tri(Rs)
  cat(sprintf("  %-12s %d/%d inter-item correlations carry the key-predicted sign\n", label, sum(sign(Rs[u]) == p[u]), sum(u)))
}
cat("\n(C) display-order corroboration from sibling scales in the same export\n")
chk(paste0("Constru", 1:4),  c(-1, 1, 1, -1),     "SelfExp")
chk(paste0("Constru", 5:9),  c(1, -1, -1, 1, -1), "SelfInt")
chk(paste0("Constru", 10:13), c(-1, -1, 1, 1),    "Consistency")
chk(paste0("LOT", 1:6),      c(1, -1, 1, -1, -1, 1), "LOT")

cat("\nNOT ESTABLISHED: the predictions in (A) are post-hoc content readings, not published\n",
    "statistics. They single out Trust4 (level) and Trust3 (weakest link) and pair Trust1 with\n",
    "Trust2, but nothing separates Trust1 from Trust2 (honest vs good-natured) or pins Trust5\n",
    "beyond elimination. All five items are positively worded and share one scale; no source\n",
    "publishes per-item trust statistics. The rest rests on the export keeping display order,\n",
    "which (C) supports for sibling scales but does not test for this one. PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
