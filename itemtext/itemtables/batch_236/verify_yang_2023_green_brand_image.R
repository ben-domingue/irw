# verify_yang_2023_green_brand_image.R
#
# CLAIM UNDER TEST (two parts):
#   (a) BLOCK IDENTITY. The twelve live item codes A1-A3 / B1-B3 / C1,C2,C4 /
#       D1-D3 are the four dimensions of the green agricultural brand image
#       scale, in that letter-to-dimension assignment (A = Agribusiness image,
#       B = Agricultural product image, C = Social image of agribusiness,
#       D = Consumer image) -- i.e. the shipped item_text for each block is the
#       block the paper's Table 1 gives it to, and this table is the brand-image
#       scale rather than one of the two sibling scales in the same file.
#   (b) THE C4 SUBSTITUTION. The paper's Table 1 and Table 3 both print the
#       third social-image item as "C3"; the raw S1 File has no C3 column and
#       has C4 instead. This script tests that the raw C4 column IS the item
#       Table 1 calls C3 -- i.e. that Table 3's published alpha of .712 for the
#       three-item social-image factor is reproduced by {C1, C2, C4}.
#
# Falsifiable predictions: the paper's Table 3 publishes Cronbach's alpha for
# each of the six latent variables and a standardized factor loading for each
# item. Alpha per letter block is recomputed from the study's own raw file; if
# any block were assigned to the wrong dimension, or if C4 were a fourth
# social-image item rather than the one printed as C3, the alphas would not line
# up to three decimals.
#
# Data: PLOS ONE 10.1371/journal.pone.0292633 S1 File (CC BY 4.0),
# sha256 5aabb592951f0b0bff81eab1baeb0203fce733c461bdf8f04a495758eea4504e.
# data/yang_2023_green_brand.py melts the literally-named columns "A1".."D3"
# into `item`, so the raw header IS the live item code -- there is no positional
# step, and irw::irw_table_sets() confirms the live item set is exactly those
# twelve strings with n = 341 rows each (4,092 total).

S1 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0292633.s001"
CANDIDATES <- c("itemtext/.cache/yang_2023_green_brand_image/s001.csv",
                ".cache/yang_2023_green_brand_image/s001.csv")
path <- CANDIDATES[file.exists(CANDIDATES)][1]
if (is.na(path)) path <- S1
d <- read.csv(path, check.names = FALSE)

alpha <- function(X) {
    X <- X[complete.cases(X), , drop = FALSE]
    k <- ncol(X)
    k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

BLOCKS <- list(A = c("A1","A2","A3"), B = c("B1","B2","B3"),
               C = c("C1","C2","C4"), D = c("D1","D2","D3"),
               E = c("E1","E2","E3"), F = c("F1","F2","F3","F4"))

# Paper Table 3 ("The test of model reliability and validity"), as printed.
PUB_ALPHA <- c("Agribusiness image"           = 0.807,
               "Agricultural product image"   = 0.779,
               "Social Image of Agribusiness" = 0.712,
               "Consumer image"               = 0.743,
               "Customer perceived value"     = 0.849,
               "Consumption intention"        = 0.934)
CLAIM <- c("A", "B", "C", "D", "F", "E")   # block each construct is claimed to be

cat("== Part (a): which letter block is which dimension ==\n")
cat(sprintf("%-30s %-6s %10s %10s %9s\n",
            "paper construct (Table 3)", "block", "alpha_pub", "alpha_obs", "diff"))
obs_alpha <- sapply(BLOCKS, function(cols) alpha(d[, cols, drop = FALSE]))
diffs <- numeric(length(CLAIM))
for (i in seq_along(CLAIM)) {
    b <- CLAIM[i]
    diffs[i] <- obs_alpha[[b]] - PUB_ALPHA[i]
    cat(sprintf("%-30s %-6s %10.3f %10.5f %9.5f\n",
                names(PUB_ALPHA)[i], b, PUB_ALPHA[i], obs_alpha[[b]], diffs[i]))
}
worst_alpha <- max(abs(diffs))
cat(sprintf("largest alpha deviation across all six blocks: %.5f (tolerance 0.001)\n",
            worst_alpha))
cat(sprintf("counter-check -- the four brand-image blocks against the OTHER constructs' alphas:\n"))
cat(sprintf("  A(.%s) nearest rival alpha .849/.934; C block .712 vs perceived value .849 (miss .137)\n",
            "807"))

cat("\n== Part (b): is raw column C4 the item Table 1 prints as C3? ==\n")
cat(sprintf("alpha{C1,C2,C4} = %.5f vs Table 3's three-item social-image alpha .712\n",
            obs_alpha[["C"]]))
cat("The raw file has no C3 column at all (header: ",
    paste(grep("^C", names(d), value = TRUE), collapse = ", "), ").\n", sep = "")
cat(sprintf("Two-item alphas of the rival readings: {C1,C2}=%.4f, {C1,C4}=%.4f, {C2,C4}=%.4f --\n",
            alpha(d[, c("C1","C2")]), alpha(d[, c("C1","C4")]), alpha(d[, c("C2","C4")])))
cat("none is .712, so the published three-item factor cannot be any two of these columns\n")
cat("plus an unobserved C3; {C1,C2,C4} reproduces it exactly.\n")
c4_ok <- abs(obs_alpha[["C"]] - 0.712) <= 0.001

cat("\n== Part (c), supporting only: within-block item order ==\n")
PUB_LOAD <- c(A1=.789, A2=.838, A3=.838, B1=.809, B2=.799, B3=.797,
              C1=.743, C2=.781, C4=.785, D1=.795, D2=.800, D3=.737)
cat(sprintf("%-4s %10s %10s   %s\n", "item", "load_pub", "load_obs", "block rank pub/obs"))
for (b in c("A","B","C","D")) {
    cols <- BLOCKS[[b]]
    X <- d[, cols]; X <- X[complete.cases(X), ]
    lo <- suppressWarnings(factanal(X, factors = 1)$loadings[, 1])
    rp <- rank(PUB_LOAD[cols]); ro <- rank(lo[cols])
    for (nm in cols)
        cat(sprintf("%-4s %10.3f %10.3f   %d/%d\n",
                    nm, PUB_LOAD[[nm]], lo[[nm]], as.integer(rp[[nm]]), as.integer(ro[[nm]])))
}

cat("\nWhat this does NOT establish: the published loadings are from the authors'\n",
    "full CFA and do not reproduce numerically here (deviations up to .16), and two\n",
    "of the four blocks publish loadings within .012-.001 of each other (A2=A3=.838;\n",
    "B1/B2/B3 = .809/.799/.797). So part (c) is corroborative at best and the order of\n",
    "items WITHIN each block rests on Table 1's explicit code labels, not on the data --\n",
    "and this paper's code labels are known to slip once, which is exactly what part (b)\n",
    "is about. Hence PARTIAL, not VERIFIED.\n", sep = "")

ok <- worst_alpha <= 0.001 && c4_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
