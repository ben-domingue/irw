# verify_smoking_perseverance_mcneish_2025.R -- Step 5b mapping check (batch_421).
#
# Claim: i44 = "worked on what I planned until I succeeded", i45 = "set goals and
# kept track of my progress toward goals", i47 = "been able to finish projects I
# started". The OSF Supplementary Material (osf.io/3zuwb, "Data" section) states this
# tie by code outright; the Primer (osf.io/dmpwc) lists the same three prompts as
# (a), (b), (c) and reports Table 1 estimates for "Item 1/2/3". This script checks
# that Table 1's Item 1/2/3 are i44/i45/i47 respectively, i.e. that the paper's own
# item order and the supplement's code labels agree, using two parameter sets that
# separate every item from every other:
#   * configural-model between-person intercepts (3.25 / 3.27 / 3.38) vs the mean
#     of person means per item;
#   * partially-saturated within-person loadings and residual variances, whose
#     implied within-person variance lambda^2 + theta (0.996 / 0.946 / 0.898) vs the
#     observed variance of person-centred responses.
# It then checks every permutation of the three codes and requires the claimed one
# to fit best on both.
#
# Data: the study's OSF file "Smoking Perseverance Data.csv" (osf.io/26qpz), which
# data/smoking_perseverance_mcneish_2025.R pivots with item = source column name (no
# rename). Row counts are checked against the live table via irw_table_sets() (a
# server-side query, no export).
#
# Does NOT establish: that Table 1's "Item 1" is prompt (a) -- that rests on the
# paper's listing order and on the supplement's explicit code labels, not on data.
# Nor the anchor direction (1 = "not at all", 5 = "extremely"): all three items are
# positively worded, so no polarity contrast exists to test it.

suppressMessages(library(irw))
TABLE <- "smoking_perseverance_mcneish_2025"
codes <- c("i44", "i45", "i47")

PUB_INTERCEPT <- c(3.25, 3.27, 3.38)          # Table 1, configural model, between intercepts
PUB_LOAD      <- c(0.81, 0.81, 0.72)          # Table 1, partially saturated, within loadings
PUB_RESVAR    <- c(0.34, 0.29, 0.38)          # Table 1, partially saturated, within residual var
PUB_WVAR      <- PUB_LOAD^2 + PUB_RESVAR      # implied within-person variance (factor var = 1)

d <- read.csv("https://osf.io/download/26qpz/")
live <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- live$per_item
cat("OSF rows per item:", sapply(codes, function(v) sum(!is.na(d[[v]]))), "\n")
print(pi)
n_ok <- all(sapply(codes, function(v) sum(!is.na(d[[v]]))) ==
            pi$n[match(codes, pi$item)])
cat("OSF file matches live per-item n:", n_ok, "\n\n")

obs_int  <- sapply(codes, function(v) mean(tapply(d[[v]], d$ID, mean, na.rm = TRUE)))
obs_wvar <- sapply(codes, function(v) {
  x <- d[[v]]; mean((x - ave(x, d$ID, FUN = function(z) mean(z, na.rm = TRUE)))^2, na.rm = TRUE)
})

cat(sprintf("%-5s %10s %10s %10s %10s\n", "code", "pub_int", "obs_int", "pub_wvar", "obs_wvar"))
for (i in 1:3) cat(sprintf("%-5s %10.3f %10.4f %10.3f %10.4f\n",
                           codes[i], PUB_INTERCEPT[i], obs_int[i], PUB_WVAR[i], obs_wvar[i]))

perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
sse <- t(sapply(perms, function(p) c(
  int  = sum((obs_int[p]  - PUB_INTERCEPT)^2),
  wvar = sum((obs_wvar[p] - PUB_WVAR)^2))))
rownames(sse) <- sapply(perms, function(p) paste(codes[p], collapse = ","))
cat("\nSSE of each assignment of codes to Item 1,2,3:\n"); print(round(sse, 5))

best_int  <- which.min(sse[, "int"])  == 1
best_wvar <- which.min(sse[, "wvar"]) == 1
max_int_dev <- max(abs(obs_int - PUB_INTERCEPT))
cat(sprintf("\nclaimed order best on intercepts: %s (max |dev| %.4f); best on within variance: %s\n",
            best_int, max_int_dev, best_wvar))
cat("Not established: Item-number -> prompt text (rests on the supplement's code labels\n",
    "and the paper's (a)(b)(c) order); anchor direction (no reverse-keyed item).\n", sep = "")

cat(if (n_ok && best_int && best_wvar && max_int_dev < 0.02) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
