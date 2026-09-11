# verify_rosetti_2023_cas.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: item code CAS_q<i> carries Clayton & Karazsia's (2020)
# 22-item Climate Change Anxiety Scale item number <i>, in the canonical
# ordering (1-8 cognitive-emotional impairment, 9-13 functional impairment,
# 14-16 personal experience, 17-22 behavioural engagement).
#
# DATA SOURCE. This fetches the study's own figshare deposit
# (ClimateAnxietyDataBase.csv, 102 kB) rather than irw::irw_fetch(), which would
# export the whole live table against the shared 200GB/30d Redivis quota. That is
# sound here because data/rosetti_2023_climate_anxiety.py melts the CAS_q1..CAS_q22
# columns with NO rename (var_name="item"), so the deposit's column name IS the live
# item code, and validate_items.R --table-sets already confirmed the item and resp
# sets match live exactly. The deposit also carries the four subscale-sum columns the
# live table does not, which is what makes check A possible at all.

TOL_RHO <- 0.80

url <- "https://ndownloader.figshare.com/files/40839032"
d <- read.csv(url, stringsAsFactors = FALSE)
q <- paste0("CAS_q", 1:22)
stopifnot(all(q %in% names(d)))
cat(sprintf("deposit rows: %d\n\n", nrow(d)))

## ---- A. The deposit's own subscale sums pin the block boundaries -------------
## Rosetti et al. shipped CEI_sum / FI_sum / EXP_sum / BEH_sum / CAS_sum alongside
## the items. If CAS_q1..q22 are the canonical items, those columns must be exactly
## reproducible from the canonical 8/5/3/6 blocks -- for every one of the 468 rows.
blocks <- list(CEI_sum = 1:8, FI_sum = 9:13, EXP_sum = 14:16,
               BEH_sum = 17:22, CAS_sum = 1:13)
cat("A. subscale-sum reconstruction (exact integer identity, all rows)\n")
okA <- TRUE
for (nm in names(blocks)) {
    idx <- blocks[[nm]]
    hit <- sum(d[[nm]] == rowSums(d[, q[idx], drop = FALSE]))
    cat(sprintf("   %-8s = sum(CAS_q%d..q%d)  matched %d / %d rows\n",
                nm, min(idx), max(idx), hit, nrow(d)))
    if (hit != nrow(d)) okA <- FALSE
}
## and the same identity must BREAK if the boundary is moved by one item
shift1 <- sum(d$CEI_sum == rowSums(d[, q[1:7], drop = FALSE]))
shift2 <- sum(d$FI_sum  == rowSums(d[, q[10:14], drop = FALSE]))
cat(sprintf("   falsifier: CEI_sum = sum(q1..q7)  matched only %d / %d rows\n",
            shift1, nrow(d)))
cat(sprintf("   falsifier: FI_sum  = sum(q10..q14) matched only %d / %d rows\n\n",
            shift2, nrow(d)))
okA <- okA && shift1 < nrow(d) && shift2 < nrow(d)

## ---- B. Cross-sample per-item profile ----------------------------------------
## Independent published per-item means for the full 22-item CAS: Behavioral
## Sciences 2023, 13(12):966 (doi 10.3390/bs13120966, CC BY 4.0), Table A1.
## That paper prints the items in a DIFFERENT block order (its 9-14 are the
## behavioural-engagement items, 15-17 experience, 18-22 functional), so its means
## are re-indexed into canonical order below. Published scale is 1-5; this table
## stores 0-4, hence the -1.
bs_mean <- c(2.24,1.81,1.41,1.29,1.78,1.60,1.34,1.66,3.47,3.80,4.50,
             3.90,3.40,3.20,2.46,2.08,2.79,1.58,1.76,1.42,1.44,1.42)
bs_sd   <- c(0.97,0.88,0.70,0.62,0.93,0.82,0.71,0.92,1.03,1.10,0.70,
             0.93,1.04,1.00,1.03,1.18,1.20,0.78,0.93,0.68,0.72,0.79)
bs_sk   <- c(0.37,0.92,1.80,2.16,0.97,1.32,2.28,1.40,-0.54,-0.56,-1.45,
             -0.61,-0.05,-0.02,0.31,0.76,-0.04,1.17,1.09,1.59,1.67,2.07)
