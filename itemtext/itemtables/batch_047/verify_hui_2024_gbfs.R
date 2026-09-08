# verify_hui_2024_gbfs.R -- Step 5b evidence, re-runnable.
#
# CLAIM: IRW item code b<n> carries the wording printed as item <n> of the
# Chinese GBFS questionnaire in S1 File of Hui et al. (2024) PLOS ONE 19(5):
# e0300064 (10.1371/journal.pone.0300064.s001).
#
# FALSIFIABLE PREDICTION: the same paper's Table 3 (.t003) publishes, for each
# of its numbered items 1-28, M (SD), skewness, kurtosis and the item-total
# correlation, computed on the same Phase-3 sample (N = 309) that IRW ships.
# Skewness and kurtosis are given to 3 decimals and all 28 values are distinct,
# so they are a per-item fingerprint: if item_text for any two items were
# swapped, the corresponding pair of fingerprints would swap with it.
#
# What this does NOT establish: that Table 3's item numbering is the same
# numbering the S1 questionnaire prints. That link is internal to one paper and
# is corroborated separately, by the subscale block structure -- the paper
# assigns items 1-5 acceptance, 6-9 family bonds, 10-15 growth, 16-19
# relationships, 20-24 empathy, 25-28 reprioritisation, and the S1 wording at
# each of those positions is of that content. The correlation check at the end
# of this script tests that block structure against the live data.

suppressMessages(library(irw))

TABLE <- "hui_2024_gbfs"

# Hui et al. (2024) Table 3, "Items 1-28": M (SD), skewness, kurtosis.
PUB <- data.frame(
  n    = 1:28,
  M    = c(3.4,3.8,3.6,3.6,3.8,3.6,3.9,4.0,4.0,3.5,3.8,3.9,3.8,3.8,
           4.0,3.8,3.9,3.3,3.6,4.0,3.7,3.8,4.0,3.9,3.5,3.2,3.5,3.9),
  SD   = c(1.01,0.85,0.97,0.96,0.97,1.00,0.90,0.89,0.91,0.99,0.88,0.86,0.97,0.92,
           0.81,0.95,0.85,1.01,0.96,0.85,0.98,0.90,0.88,0.88,1.05,1.04,0.99,0.89),
  skew = c(-0.414,-0.653,-0.491,-0.636,-0.673,-0.360,-0.660,-0.680,-0.810,-0.427,
           -0.685,-0.865,-0.704,-0.728,-0.861,-0.691,-0.566,-0.231,-0.499,-0.981,
           -0.571,-0.419,-1.111,-0.881,-0.339,-0.057,-0.346,-0.764),
  kurt = c(-0.291,0.457,-0.280,0.099,0.216,-0.405,0.254,0.035,0.390,-0.284,
           0.439,0.961,0.259,0.609,1.199,0.011,0.242,-0.317,0.135,1.440,
           0.033,-0.212,1.729,0.993,-0.406,-0.622,-0.362,0.647)
)

g1 <- function(x) { n <- length(x); z <- (x - mean(x)) / sd(x)
                    n / ((n - 1) * (n - 2)) * sum(z^3) }
g2 <- function(x) { n <- length(x); z <- (x - mean(x)) / sd(x)
                    n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) * sum(z^4) -
                    3 * (n - 1)^2 / ((n - 2) * (n - 3)) }

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)

cat(sprintf("%-5s %6s %6s | %6s %6s | %8s %8s | %8s %8s | %s\n",
            "item", "M.pub", "M.obs", "SD.pub", "SD.obs",
            "skew.pub", "skew.obs", "kurt.pub", "kurt.obs", "ok"))
bad <- 0
for (k in 1:28) {
    x <- d$resp[d$item == paste0("b", k)]
    m <- mean(x); s <- sd(x); sk <- g1(x); ku <- g2(x)
    p <- PUB[k, ]
    # M is published to 1 dp only, so it is the loosest of the four columns;
    # skewness and kurtosis (3 dp) are what actually separate the items.
    ok <- abs(m - p$M) <= 0.06 && abs(s - p$SD) <= 0.01 &&
          abs(sk - p$skew) <= 0.001 && abs(ku - p$kurt) <= 0.001
    if (!ok) bad <- bad + 1
    cat(sprintf("%-5s %6.1f %6.2f | %6.2f %6.3f | %8.3f %8.3f | %8.3f %8.3f | %s\n",
                paste0("b", k), p$M, m, p$SD, s, p$skew, sk, p$kurt, ku,
                if (ok) "OK" else "MISMATCH"))
}
cat(sprintf("\nper-item fingerprint mismatches: %d of 28\n", bad))

# Are the published fingerprints actually distinct? (If they were not, matching
# them would not separate the items and the route would prove nothing.)
dup <- sum(duplicated(paste(PUB$skew, PUB$kurt)))
cat(sprintf("duplicate (skew,kurt) pairs among the 28 published items: %d\n", dup))

# Corroboration of the questionnaire numbering: subscale block structure.
grp <- c(rep("acceptance", 5), rep("family", 4), rep("growth", 6),
         rep("relationships", 4), rep("empathy", 5), rep("reprioritisation", 4))
names(grp) <- paste0("b", 1:28)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
mat <- as.matrix(w[, paste0("resp.b", 1:28)])
colnames(mat) <- paste0("b", 1:28)
C <- cor(mat, use = "pairwise.complete.obs")
hit <- 0
for (k in 1:28) {
    it <- paste0("b", k)
    r <- C[it, ]; r[it] <- NA
    nn <- names(which.max(r))
    hit <- hit + (grp[[nn]] == grp[[it]])
}
cat(sprintf("nearest-neighbour item in the same published subscale: %d of 28\n", hit))

cat(if (bad == 0 && dup == 0 && hit >= 24) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
