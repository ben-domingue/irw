# verify_ma2026_bsmas.R -- Step 5b mapping verification.
#
# CLAIM UNDER TEST: live item code bsmasK carries the wording of BSMAS item K
# (K = 1..6) as numbered in Ma, An, Chen & Liu (2026) Table 5.
#
# ROUTE 1 (per-item published statistics), in its strongest form: the source
# preprint publishes a full graded-response-model solution per item -- one
# discrimination and four difficulty thresholds, i.e. five numbers per item.
# Refitting the same model (unidimensional GRM, EM) on the live IRW data and
# recovering Table 5 item-for-item is a falsifiable per-item prediction: if
# item_text for any two items were swapped, that item's five-number signature
# would land on the other item's row. The signatures are well separated -- e.g.
# items 2 and 3 tie on alpha (1.69 vs 1.70) but differ by 0.73 on beta1 --
# so no pair of items is confusable.
#
# The chain from a Table 5 row number to a WORDING is Table 5's own construct
# labels (Salience / Craving-tolerance / Mood modification / Relapse-loss of
# control / Withdrawal / Conflict), which are the six addiction-components
# criteria in canonical BSMAS order; each component is realised by exactly one
# BSMAS item, so the label pins the item. Corroborated independently by the
# Swedish BSMAS validation (PMC13191657), which quotes items 1, 2, 5 and 6 with
# those numbers and the same wordings shipped here.
#
# ALSO CHECKED: the option_text <-> resp direction. The preprint states "item 2
# exhibited the lowest difficulty for the response category 'very rarely'" and
# "item 3 showed the highest difficulty for 'very often'". If resp 1 = "Very
# rarely" and resp 5 = "Very often" (as shipped), those two sentences are
# predictions about beta1 and beta4, and both are tested below.
#
# NOT ESTABLISHED by this script: the administered CHINESE wording (the deposit
# and the preprint carry none, so English canonical wording is shipped as a
# translated_substitute), and the exact English rendering -- the BSMAS
# circulates in an interrogative form (shipped) and a declarative one.

suppressMessages({library(irw); library(mirt)})

TABLE <- "ma2026_bsmas"

# Ma, An, Chen & Liu (2026), Research Square rs-9429022 v1, Table 5.
PUB_A  <- c(1.88, 1.69, 1.70, 1.62, 1.64, 1.38)
PUB_B  <- rbind(c(0.33, 1.29, 2.44, 3.37),
                c(0.26, 1.30, 2.44, 3.34),
                c(0.99, 1.95, 2.83, 3.43),
                c(0.37, 1.16, 1.96, 3.02),
                c(0.50, 1.30, 2.13, 2.80),
                c(0.80, 1.61, 2.47, 3.00))
TOL <- 0.06

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
w <- w[, paste0("bsmas", 1:6)]

m   <- mirt(w, 1, itemtype = "graded", verbose = FALSE, technical = list(NCYCLES = 2000))
est <- coef(m, simplify = TRUE, IRTpars = TRUE)$items[paste0("bsmas", 1:6), ]

cat("Per-item GRM parameters: published (Table 5) vs refit on live IRW data\n\n")
cat(sprintf("%-8s %-6s %6s %6s %6s %6s %6s\n",
            "item", "src", "alpha", "beta1", "beta2", "beta3", "beta4"))
for (i in 1:6) {
    cat(sprintf("%-8s %-6s %6.2f %6.2f %6.2f %6.2f %6.2f\n",
                paste0("bsmas", i), "pub", PUB_A[i], PUB_B[i, 1], PUB_B[i, 2],
                PUB_B[i, 3], PUB_B[i, 4]))
    cat(sprintf("%-8s %-6s %6.2f %6.2f %6.2f %6.2f %6.2f\n",
                "", "live", est[i, "a"], est[i, "b1"], est[i, "b2"],
                est[i, "b3"], est[i, "b4"]))
}

dev <- max(abs(c(est[, "a"] - PUB_A, as.vector(est[, paste0("b", 1:4)]) - as.vector(PUB_B))))
cat(sprintf("\nlargest absolute deviation across all 30 parameters: %.3f (tolerance %.2f)\n",
            dev, TOL))

# Is the fit item-specific, or would any permutation do? Compare each live item's
# 5-number signature against every published row and check the best match is itself.
sig  <- cbind(est[, "a"], est[, paste0("b", 1:4)])
pubs <- cbind(PUB_A, PUB_B)
D    <- as.matrix(dist(rbind(sig, pubs)))[1:6, 7:12]
best <- apply(D, 1, which.min)
cat("\nnearest published row for each live item (diagonal = correct mapping):\n")
cat(sprintf("  bsmas%d -> published item %d  (self %.3f, next-best %.3f)\n",
            1:6, best, diag(D), apply(D, 1, function(r) sort(r)[2])), sep = "")
perm_ok <- all(best == 1:6)

# Option direction: resp 1 = "Very rarely", resp 5 = "Very often".
b1_ok <- which.min(est[, "b1"]) == 2   # "item 2 ... lowest difficulty for 'very rarely'"
b4_ok <- which.max(est[, "b4"]) == 3   # "item 3 ... highest difficulty for 'very often'"
cat(sprintf("\noption direction: lowest beta1 is item %d (preprint says item 2, 'very rarely') -- %s\n",
            which.min(est[, "b1"]), if (b1_ok) "ok" else "MISMATCH"))
cat(sprintf("option direction: highest beta4 is item %d (preprint says item 3, 'very often') -- %s\n",
            which.max(est[, "b4"]), if (b4_ok) "ok" else "MISMATCH"))

cat("\nNot established here: the administered Chinese wording (not published anywhere\n",
    "in the deposit or the preprint), and which of the two circulating English\n",
    "renderings of the BSMAS this study translated from.\n", sep = "")

cat(if (dev <= TOL && perm_ok && b1_ok && b4_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