map <- c(1:8, 18,19,20,21,22, 15,16,17, 9,10,11,12,13,14)   # canonical -> bs row
pub <- bs_mean[map] - 1

obs <- sapply(q, function(k) mean(d[[k]], na.rm = TRUE))
skew <- function(x) { x <- x[!is.na(x)]; m <- mean(x)
                      mean((x - m)^3) / (mean((x - m)^2))^1.5 }
obs_sd <- sapply(q, function(k) sd(d[[k]], na.rm = TRUE))
obs_sk <- sapply(q, function(k) skew(d[[k]]))

cat("B. per-item means, this sample vs an independent 22-item administration\n")
cat(sprintf("   %-8s %9s %9s %9s %7s %7s\n",
            "item", "published", "observed", "diff", "obsSD", "pubSD"))
for (i in 1:22)
    cat(sprintf("   %-8s %9.2f %9.2f %9.2f %7.2f %7.2f\n",
                q[i], pub[i], obs[i], obs[i] - pub[i], obs_sd[i], bs_sd[map[i]]))
rho <- suppressWarnings(cor(obs, pub, method = "spearman"))
set.seed(1)
null <- replicate(2000, suppressWarnings(
            cor(obs[sample(22)], pub, method = "spearman")))
cat(sprintf("\n   Spearman rho over all 22 items = %.3f  (random-permutation null:\n",
            rho))
cat(sprintf("   95th pct of |rho| = %.3f, so a scrambled mapping would not reach this)\n",
            quantile(abs(null), 0.95)))
for (b in list(c("CEI", 1, 8), c("FI", 9, 13), c("EXP", 14, 16), c("BEH", 17, 22))) {
    i <- as.integer(b[2]):as.integer(b[3])
    cat(sprintf("   within-block rho, %-4s (items %2d-%2d) = %+.2f\n",
                b[1], min(i), max(i),
                suppressWarnings(cor(obs[i], pub[i], method = "spearman"))))
}
okB <- rho >= TOL_RHO

## ---- C. Response-scale direction ---------------------------------------------
## resp 0 = Never .. 4 = Almost always. If the coding ran the other way, the
## nightmares item would be near-universally endorsed and the light-switch item
## near-never, in a general student sample.
cat(sprintf("\nC. direction: CAS_q19 'I turn off lights' mean = %.2f, CAS_q3 'I have nightmares about climate change' mean = %.2f\n",
            obs[19], obs[3]))
okC <- obs[19] > obs[3]

## ---- D. The one near-tie the means cannot separate ----------------------------
## CAS_q14 and CAS_q15 sit 0.026 apart, so the mean profile does not order them.
## Published SD and skew do: 'I know someone who has been directly affected'
## is the more dispersed and more right-skewed of the pair.
cat(sprintf("\nD. EXP near-tie tie-break (means %.3f vs %.3f, gap %.3f)\n",
            obs[14], obs[15], abs(obs[14] - obs[15])))
cat(sprintf("   SD   q14 %.2f < q15 %.2f   (published 1.03 < 1.18)\n", obs_sd[14], obs_sd[15]))
cat(sprintf("   skew q14 %.2f < q15 %.2f   (published 0.31 < 0.76)\n", obs_sk[14], obs_sk[15]))
okD <- obs_sd[14] < obs_sd[15] && obs_sk[14] < obs_sk[15]

## ---- What this does NOT establish --------------------------------------------
cat("\nNOT ESTABLISHED: check A pins each item's SUBSCALE MEMBERSHIP exactly, and\n",
    "therefore the block boundaries at 8/13/16/22, but says nothing about the order\n",
    "of items WITHIN a block. Check B is a cross-sample comparison, so its high overall\n",
    "rho is driven mostly by between-block level differences; within-block rho is 0.69\n",
    "(CEI) and 0.54 (BEH), which is not enough to rule out a swap of two similar items\n",
    "inside one subscale. This is why the recorded status is PARTIAL, not VERIFIED.\n",
    sep = "")

cat("\nA:", okA, " B:", okB, " C:", okC, " D:", okD, "\n")
cat(if (okA && okB && okC && okD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
