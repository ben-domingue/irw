# verify_ren2019_scpv.R -- Step 5b mapping verification for ren2019_scpv.
#
# CLAIM UNDER TEST: the source spreadsheet's column SCPVk (k = 1..12), which the
# processing script melts straight through to the IRW item code SCPVk, holds item
# number k of the Social Competence Scale - Parent Version (CPPRG 1995) as printed
# on the Fast Track measure form. Neither the deposit (bare numeric .xlsx, no
# labels) nor Ren et al. (2019) reproduces any item wording, so the tie between
# code and text is the numeric suffix and nothing else. That is an inference, and
# this is the check on it.
#
# ROUTE 1 (per-item descriptive statistics, cross-sample). The Fast Track
# technical reports publish per-item means for the same 12 numbered items in two
# independent US samples. If SCPVk were not item k, the live per-item mean profile
# would not track the published profile.
# ROUTE 3/5 (published subscale alphas) is run as corroboration only.
#
# Verifies the item_text <-> item axis. The option_text <-> resp axis is not
# tested here: the source publishes no per-level frequencies to match against.

suppressMessages(library(irw))
TABLE <- "ren2019_scpv"
ITEMS <- paste0("SCPV", 1:12)

# --- Published values, hard-coded ----------------------------------------------
# Corrigan, A. (2003). Social Competence Scale - Parent Version, Grade 2 /Year 3
# (Fast Track Project Technical Report), section VI, item means, items 1..12.
FT_NORM <- c(1.96, 1.89, 2.25, 2.27, 2.30, 2.66, 2.92, 2.09, 2.95, 3.27, 2.64, 2.42)
FT_CTRL <- c(1.52, 1.50, 1.77, 1.94, 1.86, 2.23, 2.42, 1.59, 2.55, 3.01, 2.27, 1.99)
# Same report, section III: subscale membership.
EMO <- c(1, 2, 3, 5, 6, 8)          # Emotional Regulation Skills
PRO <- c(4, 7, 9, 10, 11, 12)       # Prosocial/Communication Skills
# Ren et al. (2019), Frontiers in Psychology 10:2550, Measures section:
# "Cronbach's alphas for the current sample were 0.90, 0.78, and 0.88 for the
#  total score, emotion regulation, and prosocial/communication, respectively."
A_TOT <- 0.90; A_EMO <- 0.78; A_PRO <- 0.88

# Thresholds.
MIN_SPEARMAN <- 0.80    # rank agreement with the published item profile
MAX_PERM_P   <- 0.01    # against random relabelings of the 12 codes

# --- Live data ------------------------------------------------------------------
d <- as.data.frame(irw::irw_fetch(TABLE))
# The Fast Track form is coded 0-4; Ren et al. coded the same five points 1-5,
# so the live scores are shifted by -1 before comparison. A shift is monotone and
# cannot affect the rank statistic; it only makes the printed columns comparable.
obs <- sapply(ITEMS, function(i) mean(d$resp[d$item == i], na.rm = TRUE)) - 1
n   <- sapply(ITEMS, function(i) sum(d$item == i & !is.na(d$resp)))

cat("=== Route 1: per-item means, live (Chinese parents, N=299) vs Fast Track ===\n")
cat(sprintf("%-8s %5s %10s %12s %12s\n", "item", "n", "live-1", "FT norm", "FT control"))
for (i in 1:12)
  cat(sprintf("%-8s %5d %10.2f %12.2f %12.2f\n", ITEMS[i], n[i], obs[i], FT_NORM[i], FT_CTRL[i]))

s_norm <- cor(obs, FT_NORM, method = "spearman")
s_ctrl <- cor(obs, FT_CTRL, method = "spearman")
p_norm <- cor(obs, FT_NORM)
cat(sprintf("\nSpearman live vs FT normative : %.3f\n", s_norm))
cat(sprintf("Spearman live vs FT control   : %.3f\n", s_ctrl))
cat(sprintf("Pearson  live vs FT normative : %.3f\n", p_norm))

