# verify_liu_2023_attitude.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST (mapping_basis = paper_order): the three sentences shipped as item_text
# are the S1 File (pone.0295133.s002) "Attitudes toward agricultural products' regional
# public brand" block, assigned to ATT1..ATT3 in listing order. The IRW code IS the S1 Data
# (.s001 xlsx) column name (data/liu_2023_brand_trust.py selects ^ATT\d+$ by name), and the
# annex lists the block under its construct heading without codes. So there are two links:
#   (a) block: xlsx ATT columns = the paper's Attitude construct = the annex Attitudes block;
#   (b) order: ATT1/2/3 = the 1st/2nd/3rd sentence of that block.
#
# ROUTE 3 (published construct statistics) + structural paths, for link (a).
# Liu & Wang (2023) PLOS ONE 18(11):e0295133. Table 2 prints per construct Cronbach's
# alpha / CR / AVE; Table 5 prints the standardized SEM paths. Refitting the paper's model
# on the six live liu_2023_* tables must reproduce both, with the ATT block landing on the
# published Attitude row and nowhere else.
#
# SOURCE DEFECT this script also documents: Table 2's per-ITEM loadings for the three
# 3-item TPB blocks are printed one row-block off. The published "ATT1-3" loadings
# (.742/.755/.807) are the data's SN loadings, the published "SN" row (.785/.838/.813) is
# the data's PBC, and the published "PBC" row (.743/.796/.726) is the data's ATT. The
# construct-level alpha/CR/AVE on those same rows, and all of Table 5, match the data's own
# column labels -- and relabelling the data to follow the loading rows breaks Table 5
# (BT->ATT 0.095 vs published 0.428). So the misprint is in the loading column, not the data.
#
# WHAT THIS DOES NOT ESTABLISH: link (b). The annex prints the three Attitude sentences
# unnumbered, and nothing published separates them per item (the loading column is the
# only per-item statistic and it is misprinted; no item means are reported). Order within
# the block rests on listing order alone. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABS <- c(BT = "liu_2023_brand_trust", ATT = "liu_2023_attitude",
          SN = "liu_2023_subjective_norm", PBC = "liu_2023_perceived_control",
          PI = "liu_2023_purchase_intention", PB = "liu_2023_purchase_behavior")
w <- NULL
for (k in names(TABS)) {
    d <- as.data.frame(irw::irw_fetch(TABS[[k]])[, c("id", "item", "resp")])
    wk <- reshape(d, idvar = "id", timevar = "item", direction = "wide")
    names(wk) <- sub("^resp\\.", "", names(wk))
    w <- if (is.null(w)) wk else merge(w, wk, by = "id")
}
cat(sprintf("live data: %d respondents x %d items (six liu_2023_* tables joined on id)\n\n",
            nrow(w), ncol(w) - 1))

bl <- list(BT = paste0("BT", 1:4), ATT = paste0("ATT", 1:3), SN = paste0("SN", 1:3),
           PBC = paste0("PBC", 1:3), PI = paste0("PI", 1:3), PB = paste0("PB", 1:3))
meas <- paste(sapply(names(bl), function(k) paste0(k, " =~ ", paste(bl[[k]], collapse = " + "))),
              collapse = "\n")
f <- lavaan::sem(paste0(meas, "\nATT ~ BT + SN\nPI ~ BT + ATT + SN + PBC\nPB ~ BT + PI\n"), data = w)
ss <- lavaan::standardizedSolution(f)
L <- ss[ss$op == "=~", ]

alpha <- function(v) { k <- length(v); S <- cov(w[, v]); k / (k - 1) * (1 - sum(diag(S)) / sum(S)) }
obs <- t(sapply(names(bl), function(k) {
    l <- L$est.std[L$lhs == k]
    c(alpha = alpha(bl[[k]]), CR = sum(l)^2 / (sum(l)^2 + sum(1 - l^2)), AVE = mean(l^2))
}))
# Table 2, construct-level columns (alpha, CR, AVE), in the paper's row order.
PUB <- rbind(BT = c(0.875, 0.876, 0.639), ATT = c(0.798, 0.799, 0.571),
             SN = c(0.810, 0.812, 0.591), PBC = c(0.852, 0.853, 0.660),
             PI = c(0.809, 0.809, 0.586), PB = c(0.863, 0.867, 0.687))

cat("ROUTE 3 -- live ATT block (alpha, CR, AVE) against every published construct row\n")
cat(sprintf("  live ATT: alpha %.3f  CR %.3f  AVE %.3f\n", obs["ATT", 1], obs["ATT", 2], obs["ATT", 3]))
dev <- apply(PUB, 1, function(p) max(abs(obs["ATT", ] - p)))
for (k in rownames(PUB))
    cat(sprintf("  vs published %-4s %.3f/%.3f/%.3f  max|diff| %.4f\n", k, PUB[k, 1], PUB[k, 2], PUB[k, 3], dev[k]))
best <- names(which.min(dev))
cat(sprintf("  best match: %s (%.4f); runner-up %s (%.4f)\n\n", best, min(dev),
            names(sort(dev))[2], sort(dev)[2]))

cat("Table 5 standardized paths (published vs live)\n")
PATHS <- data.frame(lhs = c("ATT", "PI", "PB", "PI", "ATT", "PI", "PI", "PB"),
                    rhs = c("BT", "BT", "BT", "ATT", "SN", "SN", "PBC", "PI"),
                    pub = c(0.428, 0.194, 0.417, 0.329, 0.342, 0.057, 0.373, 0.293))
R <- ss[ss$op == "~", ]
PATHS$obs <- sapply(seq_len(nrow(PATHS)), function(i)
    R$est.std[R$lhs == PATHS$lhs[i] & R$rhs == PATHS$rhs[i]])
for (i in seq_len(nrow(PATHS)))
    cat(sprintf("  %-3s -> %-3s  pub %.3f  live %.3f  diff %+.4f\n", PATHS$rhs[i], PATHS$lhs[i],
                PATHS$pub[i], PATHS$obs[i], PATHS$obs[i] - PATHS$pub[i]))
pdev <- max(abs(PATHS$obs - PATHS$pub))
cat(sprintf("  largest path deviation: %.4f\n\n", pdev))

cat("SOURCE DEFECT -- Table 2 per-item loadings vs live loadings (3-item TPB blocks)\n")
PUBL <- list(ATT = c(0.742, 0.755, 0.807), SN = c(0.785, 0.838, 0.813), PBC = c(0.743, 0.796, 0.726))
for (k in names(PUBL)) {
    cat(sprintf("  published %-3s row %s", k, paste(sprintf("%.3f", PUBL[[k]]), collapse = "/")))
    m <- sapply(c("ATT", "SN", "PBC"), function(j) max(abs(L$est.std[L$lhs == j] - PUBL[[k]])))
    cat(sprintf("  -> matches live %s (max|diff| %.4f)\n", names(which.min(m)), min(m)))
}
cat("  (construct-level stats and Table 5 follow the data labels; the loading column does not)\n\n")

cat("SCOPE. Establishes that the live ATT1-ATT3 columns are the paper's Attitude construct, so\n")
cat("the annex's Attitudes block is the right three sentences. Does NOT establish which of the\n")
cat("three sentences is ATT1 vs ATT2 vs ATT3: that rests on listing order. PARTIAL.\n")
ok <- best == "ATT" && min(dev) <= 0.002 && sort(dev)[2] > 0.005 && pdev <= 0.005
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
