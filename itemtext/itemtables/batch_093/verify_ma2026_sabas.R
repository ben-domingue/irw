# verify_ma2026_sabas.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: live item code sabasK carries the wording of SABAS item K
# (K = 1..6) as numbered in Csibi, Griffiths, Cook, Demetrovics & Szabo (2018)
# Appendix 1, and as numbered by Ma, An, Chen & Liu (2026) Table 6.
#
# ROUTE 1 (per-item published statistics), in its strongest form. The source
# preprint's Table 6 publishes a full graded-response-model solution per item --
# one discrimination and FIVE difficulty thresholds, i.e. six numbers per item,
# 36 in all. Refitting the same model (unidimensional GRM, EM) on the live IRW
# data and recovering Table 6 item-for-item is a falsifiable per-item
# prediction: if item_text for any two items were swapped, that item's
# six-number signature would land on the other item's row. Item-specificity is
# tested explicitly below (nearest published row for each live item).
#
# The chain from a Table 6 row number to a WORDING is Table 6's own per-row
# content labels -- "Most important thing", "Conflicts have arisen",
# "Preoccupying myself", "Fiddle around more", "Irritable", "Fail to use less" --
# each of which is a fragment of exactly one item of the canonical SABAS
# (Csibi et al. 2018, Appendix 1, CC BY 4.0), in that order. So the row number
# -> wording step is explicit in the source, and this script tests the remaining
# step, live item code -> row number.
#
# SECOND AXIS (option_text <-> resp) is NOT an inference and is not tested
# statistically: Csibi et al. (2018) Appendix 1 prints the numerals 1..6 under
# the anchors Strongly Disagree / Disagree / Slightly Disagree / Slightly Agree /
# Agree / Strongly Agree, and the preprint states "Higher scores indicate
# greater addiction risk". A direction sanity check is printed anyway (all six
# GRM thresholds increase with resp, so higher resp = more of the trait the
# paper calls addiction severity), but it is a corroboration, not the basis.
#
# NOT ESTABLISHED by this script: the administered CHINESE wording. Neither the
# figshare deposit (one file, rawdata_.csv, bare headers, zero CJK characters)
# nor the Research Square preprint (zero CJK characters) publishes it, so the
# canonical English ships as a translated_substitute.
#
# NOTE ON THE PREPRINT'S PROSE: two sentences in the Results contradict its own
# Table 6 (it lists the discriminations "from highest to lowest: 1, 3, 6, 2, 4,
# 5", which is the ascending order, and says item 2 had "the highest difficulty
# for 'strongly agree'" when Table 6 gives item 1 the largest beta5). Those
# sentences are therefore NOT used as tests here; the 36 tabulated numbers are.

suppressMessages({library(irw); library(mirt)})

TABLE <- "ma2026_sabas"

# Ma, An, Chen & Liu (2026), Research Square rs-9429022 v1, Table 6.
PUB_A <- c(1.47, 2.10, 1.69, 2.45, 2.48, 2.09)
PUB_B <- rbind(c( 0.10, 0.87, 1.62, 2.43, 3.03),
               c( 0.74, 1.25, 1.66, 2.10, 2.75),
               c(-0.04, 0.68, 1.22, 2.00, 2.67),
               c( 0.27, 0.99, 1.40, 2.01, 2.54),
               c( 0.46, 1.01, 1.35, 1.89, 2.36),
               c( 0.31, 1.04, 1.46, 1.72, 2.23))
TOL <- 0.06

# The live table is 6,648 rows (6 items x 1,108 respondents); the fetch is
# ~0.1 MB against the 200GB/30-day export cap.
d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, paste0("sabas", 1:6)]

m   <- mirt(w, 1, itemtype = "graded", verbose = FALSE,
            technical = list(NCYCLES = 2000))
est <- coef(m, simplify = TRUE, IRTpars = TRUE)$items[paste0("sabas", 1:6), ]

cat("Per-item GRM parameters: published (Table 6) vs refit on live IRW data\n\n")
cat(sprintf("%-8s %-6s %6s %6s %6s %6s %6s %6s\n",
            "item", "src", "alpha", "beta1", "beta2", "beta3", "beta4", "beta5"))
for (i in 1:6) {
    cat(sprintf("%-8s %-6s %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n",
                paste0("sabas", i), "pub", PUB_A[i], PUB_B[i, 1], PUB_B[i, 2],
                PUB_B[i, 3], PUB_B[i, 4], PUB_B[i, 5]))
    cat(sprintf("%-8s %-6s %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f\n",
                "", "live", est[i, "a"], est[i, "b1"], est[i, "b2"],
                est[i, "b3"], est[i, "b4"], est[i, "b5"]))
}

dev <- max(abs(c(est[, "a"] - PUB_A,
                 as.vector(est[, paste0("b", 1:5)]) - as.vector(PUB_B))))
cat(sprintf("\nlargest absolute deviation across all 36 parameters: %.4f (tolerance %.2f)\n",
            dev, TOL))

# Is the fit item-specific, or would any permutation do? Compare each live
# item's 6-number signature against every published row; the best match must be
# its own row, and by a wide margin.
sig  <- cbind(est[, "a"], est[, paste0("b", 1:5)])
pubs <- cbind(PUB_A, PUB_B)
D    <- as.matrix(dist(rbind(sig, pubs)))[1:6, 7:12]
best <- apply(D, 1, which.min)
cat("\nnearest published row for each live item (diagonal = correct mapping):\n")
cat(sprintf("  sabas%d -> published item %d  (self %.3f, next-best %.3f)\n",
            1:6, best, diag(D), apply(D, 1, function(r) sort(r)[2])), sep = "")
perm_ok <- all(best == 1:6)

# Corroboration only -- option direction. Anchors are published against the
# numerals 1..6 by Csibi et al. (2018), so this is a sanity check, not the basis.
mono_ok <- all(apply(est[, paste0("b", 1:5)], 1, function(b) all(diff(b) > 0)))
cat(sprintf("\nGRM thresholds increase with resp for all 6 items: %s\n",
            if (mono_ok) "yes" else "NO"))
cat(sprintf("per-item means %s (scale mean %.2f vs preprint Table 2 mean 1.88, SD 1.33)\n",
            paste(sprintf("%.2f", colMeans(w)), collapse = " "), mean(colMeans(w))))

cat("\nNot established here: the administered Chinese wording (published nowhere\n",
    "in the deposit or the preprint; canonical English ships as a\n",
    "translated_substitute).\n", sep = "")

cat(if (dev <= TOL && perm_ok && mono_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
