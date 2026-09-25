# verify_SABFI2_Gallardo_Pujol_2018_Constru.R -- Step 5b re-runnable check (batch_404)
#
# CLAIM. The live codes Constru1..Constru13 are the 13 self-construal items (Vignoles et al.
# 2016) in the order the International Situations Project (ISP) survey displayed them
# (ISP 'Spanish ISP.pdf', osf.io/download/3vche, pp. 24-27; 'English ISP.pdf',
# osf.io/download/wft8k, pp. 19-21; same order in every ISP translation .docx, e.g.
# osf.io/download/hp967):
#   self-expression vs harmony   1 say/express what you think (+SE), 2 adapt/hide feelings (+H),
#                                3 preserve harmony (+H), 4 good to express disagreement (+SE)
#   self-interest vs commitment  5 protect own interests (+SI), 6 priority to others (+C),
#                                7 look after close people (+C), 8 value achievements over
#                                relations (+SI), 9 sacrifice for family (+C)
#   consistency vs variability   10 behave differently (+V), 11 see self differently (+V),
#                                12 see self the same way (+C), 13 behave the same way (+C)
# Stored raw, 1 = "no me describe para nada" (Doesn't describe me at all) ... 9 = "me describe
# con exactitud" (Describes me exactly), as on the survey screen.
#
# DATA. The study's own Study 3 file on OSF kp572 ('Data/Study 3/Study 3 data.csv'), which
# data/SABFI2_Gallardo_Pujol_2018.R melts with names kept (select(starts_with("Constru")) +
# pivot_longer, no recode). Used instead of irw_fetch() to stay off the Redivis export cap;
# step (0) ties it to the live table by per-item n and mean (item_stats.R, 2026-09-24).

csv <- file.path(tempdir(), "sabfi2_study3.csv")
if (!file.exists(csv)) download.file("https://osf.io/download/r2zhc/", csv, quiet = TRUE, mode = "wb")
d <- read.csv(csv)
X <- d[, paste0("Constru", 1:13)]
ok <- TRUE

# (0) OSF file == live table
LIVE_MEAN <- c(5.16, 4.65, 3.85, 6.97, 4.24, 5.62, 6.77, 3.55, 6.32, 4.62, 5.00, 4.82, 4.93)
obs_n <- colSums(!is.na(X)); obs_m <- colMeans(X, na.rm = TRUE)
cat("(0) OSF Study 3 file vs live item_stats.R (live n = 419 for every item)\n")
for (i in 1:13) cat(sprintf("  %-9s osf n=%d  live mean %.2f  osf mean %.4f\n", names(X)[i], obs_n[i], LIVE_MEAN[i], obs_m[i]))
if (any(obs_n != 419) || any(abs(obs_m - LIVE_MEAN) > 0.006)) { cat("  -> OSF file does NOT reproduce live table\n"); ok <- FALSE }

# (A) route 3: published subscale statistics (postprint descriptives table, 'Self-Construal
# Scale' rows: men / women / total M, SD, alpha) reproduced from the claimed block membership
# and the authors' own keys (Scripts/study.3.nomological.network.short.versions.R l.214-246).
blocks <- list(SelfExpression = list(1:4,  c(-1, 1, 1, -1)),
               SelfInterest   = list(5:9,  c(1, -1, -1, 1, -1)),
               Consistency    = list(10:13, c(-1, -1, 1, 1)))
PUB <- rbind(SelfExpression = c(4.02, 1.49, 4.10, 1.51, 4.09, 1.50, 0.71),
             SelfInterest   = c(4.43, 1.40, 3.71, 1.15, 3.82, 1.21, 0.61),
             Consistency    = c(4.55, 2.10, 5.11, 1.98, 5.03, 2.00, 0.91))
