# verify_ngo_2025_green_purchase_behavior.R
#
# Claim under test (mapping_basis = paper_order): the four sentences listed under
# "Green purchasing behavior" in S2 File of Ngo & Nguyen (2025), PLOS ONE
# 10.1371/journal.pone.0323879, correspond IN THE ORDER PRINTED to the live item
# codes G_PB_1..G_PB_4. The S2 supplement prints no codes beside the wording, so the
# within-block order is inferred and this script is what tests it.
#
# Two independent checks, both against numbers published in the paper's own Table 2
# (an image table; values transcribed 2026-09-09) and against a semantic prediction
# that would break if a "low-endorsement" sentence were attached to a "high" code.

suppressMessages(library(irw))
TABLE <- "ngo_2025_green_purchase_behavior"
ITEMS <- paste0("G_PB_", 1:4)

# Published, paper Table 2 ("Measurement model's validity and reliability"), G_PB block.
PUB_LOADING <- c(G_PB_1 = 0.854, G_PB_2 = 0.847, G_PB_3 = 0.872, G_PB_4 = 0.857)
PUB_ALPHA   <- 0.880

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))
X <- as.matrix(w[, ITEMS, drop = FALSE])
X <- X[complete.cases(X), , drop = FALSE]
cat(sprintf("n complete cases: %d (paper: 237)\n\n", nrow(X)))

## --- Check 1: block identity -------------------------------------------------
# Cronbach alpha and first-principal-component loadings for the four live columns,
# against the values the paper prints for its G_PB construct. This establishes that
# these four columns ARE the paper's G_PB indicators (and not, say, a G_PI item
# swapped in), and it ties each live column to the paper's own code.
k <- ncol(X)
alpha <- (k / (k - 1)) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
Z <- scale(X)
pc <- svd(Z)$v[, 1]
score <- as.numeric(Z %*% pc)
load <- abs(apply(X, 2, function(x) cor(x, score)))

cat(sprintf("Cronbach alpha  published %.3f   observed %.3f   diff %.3f\n\n",
            PUB_ALPHA, alpha, alpha - PUB_ALPHA))
cat(sprintf("%-8s %10s %10s %8s\n", "item", "published", "observed", "diff"))
for (i in ITEMS)
  cat(sprintf("%-8s %10.3f %10.3f %8.3f\n", i, PUB_LOADING[[i]], load[[i]],
              load[[i]] - PUB_LOADING[[i]]))
rank_ok <- identical(order(-load), order(-PUB_LOADING))
cat(sprintf("\nloading rank order (published %s / observed %s; identical: %s)\n",
            paste(ITEMS[order(-PUB_LOADING)], collapse = ">"),
            paste(ITEMS[order(-load)], collapse = ">"), rank_ok))
cat("  -- rank order is NOT part of the pass criterion: the published values are PLS\n",
    "  outer loadings and the observed ones are first-PC correlations, and the\n",
    "  G_PB_1/G_PB_4 pair differs by 0.003 published and 0.002 observed, well inside\n",
    "  the 0.006 spread between the two estimators. Magnitudes are the signal.\n", sep = "")

## --- Check 2: endorsement structure vs the assigned wording -------------------
# S2 order assigns: 1 = "deliberately check products for environmentally harmful
# ingredients", 2 = "choose products with environmentally friendly packaging",
# 3 = "buy environment-friendly products even if they are more expensive",
# 4 = "look for a certified environmental label".
# Prediction: the two costly/effortful behaviours (1 = read ingredient lists,
# 3 = pay a price premium) are less endorsed than the two low-cost ones
# (2 = notice packaging, 4 = notice a label). A mapping that attached either low
# sentence to a high-mean code would fail this.
PRED_LOW  <- c("G_PB_1", "G_PB_3")
PRED_HIGH <- c("G_PB_2", "G_PB_4")
m <- colMeans(X)
cat("\nper-item means:\n")
for (i in ITEMS) cat(sprintf("  %-8s %.3f  (%s)\n", i, m[[i]],
                             if (i %in% PRED_LOW) "predicted LOW" else "predicted HIGH"))
gap <- min(m[PRED_HIGH]) - max(m[PRED_LOW])
cat(sprintf("gap (lowest predicted-HIGH minus highest predicted-LOW): %.3f\n", gap))

cat("\nWhat this does NOT establish: the within-pair order. G_PB_1 (2.70) and G_PB_3",
    "\n(2.76) differ by 0.06 and G_PB_2 (3.76) and G_PB_4 (3.68) by 0.08, and the",
    "\npublished loadings for those pairs differ by <0.02, so swapping the two",
    "\nlow-endorsement wordings with each other -- or the two high ones -- would pass",
    "\nevery check here. 4 of the 24 possible assignments survive. Hence PARTIAL.\n")

ok <- abs(alpha - PUB_ALPHA) <= 0.005 &&
      max(abs(load[ITEMS] - PUB_LOADING[ITEMS])) <= 0.02 &&
      gap > 0.5
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
