# verify_yang_2023_consumption_intent.R
#
# CLAIM UNDER TEST (two parts):
#   (a) The IRW table named `yang_2023_consumption_intent` holds columns F1-F4 of
#       the PLOS ONE S1 File, and per the source paper that block is the CUSTOMER
#       PERCEIVED VALUE scale -- NOT consumption intention (which is E1-E3, shipped
#       as `yang_2023_perceived_value`). The two IRW table names are swapped.
#   (b) Within that block, the item_text shipped for F1..F4 is the Table 1 wording
#       carrying those same codes.
#
# Part (a) is falsifiable: the paper's Table 3 publishes Cronbach's alpha per latent
# variable. Recomputing alpha per letter block from the raw file identifies which
# construct each block is, to three decimals.
# Part (b) is falsifiable via Table 3's per-item standardized factor loadings.
#
# Data: PLOS ONE 10.1371/journal.pone.0292633 S1 File (CC BY 4.0). The IRW script
# data/yang_2023_green_brand.py melts the literally-named columns "F1".."F4" into
# `item`, so the raw header IS the live item code -- no positional step to check.

S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0292633.s001"
CACHE <- "itemtext/.cache/yang_2023_consumption_intent/s001.raw"
path <- if (file.exists(CACHE)) CACHE else
        if (file.exists(".cache/yang_2023_consumption_intent/s001.raw"))
            ".cache/yang_2023_consumption_intent/s001.raw" else S1
d <- read.csv(path, check.names = FALSE)

alpha <- function(X) {
    X <- X[complete.cases(X), , drop = FALSE]
    k <- ncol(X)
    k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

BLOCKS <- list(
    A = c("A1","A2","A3"), B = c("B1","B2","B3"), C = c("C1","C2","C4"),
    D = c("D1","D2","D3"), E = c("E1","E2","E3"), F = c("F1","F2","F3","F4"))

# Paper Table 3, in the order the table prints them.
PUB_ALPHA <- c("Agribusiness image" = 0.807, "Agricultural product image" = 0.779,
               "Social Image of Agribusiness" = 0.712, "Consumer image" = 0.743,
               "Customer perceived value" = 0.849, "Consumption intention" = 0.934)
# The block each of those constructs is claimed to be (paper Tables 1 and 3).
CLAIM <- c("A", "B", "C", "D", "F", "E")

cat("== Part (a): which letter block is which construct ==\n")
cat(sprintf("%-28s %-7s %10s %10s %8s\n",
            "paper construct (Table 3)", "block", "alpha_pub", "alpha_obs", "diff"))
obs_alpha <- sapply(BLOCKS, function(cols) alpha(d[, cols, drop = FALSE]))
diffs <- numeric(length(CLAIM))
for (i in seq_along(CLAIM)) {
    b <- CLAIM[i]
    diffs[i] <- obs_alpha[[b]] - PUB_ALPHA[i]
    cat(sprintf("%-28s %-7s %10.3f %10.3f %8.4f\n",
                names(PUB_ALPHA)[i], b, PUB_ALPHA[i], obs_alpha[[b]], diffs[i]))
}
worst_alpha <- max(abs(diffs))
cat(sprintf("largest alpha deviation: %.4f (tolerance 0.001)\n", worst_alpha))
cat(sprintf("counter-check -- F block against the CONSUMPTION INTENTION alpha: %.3f vs %.3f (miss of %.3f)\n",
            obs_alpha[["F"]], PUB_ALPHA[["Consumption intention"]],
            abs(obs_alpha[["F"]] - PUB_ALPHA[["Consumption intention"]])))

cat("\n== Part (b): within-block item order, F1..F4 ==\n")
PUB_LOAD <- c(F1 = 0.809, F2 = 0.738, F3 = 0.728, F4 = 0.823)
Fb <- d[, c("F1","F2","F3","F4")]
Fb <- Fb[complete.cases(Fb), ]
load1 <- factanal(Fb, factors = 1)$loadings[, 1]
cat(sprintf("%-6s %12s %12s\n", "item", "load_pub", "load_obs"))
for (nm in names(PUB_LOAD))
    cat(sprintf("%-6s %12.3f %12.3f\n", nm, PUB_LOAD[[nm]], load1[[nm]]))
rho <- suppressWarnings(cor(PUB_LOAD, load1[names(PUB_LOAD)], method = "spearman"))
cat(sprintf("Spearman(published, observed loadings) = %.2f over 4 items\n", rho))

cat("\nWhat this does NOT establish: the loading pattern separates {F1,F4} (high)\n",
    "from {F2,F3} (low) but not F1 from F4 (published .809 vs .823; observed order\n",
    "reverses) nor F2 from F3 (.738 vs .728). Within-pair order rests on Table 1's\n",
    "explicit code labels, and this paper's code labels are known to slip once\n",
    "(Table 1 prints C3 where the raw file has C4). Hence PARTIAL, not VERIFIED.\n", sep = "")

ok <- worst_alpha <= 0.001 && rho >= 0.8
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
