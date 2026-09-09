# verify_li_2025_corporate_performance.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the ten labels shipped as item_text
# are the "6. Corporate performance (PERF)" block of Table 3 in Li et al. (2025)
# PLOS ONE 20(6):e0326329, read in the printed order Net Profit, Sales Profit Margin,
# Cash Flow, Return on Investment (ROI), Operating Costs, Sales Growth Rate,
# Market Share, Development of New Products, Market Expansion, Research and
# Development Achievements, assigned to live items Perfo416..Perfo425 in that order.
#
# The .sav deposit carries NO variable labels (only value labels), so nothing in the
# data file ties Perfo4xx to a label; the tie is Table 3's presentation order alone.
#
# ROUTE 1 (published per-item statistics). Table 3 is an IMAGE -- its numbers exist in
# no machine-readable form -- and prints a standardized factor loading (SFL) for each
# of the ten items. Refitting a one-factor CFA on the live data must reproduce them.
#
# WHAT THIS DOES NOT ESTABLISH: the ten published loadings span only 0.774-0.813 and
# contain exact ties (0.780 at printed positions 2 and 9; 0.807 at positions 5 and 10)
# and near-ties (0.774/0.776/0.779/0.780). Reproducing them pins the block's ORDER as
# a whole -- a random permutation is excluded -- but cannot separate the tied and
# near-tied labels from one another. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "li_2025_corporate_performance"
ITEMS <- paste0("Perfo4", 16:25)
LABEL <- c("Net Profit", "Sales Profit Margin", "Cash Flow", "Return on Investment (ROI)",
           "Operating Costs", "Sales Growth Rate", "Market Share",
           "Development of New Products", "Market Expansion",
           "Research and Development Achievements")
# Li et al. (2025) PLOS ONE 20(6):e0326329, Table 3, block 6 (PERF), SFL column.
PUB <- c(0.813, 0.780, 0.774, 0.804, 0.807, 0.808, 0.776, 0.779, 0.780, 0.807)
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]),
             idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[, ITEMS]
w <- w[complete.cases(w), ]
cat(sprintf("live data: %d respondents x %d items\n\n", nrow(w), length(ITEMS)))

fit <- lavaan::cfa(paste("F =~", paste(ITEMS, collapse = " + ")), data = w, std.lv = TRUE)
p <- lavaan::parameterEstimates(fit, standardized = TRUE)
p <- p[p$op == "=~", ]
obs <- setNames(p$std.all, p$rhs)[ITEMS]

cat("ROUTE 1 -- one-factor CFA loadings vs Table 3's SFL column\n")
cat(sprintf("%-9s %-38s %9s %9s %8s\n", "item", "shipped item_text", "pub.SFL", "obs.SFL", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-9s %-38s %9.3f %9.3f %8.3f\n",
                ITEMS[i], LABEL[i], PUB[i], obs[i], obs[i] - PUB[i]))
worst <- max(abs(obs - PUB))
sad   <- sum(abs(obs - PUB))
cat(sprintf("\nlargest deviation: %.3f (tolerance %.2f); sum |diff| = %.3f; r = %.3f\n",
            worst, TOL, sad, cor(obs, PUB)))

# How much better is the shipped assignment than every alternative permutation?
# Full enumeration of 10! is unnecessary: the optimal assignment (minimum sum of
# absolute differences) is found exactly by the Hungarian algorithm.
best_is_identity <- NA
if (requireNamespace("clue", quietly = TRUE)) {
    cost <- outer(obs, PUB, function(a, b) abs(a - b))
    perm <- as.integer(clue::solve_LSAP(cost))
    cat(sprintf("optimal assignment SAD = %.3f (identity %.3f); permutation = %s\n",
                sum(cost[cbind(seq_along(perm), perm)]), sad,
                paste(perm, collapse = " ")))
    best_is_identity <- identical(perm, seq_along(ITEMS))
    cat(sprintf("optimal assignment IS the shipped one: %s -- expected FALSE, see below\n",
                best_is_identity))
}

# Null: how well would an arbitrary permutation of the labels do? This is the
# falsifiable part -- a wrong block order is excluded, a swap among the ties is not.
set.seed(1)
null <- replicate(20000, sum(abs(sample(obs) - PUB)))
frac <- mean(null < sad)
cat(sprintf("null over 20000 random permutations: median SAD %.3f, min %.3f; fraction beating the shipped assignment = %.5f\n",
            median(null), min(null), frac))

# Honest limitation: which single swaps the route cannot rule out.
cat("\nswaps this route does NOT exclude (SAD within 0.010 of the shipped assignment):\n")
n_amb <- 0
for (i in 1:(length(ITEMS) - 1)) for (j in (i + 1):length(ITEMS)) {
    o <- obs; o[c(i, j)] <- o[c(j, i)]
    s <- sum(abs(o - PUB))
    if (s - sad <= 0.010) {
        n_amb <- n_amb + 1
        cat(sprintf("  %s <-> %s   SAD %.3f vs %.3f\n", ITEMS[i], ITEMS[j], s, sad))
    }
}
cat(sprintf("  (%d of 45 pairwise swaps are within tolerance -- this is why the status is PARTIAL)\n", n_amb))

# PASS tests the claim actually made (PARTIAL): the shipped order reproduces the
# published loadings, and essentially no permutation of the labels does as well.
# It deliberately does NOT require the shipped order to be the unique optimum --
# the ties in the published column make that unattainable, which is the limitation
# recorded in the verification row.
pass <- worst <= TOL && frac < 0.001
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
