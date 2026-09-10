# verify_ngo_2025_green_subjective_norm.R -- Step 5b re-runnable evidence.
#
# STATUS RECORDED: NO_ROUTE for the item_text <-> item axis.
#
# The claim under test is that the S2 File ("Research instruments",
# 10.1371/journal.pone.0323879.s002) lists its four "Green subjective norm"
# sentences in the order G_SN_1 .. G_SN_4.  The S2 File prints NO item codes,
# and the paper's Table 2 prints codes with loadings but NO wording, so nothing
# joins a sentence to a code and that order assumption is not testable.
#
# This script therefore
#   (a) reproduces the half of the mapping that IS exact -- the live item codes
#       are the deposit's own column headers, checked cell for cell;
#   (b) confirms the four live columns really are the paper's G_SN block
#       (Cronbach alpha and first-PC loadings vs the published Table 2 values),
#       which pins BLOCK membership but not order within the block; and
#   (c) demonstrates positively that the one visible within-block structure -- a
#       clean low/high 2-2 split of the item means -- is NOT semantic and so
#       cannot pin any item: the identical odd-low / even-high alternation
#       appears in ALL FIVE constructs of this deposit, whose item contents have
#       nothing in common.  That is a property of the data, not of the wording.
#
# PASS means (a) and (b) reproduce and (c) still holds.  It does NOT mean any
# sentence-to-code assignment was verified.

suppressMessages(library(irw))

TABLE <- "ngo_2025_green_subjective_norm"
ITEMS <- c("G_SN_1", "G_SN_2", "G_SN_3", "G_SN_4")

# Published values, paper Table 2 (10.1371/journal.pone.0323879.t002), read from
# the .t002 image (the table is served as a PNG, not as text).
PUB_LOADING <- c(G_SN_1 = 0.849, G_SN_2 = 0.832, G_SN_3 = 0.845, G_SN_4 = 0.849)
PUB_ALPHA   <- 0.866

S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0323879.s001")

raw <- read.csv(S1, check.names = FALSE)
names(raw) <- sub("^﻿", "", names(raw))
d   <- irw::irw_fetch(TABLE)

## (a) live codes vs deposit column headers -------------------------------
cat("== (a) live item codes vs S1 File column headers: full 1-5 frequency table ==\n")
cat(sprintf("%-8s %-24s %-24s %s\n", "item", "S1 column counts", "live counts", "match"))
ok_a <- TRUE
for (it in ITEMS) {
    r <- as.integer(table(factor(raw[[it]],                levels = 1:5)))
    l <- as.integer(table(factor(d$resp[d$item == it],     levels = 1:5)))
    m <- identical(r, l); ok_a <- ok_a && m
    cat(sprintf("%-8s %-24s %-24s %s\n", it,
                paste(r, collapse = "/"), paste(l, collapse = "/"),
                if (m) "yes" else "NO"))
}

## (b) block identity ------------------------------------------------------
cat("\n== (b) are these four live columns the paper's G_SN block? ==\n")
M <- as.matrix(raw[, ITEMS]); k <- ncol(M)
alpha <- (k / (k - 1)) * (1 - sum(apply(M, 2, var)) / var(rowSums(M)))
pc1 <- prcomp(scale(M))$x[, 1]
if (cor(pc1, rowSums(M)) < 0) pc1 <- -pc1
load <- sapply(ITEMS, function(it) cor(M[, it], pc1))
cat(sprintf("Cronbach alpha: observed %.3f vs published %.3f (diff %.4f)\n",
            alpha, PUB_ALPHA, alpha - PUB_ALPHA))
cat(sprintf("%-8s %12s %12s %8s\n", "item", "pub loading", "obs PC1 load", "diff"))
for (it in ITEMS)
    cat(sprintf("%-8s %12.3f %12.3f %8.3f\n", it, PUB_LOADING[it], load[it],
                load[it] - PUB_LOADING[it]))
worst <- max(abs(load[ITEMS] - PUB_LOADING[ITEMS]))
cat(sprintf("largest loading deviation: %.3f\n", worst))
ok_b <- abs(alpha - PUB_ALPHA) < 0.01 && worst < 0.05

## (c) the 2-2 mean split is structural, not semantic ----------------------
cat("\n== (c) the only within-block structure is not item-specific ==\n")
mu <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
tot <- rowSums(M)
ir  <- sapply(ITEMS, function(it) cor(M[, it], tot - M[, it]))
cat(sprintf("%-8s %8s %8s %12s\n", "item", "mean", "sd", "item-rest r"))
for (it in ITEMS)
    cat(sprintf("%-8s %8.3f %8.3f %12.3f\n", it, mu[it], sd(M[, it]), ir[it]))

prefixes <- c("G_ATT", "G_SN", "G_PBC", "G_PI", "G_PB")
cat("\nSame odd-low / even-high alternation in every construct of the deposit:\n")
alt <- logical(0)
for (p in prefixes) {
    cols <- paste0(p, "_", 1:4)
    m4 <- sapply(cols, function(cc) mean(raw[[cc]]))
    a  <- max(m4[c(1, 3)]) < min(m4[c(2, 4)])   # both odd items below both even
    alt <- c(alt, a)
    cat(sprintf("  %-6s %s   odd<even: %s\n", p,
                paste(sprintf("%.2f", m4), collapse = " / "), if (a) "yes" else "no"))
}
ok_c <- all(alt)

cat("\nWhat this does NOT establish: which of the four S2 File sentences belongs\n",
    "to which code. Table 2 ties codes to loadings but prints no wording; the S2\n",
    "File prints wording but no codes. Step 5b routes are each unavailable: no\n",
    "per-item means/SDs are published (1); all four items share resp {1..5} (2);\n",
    "the construct is a single 4-item block with no order-dependent published\n",
    "total (3); the wording implies no quantitative parameter (4); there is one\n",
    "factor, not several subscales (5); no item is reverse-worded, and all six\n",
    "inter-item correlations are +0.589..+0.664 (6); no marker item -- and the\n",
    "one candidate semantic signal (8), the 2-2 mean split, is ruled out by (c),\n",
    "since it recurs identically across five constructs with unrelated content.\n",
    "Hence NO_ROUTE, not PARTIAL.\n", sep = "")

cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
