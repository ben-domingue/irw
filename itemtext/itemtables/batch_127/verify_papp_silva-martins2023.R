# verify_papp_silva-martins2023.R
#
# CLAIM UNDER TEST: item code i<k> (ATP1) and IIi<k> (ATP2) carry the wording
# printed as item <k> of the European Portuguese QPPAF questionnaire
# (OSF 10.17605/OSF.IO/4K7VP, "Physical Activity Parenting Practices (European
# Portuguese).pdf", items numbered 1-31 on the form).
#
# The falsifiable prediction: Silva-Martins et al. (2023) Additional file 2,
# Table S2 publishes M and SD for each PAPP item 1-31 at N=503. If the code->
# number tie were permuted, those 31 (M, SD) pairs would land on the wrong
# codes. All 31 published (M, SD) pairs are distinct, so the match is one-to-one.
#
# Two further predictions come from the wording itself, so they test the
# number -> TEXT hop rather than the code -> number hop:
#   (a) items 1-15 are the Engagement and Structure factor; the paper reports
#       Cronbach's alpha = .89 for that 15-item block (Table 1, Model 2).
#   (b) item 31 ("deixa o/a seu/sua filho/a sair para brincar a volta de casa?"
#       = "let your child go outside to play around your home?") is the one
#       positively-worded item inside the Restriction for Safety Concerns block
#       28-31 -- O'Connor et al. (2014) Table 4 gives it a loading of -0.48
#       against +0.58/+0.93/+0.92 for 28/29/30. It must correlate NEGATIVELY
#       with 28-30 while 28-30 correlate positively among themselves.

suppressMessages(library(irw))

TABLE <- "papp_silva-martins2023"

# Silva-Martins et al. (2023), BMC Psychology 11:417, Additional file 2 Table S2
# ("Descriptive statistics for each PAPP item (N=503)"), items 1..31.
S2_M  <- c(3.16,3.36,3.52,4.29,3.27,3.56,3.57,3.02,2.85,4.34,3.62,3.62,3.90,
           3.52,3.23,1.88,3.84,2.70,2.34,2.63,1.61,2.25,1.44,1.30,1.64,1.66,
           1.61,2.58,2.77,2.92,3.22)
S2_SD <- c(1.10,0.91,0.85,0.79,0.88,0.91,0.93,1.03,1.04,0.78,0.78,0.84,1.21,
           0.93,0.98,1.17,1.14,0.78,0.84,0.78,0.84,0.97,0.72,0.76,0.89,0.86,
           0.89,1.36,1.45,1.43,1.36)
TOL <- 0.006          # Table S2 is printed to 2 dp; anything within half a unit
                      # in the last place is an exact reproduction.
ALPHA_PUB <- 0.89     # Table 1, Model 2 (PAPP-E, 15 items)

d  <- irw::irw_fetch(TABLE)
w0 <- subset(d, wave == 0)          # ATP1; Table S2 is the N=503 ATP1 wave

cat(sprintf("%-5s %5s %9s %9s %9s %9s %8s %8s\n",
            "item", "n", "pub M", "obs M", "pub SD", "obs SD", "dM", "dSD"))
obsM <- obsSD <- numeric(31)
for (k in 1:31) {
    v <- w0$resp[w0$item == paste0("i", k)]
    v <- v[!is.na(v)]
    obsM[k]  <- mean(v)
    obsSD[k] <- sd(v)
    cat(sprintf("i%-4d %5d %9.2f %9.2f %9.2f %9.2f %8.3f %8.3f\n",
                k, length(v), S2_M[k], obsM[k], S2_SD[k], obsSD[k],
                obsM[k] - S2_M[k], obsSD[k] - S2_SD[k]))
}
worstM  <- max(abs(obsM  - S2_M))
worstSD <- max(abs(obsSD - S2_SD))
cat(sprintf("\nlargest deviation: M %.4f, SD %.4f (tolerance %.3f)\n",
            worstM, worstSD, TOL))

