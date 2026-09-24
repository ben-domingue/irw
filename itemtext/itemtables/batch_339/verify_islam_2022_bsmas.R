# verify_islam_2022_bsmas.R -- Step 5b mapping verification (copied from
# references/verify_template.R).
#
# CLAIM UNDER TEST: live item code BSMASK is the paper's item BSMASK (K = 1..6),
# and resp 1..5 runs 'very rarely' .. 'very often' as shipped.
#
# ROUTE 1 (per-item published statistics): Islam et al. (2022) PLOS ONE
# 10.1371/journal.pone.0279062, Table 1, publishes Mean, SD, Skewness and
# Kurtosis for BSMAS1..BSMAS6 (N = 428). Each live item's 4-number signature is
# compared to every published row; the claim holds only if every item is nearest
# its own row. BSMAS4 and BSMAS6 tie on mean (2.484 vs 2.493), so SD, skewness
# and kurtosis are what separate them.
#
# ROUTE 9-adjacent (option direction): Table 4 reports r = .225 between the
# BSMAS total and daily hours of internet use. The live table carries that
# covariate (cov_hours_internet_use); with resp 1 = 'very rarely' .. 5 = 'very
# often' the live r must be positive and near .225. A reversed scale would give
# r near -.225.
#
# NOT ESTABLISHED by this script -- and this is the part that matters: the paper
# never prints BSMAS item wording, and the source file's headers are bare codes
# (BSMAS1..BSMAS6) with no labels. Every published statistic is keyed to those
# same bare codes. So this route proves the codes are the paper's own and the
# direction is right, but NOTHING in the source ties BSMASK to a wording. That
# tie rests on the convention that BSMASK = canonical BSMAS item K (Andreassen et
# al. 2016 numbering, as reproduced in Ozimek et al. 2025, Behav Sci 15(12):1719,
# PMC12729781, Table A5). If the Bangla form were administered in a different
# order, the shipped text would be permuted and this script would still PASS.

suppressMessages(library(irw))

TABLE <- "islam_2022_bsmas"
ITEMS <- paste0("BSMAS", 1:6)

# Published Table 1 (N = 428): Mean, SD, Skewness, Kurtosis.
PUB <- rbind(
  BSMAS1 = c(2.411, 1.332, 0.466, -0.903),
  BSMAS2 = c(2.367, 1.280, 0.551, -0.712),
  BSMAS3 = c(2.621, 1.421, 0.274, -1.221),
  BSMAS4 = c(2.484, 1.400, 0.465, -1.050),
  BSMAS5 = c(2.250, 1.360, 0.723, -0.738),
  BSMAS6 = c(2.493, 1.441, 0.449, -1.141))
colnames(PUB) <- c("mean", "sd", "skew", "kurt")
PUB_R_INTERNET <- 0.225

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)

skew <- function(x) { m <- mean(x); n <- length(x); s <- sd(x)
  (sum((x - m)^3) / n) / (sum((x - m)^2) / n)^1.5 }
kurt <- function(x) { m <- mean(x); n <- length(x)
  (sum((x - m)^4) / n) / (sum((x - m)^2) / n)^2 - 3 }

OBS <- t(sapply(ITEMS, function(it) { x <- d$resp[d$item == it]
  c(mean = mean(x), sd = sd(x), skew = skew(x), kurt = kurt(x)) }))

cat("Per-item statistics, published (Table 1) vs live:\n")
cat(sprintf("%-7s %6s %6s | %6s %6s | %6s %6s | %6s %6s\n", "item",
            "M_pub", "M_liv", "SD_pub", "SD_liv", "Sk_pub", "Sk_liv", "Ku_pub", "Ku_liv"))
for (it in ITEMS)
  cat(sprintf("%-7s %6.3f %6.3f | %6.3f %6.3f | %6.3f %6.3f | %6.3f %6.3f\n", it,
              PUB[it, 1], OBS[it, 1], PUB[it, 2], OBS[it, 2],
              PUB[it, 3], OBS[it, 3], PUB[it, 4], OBS[it, 4]))

# Nearest-row test: Euclidean distance between each live signature and every
# published row. (Skew/kurtosis estimators differ slightly across software, so
# absolute agreement is judged loosely; identification is judged by nearest row.)
D <- as.matrix(dist(rbind(OBS, PUB)))[1:6, 7:12]
dimnames(D) <- list(paste0("live_", ITEMS), paste0("pub_", ITEMS))
nearest <- colnames(D)[apply(D, 1, which.min)]
self <- diag(D)
nextbest <- sapply(1:6, function(i) min(D[i, -i]))
cat("\nNearest published row for each live item:\n")
for (i in 1:6)
  cat(sprintf("  %-7s -> %-11s self-dist %.3f  next-best %.3f\n",
              ITEMS[i], nearest[i], self[i], nextbest[i]))
ok_rows <- all(nearest == paste0("pub_", ITEMS))
worst_mean <- max(abs(OBS[, "mean"] - PUB[, "mean"]))
worst_sd <- max(abs(OBS[, "sd"] - PUB[, "sd"]))
cat(sprintf("largest |mean| deviation %.4f, largest |SD| deviation %.4f\n", worst_mean, worst_sd))

# Direction: BSMAS total vs daily hours of internet use.
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
w$total <- rowSums(w[, paste0("resp.", ITEMS)])
cov <- unique(d[, c("id", "cov_hours_internet_use")])
w <- merge(w, cov, by = "id")
r <- cor(w$total, w$cov_hours_internet_use, use = "complete.obs")
cat(sprintf("\nBSMAS total vs daily internet hours: published r = %.3f, live r = %.3f (n = %d)\n",
            PUB_R_INTERNET, r, sum(complete.cases(w$total, w$cov_hours_internet_use))))
ok_dir <- r > 0 && abs(r - PUB_R_INTERNET) < 0.02

cat("\nNOT established: which WORDING belongs to which code. The source ties codes to\n",
    "statistics only; code->text rests on canonical BSMAS numbering (see header).\n", sep = "")

cat(if (ok_rows && worst_mean < 0.005 && worst_sd < 0.005 && ok_dir) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
