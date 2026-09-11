# verify_thanh_2025_attitude.R -- Step 5b mapping check for thanh_2025_attitude (batch_187).
#
# Claim: ATT1..ATT5 carry S1 Appendix items "Attitude 1".."Attitude 5" of Thanh & Cong (2025),
# PLoS ONE 20(3): e0320053. The paper's Table 2 prints item WORDING next to its PLS-SEM outer
# loading for the three retained Attitude items (plus 19 retained items of the other four
# constructs), and Table 2/3 give Attitude alpha 0.774, CR 0.868, AVE 0.688.
#
# Falsifiable prediction: re-estimating the published PLS path model (EC->ATT, EC->PBC, EC->GK,
# ATT/PBC/GK/EC->EGB; path-weighting scheme) on the LIVE tables, with the retained items taken
# as the items whose wording Table 2 prints, reproduces every published loading to rounding.
# The ATT1/ATT2/ATT3 loadings are 0.8174/0.8359/0.8341, so the wording->code tie is pinned for
# those three items, including the ATT2-vs-ATT3 near-tie (a swap misses both by ~0.002, four
# times the 0.0005 rounding slack).
#
# NOT established: ATT4 vs ATT5. Both were dropped by the authors, no statistic is published
# for them, and their live responses are uncorrelated with every other column (|r| <= 0.11),
# so no data route can separate them; their tie rests on the S1 Appendix numbering alone.

suppressMessages(library(irw))

get_wide <- function(tb) {
  d <- as.data.frame(irw::irw_fetch(tb))[, c("id", "item", "resp")]
  w <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
  names(w) <- sub("^resp\\.", "", names(w))
  w
}
tabs <- c("thanh_2025_attitude", "thanh_2025_green_behavior", "thanh_2025_environ_concern",
          "thanh_2025_perceived_control", "thanh_2025_green_knowledge")
X <- Reduce(function(a, b) merge(a, b, by = "id"), lapply(tabs, get_wide))
cat("respondents joined across the five live tables:", nrow(X), "\n\n")

blocks <- list(EGB = paste0("EGB", 1:5), ATT = paste0("ATT", 1:3), EC = paste0("EC", 1:5),
               PBC = paste0("PBC", 1:5), GK = paste0("GK", 1:4))
pub <- list(EGB = c(.774, .880, .831, .832, .758), ATT = c(.817, .836, .834),
            EC = c(.877, .882, .853, .912, .926), PBC = c(.831, .901, .888, .900, .826),
            GK = c(.908, .902, .922, .906))
paths <- rbind(c("EC", "ATT"), c("EC", "PBC"), c("EC", "GK"), c("ATT", "EGB"),
               c("PBC", "EGB"), c("GK", "EGB"), c("EC", "EGB"))

pls_loadings <- function(blocks) {
  L <- names(blocks)
  Z <- scale(X[, unlist(blocks)])
  score <- function(w) sapply(L, function(l) as.numeric(scale(Z[, blocks[[l]], drop = FALSE] %*% w[[l]])))
  w <- lapply(blocks, function(b) rep(1, length(b)))
  for (it in 1:500) {
    Y <- score(w)
    E <- matrix(0, length(L), length(L), dimnames = list(L, L))
    for (l in L) {
      for (s in paths[paths[, 1] == l, 2]) E[l, s] <- cor(Y[, l], Y[, s])
      pred <- paths[paths[, 2] == l, 1]
      if (length(pred)) E[l, pred] <- coef(lm(Y[, l] ~ Y[, pred, drop = FALSE] - 1))
    }
    inner <- Y %*% t(E)
    wn <- setNames(lapply(L, function(l) as.numeric(cor(Z[, blocks[[l]], drop = FALSE], inner[, l]))), L)
    if (max(abs(unlist(wn) - unlist(w))) < 1e-10) break
    w <- wn
  }
  Y <- score(w)
  setNames(lapply(L, function(l) cor(Z[, blocks[[l]], drop = FALSE], Y[, l])[, 1]), L)
}

TOL <- 0.0006   # 3-dp rounding slack (0.0005) plus float noise
ld <- pls_loadings(blocks)
cat(sprintf("%-6s %9s %9s %8s\n", "item", "live_PLS", "published", "diff"))
dev <- c()
for (l in names(blocks)) for (k in seq_along(blocks[[l]])) {
  dd <- ld[[l]][k] - pub[[l]][k]; dev <- c(dev, dd)
  cat(sprintf("%-6s %9.4f %9.3f %8.4f\n", blocks[[l]][k], ld[[l]][k], pub[[l]][k], dd))
}
worst <- max(abs(dev))
cat(sprintf("\nall 22 loadings: largest |diff| %.4f (tol %.4f)\n", worst, TOL))
att_dev <- max(abs(ld$ATT - pub$ATT))

# Alternative assignments of the three worded Attitude rows to live codes.
alts <- list(c("ATT1", "ATT3", "ATT2"), c("ATT2", "ATT1", "ATT3"), c("ATT3", "ATT2", "ATT1"),
             c("ATT1", "ATT2", "ATT4"), c("ATT1", "ATT2", "ATT5"))
alt_min <- Inf
for (a in alts) {
  b2 <- blocks; b2$ATT <- a
  e <- max(abs(pls_loadings(b2)$ATT - pub$ATT)); alt_min <- min(alt_min, e)
  cat(sprintf("alternative ATT rows = %-16s worst ATT |diff| %.4f\n", paste(a, collapse = ","), e))
}

alpha <- function(m) { k <- ncol(m); k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m))) }
trip <- combn(paste0("ATT", 1:5), 3)
al <- apply(trip, 2, function(ix) alpha(X[, ix]))
names(al) <- apply(trip, 2, paste, collapse = "+")
cat("\nCronbach alpha by retained triple (published Attitude alpha 0.774):\n")
print(round(sort(al, decreasing = TRUE), 3))
l <- ld$ATT
cat(sprintf("ATT CR %.3f (pub 0.868)  AVE %.3f (pub 0.688)\n",
            sum(l)^2 / (sum(l)^2 + sum(1 - l^2)), mean(l^2)))

R <- cor(X[, paste0("ATT", 1:5)])
cat("\nATT4/ATT5 max |r| with ATT1-3:", round(max(abs(R[4:5, 1:3])), 3),
    "-- no data route separates ATT4 from ATT5 (not established by this script).\n")

ok <- worst <= TOL && alt_min > TOL && names(al)[which.max(al)] == "ATT1+ATT2+ATT3" &&
  abs(max(al) - 0.774) <= TOL
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