alpha <- function(M) { M <- as.matrix(M); p <- ncol(M); v <- cov(M, use = "pairwise"); p / (p - 1) * (1 - sum(diag(v)) / sum(v)) }
cat("\n(A) published subscale stats (Gender 1 = men n=62, 2 = women n=357)\n")
cat(sprintf("  %-15s %s\n", "", "menM menSD womM womSD totM totSD alpha"))
for (b in names(blocks)) {
  idx <- blocks[[b]][[1]]; k <- blocks[[b]][[2]]
  M <- as.matrix(X[, idx]); for (j in seq_along(k)) if (k[j] < 0) M[, j] <- 10 - M[, j]
  s <- rowMeans(M)
  o <- c(mean(s[d$Gender == 1]), sd(s[d$Gender == 1]), mean(s[d$Gender == 2]), sd(s[d$Gender == 2]),
         mean(s), sd(s), alpha(M))
  cat(sprintf("  %-15s pub %s\n  %-15s obs %s\n", b, paste(sprintf("%5.2f", PUB[b, ]), collapse = " "),
              "", paste(sprintf("%5.2f", o), collapse = " ")))
  if (max(abs(o - PUB[b, ])) > 0.011) { cat("  -> does not reproduce\n"); ok <- FALSE }
}

# (B) route 6: keying polarity. Within each block, the content of the screen order predicts
# same-pole items correlate positively and opposite-pole items negatively.
R <- cor(X)
poles <- list(c(1, 4), c(2, 3), c(5, 8), c(6, 7, 9), c(10, 11), c(12, 13))
pole_of <- integer(13); for (p in seq_along(poles)) pole_of[poles[[p]]] <- p
block_of <- rep(1:3, c(4, 5, 4))
hit <- 0; tot <- 0
cat("\n(B) within-block correlation signs (same pole should be +, opposite pole -)\n")
for (i in 1:12) for (j in (i + 1):13) if (block_of[i] == block_of[j]) {
  pred <- if (pole_of[i] == pole_of[j]) 1 else -1
  good <- sign(R[i, j]) == pred; hit <- hit + good; tot <- tot + 1
  cat(sprintf("  Constru%-2d x Constru%-2d  r=%6.2f  predicted %s  %s\n", i, j, R[i, j], ifelse(pred > 0, "+", "-"), ifelse(good, "ok", "MISS")))
}
cat(sprintf("  %d/%d signs as predicted\n", hit, tot))
if (hit != tot) ok <- FALSE

# (C) direction of the stored 1-9 coding: cross-scale correlations with BFI-2 items whose
# direction is fixed (BFI1 'outgoing, sociable', mean 3.9 of 5; BFI2 'compassionate', 4.3).
r1 <- cor(d$Constru1, d$BFI1, use = "pair"); r7 <- cor(d$Constru7, d$BFI2, use = "pair"); r8 <- cor(d$Constru8, d$BFI2, use = "pair")
cat(sprintf("\n(C) direction: r(Constru1 say-what-you-think, BFI1 outgoing) = %.2f (predicted +)\n", r1))
cat(sprintf("    r(Constru7 look after close people, BFI2 compassionate) = %.2f (predicted +)\n", r7))
cat(sprintf("    r(Constru8 achievements over relations, BFI2 compassionate) = %.2f (predicted -)\n", r8))
cat(sprintf("    item means: Constru7 %.2f (0%% at 1) > Constru8 %.2f; under the reversed reading Constru7 would be %.2f\n",
            obs_m[7], obs_m[8], 10 - obs_m[7]))
if (!(r1 > 0 && r7 > 0 && r8 < 0 && obs_m[7] > 5 && obs_m[8] < 5)) ok <- FALSE

# (D) weak, informative only: in the consistency block the 'behave' and 'see' items should pair
r_match <- R[10, 13] + R[11, 12]; r_swap <- R[10, 12] + R[11, 13]
cat(sprintf("\n(D) consistency pairing: r(10,13)+r(11,12) = %.2f vs r(10,12)+r(11,13) = %.2f (claimed pairing more negative: %s; weak)\n",
            r_match, r_swap, r_match < r_swap))

cat("\nESTABLISHED: block membership (1-4 / 5-9 / 10-13), each item's polarity class, raw storage\n",
    "and direction 1 = doesn't describe me at all ... 9 = describes me exactly.\n",
    "NOT ESTABLISHED: order within {1,4}, {2,3}, {5,8}, {6,7,9}, {10,11}, {12,13}; no per-item\n",
    "statistics are published for this administration. (D) is suggestive only.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
