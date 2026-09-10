# verify_mpsycho_avlancheprep.R -- Step 5b evidence, re-runnable.
#
# CLAIM 1 (item axis): each IRW `item` code is the AvalanchePrep column of the same
#   name, and the shipped item_text is that column's own .Rd label.
#   Falsifiable prediction: the per-item x per-level response counts in the live IRW
#   table reproduce, cell for cell, the counts of the identically named column in
#   MPsychoR::AvalanchePrep. Swapping item_text between `info` and `discuss` (the two
#   4-level items) would break this, because their distributions are nothing alike.
#
# CLAIM 2 (option axis): resp level k is the k-th response category as listed, in
#   order, in the AvalanchePrep .Rd Description -- i.e. all four items run
#   most-prepared (1) to least-prepared (max). The .Rd does not print "1 = ...", so
#   this is an inference from listing order. Falsifiable prediction: under that
#   reading all four preparedness items must intercorrelate POSITIVELY; if any single
#   item's categories were listed in the reverse order to their coding, that item
#   would correlate negatively with the other three.
#
# What this does NOT establish: the internal order of the middle categories within an
# item (discuss 2 vs 3; gear 2 vs 3 vs 4; info 2 vs 3). Those rest on the .Rd's
# listing order alone. Hence PARTIAL, not VERIFIED, on the option axis.

suppressMessages(library(irw))

TABLE <- "mpsycho_avlancheprep"
ok <- TRUE

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(as.character(d$resp))

utils::data("AvalanchePrep", package = "MPsychoR")
x <- get("AvalanchePrep")

## ---- CLAIM 1: cell-for-cell count match, live vs package column ----
cat("== item axis: live IRW counts vs MPsychoR::AvalanchePrep column counts ==\n")
cat(sprintf("%-10s %6s %10s %10s %6s\n", "item", "resp", "n_live", "n_package", "ok"))
n_cells <- 0; n_match <- 0
for (it in sort(names(x))) {
    tt <- table(x[[it]])
    for (lv in names(tt)) {
        n_pkg  <- as.integer(tt[[lv]])
        n_live <- sum(d$item == it & d$resp == as.numeric(lv))
        hit <- identical(n_live, n_pkg)
        n_cells <- n_cells + 1; n_match <- n_match + hit
        cat(sprintf("%-10s %6s %10d %10d %6s\n", it, lv, n_live, n_pkg,
                    if (hit) "OK" else "MISMATCH"))
    }
}
cat(sprintf("\ncells matching: %d/%d\n", n_match, n_cells))
if (n_match != n_cells) ok <- FALSE

## ---- CLAIM 2: polarity under the .Rd's listed category order ----
cat("\n== option axis: Spearman correlations under the .Rd listing order ==\n")
xn <- as.data.frame(lapply(x, function(f) as.numeric(as.character(f))))
cm <- cor(xn, method = "spearman", use = "pairwise.complete.obs")
print(round(cm, 3))
offdiag <- cm[upper.tri(cm)]
cat(sprintf("\noff-diagonal range: %.3f to %.3f; all positive: %s\n",
            min(offdiag), max(offdiag), all(offdiag > 0)))
if (!all(offdiag > 0)) ok <- FALSE

cat("\nNote: the correlation route fixes each item's DIRECTION only. It does not\n",
    "separate the middle categories within an item; those follow the .Rd's listing\n",
    "order and are recorded as PARTIAL.\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
