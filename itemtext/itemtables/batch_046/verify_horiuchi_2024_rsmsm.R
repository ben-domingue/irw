# verify_horiuchi_2024_rsmsm.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: MSM1..MSM12 carry the twelve Factor-1 items of the paper's
# S4 Table (in that table's printed order) and MSM13..MSM20 its eight Factor-2
# items. Two falsifiable predictions follow from that claim.
#
#  (A) Per-item loadings. S6 Table publishes the Survey-2 CFA standardized
#      loading and SE for every item as F1-1..F1-12 / F2-1..F2-8. Refitting that
#      CFA on the live IRW data under the claimed assignment must reproduce each
#      published value item by item.
#  (B) The partition itself. The claimed 12/8 split of the 20 items must fit
#      better than randomly chosen 12/8 splits of the same items.
#
# What this does NOT establish: several published loadings tie to within ~0.005
# (F1-2/F1-3/F1-4 = .842/.834/.835; F1-7/F1-9 = .517/.520; F2-2/F2-6 = .859/.860;
# F2-4/F2-8 = .841/.836), so (A) cannot separate items *within* those near-tied
# clusters, and (B) speaks to the partition, not to order inside a block.
# Block membership and the items with distinctive loadings are pinned; the order
# of the near-tied clusters rests on the S4 Table's printed order alone. PARTIAL.

suppressMessages(library(irw))
suppressMessages(library(lavaan))

TABLE <- "horiuchi_2024_rsmsm"
ITEMS <- paste0("MSM", 1:20)
NPERM <- 200
set.seed(1)

# PLOS ONE 10.1371/journal.pone.0298214, S6 Table (CFA of RS-MSM items, Survey 2).
PUB    <- c(0.653,0.842,0.834,0.835,0.776,0.621,0.517,0.246,0.520,0.806,0.457,0.297,
            0.528,0.859,0.810,0.841,0.475,0.860,0.645,0.836)
PUB_SE <- c(.057,.030,.042,.051,.081,.087,.093,.083,.099,.048,.089,.103,
            .099,.038,.049,.036,.100,.035,.086,.043)
TOL <- 0.05

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
X <- w[, ITEMS]
cat(sprintf("live data: %d respondents x %d items\n\n", nrow(X), ncol(X)))

mk <- function(g1) paste("F1 =~", paste(ITEMS[g1], collapse = " + "), "\n",
                         "F2 =~", paste(ITEMS[-g1], collapse = " + "))
fit <- lavaan::cfa(mk(1:12), data = X, std.lv = TRUE, estimator = "MLR")
s <- lavaan::standardizedSolution(fit); s <- s[s$op == "=~", ]
obs    <- s$est.std[match(ITEMS, s$rhs)]
obs_se <- s$se[match(ITEMS, s$rhs)]

lab <- c(sprintf("F1-%d", 1:12), sprintf("F2-%d", 1:8))
cat("(A) per-item standardized loading, live refit vs S6 Table\n")
cat(sprintf("%-6s %-6s %9s %9s %8s %9s %9s\n",
            "item","S6 row","published","observed","diff","pub SE","obs SE"))
for (i in seq_along(ITEMS))
  cat(sprintf("%-6s %-6s %9.3f %9.3f %8.3f %9.3f %9.3f\n",
              ITEMS[i], lab[i], PUB[i], obs[i], obs[i] - PUB[i], PUB_SE[i], obs_se[i]))
worst <- max(abs(obs - PUB))
cat(sprintf("largest deviation: %.3f (tolerance %.2f); r(obs, published) = %.4f\n\n",
            worst, TOL, cor(obs, PUB)))

cat("(B) claimed 12/8 partition vs random 12/8 partitions of the same 20 items\n")
base_cfi <- unname(lavaan::fitMeasures(fit, "cfi"))
perm <- rep(NA_real_, NPERM)
for (k in seq_len(NPERM)) {
  g <- sample(20, 12)
  f <- try(suppressWarnings(lavaan::cfa(mk(g), data = X, std.lv = TRUE,
                                        estimator = "MLR")), silent = TRUE)
  if (!inherits(f, "try-error") && lavaan::lavInspect(f, "converged"))
    perm[k] <- unname(lavaan::fitMeasures(f, "cfi"))
}
nbeat <- sum(perm >= base_cfi, na.rm = TRUE); nok <- sum(!is.na(perm))
cat(sprintf("claimed split CFI %.4f | random splits (n=%d): mean %.4f, max %.4f, >= claimed: %d\n",
            base_cfi, nok, mean(perm, na.rm = TRUE), max(perm, na.rm = TRUE), nbeat))
cat(sprintf("published Survey-2 fit: CFI 0.858 TLI 0.840 SRMR 0.069 | live refit (robust): CFI %.3f TLI %.3f SRMR %.3f\n\n",
            unname(lavaan::fitMeasures(fit, "cfi.robust")),
            unname(lavaan::fitMeasures(fit, "tli.robust")),
            unname(lavaan::fitMeasures(fit, "srmr"))))

cat("Note: pins block membership and the distinctively-loading items; does NOT\n",
    "separate the near-tied within-block clusters listed in the header.\n", sep = "")

cat(if (worst <= TOL && nbeat == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
