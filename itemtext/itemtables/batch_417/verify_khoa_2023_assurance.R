# verify_khoa_2023_assurance.R -- Step 5b, route 1 (per-item descriptive statistics).
#
# Claim: live items ASS1..ASS3 carry the wording that Khoa & Huynh (2023, Data in Brief
# 49:109454, PMC10415701) Table 2 prints against the codes ASS1..ASS3. The live item code IS
# the deposit CSV's column name (data/khoa_2023_knowledge_management.py melts the columns
# unchanged), so the only thing to establish is that the live columns are the ones the paper
# describes under those codes. Paper Table 4 publishes per-item mean, SD, skewness and
# kurtosis for ASS1..ASS3; a swap of any two items' text would require their statistics to
# swap too.
#
# Caveat built into the tolerances: the paper's Table 4 was computed on the raw deposit,
# which holds two out-of-range 6s on ASS2; the IRW script drops them (n=674 live vs 676),
# so ASS2's live moments differ slightly from the published ones. The raw deposit reproduces
# Table 4 exactly (ASS2 mean 3.969, SD 1.100).

suppressMessages(library(irw))

TABLE <- "khoa_2023_assurance"
items <- c("ASS1", "ASS2", "ASS3")
PUB <- data.frame(item = items,
                  mean = c(4.05, 3.97, 3.96),
                  sd   = c(0.990, 1.100, 1.014),
                  skew = c(-1.008, -1.024, -0.833),
                  kurt = c(0.726, 0.643, 0.351))

d <- irw::irw_fetch(TABLE)
skew <- function(x) { n <- length(x); m <- mean(x); s <- sd(x)
  n / ((n - 1) * (n - 2)) * sum(((x - m) / s)^3) }
kurt <- function(x) { n <- length(x); m <- mean(x); s <- sd(x)
  n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) * sum(((x - m) / s)^4) -
    3 * (n - 1)^2 / ((n - 2) * (n - 3)) }
obs <- do.call(rbind, lapply(items, function(i) { x <- d$resp[d$item == i]
  data.frame(item = i, n = length(x), mean = mean(x), sd = sd(x), skew = skew(x), kurt = kurt(x)) }))

cat(sprintf("%-5s %4s | %6s %6s | %6s %6s | %7s %7s | %6s %6s\n",
            "item", "n", "pubM", "obsM", "pubSD", "obsSD", "pubSk", "obsSk", "pubK", "obsK"))
for (k in seq_along(items))
  cat(sprintf("%-5s %4d | %6.2f %6.3f | %6.3f %6.3f | %7.3f %7.3f | %6.3f %6.3f\n", items[k], obs$n[k],
              PUB$mean[k], obs$mean[k], PUB$sd[k], obs$sd[k], PUB$skew[k], obs$skew[k], PUB$kurt[k], obs$kurt[k]))

# Each live item must match its own published row better than any other published row
# (distance on standardised mean+SD+skew+kurt), and be within tolerance of it.
D <- outer(seq_along(items), seq_along(items), Vectorize(function(a, b)
  abs(obs$mean[a] - PUB$mean[b]) / 0.05 + abs(obs$sd[a] - PUB$sd[b]) / 0.02 +
  abs(obs$skew[a] - PUB$skew[b]) / 0.05 + abs(obs$kurt[a] - PUB$kurt[b]) / 0.1))
dimnames(D) <- list(paste0("live_", items), paste0("pub_", items))
cat("\nDistance matrix (live row vs published row; lower = closer):\n"); print(round(D, 2))
best <- apply(D, 1, which.min)
tol_ok <- all(abs(obs$mean - PUB$mean) <= 0.02, abs(obs$sd - PUB$sd) <= 0.01,
              abs(obs$skew - PUB$skew) <= 0.05, abs(obs$kurt - PUB$kurt) <= 0.10)
cat("\nBest published match per live item:", paste(items, "->", items[best]), "\n")
cat("All moments within tolerance (mean .02, SD .01, skew .05, kurt .10):", tol_ok, "\n")
cat("Not established: that respondents read this English wording (administration language\n",
    "is not stated; see notes). ASS2 vs ASS3 means are 0.01 apart -- SD/skew/kurtosis separate them.\n", sep = "")
cat(if (tol_ok && all(best == seq_along(items))) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
