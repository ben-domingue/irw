# verify_SABFI2_Gallardo_Pujol_2018_LOT.R -- Step 5b re-runnable check (batch_165)
#
# CLAIM. The live codes LOT1..LOT6 are the six scored LOT-R items in canonical order
# (LOT-R items 1, 3, 4, 7, 9, 10), so {LOT1, LOT3, LOT6} are the OPTIMISM items
# (LOT-R 1, 4, 10) and {LOT2, LOT4, LOT5} the PESSIMISM items (LOT-R 3, 7, 9);
# the values are stored RAW (pessimism not pre-reversed) with high = agree, so
# resp 1 = "strongly disagree" ... 5 = "strongly agree" on every item.
#
# DATA. The study's own Study 3 file on OSF kp572 (CC BY 4.0), which
# data/SABFI2_Gallardo_Pujol_2018.R melts without renaming or recoding
# (select(starts_with("LOT")) + pivot_longer). Used instead of irw_fetch() to keep
# this check off the 200GB/30-day Redivis export cap; step (0) ties it to the live
# table by per-item n and mean, hard-coded from item_stats.R run 2026-09-10.
#
# PUBLISHED. Gallardo-Pujol et al. (2022) postprint (OSF kp572
# Spanish_BFI-2_Final_Postprint.pdf), descriptives table, row "LOT / Optimism":
# men 3.22 (0.9), women 3.35 (0.81), total 3.33 (0.83), alpha .88; N = 62 / 357 / 419.
# The study's own script (OSF kp572 Scripts/study.3.nomological.network.short.versions.R,
# line 264) scores it with keysLOT <- c(1,-1,1,-1,-1,1).

csv <- file.path(tempdir(), "sabfi2_study3.csv")
if (!file.exists(csv)) download.file("https://osf.io/download/r2zhc/", csv, quiet = TRUE, mode = "wb")
d <- read.csv(csv)
L <- d[, paste0("LOT", 1:6)]
ok <- TRUE

# (0) the OSF file is the live table
LIVE_N    <- rep(419, 6)
LIVE_MEAN <- c(3.03, 2.83, 3.22, 2.44, 2.55, 3.56)
obs_n <- colSums(!is.na(L)); obs_m <- colMeans(L, na.rm = TRUE)
cat("(0) OSF Study 3 file vs live item_stats.R\n")
for (i in 1:6) cat(sprintf("  %-5s live n=%d osf n=%d   live mean %.2f  osf mean %.4f\n", names(L)[i], LIVE_N[i], obs_n[i], LIVE_MEAN[i], obs_m[i]))
if (any(obs_n != LIVE_N) || any(abs(obs_m - LIVE_MEAN) > 0.006)) { cat("  -> OSF file does NOT reproduce live table\n"); ok <- FALSE }

alpha <- function(M) { M <- as.matrix(M); p <- ncol(M); v <- cov(M, use = "pairwise"); p / (p - 1) * (1 - sum(diag(v)) / sum(v)) }
score <- function(opt) { M <- L; pes <- setdiff(1:6, opt); M[, pes] <- 6 - L[, pes]; M }

# (1) which optimism triple reproduces the published scale? all 20 choices
PUB_M <- 3.33; PUB_SD <- 0.83; PUB_A <- 0.88
cmb <- combn(6, 3)
res <- t(apply(cmb, 2, function(o) { M <- score(o); s <- rowMeans(M)
  c(mean = mean(s), sd = sd(s), alpha = alpha(M)) }))
res <- data.frame(optimism = apply(cmb, 2, function(o) paste0("LOT", o, collapse = "+")), round(res, 3))
res$dist <- round(abs(res$mean - PUB_M) + abs(res$sd - PUB_SD) + abs(res$alpha - PUB_A), 3)
res <- res[order(res$dist), ]
cat("\n(1) all 20 optimism/pessimism assignments vs published M 3.33 / SD 0.83 / alpha .88\n")
for (i in seq_len(nrow(res))) cat(sprintf("  %-16s M %.3f  SD %.3f  alpha %6.3f  dist %.3f\n", res$optimism[i], res$mean[i], res$sd[i], res$alpha[i], res$dist[i]))
if (res$optimism[1] != "LOT1+LOT3+LOT6" || res$dist[1] > 0.02 || res$dist[2] < 0.3) {
  cat("  -> {LOT1,LOT3,LOT6} is not the unique match\n"); ok <- FALSE }
cat("  note: the mirror assignment LOT2+LOT4+LOT5 gives alpha", res$alpha[res$optimism == "LOT2+LOT4+LOT5"],
    "but mean", res$mean[res$optimism == "LOT2+LOT4+LOT5"], "-- that is the DIRECTION check: it is the\n",
    "  reading in which high resp = disagree, and it misses the published 3.33.\n")

# (2) gender subgroups, keyed as claimed
s <- rowMeans(score(c(1, 3, 6)))
g <- tapply(s, d$Gender, function(x) c(n = length(x), m = mean(x), sd = sd(x)))
cat("\n(2) subgroups (published men 3.22/0.90 n=62, women 3.35/0.81 n=357)\n")
for (k in names(g)) cat(sprintf("  Gender=%s  n=%d  M=%.3f  SD=%.3f\n", k, g[[k]]["n"], g[[k]]["m"], g[[k]]["sd"]))
gm <- g[[which(sapply(g, `[`, "n") == 62)]]; gw <- g[[which(sapply(g, `[`, "n") == 357)]]
if (abs(gm["m"] - 3.22) > 0.03 || abs(gw["m"] - 3.35) > 0.01) { cat("  -> subgroup means miss\n"); ok <- FALSE }

# (3) raw polarity: sign of every inter-item correlation
R <- cor(L); cls <- c(1, -1, 1, -1, -1, 1)
cat("\n(3) inter-item correlations (predicted sign = + within class, - across)\n"); print(round(R, 2))
pred <- outer(cls, cls); up <- upper.tri(R)
nmatch <- sum(sign(R[up]) == pred[up])
cat(sprintf("  %d/15 correlations carry the predicted sign; within-class r %.2f..%.2f, cross-class r %.2f..%.2f\n",
    nmatch, min(R[up][pred[up] > 0]), max(R[up][pred[up] > 0]), min(R[up][pred[up] < 0]), max(R[up][pred[up] < 0])))
if (nmatch != 15) ok <- FALSE

cat("\nNOT ESTABLISHED: order WITHIN each polarity class. Nothing here separates LOT1/LOT3/LOT6\n",
    "(LOT-R 1 'uncertain times', 4 'optimistic about my future', 10 'more good things') from one\n",
    "another, nor LOT2/LOT4/LOT5 (LOT-R 3, 7, 9); that rests on the deposit keeping canonical order,\n",
    "which the study's key c(1,-1,1,-1,-1,1) is consistent with but does not prove. PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
