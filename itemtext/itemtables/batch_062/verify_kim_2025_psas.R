# verify_kim_2025_psas.R -- Step 5b route 1 (per-item descriptive statistics).
#
# CLAIM UNDER TEST: the paper's Table 3 numbers each item Q1..Q16 (Q1-Q8 =
# somatic arousal, Q9-Q16 = cognitive arousal) while the live data codes them
# PSAS_S1..S8 / PSAS_C1..C8. The shipped mapping is Qk -> PSAS_Sk for k=1..8 and
# Q(8+k) -> PSAS_Ck for k=1..8. Table 3 publishes a mean, an SD and a corrected
# item-total correlation for every item, so that mapping is falsifiable: if any
# two item texts were swapped, the triple would land on the wrong code.
#
# Kim N, Lee BG (2025) PLOS ONE 20(9):e0333390, Table 3 (N = 286).

suppressMessages(library(irw))

TABLE <- "kim_2025_psas"
CODE  <- c(paste0("PSAS_S", 1:8), paste0("PSAS_C", 1:8))   # = paper Q1..Q16
PUB_MEAN <- c(1.42, 1.45, 1.30, 1.33, 1.29, 1.52, 1.44, 1.94,
              1.49, 2.09, 1.67, 2.04, 2.54, 2.06, 2.11, 1.82)
PUB_SD   <- c(0.78, 0.79, 0.69, 0.70, 0.71, 0.84, 0.86, 1.02,
              0.88, 1.09, 0.98, 1.05, 1.06, 1.13, 1.11, 1.05)
PUB_ITC  <- c(0.60, 0.67, 0.50, 0.56, 0.54, 0.61, 0.43, 0.56,
              0.55, 0.67, 0.71, 0.72, -0.10, 0.65, 0.69, 0.60)
TOL_MEAN <- 0.01; TOL_SD <- 0.02; TOL_ITC <- 0.02

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
m <- as.matrix(w[, -1]); colnames(m) <- sub("^resp\\.", "", colnames(m))
m <- m[, CODE]
tot <- rowSums(m)

obs_mean <- colMeans(m)
obs_sd   <- apply(m, 2, sd)
obs_itc  <- sapply(CODE, function(i) cor(m[, i], tot - m[, i]))

cat(sprintf("%-9s %-4s | %9s %9s %7s | %8s %8s %7s | %7s %7s %7s\n",
            "code", "Q", "pub_mean", "obs_mean", "d", "pub_sd", "obs_sd", "d",
            "pub_itc", "obs_itc", "d"))
for (k in seq_along(CODE))
    cat(sprintf("%-9s Q%-3d | %9.2f %9.3f %7.3f | %8.2f %8.3f %7.3f | %7.2f %7.3f %7.3f\n",
                CODE[k], k, PUB_MEAN[k], obs_mean[k], obs_mean[k] - PUB_MEAN[k],
                PUB_SD[k], obs_sd[k], obs_sd[k] - PUB_SD[k],
                PUB_ITC[k], obs_itc[k], obs_itc[k] - PUB_ITC[k]))

wm <- max(abs(obs_mean - PUB_MEAN)); ws <- max(abs(obs_sd - PUB_SD))
wi <- max(abs(obs_itc - PUB_ITC))
cat(sprintf("\nlargest deviation: mean %.3f (tol %.2f) | sd %.3f (tol %.2f) | itc %.3f (tol %.2f)\n",
            wm, TOL_MEAN, ws, TOL_SD, wi, TOL_ITC))

# Uniqueness: is the published triple distinguishing, or would a permutation pass?
perm_ok <- 0
for (a in seq_along(CODE)) for (b in seq_along(CODE)) if (a != b)
    if (abs(obs_mean[b] - PUB_MEAN[a]) <= TOL_MEAN &&
        abs(obs_sd[b]   - PUB_SD[a])   <= TOL_SD &&
        abs(obs_itc[b]  - PUB_ITC[a])  <= TOL_ITC) perm_ok <- perm_ok + 1
cat(sprintf("off-diagonal (code, published-item) pairs also within tolerance: %d of 240\n",
            perm_ok))
cat("A count of 0 means no item could be swapped with any other and still match,\n",
    "i.e. the route distinguishes every item from every other item.\n", sep = "")

# Published subscale and total scores (Table 3), a second, independent check that
# the S/C split is the right way round and that the items are stored raw.
cat(sprintf("\nsomatic subtotal   published 11.70 +/- 4.62   observed %.2f +/- %.2f\n",
            mean(rowSums(m[, paste0("PSAS_S", 1:8)])), sd(rowSums(m[, paste0("PSAS_S", 1:8)]))))
cat(sprintf("cognitive subtotal published 15.82 +/- 5.77   observed %.2f +/- %.2f\n",
            mean(rowSums(m[, paste0("PSAS_C", 1:8)])), sd(rowSums(m[, paste0("PSAS_C", 1:8)]))))
cat(sprintf("K-PSAS-16 total    published 27.52 +/- 9.20   observed %.2f +/- %.2f\n",
            mean(tot), sd(tot)))

ok <- wm <= TOL_MEAN && ws <= TOL_SD && wi <= TOL_ITC && perm_ok == 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
