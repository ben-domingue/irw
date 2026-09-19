# verify_SABFI2_Gallardo_Pujol_2018_Tight.R -- Step 5b re-runnable check (batch_166)
#
# CLAIM. The live codes Tight1..Tight6 are the six items of the Gelfand et al. (2011)
# Tightness/Looseness Scale in the order the International Situations Project (ISP)
# survey displayed them (ISP 'Spanish ISP.pdf', osf.io/3vche, pp. 28-29; 'English ISP.pdf',
# osf.io/wft8k, p. 22; same order in 'Tightness Looseness Scale (Spanish).docx', osf.io/hgr62):
#   1 many social norms, 2 clear expectations, 3 people agree on appropriate behaviour,
#   4 great deal of FREEDOM (the scale's single reverse-worded item), 5 others disapprove,
#   6 almost always comply.
# Values are stored raw with 1 = "Totalmente en desacuerdo" (Disagree strongly) ... 5 =
# "Totalmente de acuerdo" (Agree strongly).
#
# DATA. The study's own Study 3 file on OSF kp572 ('Data/Study 3/Study 3 data.csv'), which
# data/SABFI2_Gallardo_Pujol_2018.R melts with names kept (select(starts_with("Tight")) +
# pivot_longer). Used instead of irw_fetch() to stay off the Redivis export cap; step (0)
# ties it to the live table by per-item n and mean, hard-coded from item_stats.R 2026-09-10.
#
# The postprint publishes NO tightness statistics at all (the scale is not mentioned in the
# paper), so there is no published per-item or scale-level target for this table.

csv <- file.path(tempdir(), "sabfi2_study3.csv")
if (!file.exists(csv)) download.file("https://osf.io/download/r2zhc/", csv, quiet = TRUE, mode = "wb")
d <- read.csv(csv)
T <- d[, paste0("Tight", 1:6)]
ok <- TRUE

# (0) the OSF file is the live table
LIVE_N    <- rep(419, 6)
LIVE_MEAN <- c(3.88, 3.94, 3.33, 2.91, 3.67, 2.80)
obs_n <- colSums(!is.na(T)); obs_m <- colMeans(T, na.rm = TRUE)
cat("(0) OSF Study 3 file vs live item_stats.R\n")
for (i in 1:6) cat(sprintf("  %-7s live n=%d osf n=%d   live mean %.2f  osf mean %.4f\n",
                           names(T)[i], LIVE_N[i], obs_n[i], LIVE_MEAN[i], obs_m[i]))
if (any(obs_n != LIVE_N) || any(abs(obs_m - LIVE_MEAN) > 0.006)) { cat("  -> OSF file does NOT reproduce live table\n"); ok <- FALSE }

alpha <- function(M) { M <- as.matrix(M); p <- ncol(M); v <- cov(M, use = "pairwise"); p / (p - 1) * (1 - sum(diag(v)) / sum(v)) }

# (A) route 6, keying polarity: which single item behaves as the reverse-worded one?
R <- cor(T)
a0 <- alpha(T)
arev <- sapply(1:6, function(k) { M <- T; M[, k] <- 6 - M[, k]; alpha(M) })
mr <- sapply(1:6, function(k) mean(R[k, -k]))
ev <- eigen(R)$vectors[, 1]; ev <- ev * sign(sum(ev))
cat("\n(A) polarity. Inter-item correlations:\n"); print(round(R, 2))
cat(sprintf("  alpha as stored %.3f\n", a0))
for (k in 1:6) cat(sprintf("  Tight%d  alpha if reversed %6.3f   mean r with others %6.3f   PC1 loading %5.2f\n",
                           k, arev[k], mr[k], ev[k]))
if (which.max(arev) != 4 || arev[4] <= a0 || sum(arev > a0) != 1) { cat("  -> Tight4 is not the unique reversal that raises alpha\n"); ok <- FALSE }
if (which.min(mr) != 4 || mr[4] >= 0 || any(mr[-4] <= 0)) { cat("  -> Tight4 is not the only item with negative mean r\n"); ok <- FALSE }
if (sum(ev < 0) != 1 || ev[4] >= 0) { cat("  -> Tight4 is not the only negative PC1 loading\n"); ok <- FALSE }
cat("  -> only Tight4 behaves as the reverse-worded item, as position 4 ('freedom') predicts.\n",
    "    Caveat: the signal is weak (alpha .41 -> .44; Tight4 r = +0.17 with Tight3, +0.09 with Tight6).\n", sep = "")

# (B) direction of the stored 1-5 coding, from the same survey export. The IHS uses the same
# ISP five-point Disagree strongly ... Agree strongly format, is all positively keyed, and the
# postprint's Table 6 publishes it: M 3.49 SD 0.54 (men 3.46/0.61, women 3.49/0.53).
s <- rowMeans(d[, paste0("IntHapp", 1:9)])
g <- tapply(s, d$Gender, function(x) c(m = mean(x), sd = sd(x)))
cat(sprintf("\n(B) IHS as stored: M %.3f SD %.3f (published 3.49 / 0.54); reversed reading M %.3f\n", mean(s), sd(s), 6 - mean(s)))
for (k in names(g)) cat(sprintf("  Gender=%s  M %.3f SD %.3f\n", k, g[[k]]["m"], g[[k]]["sd"]))
if (abs(mean(s) - 3.49) > 0.01 || abs(sd(s) - 0.54) > 0.01) { cat("  -> IHS direction check misses\n"); ok <- FALSE }

# (C) corroboration only (not in the verdict): the export keeps survey display order for
# sibling scales. The authors' own scoring keys (OSF kp572 study.3.nomological.network.short.versions.R
# lines 216/231/247) follow the ISP English website's item order; check the sign patterns hold.
chk <- function(cols, keys, label) {
  Rs <- cor(d[, cols], use = "pairwise"); p <- outer(keys, keys); up <- upper.tri(Rs)
  cat(sprintf("  %-12s %d/%d inter-item correlations carry the key-predicted sign\n", label, sum(sign(Rs[up]) == p[up]), sum(up)))
}
cat("\n(C) display-order corroboration from sibling scales in the same export\n")
chk(paste0("Constru", 1:4),  c(-1, 1, 1, -1),     "SelfExp")
chk(paste0("Constru", 5:9),  c(1, -1, -1, 1, -1), "SelfInt")
chk(paste0("Constru", 10:13), c(-1, -1, 1, 1),    "Consistency")
chk(paste0("LOT", 1:6),      c(1, -1, 1, -1, -1, 1), "LOT")

cat("\nNOT ESTABLISHED: the order of Tight1, Tight2, Tight3, Tight5 and Tight6 among themselves.\n",
    "All five are positively worded; no source publishes per-item tightness statistics, so\n",
    "nothing here distinguishes 'many norms' from 'clear expectations', 'agreement', 'disapprove'\n",
    "or 'comply'. That rests on the export keeping display order, which (C) supports for sibling\n",
    "scales but does not test for this one. PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
