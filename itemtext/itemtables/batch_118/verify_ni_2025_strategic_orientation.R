# verify_ni_2025_strategic_orientation.R
#
# CLAIM UNDER TEST: item codes SO3-1 / SO3-2 / SO3-3 correspond, in that order,
# to the three innovation-strategic-orientation items the paper reports as
# PI-9 / PI-10 / PI-11 in Table 3, and therefore to the paper's prose items
# (1) / (2) / (3) in section 3.2(4), whose wording this table ships.
#
# FALSIFIABLE PREDICTION: Table 3 of Ni & Wang (2025), PLoS ONE 20(6):e0326490,
# prints principal-component factor loadings for the three items:
#   PI-9 = 0.914, PI-10 = 0.920, PI-11 = 0.919.
# Recomputing the within-scale first-principal-component loadings from the LIVE
# IRW table must reproduce those three numbers, item for item. A swap of any two
# item codes changes which loading lands on which code; the three published
# values are distinct at the printed precision (0.914 / 0.920 / 0.919), so all
# six permutations are separable.
#
# WHAT THIS DOES NOT ESTABLISH: the paper's Table 3 keys loadings to PI numbers,
# not to wording. The tie from PI-9/10/11 to the prose items (1)/(2)/(3) rests on
# the paper listing them in questionnaire order. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "ni_2025_strategic_orientation"
ITEMS <- c("SO3-1", "SO3-2", "SO3-3")             # = PI-9, PI-10, PI-11
PUBLISHED <- c(0.914, 0.920, 0.919)               # paper Table 3
TOL <- 0.001

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
m <- as.matrix(w[, paste0("resp.", ITEMS), drop = FALSE])
m <- m[complete.cases(m), , drop = FALSE]
colnames(m) <- ITEMS
cat("respondents with complete SO block:", nrow(m), "\n\n")

R <- cor(m)
cat("observed correlation matrix:\n"); print(round(R, 4)); cat("\n")

e <- eigen(R)
k <- which.max(e$values)
load <- abs(e$vectors[, k] * sqrt(e$values[k]))

cat(sprintf("%-7s %-6s %10s %10s %8s\n", "item", "paper", "published", "observed", "diff"))
for (i in seq_along(ITEMS))
    cat(sprintf("%-7s %-6s %10.3f %10.4f %8.4f\n",
                ITEMS[i], paste0("PI-", 8 + i), PUBLISHED[i], load[i],
                load[i] - PUBLISHED[i]))

worst <- max(abs(round(load, 3) - PUBLISHED))
cat(sprintf("\nlargest deviation: %.4f (tolerance %.3f)\n", worst, TOL))

# Permutation check: no other assignment reproduces the published triple.
perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
cat("\nsum |published - observed| under each permutation of the item codes:\n")
for (p in perms)
    cat(sprintf("  (%s) -> %.4f\n", paste(ITEMS[p], collapse = ","),
                sum(abs(round(load[p], 3) - PUBLISHED))))

cat("\nNote: this pins each item CODE to a PI number in Table 3. It does not by\n",
    "itself pin the prose wording order in section 3.2(4) to those PI numbers,\n",
    "which is why the recorded status is PARTIAL rather than VERIFIED.\n", sep = "")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
