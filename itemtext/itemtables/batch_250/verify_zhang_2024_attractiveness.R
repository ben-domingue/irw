# verify_zhang_2024_attractiveness.R -- Step 5b check, batch_250.
#
# Claim: live ATR1..ATR4 are the paper's ATR1..ATR4 (Zhang & Liu 2024, PLOS ONE
# 19(2): e0296908), stored raw on 1 = Strongly disagree .. 5 = Strongly agree, and
# item_text for ATRn is item n of the S1 Appendix "Streamer attractiveness" list.
#
# What this CAN test: (a) each live code reproduces the paper's Table 2 standardized
# loading for that code (0.778 / 0.830 / 0.815 / 0.946) under a one-factor CFA, so
# the live codes are the paper's codes and are not permuted among themselves;
# (b) the ATR composite mean/SD reproduces Table 3 (3.847 / 1.027), so items are
# stored raw in the paper's direction.
# What it CANNOT test: the wording -> code tie. The appendix numbers the items 1-4
# without printing codes, and the paper publishes no per-item statistic keyed to
# wording; all four items are same-construct, same-polarity agreement items. So
# ATRn = appendix item n rests on the numbering alone (paper_order, NO_ROUTE).

suppressMessages({library(irw); library(lavaan)})
TABLE <- "zhang_2024_attractiveness"
PUB_LOAD <- c(ATR1 = 0.778, ATR2 = 0.830, ATR3 = 0.815, ATR4 = 0.946)
PUB_MEAN <- 3.847; PUB_SD <- 1.027
TOL_LOAD <- 0.02; TOL_M <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, c("id", names(PUB_LOAD))]
cat("respondents:", nrow(w), " complete:", sum(complete.cases(w)), "\n\n")

cat("per-item level counts (1..5):\n")
print(t(sapply(names(PUB_LOAD), function(i) table(factor(w[[i]], levels = 1:5)))))

fit <- cfa("ATR =~ ATR1 + ATR2 + ATR3 + ATR4", data = w, std.lv = TRUE)
st <- standardizedSolution(fit)
st <- st[st$op == "=~", ]
obs <- setNames(st$est.std, st$rhs)[names(PUB_LOAD)]
cat(sprintf("\n%-6s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in names(PUB_LOAD))
  cat(sprintf("%-6s %10.3f %10.3f %8.3f\n", i, PUB_LOAD[i], obs[i], obs[i] - PUB_LOAD[i]))

# Would a permutation of the codes also fit? Show the best non-identity assignment.
perms <- function(v) if (length(v) <= 1) list(v) else
  do.call(c, lapply(seq_along(v), function(k) lapply(perms(v[-k]), function(p) c(v[k], p))))
dev <- sapply(perms(1:4), function(p) max(abs(obs[p] - PUB_LOAD)))
cat(sprintf("\nidentity max|diff| = %.3f; best non-identity permutation max|diff| = %.3f\n",
            dev[1], min(dev[-1])))

comp <- rowMeans(w[, names(PUB_LOAD)])
cat(sprintf("ATR composite mean %.3f (pub %.3f), SD %.3f (pub %.3f)\n",
            mean(comp, na.rm = TRUE), PUB_MEAN, sd(comp, na.rm = TRUE), PUB_SD))

cat("\nNOT established: which appendix wording belongs to which code. The loadings\n",
    "pin the live codes to the paper's codes, not the text to the codes.\n", sep = "")

ok <- max(abs(obs - PUB_LOAD)) <= TOL_LOAD &&
      abs(mean(comp, na.rm = TRUE) - PUB_MEAN) <= TOL_M &&
      abs(sd(comp, na.rm = TRUE) - PUB_SD) <= TOL_M
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
