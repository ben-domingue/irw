# verify_ngo_2025_green_purchase_intention.R -- Step 5b re-runnable evidence.
#
# STATUS RECORDED: NO_ROUTE for the item_text <-> item axis.
#
# The claim under test is that the S2 File ("Research instruments",
# 10.1371/journal.pone.0323879.s002) lists the four "Green purchasing
# intention" sentences in the order G_PI_1 .. G_PI_4.  The S2 File prints NO
# item codes, and the paper's Table 2 prints codes with loadings but NO
# wording, so nothing joins text to code and that order assumption is not
# testable.  This script therefore
#   (a) establishes the half of the mapping that IS exact -- the live item
#       codes are the S1 File's own column headers, checked cell-for-cell via
#       the full 1-5 frequency vector per item, which rules out any positional
#       shift in data/ngo_2025_green_purchasing.py; and
#   (b) demonstrates positively that no statistical route (Step 5b 1-9) can
#       separate the four sentences, so "couldn't check" does not read as
#       "checked".
#
# PASS means (a) reproduces and (b) still holds; it does NOT mean any wording
# was verified.

suppressMessages(library(irw))

TABLE <- "ngo_2025_green_purchase_intention"
ITEMS <- c("G_PI_1", "G_PI_2", "G_PI_3", "G_PI_4")

# Published PLS outer loadings, paper Table 2 (10.1371/journal.pone.0323879.t002,
# an image table; values read from the .t002 PNG).  Published construct alpha .867.
PUB_LOADING <- c(G_PI_1 = 0.841, G_PI_2 = 0.849, G_PI_3 = 0.858, G_PI_4 = 0.833)
PUB_ALPHA   <- 0.867

S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0323879.s001")

raw <- read.csv(S1, check.names = FALSE)
names(raw) <- sub("^﻿", "", names(raw))
d   <- irw::irw_fetch(TABLE)

cat("== (a) live item codes vs S1 File column headers: full 1-5 frequency table ==\n")
cat(sprintf("%-8s %-22s %-22s %s\n", "item", "S1 column counts", "live counts", "match"))
ok_a <- TRUE
for (it in ITEMS) {
    r <- table(factor(raw[[it]], levels = 1:5))
    l <- table(factor(d$resp[d$item == it], levels = 1:5))
    m <- identical(as.integer(r), as.integer(l))
    ok_a <- ok_a && m
    cat(sprintf("%-8s %-22s %-22s %s\n", it,
                paste(as.integer(r), collapse = "/"),
                paste(as.integer(l), collapse = "/"),
                if (m) "yes" else "NO"))
}

cat("\n== (b) block identity: the four live columns are the paper's G_PI indicators ==\n")
X <- raw[, ITEMS]
k <- length(ITEMS)
alpha <- (k / (k - 1)) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
pc1 <- prcomp(X, scale. = TRUE)
ld  <- abs(pc1$rotation[, 1] * pc1$sdev[1])
cat(sprintf("Cronbach alpha over the four live columns = %.4f vs published %.3f (diff %.4f)\n",
            alpha, PUB_ALPHA, abs(alpha - PUB_ALPHA)))
cat(sprintf("%-8s %12s %12s\n", "item", "PC1 loading", "pub loading"))
for (it in ITEMS) cat(sprintf("%-8s %12.3f %12.3f\n", it, ld[it], PUB_LOADING[it]))
cat(sprintf("max |PC1 - published| = %.3f\n", max(abs(ld[ITEMS] - PUB_LOADING[ITEMS]))))
ok_b <- abs(alpha - PUB_ALPHA) < 0.01 && max(abs(ld[ITEMS] - PUB_LOADING[ITEMS])) < 0.05

cat("\n== (c) no statistical route separates the four sentences ==\n")
mu  <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
tot <- rowSums(raw[, ITEMS])
ir  <- sapply(ITEMS, function(it) cor(raw[[it]], tot - raw[[it]]))
cat(sprintf("%-8s %8s %12s %12s\n", "item", "mean", "item-rest r", "pub loading"))
for (it in ITEMS)
    cat(sprintf("%-8s %8.3f %12.3f %12.3f\n", it, mu[it], ir[it], PUB_LOADING[it]))
d13 <- abs(mu["G_PI_1"] - mu["G_PI_3"])
d24 <- abs(mu["G_PI_2"] - mu["G_PI_4"])
cat(sprintf("\n|mean(1) - mean(3)| = %.3f ; |mean(2) - mean(4)| = %.3f\n", d13, d24))
cat(sprintf("Spearman(published loading, observed item-rest r) = %.2f over 4 items\n",
            cor(PUB_LOADING[ITEMS], ir[ITEMS], method = "spearman")))

# The odd/even mean split is NOT a content signal: every one of the five TPB
# constructs in this deposit shows the same alternating low/high pattern, so it
# is a property of the file's column parity, not of the item wording.
ALL <- list(G_ATT = paste0("G_ATT_", 1:4), G_SN = paste0("G_SN_", 1:4),
            G_PBC = paste0("G_PBC_", 1:4), G_PI = ITEMS, G_PB = paste0("G_PB_", 1:4))
cat("\nAlternating odd-low / even-high means recur in ALL five constructs of the\n",
    "deposit, so route 8 (semantic coherence) has no discriminating power here:\n", sep = "")
same_shape <- TRUE
for (nm in names(ALL)) {
    m <- colMeans(raw[, ALL[[nm]]])
    cat(sprintf("  %-6s %s\n", nm, paste(sprintf("%.2f", m), collapse = "  ")))
    same_shape <- same_shape && (m[1] < m[2]) && (m[3] < m[4]) &&
                                (m[1] < m[4]) && (m[3] < m[2])
}
cat(sprintf("  same odd-low/even-high shape in all 5 constructs: %s\n",
            if (same_shape) "yes" else "no"))
ok_c <- (d13 < 0.10) && (d24 < 0.10) && same_shape

cat("\nWhat this does NOT establish: which of the four S2 File sentences belongs\n",
    "to which code. The S2 File prints wording but no codes; Table 2 prints codes\n",
    "but no wording. Step 5b routes are each unavailable: (1) no per-item means or\n",
    "SDs are published, only loadings, which attach to codes; (2) all four items\n",
    "share the range 1-5; (3) no total or subscale statistic depends on item order\n",
    "-- the construct IS the whole four-item scale; (4) the wording implies no\n",
    "parameter; (5) there are no subscales; (6) no reverse-worded item (item-rest r\n",
    "all positive, above); (7) no marker item is predicted; (8) the only visible\n",
    "mean structure is the deposit-wide odd/even artifact printed above, and the\n",
    "within-pair gaps are under 0.10; (9) the source stores 1-5 integers, not\n",
    "labels, and no option_text was shipped. All 24 permutations of item_text\n",
    "survive every check here. Hence NO_ROUTE.\n", sep = "")

cat(if (ok_a && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