set.seed(1)
null <- replicate(20000, cor(sample(obs), FT_NORM, method = "spearman"))
perm_p <- mean(null >= s_norm)
cat(sprintf("permutation p (20000 random relabelings of the 12 codes): %.5f\n", perm_p))

# --- Which pairs this route cannot separate ------------------------------------
cat("\n=== What route 1 does NOT establish: pairwise swaps it barely notices ===\n")
worst <- NULL
for (a in 1:11) for (b in (a + 1):12) {
  sw <- obs; sw[c(a, b)] <- sw[c(b, a)]
  s <- cor(sw, FT_NORM, method = "spearman")
  if (s >= MIN_SPEARMAN) worst <- rbind(worst, data.frame(a = a, b = b, spearman = s))
}
if (is.null(worst)) {
  cat("none: every one of the 66 single swaps drops Spearman below the threshold.\n")
} else {
  worst <- worst[order(-worst$spearman), ]
  cat(sprintf("%d of 66 single swaps still clear Spearman >= %.2f:\n", nrow(worst), MIN_SPEARMAN))
  for (i in seq_len(nrow(worst)))
    cat(sprintf("  swap SCPV%-2d <-> SCPV%-2d : %.3f (unswapped %.3f)\n",
                worst$a[i], worst$b[i], worst$spearman[i], s_norm))
}

# --- Corroboration: published subscale alphas ----------------------------------
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
alpha <- function(k) {
  m <- w[, paste0("SCPV", k)]; m <- m[complete.cases(m), ]
  p <- ncol(m); v <- var(m); (p / (p - 1)) * (1 - sum(diag(v)) / sum(v))
}
a_emo <- alpha(EMO); a_pro <- alpha(PRO); a_tot <- alpha(1:12)
cat("\n=== Corroboration (route 3/5): Cronbach's alpha vs Ren et al.'s reported values ===\n")
cat(sprintf("  total                      observed %.3f   reported %.2f\n", a_tot, A_TOT))
cat(sprintf("  emotional regulation       observed %.3f   reported %.2f   items %s\n",
            a_emo, A_EMO, paste(EMO, collapse = ",")))
cat(sprintf("  prosocial/communication    observed %.3f   reported %.2f   items %s\n",
            a_pro, A_PRO, paste(PRO, collapse = ",")))
combs <- combn(12, 6); dists <- numeric(ncol(combs))
for (j in seq_len(ncol(combs))) {
  g <- combs[, j]; h <- setdiff(1:12, g); x <- alpha(g); y <- alpha(h)
  dists[j] <- min(sqrt((x - A_EMO)^2 + (y - A_PRO)^2), sqrt((y - A_EMO)^2 + (x - A_PRO)^2))
}
jc <- which(apply(combs, 2, function(g) identical(as.integer(g), as.integer(EMO))))
rk <- sum(dists < dists[jc]) + 1
cat(sprintf("  the CPPRG partition ranks %d of %d possible 6/6 splits by closeness to (%.2f, %.2f)\n",
            rk, ncol(combs), A_EMO, A_PRO))
cat("  -- corroborative only: alpha is coarse, the published partition is not the closest,\n")
cat("     and this route pins subscale MEMBERSHIP at best, never order within a subscale.\n")

cat("\nWhat this verifies: the 12 item texts are not permuted -- the live mean profile\n")
cat("reproduces the published item-by-item profile of the same numbered instrument in two\n")
cat("independent samples. What it does NOT verify: any pair listed above as a tolerated\n")
cat("swap, and nothing at all about option_text <-> resp beyond the two endpoint anchors\n")
cat("Ren et al. print in prose. Status recorded as PARTIAL, not VERIFIED.\n")

pass <- (s_norm >= MIN_SPEARMAN) && (perm_p <= MAX_PERM_P)
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