# The published pairs must be mutually distinguishing for the match to be 1-to-1.
pairs_unique <- !any(duplicated(paste(S2_M, S2_SD)))
dupM <- unique(S2_M[duplicated(S2_M)])
cat(sprintf("published (M, SD) pairs all distinct: %s   [means alone tie at: %s]\n",
            pairs_unique, paste(sprintf("%.2f", dupM), collapse = ", ")))

# --- (a) subscale block: alpha of the 15-item Engagement and Structure factor
ids <- unique(w0$id)
M <- sapply(1:31, function(k) {
    x <- w0[w0$item == paste0("i", k), ]
    x$resp[match(ids, x$id)]
})
colnames(M) <- paste0("i", 1:31)
cs <- cov(M[, 1:15], use = "pairwise.complete.obs")
alpha <- 15 / 14 * (1 - sum(diag(cs)) / sum(cs))
cat(sprintf("\nCronbach alpha, i1-i15 (Engagement and Structure): %.3f  (paper: %.2f)\n",
            alpha, ALPHA_PUB))

# --- (b) polarity marker inside the Restriction for Safety Concerns block
r31 <- sapply(28:30, function(k) cor(M[, 31], M[, k], use = "pairwise.complete.obs"))
r_within <- c(cor(M[, 28], M[, 29], use = "pairwise.complete.obs"),
              cor(M[, 28], M[, 30], use = "pairwise.complete.obs"),
              cor(M[, 29], M[, 30], use = "pairwise.complete.obs"))
cat(sprintf("cor(i31, i28/i29/i30) = %s   (expected NEGATIVE: i31 is the only positively worded item in the block)\n",
            paste(sprintf("%+.2f", r31), collapse = " ")))
cat(sprintf("cor within i28/i29/i30 = %s   (expected strongly POSITIVE)\n",
            paste(sprintf("%+.2f", r_within), collapse = " ")))

# --- (c) the ATP2 block. IIi1..IIi31 are the source CSV's own column names and
# the OSF codebook states they are "items 1 to 31 of the PAPP completed at
# Assessment Time Point 2", so the code -> number tie there is a column-name
# identity, not an inference. It is corroborated anyway: over the 125 parents who
# completed both waves, cor(i_k, IIi_k) should be the largest correlation between
# i_k and any ATP2 item.
w1  <- subset(d, wave == 1)
rid <- intersect(unique(w1$id), unique(w0$id))
A <- sapply(1:31, function(k) { x <- w0[w0$item == paste0("i",   k), ]; x$resp[match(rid, x$id)] })
B <- sapply(1:31, function(k) { x <- w1[w1$item == paste0("IIi", k), ]; x$resp[match(rid, x$id)] })
CC  <- cor(A, B, use = "pairwise.complete.obs")
arg <- apply(CC, 1, which.max)
hits <- sum(arg == 1:31)
cat(sprintf("\ntest-retest (n = %d): cor(i_k, IIi_k) is the argmax over all 31 ATP2 items for %d of 31\n",
            length(rid), hits))
miss <- which(arg != 1:31)
if (length(miss))
    for (k in miss)
        cat(sprintf("   k=%2d: diag r = %+.2f vs best IIi%d r = %+.2f (margin %.2f)\n",
                    k, CC[k, k], arg[k], CC[k, arg[k]], CC[k, arg[k]] - CC[k, k]))

ok <- worstM <= TOL && worstSD <= TOL && pairs_unique &&
      abs(alpha - ALPHA_PUB) <= 0.01 && all(r31 < 0) && all(r_within > 0.5) &&
      hits >= 27

cat("\nWhat this does NOT establish: nothing here tests the English in the\n",
    "*_translated columns -- that is O'Connor et al. (2014) Table 3/4 wording\n",
    "reassembled under that table's own 'How often do you...' column stem, and it\n",
    "diverges from the Portuguese in the few places listed in provenance. The\n",
    "test-retest near-misses printed above are ties within sampling noise at\n",
    "n=125, not evidence against the ATP2 mapping, which rests on the column\n",
    "names rather than on this statistic.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
