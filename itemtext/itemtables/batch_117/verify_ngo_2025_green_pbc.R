# verify_ngo_2025_green_pbc.R -- Step 5b re-runnable evidence.
#
# STATUS RECORDED: NO_ROUTE for the item_text <-> item axis.
#
# The claim under test is that the S2 File ("Research instruments",
# 10.1371/journal.pone.0323879.s002) lists the four Green perceived behavioural
# control items in the order G_PBC_1 .. G_PBC_4.  The S2 File prints NO item
# codes and the paper's Table 2 prints codes but NO wording, so the two cannot
# be joined and that order assumption is not testable.  This script therefore
# (a) establishes the half of the mapping that IS exact -- live item codes are
# the source file's own column headers, verified cell-for-cell -- and
# (b) demonstrates positively that no statistical route can separate the items,
# so that "couldn't check" does not read as "checked".
#
# PASS means (a) reproduces and (b) still holds; it does NOT mean any wording
# was verified.

suppressMessages(library(irw))

TABLE <- "ngo_2025_green_pbc"
ITEMS <- c("G_PBC_1", "G_PBC_2", "G_PBC_3", "G_PBC_4")

# Published PLS loadings, paper Table 2 (10.1371/journal.pone.0323879.t002).
PUB_LOADING <- c(G_PBC_1 = 0.833, G_PBC_2 = 0.850, G_PBC_3 = 0.873, G_PBC_4 = 0.831)

S1 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0323879.s001")

raw <- read.csv(S1, check.names = FALSE)
names(raw) <- sub("^﻿", "", names(raw))
d   <- irw::irw_fetch(TABLE)

cat("== (a) live item codes vs S1 File column headers: full 1-5 frequency table ==\n")
cat(sprintf("%-9s %-22s %-22s %s\n", "item", "S1 column counts", "live counts", "match"))
ok_a <- TRUE
for (it in ITEMS) {
    r <- table(factor(raw[[it]], levels = 1:5))
    l <- table(factor(d$resp[d$item == it], levels = 1:5))
    m <- identical(as.integer(r), as.integer(l))
    ok_a <- ok_a && m
    cat(sprintf("%-9s %-22s %-22s %s\n", it,
                paste(as.integer(r), collapse = "/"),
                paste(as.integer(l), collapse = "/"),
                if (m) "yes" else "NO"))
}

cat("\n== (b) no statistical route separates the four items ==\n")
mu <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
tot <- rowSums(raw[, ITEMS])
ir  <- sapply(ITEMS, function(it) cor(raw[[it]], tot - raw[[it]]))
cat(sprintf("%-9s %8s %12s %12s\n", "item", "mean", "item-rest r", "pub loading"))
for (it in ITEMS)
    cat(sprintf("%-9s %8.3f %12.3f %12.3f\n", it, mu[it], ir[it], PUB_LOADING[it]))

d13 <- abs(mu["G_PBC_1"] - mu["G_PBC_3"])
d24 <- abs(mu["G_PBC_2"] - mu["G_PBC_4"])
cat(sprintf("\n|mean(1) - mean(3)| = %.3f ; |mean(2) - mean(4)| = %.3f\n", d13, d24))
cat(sprintf("Spearman(published loading, observed item-rest r) = %.2f over 4 items\n",
            cor(PUB_LOADING[ITEMS], ir[ITEMS], method = "spearman")))
ok_b <- (d13 < 0.10) && (d24 < 0.10)

cat("\nWhat this does NOT establish: which of the four S2 File sentences belongs to\n",
    "which code. Table 2 ties codes to loadings but prints no wording; the S2 File\n",
    "prints wording but no codes; the items are near-tied in every observable\n",
    "statistic (above), all share one 1-5 range, form a single unidimensional\n",
    "construct with no reverse-worded item and no published per-item mean, and the\n",
    "source stores integers rather than labels -- so Step 5b routes 1-9 are each\n",
    "unavailable. Hence NO_ROUTE, not PARTIAL.\n", sep = "")

cat(if (ok_a && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
